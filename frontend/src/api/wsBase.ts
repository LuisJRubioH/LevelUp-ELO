/**
 * api/wsBase.ts
 * =============
 * Base URL of the API's WebSockets (spec 004 E5, decision N6).
 *
 * The frontend's proxy (frontend/vercel.json) carries HTTP only. When the API is reached through
 * the frontend's own origin (VITE_API_URL empty), VITE_WS_URL points straight at the API, e.g.
 * "wss://levelup-elo.onrender.com". Without either, the page's own host (the dev proxy).
 */
export function wsBase(): string {
  const explicit = (import.meta.env.VITE_WS_URL as string | undefined) ?? "";
  const api = (import.meta.env.VITE_API_URL as string | undefined) ?? "";
  const base = (explicit || api).replace(/\/$/, "");
  if (base) return base.replace(/^https:/, "wss:").replace(/^http:/, "ws:");
  return `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`;
}
