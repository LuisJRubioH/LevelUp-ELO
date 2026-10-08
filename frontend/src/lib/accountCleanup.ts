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
