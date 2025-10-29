import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#020617",
        foreground: "#ffffff",
        accent: {
          DEFAULT: "#38bdf8",
          muted: "#0f172a",
        },
      },
    },
  },
  plugins: [],
};

export default config;
