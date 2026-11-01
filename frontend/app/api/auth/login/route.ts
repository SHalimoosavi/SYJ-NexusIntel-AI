import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const origin = request.headers.get("origin");
  if (origin !== request.nextUrl.origin) {
    return NextResponse.json({ detail: "Untrusted request origin" }, { status: 403 });
  }

  const backend = process.env.BACKEND_API_URL;
  if (!backend) {
    return NextResponse.json({ detail: "Backend API is not configured" }, { status: 503 });
  }

  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid login request" }, { status: 400 });
  }

  try {
    const upstream = await fetch(new URL("/auth/login", backend), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
      signal: AbortSignal.timeout(15000),
    });
    const data = await upstream.json().catch(() => ({}));

    if (!upstream.ok || typeof data.access_token !== "string") {
      return NextResponse.json(
        { detail: typeof data.detail === "string" ? data.detail : "Invalid credentials" },
        { status: upstream.status || 502 },
      );
    }

    const response = NextResponse.json({ success: true });
    response.cookies.set({
      name: "syj_session",
      value: data.access_token,
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60,
    });
    return response;
  } catch {
    return NextResponse.json({ detail: "Authentication service unavailable" }, { status: 502 });
  }
}
