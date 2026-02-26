import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0f",
        foreground: "#ffffff",
        primary: {
          DEFAULT: "#8b5cf6",
          light: "#a78bfa",
          glow: "#7c3aed",
        },
        accent: {
          DEFAULT: "#23c9ff",
          dark: "#1ab3e8",
        },
        card: {
          DEFAULT: "#1a1a24",
          border: "#2a2a3a",
        },
      },
      keyframes: {
        wave: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "float-reverse": {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(10px)" },
        },
        "glow-pulse": {
          "0%, 100%": {
            opacity: "1",
            filter: "drop-shadow(0 0 8px #7c3aed)",
          },
          "50%": {
            opacity: "0.8",
            filter: "drop-shadow(0 0 20px #7c3aed)",
          },
        },
        "glow-pulse-accent": {
          "0%, 100%": {
            opacity: "1",
            filter: "drop-shadow(0 0 8px #23c9ff)",
          },
          "50%": {
            opacity: "0.8",
            filter: "drop-shadow(0 0 20px #23c9ff)",
          },
        },
      },
      animation: {
        wave: "wave 3s ease-in-out infinite",
        float: "float 3s ease-in-out infinite",
        "float-reverse": "float-reverse 3s ease-in-out infinite",
        glow: "glow-pulse 3s ease-in-out infinite",
        "glow-accent": "glow-pulse-accent 3s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;

