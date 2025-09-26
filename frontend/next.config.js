/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove 'output: export' to enable API routes
  // output: 'export', // This disables API routes - only use for static sites
  images: {
    unoptimized: true
  },
  // Optional: Enable experimental features if needed
  experimental: {
    // Add any experimental features here if needed
  }
}

module.exports = nextConfig