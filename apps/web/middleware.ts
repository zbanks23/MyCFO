import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

// Define the routes that should be protected
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)', // Protects all routes starting with /dashboard
  '/api(.*)', // Protects all API routes
]);

export default clerkMiddleware((auth, req) => {
  // If the route is protected, run the authentication check
  if (isProtectedRoute(req)) {
    auth().protect();
  }
});

export const config = {
  // The following matcher runs middleware on all routes
  // except static assets.
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};