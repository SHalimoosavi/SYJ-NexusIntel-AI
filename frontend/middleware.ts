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
"/executive",
];

export function middleware(
request: NextRequest
) {
const token =
request.cookies.get("token")?.value;

const pathname =
request.nextUrl.pathname;

const requiresAuth =
protectedRoutes.some((route) =>
pathname.startsWith(route)
);

if (
requiresAuth &&
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
"/executive/:path*",
],
};
