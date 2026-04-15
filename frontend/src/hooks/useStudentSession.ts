/**
 * hooks/useStudentSession.ts
 * ==========================
 * Hook que orquesta la sesión de práctica: fetch de pregunta, submit de
 * respuesta, actualización del store. Desacopla la lógica de los componentes.
 *
 * Usa `usePracticeStore.getState()` dentro de los callbacks para leer el estado
 * sin crear dependencias reactivas — evita el loop infinito que ocurre cuando
 * `[store]` se usa como dep de useCallback y cada setLoading() dispara un nuevo
 * render que recrea el callback y vuelve a disparar el useEffect.
 */

import { useCallback } from "react";
import { studentApi } from "../api/student";
import { usePracticeStore } from "../stores/practiceStore";

export function useStudentSession() {
  // Solo lecturas reactivas para el render — no pasan como deps a useCallback
  const currentItem = usePracticeStore((s) => s.currentItem);
  const lastAnswer = usePracticeStore((s) => s.lastAnswer);
  const phase = usePracticeStore((s) => s.phase);
  const isLoading = usePracticeStore((s) => s.isLoading);
  const sessionQuestionsCount = usePracticeStore((s) => s.sessionQuestionsCount);

  const loadNextQuestion = useCallback(async () => {
    // Lee estado actual al momento de la llamada — sin crear subscripción reactiva
    const store = usePracticeStore.getState();
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
        usePracticeStore.getState().setPhase("empty");
      } else {
        usePracticeStore.getState().setCurrentItem(res.item);
      }
    } catch (err) {
      console.error("Error al cargar pregunta:", err);
      usePracticeStore.getState().setPhase("error");
    } finally {
      usePracticeStore.getState().setLoading(false);
    }
  }, []); // Sin deps — lee getState() en runtime

  const submitAnswer = useCallback(
    async (selectedOption: string, reasoning = "") => {
      const store = usePracticeStore.getState();
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

        usePracticeStore.getState().recordAnswer(
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
    [], // Sin deps — lee getState() en runtime
  );

  return {
    currentItem,
    lastAnswer,
    phase,
    isLoading,
    sessionQuestionsCount,
    loadNextQuestion,
    submitAnswer,
  };
}
