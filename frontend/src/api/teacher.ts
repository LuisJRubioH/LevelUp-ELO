/**
 * api/teacher.ts
 * ==============
 * Clientes HTTP tipados para los endpoints de docente y admin.
 */

import { api } from "./client";
import type { LeagueStats, SubtopicResult } from "./student";

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
  /** Spec 006 FR-041c: the «Todos» rating (the courses that link the student to the teacher),
   * as screens show it (spec 001 FR-028j); null = pending diagnostic. No other rating is sent. */
  display_rating: number | null;
  rank_label: string | null;
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

/** Spec 005 K3: how a KatIA conversation ended (FR-031) and its kind of difficulty (N2). */
export interface KatiaConversation {
  id: number;
  course_id: string | null;
  course_name: string | null;
  topic: string | null;
  item_id: string;
  turns: number;
  outcome: "superado" | "no_superado" | "abandonado";
  difficulty: string | null;
  misconception_tag: string | null;
  opened_at: string | null;
  closed_at: string | null;
}

export interface StudentPath {
  student_id: number;
  course_id: string;
  nodes: PathRecordNode[];
}

/** Spec 006 FR-041a/b: what a set is ranked on — a course, or the courses that link each student
 * to the teacher. */
export type ConsoleBasis =
  | { kind: "course"; course_id: string; course_name: string }
  | { kind: "linked_courses" };

/** Spec 006 FR-041c: a place, with the rating and label it was ranked on. */
export interface ConsolePlace {
  user_id: number;
  rank: number | null;
  display_rating: number | null;
  rank_label: string | null;
}

/** Spec 006 FR-041: a set's figures, computed by the server; screens render them as given. */
export interface ConsoleFigures {
  n: number;
  mean: number | null; // mean of rated students' display values; null if none
  accuracy: number | null; // percent, over students with attempts in the window
  attempts: number;
  attention: number[]; // user ids
  ranking: ConsolePlace[]; // competition ranks, pending last
  histogram: { label: string; count: number }[];
  basis: ConsoleBasis;
}

export interface ConsoleSummary extends ConsoleFigures {
  groups: Record<string, ConsoleFigures>; // by group id
}

/** Spec 006 FR-043: the last 7 days, the last 30, or the whole history. */
export type ConsoleWindow = "7" | "30" | "all";

export interface DashboardData {
  groups: Group[];
  students: StudentSummary[];
  summary: ConsoleSummary;
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
  /** Spec 006 FR-051: the AI's comment, shown beside its score. */
  ai_feedback?: string | null;
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
  /** Spec 004 FR-046: last day of access (YYYY-MM-DD, inclusive, Colombian time); null = none. */
  access_until?: string | null;
  access_expired?: boolean;
  /** Spec 009 FR-013: the linked identification — the admin sees it; null when none. */
  identification?: string | null;
}

/** Spec 004 FR-040: a student the admin creates one by one. */
export interface CreateStudentBody {
  username: string;
  display_name: string;
  group_id: number;
  education_level: string;
  grade?: string | null;
  access_until?: string | null;
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
  /** Spec 009 N26 (a): the institution and grade the group is for; null when not set. */
  course_id?: string | null;
  institution?: string | null;
  grade?: number | null;
}

// ── Spec 009 I1: the initial import ─────────────────────────────────────────────

/** FR-001, N19: the file's columns for each field; the display name from one or two. */
export interface ImportMapping {
  identification: string;
  name: string[];
  level?: string | null;
  grade?: string | null;
  institution?: string | null;
  recovery_email?: string | null;
}

/** N20: the level and grade where not mapped, and the last day of access. */
export interface ImportBatch {
  level?: string | null;
  grade?: number | null;
  access_until?: string | null;
}

/** N21: one (institution, grade) pair of the file and its group. */
export interface ImportPair {
  institution: string | null;
  grade: number | null;
  group_id: number | null;
  suggested_group_id?: number | null;
}

export type ImportStatus = "new" | "existing" | "duplicate" | "error";
export type ImportChangeField = "group_id" | "access_until" | "recovery_email";

export interface ImportRow {
  row: number;
  status: ImportStatus;
  reasons: string[];
  identification: string | null;
  display_name: string | null;
  level: string | null;
  grade: number | null;
  group_id: number | null;
  recovery_email: string | null;
  account_id: number | null;
  changes: Partial<Record<ImportChangeField, { from: unknown; to: unknown }>>;
}

export interface ImportColumns {
  header: string[];
  examples: string[][];
  rows: number;
  suggested: Partial<ImportMapping>;
}

export interface ImportPreview {
  rows: ImportRow[];
  counts: Record<ImportStatus, number>;
  pairs: ImportPair[];
  digest: string;
}

export type ImportResult = "created" | "updated" | "unchanged" | "skipped" | "duplicate" | "error";

export interface ImportRecord {
  import_id: string;
  state: "running" | "finished" | "interrupted";
  total_rows: number;
  started_at: string | null;
  finished_at: string | null;
  counts: Record<ImportResult, number>;
  rows?: { row: number; result: ImportResult; user_id: number | null; reason: string | null }[];
}

export interface ImportChoices {
  file: File;
  mapping: ImportMapping;
  batch: ImportBatch;
  /** A null group pairs the pair with no group, even when one would be suggested. */
  pairing: { institution: string | null; grade: number | null; group_id: number | null }[];
}

