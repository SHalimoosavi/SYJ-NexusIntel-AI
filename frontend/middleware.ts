import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// API authorization is enforced by FastAPI. The API-origin HttpOnly cookie is
// intentionally inaccessible to middleware running on the frontend origin.
export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/leads/:path*",
    "/memory/:path*",
    "/intelligence/:path*",
    "/agents/:path*",
    "/opportunities/:path*",
    "/settings/:path*",
    "/executive/:path*",
  ],
};
