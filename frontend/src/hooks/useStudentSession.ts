/**
 * hooks/useStudentSession.ts
 * ==========================
 * Hook que orquesta la sesión de práctica: fetch de pregunta, submit de
 * respuesta, actualización del store. Desacopla la lógica de los componentes.
 */

import { useCallback } from "react";
import { studentApi } from "../api/student";
import { usePracticeStore } from "../stores/practiceStore";

export function useStudentSession() {
  const store = usePracticeStore();

  const loadNextQuestion = useCallback(async () => {
    if (!store.courseId) return;
    store.setLoading(true);
    try {
      const res = await studentApi.nextQuestion({
        course_id: store.courseId,
        session_correct_ids: store.sessionCorrectIds,
        session_wrong_timestamps: store.sessionWrongTimestamps,
        session_questions_count: store.sessionQuestionsCount,
      });

      if (!res.item || res.status !== "ok") {
        store.setPhase("empty");
      } else {
        store.setCurrentItem(res.item);
      }
    } catch (err) {
      console.error("Error al cargar pregunta:", err);
      store.setPhase("error");
    } finally {
      store.setLoading(false);
    }
  }, [store]);

  const submitAnswer = useCallback(
    async (selectedOption: string, reasoning = "") => {
      if (!store.currentItem) return;

      const timeTaken = store.questionStartTime
        ? (Date.now() - store.questionStartTime) / 1000
        : undefined;

      try {
        const res = await studentApi.answer({
          item_id: store.currentItem.id,
          item_data: store.currentItem,
          selected_option: selectedOption,
          reasoning,
          time_taken: timeTaken,
          elo_topic: store.courseId ?? undefined,
        });

        store.recordAnswer(
          store.currentItem.id,
          res.is_correct,
          res.correct_option,
          selectedOption,
          res.elo_before,
          res.elo_after,
          res.delta_elo,
        );
      } catch (err) {
        console.error("Error al enviar respuesta:", err);
      }
    },
    [store],
  );

  return {
    currentItem: store.currentItem,
    lastAnswer: store.lastAnswer,
    phase: store.phase,
    isLoading: store.isLoading,
    sessionQuestionsCount: store.sessionQuestionsCount,
    loadNextQuestion,
    submitAnswer,
  };
}
