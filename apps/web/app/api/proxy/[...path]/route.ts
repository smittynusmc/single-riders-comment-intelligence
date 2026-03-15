import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { getInternalApiToken, getServerApiBaseUrl } from "@/lib/api/config";
import { getSessionCookieName, verifySessionToken } from "@/lib/auth/session";

async function buildUpstreamBody(request: NextRequest) {
  if (request.method === "GET" || request.method === "HEAD") {
    return undefined;
  }

  const contentType = request.headers.get("content-type") ?? "";
  if (contentType.includes("multipart/form-data")) {
    return request.formData();
  }
  if (contentType.includes("application/json")) {
    return request.text();
  }
  return request.arrayBuffer();
}

async function proxyRequest(request: NextRequest, pathSegments: string[]) {
  const cookieStore = await cookies();
  const token = cookieStore.get(getSessionCookieName())?.value;
  const session = token ? await verifySessionToken(token) : null;
  if (!session) {
    return NextResponse.json({ detail: "Unauthorized." }, { status: 401 });
  }

  const upstreamUrl = new URL(`/${pathSegments.join("/")}${request.nextUrl.search}`, getServerApiBaseUrl());
  const upstreamHeaders = new Headers();
  const internalApiToken = getInternalApiToken();
  if (internalApiToken) {
    upstreamHeaders.set("x-internal-api-token", internalApiToken);
  }
  upstreamHeaders.set("x-authenticated-user-email", session.email);

  const contentType = request.headers.get("content-type");
  const body = await buildUpstreamBody(request);
  if (contentType && body && !contentType.includes("multipart/form-data")) {
    upstreamHeaders.set("content-type", contentType);
  }

  const upstreamResponse = await fetch(upstreamUrl, {
    method: request.method,
    headers: upstreamHeaders,
    body,
    cache: "no-store",
  });

  const upstreamBody = await upstreamResponse.arrayBuffer();
  console.info(
    `[proxy] ${request.method} ${request.nextUrl.pathname}${request.nextUrl.search} -> ${upstreamUrl.toString()} status=${upstreamResponse.status}`,
  );

  if (!upstreamResponse.ok && upstreamResponse.status === 404) {
    return NextResponse.json(
      {
        detail: `The hosted API returned 404 for ${upstreamUrl.pathname}. Check that Railway is deployed to the latest backend code and that Vercel API_BASE_URL points to the correct Railway service.`,
      },
      { status: 404 },
    );
  }

  const responseHeaders = new Headers();
  const upstreamContentType = upstreamResponse.headers.get("content-type");
  if (upstreamContentType) {
    responseHeaders.set("content-type", upstreamContentType);
  }

  return new NextResponse(upstreamBody, {
    status: upstreamResponse.status,
    headers: responseHeaders,
  });
}

async function resolvePath(context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return path;
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, await resolvePath(context));
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, await resolvePath(context));
}

export async function PATCH(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, await resolvePath(context));
}
