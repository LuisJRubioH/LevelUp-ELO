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

/** The change the engine will apply for each outcome (spec 001, FR-030). */
export interface AnswerPreview {
  on_correct: number;
  on_wrong: number;
}

export interface NextQuestionResponse {
  item: Item | null;
  status: "ok" | "empty" | "course_empty";
  preview?: AnswerPreview | null;
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
  approximate?: boolean; // reconciled baseline, not exact history (FR-034a)
  origin?: string | null;
}

export interface CourseRating {
  course_id: string;
  course_name: string;
  rating: number | null;
  display_rating: number | null;
  rank_label: string | null;
  current_context: boolean; // false = earlier level/grade, shown as history
  topics: TopicELO[];
}

/** Spec 008 FR-042: one subtopic of the study report — results, never a rating. */
export interface SubtopicResult {
  course_id: string;
  course_name: string;
  topic: string;
  subtopic: string;
  attempts: number;
  correct: number;
  share_correct: number;
}

/** Spec 001: render display_rating + rank_label as given; null = pending diagnostic. */
/** Spec 007 FR-060: a closed League match, finished or abandoned, with subject and reason. */
export interface PvpHistoryRow {
  match_id: number;
  course_id: string;
  course_name: string;
  status: "finished" | "abandoned";
  /** The student's own reason: no_rated_topics, not_saved, orphaned, account_expired… or null. */
  reason: string | null;
  won: boolean;
  draw: boolean;
  my_score: number;
  opp_score: number;
  elo_delta: number | null;
  /** The number to show, rounded on the server (survey 007 V14); null when none recorded. */
  elo_delta_display: number | null;
  opponent: string;
  finished_at: string;
}

export interface StudentStats {
  user_id: number;
  global_elo: number | null;
  display_rating?: number | null;
  overall_status?: "rated" | "pending_diagnostic";
  topic_elos: TopicELO[];
  course_ratings?: CourseRating[];
  total_attempts: number;
  study_streak: number;
  rank_label: string | null;
  subtopics?: SubtopicResult[]; // spec 008 FR-042, weakest first
}

export interface RankingBasis {
  kind: "course" | "overall";
  course_id: string | null;
  course_name: string | null;
  source: "requested" | "group" | "overall";
}

export interface RankingEntry {
  user_id: number;
  /** Spec 004 FR-021: the display name, else the username of an account without one. */
  name: string;
  rating: number | null; // backend whole number: render as given
  rank_label: string | null;
  status: "rated" | "pending_diagnostic";
  rank: number | null; // competition rank (1, 2, 2, 4); null = pending
}

export interface GroupRanking {
  basis: RankingBasis | null;
  ranking: RankingEntry[];
  my_rank: number | null;
}

export interface Course {
  id: string;
  name: string;
  block: string;
  enrolled: boolean;
  group_id?: number;
  diagnostic_done?: boolean;
  /** false: reached by invitation outside the student's catalogue (spec 001 FR-028l). */
  in_catalogue?: boolean;
  /** true: the teacher of the student's group reviews it, so /enroll accepts it (FR-028v, FR-028w). */
  enrollable?: boolean;
}

// ── Examen diagnóstico (inicio de materia) ──────────────────────────────────
export interface DiagnosticQuestion {
  id: string;
  content: string;
  topic: string | null;
  difficulty: number;
  options: string[];
}
export interface DiagnosticTheme {
  topic: string;
  correct: number;
  total: number;
  ratio: number;
  status: "strong" | "mid" | "gap";
  /** The diagnostic's own value for the topic: a record, never shown (spec 001 FR-020a, FR-020b). */
  elo: number;
  /** What this diagnostic did to the topic; null for a result stored before the mark (FR-020c). */
  outcome?: "initialized" | "kept" | null;
}
/** The student's current rating in the course (spec 001 FR-020a). */
export interface DiagnosticCourseRating {
  display_rating: number | null;
  rank_label: string | null;
  status: "rated" | "pending_diagnostic";
}
export interface DiagnosticLeague {
  name: string;
  min: number;
  color: string;
  rank: string;
}
export interface DiagnosticResult {
  initial_elo: number;
  score_pct: number;
  league: DiagnosticLeague;
  themes: DiagnosticTheme[];
  correct_total: number;
  answered: number;
  completed?: boolean;
  course_rating?: DiagnosticCourseRating | null;
  /** All topics initialized, all kept, or some of each; null when unknown (FR-020c). */
  outcome_summary?: "initialized" | "kept" | "mixed" | null;
}
export interface DiagnosticStatus {
  completed: boolean;
  course_id: string;
  course_name?: string;
  questions?: DiagnosticQuestion[];
  result?: DiagnosticResult | null;
}
export interface DiagnosticAnswer {
  item_id: string;
  selected_option: string;
}

