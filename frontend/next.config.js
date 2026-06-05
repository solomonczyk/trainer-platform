/**
 * Resolve the API base URL with environment-aware fallback.
 *
 * - If NEXT_PUBLIC_API_URL is set → use it.
 * - If unset and APP_ENV is "local" or "development" → fall back to localhost.
 * - If unset and APP_ENV is staging / production → return empty (fail loudly).
 */
function getApiBaseUrl() {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (url) return url;

  const env = process.env.NEXT_PUBLIC_APP_ENV || 'development';
  if (env === 'local' || env === 'development') {
    return 'http://localhost:8000';
  }

  console.error(
    `[next.config.js] Fatal: NEXT_PUBLIC_API_URL is not set ` +
    `(environment="${env}"). API rewrites will fail.`,
  );
  return '';
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${getApiBaseUrl()}/api/:path*`,
      },
    ];
  },
  // Allow env vars at runtime via env block
  env: {
    NEXT_PUBLIC_API_URL: getApiBaseUrl(),
  },
};

module.exports = nextConfig;
