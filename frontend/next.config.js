/** @type {import('next').NextConfig} */
const nextConfig = {
  // 禁用 React Strict Mode，避免开发模式下 WebSocket 双重挂载问题
  reactStrictMode: false,
  // 允许访问后端的静态文件
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/static/:path*',
        destination: 'http://localhost:8000/static/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
