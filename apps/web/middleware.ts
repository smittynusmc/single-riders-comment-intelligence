import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { getSessionCookieName, verifySessionToken } from "@/lib/auth/session";

function isPublicPath(pathname: string) {
  return pathname.startsWith("/_next") || pathname.startsWith("/favicon") || pathname.startsWith("/api/auth") || pathname === "/login";
}

export async function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (isPublicPath(pathname)) {
    const sessionToken = request.cookies.get(getSessionCookieName())?.value;
    const session = sessionToken ? await verifySessionToken(sessionToken) : null;
    if (pathname === "/login" && session) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
    return NextResponse.next();
  }

  const sessionToken = request.cookies.get(getSessionCookieName())?.value;
  const session = sessionToken ? await verifySessionToken(sessionToken) : null;
  if (session) {
    return NextResponse.next();
  }

  if (pathname.startsWith("/api/proxy")) {
    return NextResponse.json({ detail: "Unauthorized." }, { status: 401 });
  }

  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("next", `${pathname}${search}`);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
