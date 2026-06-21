import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = [
  "/dashboard",
  "/leads",
  "/memory",
  "/intelligence",
  "/agents",
  "/opportunities",
  "/settings",
];

export function middleware(
  request: NextRequest
) {
  const token =
    request.cookies.get("token")
      ?.value;

  const pathname =
    request.nextUrl.pathname;

  const isProtected =
    protectedRoutes.some((route) =>
      pathname.startsWith(route)
    );

  if (
    isProtected &&
    !token
  ) {
    return NextResponse.redirect(
      new URL(
        "/login",
        request.url
      )
    );
  }

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
  ],
};
