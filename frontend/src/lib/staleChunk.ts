/**
 * lib/staleChunk.ts
 * ==================
 * Recuperación automática cuando Vite/Vercel sirvió un chunk con hash viejo
 * tras un deploy nuevo. El cliente con la app anterior cacheada intenta
 * cargar `/assets/foo-XYZ.js` que ya no existe → "Failed to fetch dynamically
 * imported module".
 *
 * Estrategia escalonada:
 *   1ª vez en la sesión   → reload simple (rápido, normalmente basta)
 *   2ª vez en la sesión   → unregister SW + clear Cache Storage + reload
 *   3ª vez en adelante    → se rinde y deja que la UI muestre el error
 *
 * Los flags se limpian 5s después de un load exitoso, así que un incidente
 * más tarde en la misma sesión vuelve a tener todos los reintentos
 * disponibles.
 */

const FLAG_RELOAD = "levelup-chunk-reload";
const FLAG_AGGRESSIVE = "levelup-chunk-reload-aggressive";

export function isStaleChunkError(error: unknown): boolean {
  if (!error) return false;
  const msg =
    error instanceof Error
      ? error.message
      : typeof error === "object" && error !== null && "message" in error
        ? String((error as { message: unknown }).message)
        : String(error);
  return (
    msg.includes("Failed to fetch dynamically imported module") ||
    msg.includes("Importing a module script failed") ||
    msg.includes("error loading dynamically imported module") ||
    msg.includes("Loading chunk") ||
    msg.includes("Loading CSS chunk")
  );
}

async function clearCachesAndSW(): Promise<void> {
  try {
    if ("serviceWorker" in navigator) {
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map((r) => r.unregister()));
    }
  } catch {
    /* noop */
  }
  try {
    if ("caches" in window) {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
    }
  } catch {
    /* noop */
  }
}

/**
 * Intenta recuperar de un error de chunk viejo. Devuelve `true` si disparó
 * una recarga (el caller debe abortar lo que iba a hacer con el error).
 */
export function recoverFromStaleChunk(): boolean {
  if (!sessionStorage.getItem(FLAG_RELOAD)) {
    sessionStorage.setItem(FLAG_RELOAD, "1");
    window.location.reload();
    return true;
  }
  if (!sessionStorage.getItem(FLAG_AGGRESSIVE)) {
    sessionStorage.setItem(FLAG_AGGRESSIVE, "1");
    void clearCachesAndSW().finally(() => window.location.reload());
    return true;
  }
  return false;
}

/**
 * Programa la limpieza de los flags 5s después de un load exitoso para
 * que un segundo incidente en la misma sesión vuelva a recuperarse.
 */
export function startStaleChunkFlagCleanup(): void {
  const clear = () => {
    setTimeout(() => {
      try {
        sessionStorage.removeItem(FLAG_RELOAD);
        sessionStorage.removeItem(FLAG_AGGRESSIVE);
      } catch {
        /* noop */
      }
    }, 5000);
  };
  if (document.readyState === "complete") clear();
  else window.addEventListener("load", clear, { once: true });
}
