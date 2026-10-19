/**
 * stores/settingsStore.ts
 * =======================
 * Configuración de IA del usuario: solo su API key (spec 005 FR-011: el servidor elige
 * proveedor y modelo a partir del prefijo de la key).
 * Persiste en localStorage — la key NUNCA se envía al backend excepto
 * en el body de las peticiones de IA (y el backend no la persiste).
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SettingsState {
  apiKey: string;
  setApiKey: (key: string) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      apiKey: "",
      setApiKey: (key) => set({ apiKey: key }),
    }),
    {
      name: "levelup-settings",
      version: 1,
      // Version 0 also kept `provider` and `model`: dropped, the key stays.
      migrate: (persisted) => ({ apiKey: (persisted as { apiKey?: string } | null)?.apiKey ?? "" }),
      partialize: (state) => ({ apiKey: state.apiKey }),
    },
  ),
);

/** Spec 005 FR-014: the procedure review runs on Groq only. */
export const GROQ_ONLY = "La revisión con IA usa Groq";

export const isGroqKey = (key: string) => key.trim().startsWith("gsk_");
