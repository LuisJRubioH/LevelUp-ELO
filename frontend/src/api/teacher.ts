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
  student_count: number;
}

/** Spec 001 FR-028t: a single-use invitation as its group's teacher sees it. */
export type InvitationStatus = "unused" | "used" | "expired" | "revoked";

export interface Invitation {
  id: number;
  /** XXXXX-XXXXX */
  token: string;
  status: InvitationStatus;
  /** "YYYY-MM-DD HH:MM:SS" */
  created_at: string;
  expires_at: string;
  used_at: string | null;
  /** The student's public name (spec 004 FR-023), for a used invitation. */
  used_by_name: string | null;
}

export interface InvitationList {
  /** Days an unused invitation stays valid (server setting). */
  ttl_days: number;
  invitations: Invitation[];
}

export interface StudentSummary {
  user_id: number;
  /** Spec 004 FR-023: the display name, else the username of an account without one. */
  name: string;
  global_elo: number | null; // null = pending diagnostic (spec 001)
  display_rating: number | null; // what screens show (FR-028j)
  rank_label: string | null;
  overall_status: "rated" | "pending_diagnostic";
  total_attempts: number;
  accuracy: number;
  last_activity: string | null;
  group_id?: number | null;
  group_name?: string | null;
  education_level?: string | null;
}

/** Spec 003 L4 (FR-042): one answer — where, right or wrong, the tag; never the value (N11). */
export interface PathAnswer {
  label: string;
  is_expected: boolean | null;
  misconception_tag: string | null;
  answered_at: string;
}

export interface PathRecordNode {
  node_id: string;
  title: string;
  state: string | null;
  answers: PathAnswer[];
  outcome: { diagnostic_correct: number; post_correct: number; items: number; outcome: "gain" | "flat" } | null;
}

export interface StudentPath {
  student_id: number;
  course_id: string;
  nodes: PathRecordNode[];
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
  student_name: string;
  item_id: string;
  item_content: string | null;
  ai_score: number | null;
  status: string;
  created_at: string;
  has_image: boolean;
  /** Spec 001 FR-024g: the review being graded, sent back with the grade. */
  review_round?: number;
}

export interface GradeResult {
  submission_id: number;
  teacher_score: number;
  /** Spec 001 FR-024f: the amount applied to the rating, never the computed delta. */
  elo_delta: number;
  status: string;
  computed_delta?: number | null;
  contribution?: number | null;
  review_round?: number | null;
}

/** Spec 001 FR-024i: a procedure graded 0 automatically as a copy. */
export interface ProcedureCopy {
  submission_id: number;
  student_id: number;
  student_name: string;
  item_id: string;
  item_content: string | null;
  reviewed_at: string | null;
}

export interface AdminUser {
  id?: number;
  user_id?: number;
  username: string;
  /** Spec 004 FR-024: students only; null on accounts that have none. */
  display_name?: string | null;
  role: string;
  approved: boolean | number;
  active: boolean | number;
  education_level: string | null;
  group_name: string | null;
  /** Spec 004 FR-030: a temporary password is still pending. */
  must_change_password?: boolean;
}

/** Spec 004 E2: shown once to the admin, never stored readable. */
export interface TemporaryPassword {
  user_id: number;
  username?: string;
  temporary_password: string;
}

export interface AccountEvent {
  id: number;
  action: "password_reset" | "teacher_created" | string;
  actor_id: number;
  admin_username?: string | null;
  user_id: number;
  user_username?: string | null;
  user_role?: string | null;
  created_at: string | null;
}

export interface AdminGroup {
  id: number;
  name: string;
  teacher_id: number;
  teacher_name: string;
  student_count: number;
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

  invitations: (group_id: number) =>
    api.get<InvitationList>(`/api/teacher/groups/${group_id}/invitations`),

  createInvitations: (group_id: number, count: number) =>
    api.post<{ tokens: string[]; ttl_days: number }>(
      `/api/teacher/groups/${group_id}/invitations`,
      { count },
    ),

  revokeInvitation: (invitation_id: number) =>
    api.delete<void>(`/api/teacher/invitations/${invitation_id}`),

  procedures: () => api.get<PendingProcedure[]>("/api/teacher/procedures"),

  gradeProcedure: (
    submission_id: number,
    teacher_score: number,
    teacher_feedback?: string,
    review_round?: number,
  ) =>
    api.post<GradeResult>("/api/teacher/procedures/grade", {
      submission_id,
      teacher_score,
      teacher_feedback,
      review_round,
    }),

  procedureCopies: () => api.get<ProcedureCopy[]>("/api/teacher/procedures/copies"),

  studentReport: (student_id: number) =>
    api.get<Record<string, unknown>>(`/api/teacher/student/${student_id}`),

  studentEloHistory: (student_id: number) =>
    api.get<{ attempts: Record<string, unknown>[] }>(`/api/teacher/student/${student_id}/elo-history`),

  /** Spec 003 L4: the student's learning path — states, answer history, outcomes. */
  studentPath: (student_id: number, course_id: string) =>
    api.get<StudentPath>(
      `/api/teacher/student/${student_id}/path/${encodeURIComponent(course_id)}`,
    ),

