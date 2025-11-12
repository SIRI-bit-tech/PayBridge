/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'upload.wikimedia.org',
      },
      {
        protocol: 'https',
        hostname: 'paystack.com',
      },
      {
        protocol: 'https',
        hostname: 'flutterwave.com',
      },
    ],
  },
}

export default nextConfig
