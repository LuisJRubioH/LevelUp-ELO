/**
 * stores/settingsStore.ts
 * =======================
 * Configuración de IA del usuario: API key y proveedor.
 * Persiste en localStorage — la key NUNCA se envía al backend excepto
 * en el body de las peticiones de IA (y el backend no la persiste).
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SettingsState {
  apiKey: string;
  provider: string;

  setApiKey: (key: string) => void;
  setProvider: (provider: string) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      apiKey: "",
      provider: "groq",

      setApiKey: (key) => set({ apiKey: key }),
      setProvider: (provider) => set({ provider }),
    }),
    {
      name: "levelup-settings",
      partialize: (state) => ({ apiKey: state.apiKey, provider: state.provider }),
    },
  ),
);