  studentKatiaHistory: (student_id: number) =>
    api.get<{ interactions: Record<string, unknown>[] }>(
      `/api/teacher/student/${student_id}/katia-history`,
    ),

  /** Spec 005 FR-010/FR-011: the server picks provider and model from the key. */
  studentAiAnalysis: (student_id: number, api_key?: string) =>
    api.post<{ analysis: string }>(`/api/teacher/student/${student_id}/ai-analysis`, {
      api_key,
    }),

  /** The submitted file as an object URL with its type: a photo, or a PDF as uploaded. */
  procedureImage: async (submission_id: number): Promise<{ url: string; type: string }> => {
    const { useAuthStore } = await import("../stores/authStore");
    const token = useAuthStore.getState().accessToken;
    const r = await fetch(`${API_BASE}/api/teacher/procedures/${submission_id}/image`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const blob = await r.blob();
    return { url: URL.createObjectURL(blob), type: blob.type };
  },

  metrics: () => api.get<TeacherMetrics>("/api/teacher/metrics"),

  downloadCsv: () => _downloadBlob("/api/teacher/export/csv", "levelup_intentos.csv"),

  downloadXlsx: () => _downloadBlob("/api/teacher/export/xlsx", "levelup_datos_completos.xlsx"),

  // ── Sprint C: plantillas de examen del docente ───────────────────────────
  allCourses: () => api.get<{ id: string; name: string; block: string }[]>("/api/teacher/courses"),

  examTemplates: (course_id?: string, include_archived = false) => {
    const qs = new URLSearchParams();
    if (course_id) qs.set("course_id", course_id);
    if (include_archived) qs.set("include_archived", "true");
    return api.get<ExamTemplate[]>(
      `/api/teacher/exam-templates${qs.toString() ? "?" + qs.toString() : ""}`,
    );
  },

  createExamTemplate: (input: {
    course_id: string;
    title: string;
    time_limit_min: number;
    item_ids: string[];
  }) => api.post<ExamTemplate>("/api/teacher/exam-templates", input),

  updateExamTemplate: (
    id: number,
    patch: {
      title?: string;
      time_limit_min?: number;
      item_ids?: string[];
    },
  ) => api.patch<ExamTemplate>(`/api/teacher/exam-templates/${id}`, patch),

  archiveExamTemplate: (id: number) =>
    api.delete<void>(`/api/teacher/exam-templates/${id}`),

  itemsCatalog: (course_id: string) =>
    api.get<ItemCatalogEntry[]>(
      `/api/teacher/items?course_id=${encodeURIComponent(course_id)}`,
    ),

  // ── Asignación de plantillas a grupos + ventana de tiempo ──────────────
  listAssignments: (template_id: number) =>
    api.get<ExamAssignment[]>(`/api/teacher/exam-templates/${template_id}/assignments`),

  createAssignments: (
    template_id: number,
    body: { group_ids: number[]; starts_at?: string | null; ends_at?: string | null },
  ) =>
    api.post<ExamAssignment[]>(
      `/api/teacher/exam-templates/${template_id}/assignments`,
      body,
    ),

  deleteAssignment: (template_id: number, assignment_id: number) =>
    api.delete<void>(
      `/api/teacher/exam-templates/${template_id}/assignments/${assignment_id}`,
    ),

  examResults: (template_id: number) =>
    api.get<ExamResults>(`/api/teacher/exam-templates/${template_id}/results`),
};

export interface ExamQuestionStat {
  item_id: string;
  content: string;
  topic: string | null;
  total: number;
  correct: number;
  accuracy: number;
}
export interface ExamTopicStat {
  topic: string;
  total: number;
  correct: number;
  accuracy: number;
}
export interface ExamResults {
  title: string;
  n_sessions: number;
  n_students: number;
  avg_score: number;
  questions: ExamQuestionStat[];
  topics: ExamTopicStat[];
  best_question: ExamQuestionStat | null;
  worst_question: ExamQuestionStat | null;
  reinforce_topic: ExamTopicStat | null;
}

export interface ExamAssignment {
  id: number;
  template_id: number;
  group_id: number;
  group_name: string;
  starts_at: string | null;
  ends_at: string | null;
  created_at: string;
}

export interface ExamTemplate {
  id: number;
  teacher_id: number;
  course_id: string;
  title: string;
  time_limit_min: number;
  item_ids: string[];
  archived: boolean;
  created_at: string;
}

export interface ItemCatalogEntry {
  id: string;
  content: string;
  difficulty: number;
  topic: string;
  tags: string[];
}

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

  // Spec 004 E2 (FR-029, FR-031)
  resetPassword: (user_id: number) =>
    api.post<TemporaryPassword>(`/api/admin/users/${user_id}/reset-password`),

  createTeacher: (body: { username: string; email?: string }) =>
    api.post<TemporaryPassword>("/api/admin/teachers", body),

  /** Spec 004 FR-025: the admin corrects any student's display name. */
  setDisplayName: (user_id: number, display_name: string) =>
    api.put<{ user_id: number; display_name: string }>(
      `/api/admin/users/${user_id}/display-name`,
      { display_name }
    ),

  accountAudit: (limit: number = 100) =>
    api.get<{ events: AccountEvent[] }>(`/api/admin/account-audit?limit=${limit}`),
};