// ── Mapa de contenido ───────────────────────────────────────────────────────
export interface MapNode {
  topic: string;
  label: string;
  label_key?: string | null;
  node_id?: string | null;
  node_type?: string;
  elo: number | null; // null = topic not rated yet (pending), never shown as 1000
  rd: number | null;
  approximate?: boolean; // reconciled baseline (FR-034a)
  item_count: number;
  state: "completed" | "current" | "available" | "blocked";
}
export interface CourseMap {
  course_id: string;
  course_name: string;
  diagnostic_done: boolean;
  nodes: MapNode[];
  /** Spec 003 L1: a teacher's or admin's read-only view. */
  preview?: boolean;
}

export type LessonEvent =
  | "node_viewed"
  | "objectives_viewed"
  | "math_convention_viewed"
  | "node_completed";

// N4 (Divisibilidad): un mismo nodo mezcla numeric/single_select/multi_select,
// a diferencia de N2 (solo numeric) o N3 (numeric/text_exact).
export interface N4PracticeItem {
  id: string;
  kind: "numeric" | "single_select" | "multi_select";
  prompt: string;
  expr?: string;
  options?: Array<{ id: string; text: string }>;
  valid_options?: string[];
  story?: string;
  image_slot?: boolean;
  image?: string;
  support_objects?: string[];
}

export interface LessonDetail {
  /** Spec 003 L1: a teacher's or admin's read-only view. */
  preview?: boolean;
  node_id: string;
  node_type: string;
  course_id: string;
  i18n_prefix: string;
  next_node_id: string | null;
  state: string;
  presentation: "basico" | "intermedio" | "avanzado";
  explored_complex_branch: boolean;
  affects_elo: boolean;
  is_safe_zone: boolean;
  optional_branch: boolean;
  objectives: string[];
  optional_objectives: string[];
  unlock_after: string | null;
  interactions: Array<{
    interaction_id: string;
    type: "single_select" | "numeric_input" | "multi_select" | "number_line";
    prompt_key: string;
    option_keys: string[];
    can_retry?: boolean;
  }>;
  content?: {
    kind:
      | "operation_city_hub"
      | "operation_building"
      | "property_laboratory_hub"
      | "property_machine"
      | "level_hub_port"
      | "level_hub_cards"
      | "divisibility_concept";
    level?: string;
    title: string;
    welcome_text?: string;
    scene_text?: string;
    drag_rule?: string;
    advance_text?: string;
    character?: string;
    intro?: string;
    definition?: string;
    formal_expression?: string;
    instruction?: string;
    closing?: string;
    definition_katex?: string;
    machine_id?: string;
    property?: string;
    story_contract?: {
      type: "narrative_with_integrated_definition" | "unified_set_extension" | "guided_discovery_formalization";
      practice_position: string;
      is_integrated: boolean;
    };
    katia?: { eyebrow: string; title: string; body: string; question: string; imageSrc?: string };
    discovery?: { eyebrow: string; title: string; body: string };
    definition_title?: string;
    closure?: {
      eyebrow?: string;
      title: string;
      intro: string;
      rows: Array<{ symbol: string; name: string; closed: "yes" | "no" | "partial"; latex?: string; note: string }>;
    };
    narrative_sections?: Array<{
      type: "prose" | "guided_discovery" | string;
      title: string;
      body: string;
    }>;
    opening_hook?: {
      demo: string;
      katia_message: string;
    };
    validation_status?: string;
    operation?: string;
    gating?: { rule: string; cards_required?: number; machines_required?: number };
    // Textos del hub, parametrizados: sin estos el renderer cae al vocabulario
    // del puerto de la Polis, que es de donde salio.
    image?: string;
    cards_hint?: string;
    cards_aria?: string;
    card_closed_hint?: string;
    card_cta?: string;
    gating_label?: string;
    finish_label?: string;
    buildings?: Array<{
      id: string;
      operation: string;
      symbol: string;
      node_id: string;
      card: string;
    }>;
    machines?: Array<{
      id: string;
      property: string;
      station?: string;
      symbol: string;
      node_id: string;
      demo: string;
      katia_message: string;
      state?: "completed" | "current" | "available" | "blocked";
    }>;
    cards?: Array<{
      id: string;
      concept: string;
      symbol: string;
      node_id: string;
      destination: string;
      teaser: string;
      state?: "completed" | "current" | "available" | "blocked";
    }>;
    icebreaker?: {
      title: string;
      intro: string;
      items: N4PracticeItem[];
    };
    worked_examples?: Array<{
      statement: string;
      solution: string;
      steps?: string[];
      eyebrow?: string;
      title?: string;
      latex?: string;
      image_slot?: boolean;
      image?: string;
      trap?: boolean;
    }>;
    practice?: N4PracticeItem[];
    feedback?: Record<string, string>;
    formalization?:
      | string[]
      | {
          title: string;
          intro: string;
          items: Array<{ label: string; rule: string; latex?: string }>;
        };
  } | null;
  staircase: {
    core_steps: string[];
    optional_detour: string;
  } | null;
  progress: {
    state: string;
    objectives_viewed: boolean;
    math_convention_viewed: boolean;
    viewed_at: string | null;
    completed_at: string | null;
    responses: Record<
      string,
      {
        interaction_id: string;
        selected_option: string;
        is_expected: boolean | null;
        misconception_tag: string | null;
      }
    >;
    /** Spec 003 L4: the post-diagnostic outcome the server stored, or null. */
    outcome?: LessonOutcome | null;
  };
}

