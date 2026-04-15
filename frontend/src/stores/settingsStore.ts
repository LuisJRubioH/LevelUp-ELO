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
  model: string;

  setApiKey: (key: string) => void;
  setProvider: (provider: string) => void;
  setModel: (model: string) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      apiKey: "",
      provider: "groq",
      model: "",

      setApiKey: (key) => set({ apiKey: key }),
      setProvider: (provider) => set({ provider, model: "" }),
      setModel: (model) => set({ model }),
    }),
    {
      name: "levelup-settings",
      partialize: (state) => ({
        apiKey: state.apiKey,
        provider: state.provider,
        model: state.model,
      }),
    },
  ),
);

export const PROVIDER_MODELS: Record<string, { id: string; label: string }[]> = {
  groq: [
    { id: "meta-llama/llama-4-scout-17b-16e-instruct", label: "Llama 4 Scout (visión, rápido)" },
    { id: "llama-3.3-70b-versatile", label: "Llama 3.3 70B (razonamiento)" },
    { id: "llama-3.1-8b-instant", label: "Llama 3.1 8B (más rápido)" },
  ],
  anthropic: [
    { id: "claude-sonnet-4-5", label: "Claude Sonnet 4.5" },
    { id: "claude-haiku-4-5", label: "Claude Haiku 4.5 (más rápido)" },
    { id: "claude-opus-4-6", label: "Claude Opus 4.6 (más capaz)" },
  ],
  openai: [
    { id: "gpt-4o-mini", label: "GPT-4o mini (rápido)" },
    { id: "gpt-4o", label: "GPT-4o" },
  ],
  google: [
    { id: "gemini-2.0-flash-exp", label: "Gemini 2.0 Flash" },
    { id: "gemini-1.5-pro", label: "Gemini 1.5 Pro" },
  ],
};
