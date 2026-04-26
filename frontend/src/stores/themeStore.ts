/**
 * stores/themeStore.ts
 * =====================
 * Zustand store para el tema claro/oscuro.
 * Persiste en localStorage y aplica la clase `light` a <html> en tiempo real.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Theme = "dark" | "light";

interface ThemeState {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (t: Theme) => void;
}

function applyTheme(theme: Theme) {
  if (theme === "light") {
    document.documentElement.classList.add("light");
  } else {
    document.documentElement.classList.remove("light");
  }
}

// Aplicar inmediatamente desde localStorage para evitar flash de tema incorrecto.
const _saved = localStorage.getItem("levelup-theme");
if (_saved) {
  try {
    const parsed = JSON.parse(_saved) as { state?: { theme?: string } };
    if (parsed?.state?.theme === "light") {
      document.documentElement.classList.add("light");
    }
  } catch {
    /* ignorar JSON inválido */
  }
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: "dark",
      setTheme: (theme) => {
        set({ theme });
        applyTheme(theme);
      },
      toggleTheme: () => {
        const next = get().theme === "dark" ? "light" : "dark";
        set({ theme: next });
        applyTheme(next);
      },
    }),
    {
      name: "levelup-theme",
      onRehydrateStorage: () => (state) => {
        if (state) applyTheme(state.theme);
      },
    },
  ),
);
