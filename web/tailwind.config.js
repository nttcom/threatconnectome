/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  // Storybook用に重要: MUIとの競合を避けるため、特定のコンポーネントのみをターゲットに
  corePlugins: {
    preflight: false, // グローバルリセットを無効化してMUIと共存
  },
}
