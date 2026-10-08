/**
 * stores/practiceStore.ts
 * =======================
 * Zustand store para el estado de la sesión de práctica del estudiante.
 * Mantiene la pregunta activa, historial de sesión y timers.
 */

import { create } from "zustand";
import type { AnswerPreview, Item } from "../api/student";

interface PracticeState {
  // Sesión activa
  courseId: string | null;
  block: string | null; // bloque temático activo (concursos)
  topic: string | null; // tópico activo (refuerzo desde el mapa)
  currentItem: Item | null;
  preview: AnswerPreview | null; // from /next-question (spec 001, FR-030)
  sessionCorrectIds: string[];
  sessionWrongTimestamps: Record<string, number>; // item_id → pregunta_num
  sessionQuestionsCount: number;
  questionStartTime: number | null; // timestamp ms

  // Resultado de la última respuesta
  lastAnswer: {
    isCorrect: boolean;
    selectedOption: string;
    eloBefore: number;
    eloAfter: number;
    deltaElo: number;
  } | null;

  // Estado UI
  isLoading: boolean;
  phase: "loading" | "question" | "feedback" | "empty" | "error";

  // Acciones
  startSession: (courseId: string, block?: string, topic?: string) => void;
  setCurrentItem: (item: Item, preview?: AnswerPreview | null) => void;
  recordAnswer: (
    itemId: string,
    isCorrect: boolean,
    selectedOption: string,
    eloBefore: number,
    eloAfter: number,
    deltaElo: number,
  ) => void;
  setLoading: (loading: boolean) => void;
  setPhase: (phase: PracticeState["phase"]) => void;
  resetSession: () => void;
}

export const usePracticeStore = create<PracticeState>()((set) => ({
  courseId: null,
  block: null,
  topic: null,
  currentItem: null,
  preview: null,
  sessionCorrectIds: [],
  sessionWrongTimestamps: {},
  sessionQuestionsCount: 0,
  questionStartTime: null,
  lastAnswer: null,
  isLoading: false,
  phase: "loading",

  startSession: (courseId, block, topic) =>
    set({
      courseId,
      block: block ?? null,
      topic: topic ?? null,
      currentItem: null,
  preview: null,
      sessionCorrectIds: [],
      sessionWrongTimestamps: {},
      sessionQuestionsCount: 0,
      questionStartTime: null,
      lastAnswer: null,
      phase: "loading",
    }),

  setCurrentItem: (item, preview = null) =>
    set({
      currentItem: item,
      preview,
      questionStartTime: Date.now(),
      phase: "question",
      lastAnswer: null,
    }),

  recordAnswer: (itemId, isCorrect, selectedOption, eloBefore, eloAfter, deltaElo) =>
    set((state) => {
      const count = state.sessionQuestionsCount + 1;
      const newCorrectIds = isCorrect
        ? [...state.sessionCorrectIds, itemId]
        : state.sessionCorrectIds;
      const newWrongTs = isCorrect
        ? state.sessionWrongTimestamps
        : { ...state.sessionWrongTimestamps, [itemId]: count };

      return {
        sessionCorrectIds: newCorrectIds,
        sessionWrongTimestamps: newWrongTs,
        sessionQuestionsCount: count,
        lastAnswer: {
          isCorrect,
          selectedOption,
          eloBefore,
          eloAfter,
          deltaElo,
        },
        phase: "feedback",
      };
    }),

  setLoading: (loading) => set({ isLoading: loading }),
  setPhase: (phase) => set({ phase }),

  resetSession: () =>
    set({
      courseId: null,
      block: null,
      topic: null,
      currentItem: null,
  preview: null,
      sessionCorrectIds: [],
      sessionWrongTimestamps: {},
      sessionQuestionsCount: 0,
      questionStartTime: null,
      lastAnswer: null,
      isLoading: false,
      phase: "loading",
    }),
}));
