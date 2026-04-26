import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1B5E20",
          50: "#E8F5E9",
          100: "#C8E6C9",
          200: "#A5D6A7",
          300: "#81C784",
          400: "#4CAF50",
          500: "#2E7D32",
          600: "#1B5E20",
          700: "#154A19",
          800: "#0F3712",
          900: "#0A240C",
        },
        accent: {
          DEFAULT: "#F9A825",
          50: "#FFF8E1",
          100: "#FFECB3",
          200: "#FFE082",
          300: "#FFD54F",
          400: "#FFCA28",
          500: "#F9A825",
          600: "#F57F17",
          700: "#C77800",
          800: "#9A5E00",
          900: "#6D4300",
        },
        dark: {
          DEFAULT: "#0D1B0F",
          50: "#1A2B1D",
          100: "#162519",
          200: "#121F15",
          300: "#0D1B0F",
          400: "#0A1509",
          500: "#070F07",
        },
        success: "#2E7D32",
        danger: "#C62828",
        neutral: {
          DEFAULT: "#424242",
          light: "#E8F5E9",
        },
      },
      fontFamily: {
        sans: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-syne)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "ui-monospace", "monospace"],
      },
      backgroundImage: {
        "hero-radial":
          "radial-gradient(ellipse 80% 60% at 50% 0%, rgba(249,168,37,0.18), transparent 70%)",
        "gold-gradient":
          "linear-gradient(135deg, #F9A825 0%, #FFCA28 50%, #F9A825 100%)",
      },
      boxShadow: {
        glow: "0 0 40px rgba(249,168,37,0.25)",
        "glow-green": "0 0 40px rgba(27,94,32,0.45)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.6s ease-out",
        "slide-up": "slideUp 0.6s ease-out",
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 8s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        shimmer: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
