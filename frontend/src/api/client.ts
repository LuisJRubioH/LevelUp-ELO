/**
 * api/client.ts
 * =============
 * Cliente HTTP base para comunicarse con la API FastAPI.
 * Maneja automáticamente el Bearer token del authStore.
 */

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Error de red. Se lanza cuando `fetch` falla por TypeError (sin conexión,
 * DNS, CORS o servidor caído) tras agotar los reintentos. Usa `status = 0`
 * para diferenciar de errores HTTP. El mensaje ya está en español y es
 * apto para mostrar al usuario.
 */
export class NetworkError extends ApiError {
  constructor(detail = "No pudimos conectar con el servidor. Puede estar iniciando — inténtalo de nuevo en unos segundos.") {
    super(0, detail);
    this.name = "NetworkError";
  }
}

export function isNetworkError(err: unknown): err is NetworkError {
  return err instanceof NetworkError;
}

/**
 * fetch con un único reintento ante cold start del backend (Render free tier).
 * Reintenta en errores de red (fetch lanza TypeError) y en 502/503/504.
 * Espera 3s entre intentos para darle tiempo al servidor de despertar.
 */
async function fetchWithRetry(url: string, opts: RequestInit, retries = 1): Promise<Response> {
  try {
    const res = await fetch(url, opts);
    if ((res.status === 502 || res.status === 503 || res.status === 504) && retries > 0) {
      await new Promise((r) => setTimeout(r, 3000));
      return fetchWithRetry(url, opts, retries - 1);
    }
    return res;
  } catch (err) {
    if (retries > 0) {
      await new Promise((r) => setTimeout(r, 3000));
      return fetchWithRetry(url, opts, retries - 1);
    }
    throw err;
  }
}

async function safeFetchWithRetry(
  url: string,
  opts: RequestInit,
  retries = 1,
): Promise<Response> {
  try {
    return await fetchWithRetry(url, opts, retries);
  } catch (err) {
    // fetchWithRetry agotó sus reintentos y volvió a lanzar la TypeError
    // original. La traducimos a un NetworkError con mensaje en español
    // que ya es apto para mostrar al usuario.
    if (err instanceof TypeError) {
      throw new NetworkError();
    }
    throw err;
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  extraHeaders?: Record<string, string>,
): Promise<T> {
  // Importación dinámica para evitar ciclos con el store
  const { useAuthStore } = await import("../stores/authStore");
  const token = useAuthStore.getState().accessToken;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...extraHeaders,
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await safeFetchWithRetry(`${API_BASE}${path}`, {
    method,
    headers,
    credentials: "include", // para la cookie de refresh
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail ?? detail;
    } catch {
      /* ignorar */
    }
    throw new ApiError(res.status, detail);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

async function requestForm<T>(path: string, formData: FormData): Promise<T> {
  const { useAuthStore } = await import("../stores/authStore");
  const token = useAuthStore.getState().accessToken;

  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  // No establecer Content-Type — el navegador lo hace automáticamente con el boundary

  const res = await safeFetchWithRetry(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    credentials: "include",
    body: formData,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail ?? detail;
    } catch {
      /* ignorar */
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
  patch: <T>(path: string, body?: unknown) => request<T>("PATCH", path, body),
  delete: <T>(path: string) => request<T>("DELETE", path),
  postForm: <T>(path: string, formData: FormData) => requestForm<T>(path, formData),
};

// Alias para uso directo en componentes sin importar `api`
export const apiClient = api;

/**
 * Resuelve la URL de una imagen de item del banco.
 * - "" o null → undefined (sin imagen)
 * - "http://…" o "https://…" → tal cual (URL absoluta)
 * - "items/images/foo.png" → "${API_BASE}/items/images/foo.png"
 * - "/items/images/foo.png" → "${API_BASE}/items/images/foo.png"
 */
export function resolveImageUrl(url: string | null | undefined): string | undefined {
  if (!url) return undefined;
  const trimmed = url.trim();
  if (!trimmed) return undefined;
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  const path = trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
  return `${API_BASE}${path}`;
}
