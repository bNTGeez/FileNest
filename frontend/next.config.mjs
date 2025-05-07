/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    config.resolve.alias.canvas = false;
    return config;
  },
  async rewrites() {
    return [
      {
        source: "/pdf.worker.min.js",
        destination: "/_next/static/worker/pdf.worker.min.js",
      },
    ];
  },
};

export default nextConfig;
