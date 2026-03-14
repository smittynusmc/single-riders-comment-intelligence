import { NextResponse } from "next/server";

import { createSessionToken, getSessionCookieName, getSharedAccessCode, isAllowedUserEmail, normalizeEmail } from "@/lib/auth/session";

export async function POST(request: Request) {
  const payload = (await request.json().catch(() => null)) as { email?: string; accessCode?: string } | null;
  const email = normalizeEmail(payload?.email ?? "");
  const accessCode = payload?.accessCode ?? "";

  if (!email || !accessCode) {
    return NextResponse.json({ detail: "Email and access code are required." }, { status: 400 });
  }

  if (!isAllowedUserEmail(email)) {
    return NextResponse.json({ detail: "This email is not allowlisted for internal access." }, { status: 403 });
  }

  if (accessCode !== getSharedAccessCode()) {
    return NextResponse.json({ detail: "The access code is incorrect." }, { status: 401 });
  }

  const { token, session } = await createSessionToken(email);
  const response = NextResponse.json({ user: session });
  response.cookies.set({
    name: getSessionCookieName(),
    value: token,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 12,
  });
  return response;
}
