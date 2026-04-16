/**
 * api/student.ts
 * ==============
 * Clientes tipados para los endpoints del estudiante.
 */

import { api } from "./client";

export interface Item {
  id: string;
  content: string;
  difficulty: number;
  topic: string;
  options: string[];
  image_url?: string;
  tags?: string[];
}

export interface NextQuestionResponse {
  item: Item | null;
  status: "ok" | "empty" | "course_empty";
}

export interface AnswerResponse {
  is_correct: boolean;
  elo_before: number;
  elo_after: number;
  rd_after: number;
  delta_elo: number;
  cog_data: Record<string, unknown>;
}

export interface TopicELO {
  topic: string;
  rating: number;
  rd: number;
}

export interface StudentStats {
  user_id: number;
  global_elo: number;
  topic_elos: TopicELO[];
  total_attempts: number;
  study_streak: number;
  rank_label: string | null;
}

export interface Course {
  id: string;
  name: string;
  block: string;
  enrolled: boolean;
  group_id?: number;
}

export interface ProcedureSubmissionRow {
  submission_id: number;
  item_id: string;
  item_content: string | null;
  status: string;
  ai_proposed_score: number | null;
  teacher_score: number | null;
  final_score: number | null;
  teacher_feedback: string | null;
  elo_delta: number | null;
  submitted_at: string | null;
  reviewed_at: string | null;
}

export interface ProcedureStep {
  numero?: number;
  contenido?: string;
  evaluacion?: string;
  comentario?: string;
}

export interface ProcedureReview {
  corresponde_a_pregunta?: boolean;
  transcripcion?: string;
  pasos?: ProcedureStep[];
  errores_detectados?: string[];
  saltos_logicos?: string[];
  resultado_correcto?: boolean;
  evaluacion_global?: string;
  score_procedimiento?: number;
}

export const studentApi = {
  nextQuestion: (body: {
    course_id: string;
    topic?: string;
    session_correct_ids?: string[];
    session_wrong_timestamps?: Record<string, number>;
    session_questions_count?: number;
  }) => api.post<NextQuestionResponse>("/api/student/next-question", body),

  answer: (body: {
    item_id: string;
    item_data: Item;
    selected_option: string;
    reasoning?: string;
    time_taken?: number;
    elo_topic?: string;
  }) => api.post<AnswerResponse>("/api/student/answer", body),

  stats: () => api.get<StudentStats>("/api/student/stats"),

  courses: () => api.get<Course[]>("/api/student/courses"),

  enroll: (course_id: string, group_id?: number) =>
    api.post<{ message: string }>("/api/student/enroll", { course_id, group_id }),

  enrollByCode: (invite_code: string) =>
    api.post<{ message: string; course_id: string }>("/api/student/enroll-by-code", {
      invite_code,
    }),

  unenroll: (course_id: string) => api.delete<void>(`/api/student/enroll/${course_id}`),

  myProcedures: () =>
    api.get<{ submissions: ProcedureSubmissionRow[] }>("/api/student/procedures"),

  reportProblem: (description: string) =>
    api.post<{ message: string }>("/api/student/problems", { description }),

  aiStatus: () =>
    api.get<{ available: boolean; provider: string | null }>("/api/student/ai-status"),

  analyzeProcedure: async (params: {
    item_id: string;
    item_content: string;
    api_key?: string;
    file: File;
  }): Promise<{ review: ProcedureReview; provider: string }> => {
    const fd = new FormData();
    fd.append("item_id", params.item_id);
    fd.append("item_content", params.item_content);
    if (params.api_key) fd.append("api_key", params.api_key);
    fd.append("file", params.file);
    const res = await api.postForm<{
      item_id: string;
      provider: string;
      review: ProcedureReview;
    }>("/api/student/procedure/analyze", fd);
    return { review: res.review, provider: res.provider };
  },

  history: () => api.get<{ attempts: unknown[] }>("/api/student/history"),

  activity: (days = 70) =>
    api.get<{ activity: Record<string, number> }>(`/api/student/activity?days=${days}`),

  streakByCourse: (course_id: string) =>
    api.get<{ course_id: string; streak: number }>(`/api/student/streak/${course_id}`),

  groupRanking: (course_id?: string) => {
    const q = course_id ? `?course_id=${course_id}` : "";
    return api.get<{ ranking: unknown[]; my_rank: number | null }>(`/api/student/group-ranking${q}`);
  },
};
