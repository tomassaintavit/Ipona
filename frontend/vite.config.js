import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const API_TARGET = "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/auth": API_TARGET,
      "/users": API_TARGET,
      "/events": API_TARGET,
      "/predictions": API_TARGET,
      "/leaderboard": API_TARGET,
      "/stats": API_TARGET,
      "/llm": API_TARGET,
    },
  },
  build: {
    outDir: "dist",
  },
});
