import type { QueryClient } from "@tanstack/react-query";
import { usePracticeStore } from "../stores/practiceStore";
import { useSettingsStore } from "../stores/settingsStore";

/** Elimina datos autenticados que podrían sobrevivir a un cambio de cuenta. */
export async function clearAccountCaches(): Promise<void> {
  try {
    localStorage.removeItem("levelup-exam-draft");
  } catch {
    /* almacenamiento no disponible */
  }
  if (!("caches" in window)) return;
  const names = await caches.keys();
  await Promise.all(
    names
      .filter((name) => name.startsWith("api-"))
      .map((name) => caches.delete(name)),
  );
}

/**
 * Todo lo que una cuenta anterior puede dejar en este navegador: los cachés `api-*` del service
 * worker (por URL, no por usuario), el caché de React Query (sus claves no llevan el usuario), la
 * API key propia, la sesión de práctica y el borrador de examen. Corre al cerrar sesión y al
 * iniciarla: quien entra sobre una sesión abierta (un equipo compartido, /login sin salir) no ve
 * los datos de la anterior ni usa su clave.
 */
export async function resetClientAccountState(queryClient: QueryClient): Promise<void> {
  await clearAccountCaches();
  queryClient.clear();
  useSettingsStore.getState().setApiKey("");
  usePracticeStore.getState().resetSession();
}
