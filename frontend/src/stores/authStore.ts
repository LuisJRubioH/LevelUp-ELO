/**
 * stores/authStore.ts
 * ===================
 * Zustand store para el estado de autenticación.
 * Persiste accessToken en localStorage (refresh via cookie HttpOnly).
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AuthUser {
  user_id: number;
  username: string;
  role: "student" | "teacher" | "admin";
  education_level: string | null;
  grade: string | null;
}

interface AuthState {
  accessToken: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  sessionStartTime: number | null; // timestamp ms al hacer login

  setAuth: (token: string, user: AuthUser) => void;
  clearAuth: () => void;
  updateUser: (user: Partial<AuthUser>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      isAuthenticated: false,
      sessionStartTime: null,

      setAuth: (token, user) =>
        set({ accessToken: token, user, isAuthenticated: true, sessionStartTime: Date.now() }),

      clearAuth: () =>
        set({ accessToken: null, user: null, isAuthenticated: false, sessionStartTime: null }),

      updateUser: (partial) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...partial } : null,
        })),
    }),
    {
      name: "levelup-auth",
      // Solo persistir el token y el user, no las funciones
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        sessionStartTime: state.sessionStartTime,
      }),
    },
  ),
);
