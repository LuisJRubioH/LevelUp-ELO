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
  email: string | null;
}

interface AuthState {
  accessToken: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  sessionStartTime: number | null; // timestamp ms al hacer login
  // Spec 004 FR-030: la cuenta entró con una contraseña temporal y debe cambiarla antes de seguir.
  mustChangePassword: boolean;

  setAuth: (token: string, user: AuthUser) => void;
  setMustChangePassword: (value: boolean) => void;
  updateAccessToken: (token: string) => void;
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
      mustChangePassword: false,

      setAuth: (token, user) =>
        set({ accessToken: token, user, isAuthenticated: true, sessionStartTime: Date.now() }),

      setMustChangePassword: (value) => set({ mustChangePassword: value }),

      updateAccessToken: (token) => set({ accessToken: token, isAuthenticated: true }),

      clearAuth: () =>
        set({
          accessToken: null,
          user: null,
          isAuthenticated: false,
          sessionStartTime: null,
          mustChangePassword: false,
        }),

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
        mustChangePassword: state.mustChangePassword,
      }),
    },
  ),
);
