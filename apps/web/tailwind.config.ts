import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#112031",
        mist: "#f4f1ea",
        sand: "#eadbc8",
        spruce: "#2c5545",
        coral: "#cf5f4f",
        gold: "#bb8a2f",
        slate: "#5d6d7e",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'IBM Plex Sans'", "sans-serif"],
      },
      boxShadow: {
        panel: "0 20px 45px rgba(17, 32, 49, 0.12)",
      },
      backgroundImage: {
        grain: "radial-gradient(circle at top, rgba(234,219,200,0.8), transparent 50%), linear-gradient(135deg, rgba(44,85,69,0.08), rgba(207,95,79,0.12))",
      },
    },
  },
  plugins: [],
};

export default config;
