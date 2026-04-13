/**
 * api/auth.ts
 * ===========
 * Clientes tipados para los endpoints de autenticación.
 */

import { api } from "./client";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  role: "student" | "teacher";
  education_level?: "universidad" | "colegio" | "semillero";
  grade?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: number;
  username: string;
  role: string;
}

export interface UserProfile {
  user_id: number;
  username: string;
  role: string;
  approved: boolean;
  education_level: string | null;
  grade: string | null;
}

export const authApi = {
  login: (body: LoginRequest) => api.post<TokenResponse>("/api/auth/login", body),
  register: (body: RegisterRequest) => api.post<{ message: string }>("/api/auth/register", body),
  me: () => api.get<UserProfile>("/api/auth/me"),
  logout: () => api.post<void>("/api/auth/logout"),
};
