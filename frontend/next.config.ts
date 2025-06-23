import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    // Allow production builds to complete even if there are ESLint errors
    ignoreDuringBuilds: false,
    // Directories to run ESLint on during builds
    dirs: ['src'],
  },
  typescript: {
    // Allow production builds to complete even if there are TypeScript errors
    ignoreBuildErrors: false,
  },
  // Enable experimental features
  experimental: {
    // Add any experimental features here if needed
  },
};

export default nextConfig;
