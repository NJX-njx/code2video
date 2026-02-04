import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'MathVideo - 自动化数学视频生成器',
  description: '利用 AI 和 Manim 自动生成数学讲解视频',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">{children}</body>
    </html>
  );
}
