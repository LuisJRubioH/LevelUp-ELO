/**
 * stores/practiceStore.ts
 * =======================
 * Zustand store para el estado de la sesión de práctica del estudiante.
 * Mantiene la pregunta activa, historial de sesión y timers.
 */

import { create } from "zustand";
import type { Item } from "../api/student";

interface PracticeState {
  // Sesión activa
  courseId: string | null;
  currentItem: Item | null;
  sessionCorrectIds: string[];
  sessionWrongTimestamps: Record<string, number>; // item_id → pregunta_num
  sessionQuestionsCount: number;
  questionStartTime: number | null; // timestamp ms

  // Resultado de la última respuesta
  lastAnswer: {
    isCorrect: boolean;
    correctOption: string;
    selectedOption: string;
    eloBefore: number;
    eloAfter: number;
    deltaElo: number;
  } | null;

  // Estado UI
  isLoading: boolean;
  phase: "loading" | "question" | "feedback" | "empty";

  // Acciones
  startSession: (courseId: string) => void;
  setCurrentItem: (item: Item) => void;
  recordAnswer: (
    itemId: string,
    isCorrect: boolean,
    correctOption: string,
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
  currentItem: null,
  sessionCorrectIds: [],
  sessionWrongTimestamps: {},
  sessionQuestionsCount: 0,
  questionStartTime: null,
  lastAnswer: null,
  isLoading: false,
  phase: "loading",

  startSession: (courseId) =>
    set({
      courseId,
      currentItem: null,
      sessionCorrectIds: [],
      sessionWrongTimestamps: {},
      sessionQuestionsCount: 0,
      questionStartTime: null,
      lastAnswer: null,
      phase: "loading",
    }),

  setCurrentItem: (item) =>
    set({
      currentItem: item,
      questionStartTime: Date.now(),
      phase: "question",
      lastAnswer: null,
    }),

  recordAnswer: (itemId, isCorrect, correctOption, selectedOption, eloBefore, eloAfter, deltaElo) =>
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
          correctOption,
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
      currentItem: null,
      sessionCorrectIds: [],
      sessionWrongTimestamps: {},
      sessionQuestionsCount: 0,
      questionStartTime: null,
      lastAnswer: null,
      isLoading: false,
      phase: "loading",
    }),
}));
