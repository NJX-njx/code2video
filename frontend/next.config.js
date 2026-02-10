/** @type {import('next').NextConfig} */

// Tauri 模式下使用 standalone 输出（自包含 Node.js 服务器），
// Tauri 启动时自动管理 Next.js 和 FastAPI 两个后端进程。
// Web 模式使用 rewrites 代理到 FastAPI。
const isTauri = process.env.TAURI_ENV_PLATFORM !== undefined;

const nextConfig = {
  // 禁用 React Strict Mode，避免开发模式下 WebSocket 双重挂载问题
  reactStrictMode: false,

  // 跳过尾斜杠重定向，避免 /api/projects/ 被 308 重定向后
  // 与 FastAPI 的 redirect_slashes 形成重定向循环
  skipTrailingSlashRedirect: true,

  // Tauri 模式：standalone 输出（支持动态路由）
  ...(isTauri
    ? {
        output: 'standalone',
        images: { unoptimized: true },
      }
    : {
        // Web 模式：保留 rewrites 代理
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
      }),
};

module.exports = nextConfig;
