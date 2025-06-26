import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';

export default withAuth(
  function middleware(req) {
    // Allow the request to proceed
    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ token, req }) => {
        const { pathname } = req.nextUrl;

        // Always allow access to public pages and assets
        if (
          pathname.startsWith('/login') ||
          pathname.startsWith('/sign-up') ||
          pathname.startsWith('/api/auth') ||
          pathname.startsWith('/_next') ||
          pathname.startsWith('/favicon.ico') ||
          pathname === '/' ||
          pathname.startsWith('/public') ||
          pathname.includes('.')
        ) {
          return true;
        }

        // For protected routes (like dashboard), check if user has a token
        if (pathname.startsWith('/dashboard')) {
          return !!token;
        }

        // Allow all other routes by default
        return true;
      },
    },
  }
);

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes - but we handle /api/auth specifically above)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
};
