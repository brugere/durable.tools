/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable HTTP compression
  compress: true,

  // Optimize images (no external domains needed for now)
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Minify with SWC
  swcMinify: true,

  // Useful for production deployments
  output: 'standalone',

  // Add basic security and caching headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          // Ensure cross-origin requests are allowed from our domain if needed by the browser
          { key: 'Access-Control-Allow-Origin', value: 'https://eco-lavelinge.fr' },
          { key: 'Vary', value: 'Origin' },
        ],
      },
      // Cache Next.js static assets aggressively
      {
        source: '/_next/static/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