function importForm({ file, mapping, batch, pairing }: ImportChoices): FormData {
  const form = new FormData();
  form.append("file", file);
  form.append("mapping", JSON.stringify(mapping));
  form.append("batch", JSON.stringify(batch));
  form.append("pairing", JSON.stringify(pairing));
  return form;
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
  dashboard: (days: ConsoleWindow = "30") =>
    api.get<DashboardData>(`/api/teacher/dashboard?days=${days}`),

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

  /** Spec 003 L4: the student's learning path — states, answer history, outcomes. */
  studentPath: (student_id: number, course_id: string) =>
    api.get<StudentPath>(
      `/api/teacher/student/${student_id}/path/${encodeURIComponent(course_id)}`,
    ),

  /** Spec 005 FR-033: the student's closed KatIA conversations — summaries, never text. */
  studentKatiaHistory: (student_id: number) =>
    api.get<{ conversations: KatiaConversation[] }>(
      `/api/teacher/student/${student_id}/katia-history`,
    ),

  /** Spec 007 FR-070: the student's League answers, in the courses that link them to you. */
  studentLeague: (student_id: number) =>
    api.get<LeagueStats>(`/api/teacher/student/${student_id}/league`),

  /** Spec 008 FR-042: the student's results per subtopic (from the student report). */
  studentSubtopics: (student_id: number) =>
    api.get<{ subtopics: SubtopicResult[] }>(`/api/teacher/student/${student_id}`),
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

  metrics: (days: ConsoleWindow = "30") =>
    api.get<TeacherMetrics>(`/api/teacher/metrics?days=${days}`),

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

  /** Spec 006 FR-031: a copy, unassigned and unlocked, of a template already taken. */
  duplicateExamTemplate: (id: number) =>
    api.post<ExamTemplate>(`/api/teacher/exam-templates/${id}/duplicate`, {}),

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
  /** Spec 006 FR-033: how many students chose each wrong option. */
  choices?: Record<string, number>;
}
export interface ExamTopicStat {
  topic: string;
  total: number;
  correct: number;
  accuracy: number;
}
/** Spec 006 FR-033: one student's first submission. */
export interface ExamStudentResult {
  user_id: number;
  name: string;
  submitted_at: string;
  correct: number;
  total: number;
  score_pct: number;
  answers: { item_id: string; is_correct: boolean; selected_option: string | null }[];
}

export interface ExamResults {
  title: string;
  students?: ExamStudentResult[];
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
  /** Spec 006: false = a draft no student sees (FR-030); true = items locked (FR-031). */
  assigned?: boolean;
  locked?: boolean;
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

  /** Spec 004 FR-040: the temporary password comes back once. */
  createStudent: (body: CreateStudentBody) =>
    api.post<TemporaryPassword>("/api/admin/students", body),

  /** Spec 004 FR-050: set, change, extend or remove (null) an account's last day of access. */
  setAccessUntil: (user_id: number, access_until: string | null) =>
    api.put<{ user_id: number; access_until: string | null; access_expired: boolean }>(
      `/api/admin/users/${user_id}/access-until`,
      { access_until }
    ),

  /** Spec 004 FR-025: the admin corrects any student's display name. */
  setDisplayName: (user_id: number, display_name: string) =>
    api.put<{ user_id: number; display_name: string }>(
      `/api/admin/users/${user_id}/display-name`,
      { display_name }
    ),

  accountAudit: (limit: number = 100) =>
    api.get<{ events: AccountEvent[] }>(`/api/admin/account-audit?limit=${limit}`),

  // Spec 009 I1 — the initial import. The file goes again with the confirmation (FR-003).
  importColumns: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.postForm<ImportColumns>("/api/admin/imports/columns", form);
  },

  importPreview: (choices: ImportChoices) =>
    api.postForm<ImportPreview>("/api/admin/imports/preview", importForm(choices)),

  importConfirm: (
    choices: ImportChoices,
    digest: string,
    confirm: { row: number; changes: ImportChangeField[] }[]
  ) => {
    const form = importForm(choices);
    form.append("digest", digest);
    form.append("confirm", JSON.stringify(confirm));
    return api.postForm<{ import_id: string; state: string; retry: boolean }>(
      "/api/admin/imports",
      form
    );
  },

  getImport: (import_id: string) => api.get<ImportRecord>(`/api/admin/imports/${import_id}`),

  imports: () => api.get<{ imports: ImportRecord[] }>("/api/admin/imports"),

  /** FR-007: links an identification to a student account without one. */
  linkIdentification: (user_id: number, identification: string) =>
    api.put<{ user_id: number; identification: string }>(
      `/api/admin/users/${user_id}/identification`,
      { identification }
    ),

  /** FR-017: removes a link made by mistake; the username and password stay. */
  unlinkIdentification: (user_id: number) =>
    api.delete<void>(`/api/admin/users/${user_id}/identification`),

  /** N25: the catalogue's courses, for a teacher's group. */
  courses: () =>
    api.get<{ courses: { id: string; name: string; block: string | null }[] }>(
      "/api/admin/courses"
    ),

  /** N25, N26 (a): a group owned by a teacher, for an institution and grade. */
  createGroupForTeacher: (
    teacher_id: number,
    body: { name: string; course_id: string | null; institution: string | null; grade: number | null }
  ) => api.post<{ group_id: number; name: string }>(`/api/admin/teachers/${teacher_id}/groups`, body),
};