/** Spec 003 L4 (FR-041): «gain» when the post-diagnostic beat the opening one, else «flat». */
export interface LessonOutcome {
  diagnostic_correct: number;
  post_correct: number;
  items: number;
  outcome: "gain" | "flat";
}

export interface PrealgebraSummary {
  course_id: string;
  completed_nodes: number;
  total_nodes: number;
  overall_status: "strong" | "review" | "attention";
  review: Array<{ node_id: string; label_key: string }>;
}

export interface LessonInteractionResult {
  interaction_id: string;
  selected_option: string;
  is_expected: boolean | null;
  misconception_tag: string | null;
  feedback_key: string;
  /** Spec 003 L4: set when this answer finished the post-diagnostic. */
  outcome?: "gain" | "flat" | null;
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
  /** Spec 001 FR-024f: the amount the latest grading applied (null when nobody can know). */
  elo_delta: number | null;
  computed_delta?: number | null;
  contribution?: number | null;
  /** Spec 001 FR-024i: graded 0 automatically as a copy of another student's file. */
  is_copy?: boolean;
  submitted_at: string | null;
  reviewed_at: string | null;
}

/** What `POST /api/student/procedure` answers (spec 001 block 7). */
export interface ProcedureSubmitResult {
  submission_id: number;
  ai_score: number | null;
  ai_feedback: string | null;
  status: string;
  is_copy?: boolean;
  teacher_score?: number | null;
  elo_delta?: number | null;
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

export interface ExamSession {
  id: number;
  course_id: string;
  course_name: string;
  n_questions: number;
  correct_count: number;
  score_pct: number;
  global_elo_after: number | null; // null unless global_elo_status is "rated"
  global_elo_status: "rated" | "pending" | "unknown"; // state at submission (FR-028b)
  created_at: string;
}

export interface ExamTemplateSummary {
  id: number;
  title: string;
  course_id: string;
  n_questions: number;
  time_limit_min: number;
  created_at: string;
  window_ends_at?: string | null;
}

export interface PendingExam {
  template_id: number;
  title: string;
  course_id: string;
  course_name: string;
  time_limit_min: number;
}

export const studentApi = {
  nextQuestion: (body: {
    course_id: string;
    topic?: string;
    block?: string;
    session_correct_ids?: string[];
    session_wrong_timestamps?: Record<string, number>;
    session_questions_count?: number;
  }) => api.post<NextQuestionResponse>("/api/student/next-question", body),

  courseBlocks: (course_id: string) =>
    api.get<{ block: string; item_count: number }[]>(`/api/student/blocks/${course_id}`),

  /** Spec 007 FR-060: one page of five closed matches; `before` = the last match shown. */
  pvpHistory: (before?: number) =>
    api.get<{ matches: PvpHistoryRow[]; has_more: boolean }>(
      `/api/student/pvp/history${before ? `?before=${before}` : ""}`,
    ),

  answer: (body: {
    item_id: string;
    selected_option: string;
    reasoning?: string;
    time_taken?: number;
    elo_topic?: string;
  }, idempotencyKey: string) => api.postWithHeaders<AnswerResponse>(
    "/api/student/answer", body, { "Idempotency-Key": idempotencyKey },
  ),

  stats: () => api.get<StudentStats>("/api/student/stats"),

  courses: () => api.get<Course[]>("/api/student/courses"),

  enroll: (course_id: string) =>
    api.post<{ message: string }>("/api/student/enroll", { course_id }),

  /** Spec 004 FR-025: the student's own display name, under the name filter. */
  changeDisplayName: (display_name: string) =>
    api.put<{ display_name: string }>("/api/student/display-name", { display_name }),

  enrollByCode: (invite_code: string) =>
    api.post<{ message: string; course_id: string }>("/api/student/enroll-by-code", {
      invite_code,
    }),

  unenroll: (course_id: string) => api.delete<void>(`/api/student/enroll/${course_id}`),

  diagnostic: (course_id: string, redo = false) =>
    api.get<DiagnosticStatus>(
      `/api/student/diagnostic/${encodeURIComponent(course_id)}${redo ? "?redo=true" : ""}`
    ),

  submitDiagnostic: (course_id: string, answers: DiagnosticAnswer[], course_name?: string) =>
    api.post<DiagnosticResult>(`/api/student/diagnostic/${encodeURIComponent(course_id)}/submit`, {
      answers,
      course_name: course_name ?? "",
    }),

  courseMap: (course_id: string) =>
    api.get<CourseMap>(`/api/student/map/${encodeURIComponent(course_id)}`),

  lesson: (course_id: string, node_id: string) =>
    api.get<LessonDetail>(
      `/api/student/lessons/${encodeURIComponent(course_id)}/${encodeURIComponent(node_id)}`,
    ),

  lessonEvent: (course_id: string, node_id: string, event: LessonEvent) =>
    api.post<LessonDetail>(
      `/api/student/lessons/${encodeURIComponent(course_id)}/${encodeURIComponent(node_id)}/events`,
      { event },
    ),

  lessonInteraction: (
    course_id: string,
    node_id: string,
    interaction_id: string,
    selected_option: string,
  ) =>
    api.post<LessonInteractionResult>(
      `/api/student/lessons/${encodeURIComponent(course_id)}/${encodeURIComponent(node_id)}/interactions`,
      { interaction_id, selected_option },
    ),

  prealgebraSummary: (course_id: string) =>
    api.get<PrealgebraSummary>(
      `/api/student/prealgebra-summary/${encodeURIComponent(course_id)}`,
    ),

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
  }): Promise<{ review: ProcedureReview; provider: string; analysisToken: string }> => {
    const fd = new FormData();
    fd.append("item_id", params.item_id);
    fd.append("item_content", params.item_content);
    if (params.api_key) fd.append("api_key", params.api_key);
    fd.append("file", params.file);
    const res = await api.postForm<{
      item_id: string;
      provider: string;
      review: ProcedureReview;
      analysis_token: string;
    }>("/api/student/procedure/analyze", fd);
    return { review: res.review, provider: res.provider, analysisToken: res.analysis_token };
  },

  history: () => api.get<{ attempts: unknown[] }>("/api/student/history"),

  examHistory: () => api.get<ExamSession[]>("/api/student/exam/history"),

  examTemplates: (course_id: string) =>
    api.get<ExamTemplateSummary[]>(
      `/api/student/exam/templates?course_id=${encodeURIComponent(course_id)}`,
    ),

  examPending: () => api.get<PendingExam[]>("/api/student/exam/pending"),

  activity: (days = 70) =>
    api.get<{ activity: Record<string, number> }>(`/api/student/activity?days=${days}`),

  streakByCourse: (course_id: string) =>
    api.get<{ course_id: string; streak: number }>(`/api/student/streak/${course_id}`),

  groupRanking: (course_id?: string) => {
    const q = course_id ? `?course_id=${course_id}` : "";
    return api.get<GroupRanking>(`/api/student/group-ranking${q}`);
  },
};
