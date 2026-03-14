import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getSessionCookieName, verifySessionToken } from "@/lib/auth/session";

export async function GET() {
  const cookieStore = await cookies();
  const token = cookieStore.get(getSessionCookieName())?.value;
  const session = token ? await verifySessionToken(token) : null;

  if (!session) {
    return NextResponse.json({ detail: "No active session." }, { status: 401 });
  }

  return NextResponse.json({ user: session });
}
