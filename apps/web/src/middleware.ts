import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login", "/claim"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/_next") || pathname.startsWith("/api") || pathname.includes(".")) {
    return NextResponse.next();
  }

  const hasAccessToken = Boolean(request.cookies.get("orbis_access_token")?.value);
  const isPublicPath = PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));

  if (!hasAccessToken && !isPublicPath) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (hasAccessToken && isPublicPath) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
