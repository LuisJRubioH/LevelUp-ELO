/**
 * api/teacher.ts
 * ==============
 * Clientes HTTP tipados para los endpoints de docente y admin.
 */

import { api } from "./client";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

// ── Tipos compartidos ─────────────────────────────────────────────────────────

export interface Group {
  group_id: number;
  name: string;
  course_id: string | null;
  invite_code: string | null;
  student_count: number;
}

export interface StudentSummary {
  user_id: number;
  username: string;
  global_elo: number;
  total_attempts: number;
  accuracy: number;
  last_activity: string | null;
  group_id?: number | null;
  group_name?: string | null;
  education_level?: string | null;
}

export interface DashboardData {
  teacher_id: number;
  groups: Group[];
  students: StudentSummary[];
}

export interface TopicStat {
  topic: string;
  attempts: number;
  accuracy: number;
  avg_time: number;
}

export interface TeacherMetrics {
  total_attempts: number;
  avg_time_seconds: number;
  abandonment_rate: number;
  topic_stats: TopicStat[];
  daily_attempts: { date: string; count: number }[];
  hourly_distribution: { hour: number; count: number }[];
}

export interface PendingProcedure {
  submission_id: number;
  student_id: number;
  student_username: string;
  item_id: string;
  item_content: string | null;
  ai_score: number | null;
  status: string;
  created_at: string;
  has_image: boolean;
}

export interface GradeResult {
  submission_id: number;
  teacher_score: number;
  elo_delta: number;
  status: string;
}

export interface AdminUser {
  id?: number;
  user_id?: number;
  username: string;
  role: string;
  approved: boolean | number;
  active: boolean | number;
  education_level: string | null;
  group_name: string | null;
}

export interface AdminGroup {
  id: number;
  name: string;
  teacher_id?: number;
  teacher_username?: string;
  student_count?: number;
}

export interface ProblemReport {
  id: number;
  user_id: number;
  username?: string;
  description: string;
  status: string;
  created_at: string;
}

export interface AuditEntry {
  id: number;
  student_id: number;
  student_username?: string;
  old_group_id: number | null;
  old_group_name: string | null;
  new_group_id: number | null;
  new_group_name: string | null;
  admin_id: number;
  admin_username?: string;
  timestamp: string;
}

// ── Descarga de archivos (blob) ───────────────────────────────────────────────

async function _downloadBlob(path: string, filename: string): Promise<void> {
  const { useAuthStore } = await import("../stores/authStore");
  const token = useAuthStore.getState().accessToken;
  const res = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
  });
  if (!res.ok) throw new Error(`Error al descargar: HTTP ${res.status}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ── API Docente ───────────────────────────────────────────────────────────────

export const teacherApi = {
  dashboard: () => api.get<DashboardData>("/api/teacher/dashboard"),

  groups: () => api.get<Group[]>("/api/teacher/groups"),

  createGroup: (course_id: string, group_name: string) =>
    api.post<Group>("/api/teacher/groups", { course_id, group_name }),

  generateInviteCode: (group_id: number) =>
    api.post<{ invite_code: string }>(`/api/teacher/groups/${group_id}/invite-code`),

  procedures: () => api.get<PendingProcedure[]>("/api/teacher/procedures"),

  gradeProcedure: (submission_id: number, teacher_score: number, teacher_feedback?: string) =>
    api.post<GradeResult>("/api/teacher/procedures/grade", {
      submission_id,
      teacher_score,
      teacher_feedback,
    }),

  studentReport: (student_id: number) =>
    api.get<Record<string, unknown>>(`/api/teacher/student/${student_id}`),

  studentEloHistory: (student_id: number) =>
    api.get<{ attempts: Record<string, unknown>[] }>(`/api/teacher/student/${student_id}/elo-history`),

  studentKatiaHistory: (student_id: number) =>
    api.get<{ interactions: Record<string, unknown>[] }>(
      `/api/teacher/student/${student_id}/katia-history`,
    ),

  studentAiAnalysis: (student_id: number, api_key?: string, provider = "groq") =>
    api.post<{ analysis: string }>(`/api/teacher/student/${student_id}/ai-analysis`, {
      api_key,
      provider,
    }),

  procedureImage: async (submission_id: number): Promise<string> => {
    const { useAuthStore } = await import("../stores/authStore");
    const token = useAuthStore.getState().accessToken;
    const r = await fetch(`${API_BASE}/api/teacher/procedures/${submission_id}/image`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const blob = await r.blob();
    return URL.createObjectURL(blob);
  },

  metrics: () => api.get<TeacherMetrics>("/api/teacher/metrics"),

  downloadCsv: () => _downloadBlob("/api/teacher/export/csv", "levelup_intentos.csv"),

  downloadXlsx: () => _downloadBlob("/api/teacher/export/xlsx", "levelup_datos_completos.xlsx"),
};

// ── API Admin ─────────────────────────────────────────────────────────────────

export const adminApi = {
  users: () => api.get<{ users: AdminUser[] }>("/api/admin/users"),

  pendingTeachers: () => api.get<{ teachers: AdminUser[] }>("/api/admin/teachers/pending"),

  approveTeacher: (user_id: number, action: "approve" | "reject") =>
    api.post<{ message: string }>("/api/admin/teachers/approve", { user_id, action }),

  deactivate: (user_id: number) =>
    api.patch<void>(`/api/admin/users/${user_id}/deactivate`),

  reactivate: (user_id: number) =>
    api.patch<void>(`/api/admin/users/${user_id}/reactivate`),

  changeGroup: (student_id: number, new_group_id: number | null) =>
    api.patch<void>("/api/admin/students/group", { student_id, new_group_id }),

  allGroups: () => api.get<{ groups: AdminGroup[] }>("/api/admin/groups"),

  deleteGroup: (group_id: number) => api.delete<void>(`/api/admin/groups/${group_id}`),

  reports: () => api.get<{ reports: ProblemReport[] }>("/api/admin/reports"),

  resolveReport: (report_id: number) =>
    api.patch<void>(`/api/admin/reports/${report_id}/resolve`),

  audit: (limit: number = 100) =>
    api.get<{ entries: AuditEntry[] }>(`/api/admin/audit?limit=${limit}`),
};
