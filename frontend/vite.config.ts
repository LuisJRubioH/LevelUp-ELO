import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg", "icons.svg", "KatIA/*.png", "KatIA/*.gif"],
      manifest: {
        name: "LevelUp ELO — Plataforma Adaptativa",
        short_name: "LevelUp",
        description: "Practica matemáticas con ELO adaptativo y tutoría socrática de KatIA",
        theme_color: "#7c3aed",
        background_color: "#0f172a",
        display: "standalone",
        orientation: "portrait",
        start_url: "/student",
        scope: "/",
        icons: [
          {
            src: "/icons.svg",
            sizes: "any",
            type: "image/svg+xml",
            purpose: "any maskable",
          },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,gif,woff2}"],
        runtimeCaching: [
          {
            // Cache de la API de cursos y stats (actualizados en background)
            urlPattern: /^https?:\/\/.*\/api\/student\/(courses|stats)/,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "api-student-cache",
              expiration: { maxEntries: 10, maxAgeSeconds: 300 },
            },
          },
          {
            // Cache de preguntas (offline-ready)
            urlPattern: /^https?:\/\/.*\/api\/student\/next-question/,
            handler: "NetworkFirst",
            options: {
              cacheName: "api-questions-cache",
              expiration: { maxEntries: 20, maxAgeSeconds: 86400 },
            },
          },
        ],
      },
      devOptions: {
        enabled: false, // Desactivar SW en dev para evitar conflictos
      },
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      // Proxy todas las peticiones /api/* a FastAPI en dev
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
