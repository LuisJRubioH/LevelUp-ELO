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
        // display: "browser" + start_url: "/login" hace que el navegador
        // NO ofrezca instalar la app (los estudiantes y docentes se confundían
        // con el banner "Instalar LevelUp ELO"). Service worker sigue activo
        // para caché de assets, pero la plataforma se usa solo desde browser.
        display: "browser",
        orientation: "portrait",
        start_url: "/login",
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
        // katIA.png es 6.5MB — excluirlo del precaché (se carga bajo demanda)
        globPatterns: ["**/*.{js,css,html,ico,svg,woff2}"],
        globIgnores: ["katia/**"],
        maximumFileSizeToCacheInBytes: 3 * 1024 * 1024, // 3MB
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
