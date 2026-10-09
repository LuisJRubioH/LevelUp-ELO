import type { QueryClient } from "@tanstack/react-query";
import { useAuthStore } from "../stores/authStore";
import { usePracticeStore } from "../stores/practiceStore";
import { useSettingsStore } from "../stores/settingsStore";

/** La última cuenta que inició sesión en este navegador (sobrevive a una sesión caducada). */
const LAST_ACCOUNT_KEY = "levelup-last-account";

/** Borrador de examen y cachés `api-*` del service worker; sin Cache Storage no bloquea nada. */
async function clearAccountCaches(): Promise<void> {
  try {
    localStorage.removeItem("levelup-exam-draft");
  } catch {
    /* almacenamiento no disponible */
  }
  try {
    if (!("caches" in window)) return;
    const names = await caches.keys();
    await Promise.all(
      names
        .filter((name) => name.startsWith("api-"))
        .map((name) => caches.delete(name)),
    );
  } catch {
    /* Cache Storage no disponible (p. ej. navegación privada): la sesión sigue */
  }
}

/**
 * Todo lo que una cuenta puede dejar en este navegador: los cachés `api-*` del service worker
 * (por URL, no por usuario), el caché de React Query (sus claves no llevan el usuario), la API key
 * propia, la sesión de práctica y el borrador de examen. Corre al cerrar sesión.
 */
export async function resetClientAccountState(queryClient: QueryClient): Promise<void> {
  await clearAccountCaches();
  queryClient.clear();
  useSettingsStore.getState().setApiKey("");
  usePracticeStore.getState().resetSession();
  try {
    localStorage.removeItem(LAST_ACCOUNT_KEY);
  } catch {
    /* almacenamiento no disponible */
  }
}

/**
 * Antes de guardar la sesión de `userId`. Si en este navegador había otra cuenta (una sesión
 * abierta, o la última que entró), se limpia lo que dejó: quien entra en un equipo compartido no
 * ve sus datos ni usa su API key. La misma cuenta que vuelve tras caducar su sesión conserva su
 * borrador de examen, su API key y su sesión de práctica.
 */
export async function prepareClientForAccount(
  queryClient: QueryClient,
  userId: number,
): Promise<void> {
  const current = useAuthStore.getState().user?.user_id;
  let last: string | null = null;
  try {
    last = localStorage.getItem(LAST_ACCOUNT_KEY);
  } catch {
    /* almacenamiento no disponible */
  }
  const sameAccount = current === userId || (current == null && last === String(userId));
  if (!sameAccount) await resetClientAccountState(queryClient);
  try {
    localStorage.setItem(LAST_ACCOUNT_KEY, String(userId));
  } catch {
    /* almacenamiento no disponible */
  }
}
