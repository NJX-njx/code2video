/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // 自定义颜色，与 Manim 主题协调
        'manim-bg': '#1e1e2e',
        'manim-surface': '#313244',
        'manim-accent': '#89b4fa',
        'manim-success': '#a6e3a1',
        'manim-warning': '#f9e2af',
        'manim-error': '#f38ba8',
      },
    },
  },
  plugins: [],
};
