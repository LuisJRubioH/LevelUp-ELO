/**
 * hooks/usePvpMatch.ts
 * ====================
 * Maneja la conexión WebSocket a la liga PvP.
 * Estados: idle → connecting → waiting → playing → finished
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { ACCESS_EXPIRED, ACCESS_EXPIRED_CLOSE_CODE, rememberAccessExpired } from "../api/client";
import { useAuthStore } from "../stores/authStore";
import { wsBase } from "../api/wsBase";

export type PvpPhase = "idle" | "connecting" | "waiting" | "playing" | "finished";

export interface PvpItem {
  id: string;
  content: string;
  options: string[];
  topic: string;
  difficulty: number;
}

export interface PvpResult {
  won: boolean;
  draw: boolean;
  my_score: number;
  opp_score: number;
  elo_delta: number;
  /** The number to show for the applied delta, rounded on the server (survey 007 V14). */
  elo_delta_display: number;
  /** null = applied; 'no_rated_topics' | 'not_applied' = 0 applied (spec 001). */
  elo_reason?: string | null;
  /** Spec 004 FR-051: closed without a winner and without rating change, and why. */
  abandoned?: boolean;
  reason?: string | null;
}

/** The server's verdict on the last answer, shown on that item before the next one appears. */
export interface PvpFeedback {
  itemId: string;
  correct: boolean;
}

const FEEDBACK_MS = 700;

/** Why the server closed the socket before the match ended (api/websocket/pvp.py). */
const CLOSE_NOTICES: Record<number, string> = {
  4001: "No pudimos entrar a la arena. Vuelve a iniciar sesión y revisa que estés inscrito en la materia.",
  4404: "Esta materia todavía no tiene preguntas para la liga.",
  4500: "Hubo un problema en el servidor. Intenta de nuevo.",
  [ACCESS_EXPIRED_CLOSE_CODE]: ACCESS_EXPIRED,
};

function closeNotice(code: number, phase: PvpPhase): string {
  if (CLOSE_NOTICES[code]) return CLOSE_NOTICES[code];
  if (phase === "playing") return "Se perdió la conexión con la partida.";
  if (phase === "waiting") return "La búsqueda de rival terminó sin encontrar a nadie. Intenta de nuevo.";
  return "No pudimos conectar con la arena. Intenta de nuevo.";
}

export function usePvpMatch(courseId: string | null) {
  const token = useAuthStore((s) => s.accessToken);
  const [phase, setPhase] = useState<PvpPhase>("idle");
  const [items, setItems] = useState<PvpItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [myScore, setMyScore] = useState(0);
  const [oppScore, setOppScore] = useState(0);
  // elo = the rival's shown course rating; null = pending diagnostic (spec 001)
  const [opponent, setOpponent] = useState<{ name: string; elo: number | null } | null>(null);
  const [result, setResult] = useState<PvpResult | null>(null);
  const [timeLeft, setTimeLeft] = useState(180);
  const [feedback, setFeedback] = useState<PvpFeedback | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const feedbackRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const phaseRef = useRef<PvpPhase>("idle");

  const goTo = (next: PvpPhase) => {
    phaseRef.current = next;
    setPhase(next);
  };

  const clearFeedback = () => {
    if (feedbackRef.current) clearTimeout(feedbackRef.current);
    feedbackRef.current = null;
  };

  const stopTimer = () => {
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const startTimer = (seconds: number) => {
    stopTimer();
    setTimeLeft(seconds);
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) { stopTimer(); return 0; }
        return t - 1;
      });
    }, 1000);
  };

  const connect = useCallback(() => {
    if (!courseId || !token) return;
    goTo("connecting");
    clearFeedback();
    setNotice(null);
    setItems([]);
    setCurrentIndex(0);
    setMyScore(0);
    setOppScore(0);
    setResult(null);
    setFeedback(null);

    const socket = new WebSocket(`${wsBase()}/api/ws/pvp/${courseId}`);
    ws.current = socket;

    socket.onopen = () => {
      socket.send(JSON.stringify({ token }));
    };

    socket.onmessage = (e) => {
      let msg;
      try {
        msg = JSON.parse(e.data);
      } catch {
        return;
      }
      switch (msg.type) {
        case "waiting":
          goTo("waiting");
          break;
        case "game_start":
          setItems(msg.items);
          setOpponent(msg.opponent);
          goTo("playing");
          startTimer(msg.duration_seconds ?? 180);
          break;
        case "answer_result":
          setMyScore(msg.your_score);
          setOppScore(msg.opp_score);
          // The verdict stays on the answered item for a moment, then the next item appears.
          clearFeedback();
          setFeedback({ itemId: msg.item_id, correct: msg.is_correct });
          feedbackRef.current = setTimeout(() => {
            feedbackRef.current = null;
            setFeedback(null);
            setCurrentIndex((i) => i + 1);
          }, FEEDBACK_MS);
          break;
        case "opponent_update":
          setOppScore(msg.opp_score);
          break;
        case "game_end":
          stopTimer();
          clearFeedback();
          setResult({
            won: msg.won, draw: msg.draw,
            my_score: msg.your_score, opp_score: msg.opp_score,
            elo_delta: msg.elo_delta,
            elo_delta_display: msg.elo_delta_display ?? 0,
            elo_reason: msg.elo_reason ?? null,
            abandoned: !!msg.abandoned,
            reason: msg.reason ?? null,
          });
          goTo("finished");
          break;
      }
    };

    // phaseRef lee el phase ACTUAL, no el capturado en el closure.
    // Si el servidor cierra el socket tras game_end, NO debemos volver a "idle"
    // (eso devolvía al perdedor al lobby tras recibir su resultado). Un socket que el
    // estudiante ya dejó (Cancelar, Jugar de nuevo) no cambia nada.
    socket.onclose = (e) => {
      if (ws.current !== socket) return;
      stopTimer();
      clearFeedback();
      // Spec 004 FR-047: this account expired. The result stays on screen if it arrived; the
      // next request ends the session and the login says why.
      if (e.code === ACCESS_EXPIRED_CLOSE_CODE) rememberAccessExpired();
      if (phaseRef.current === "finished") return;
      setNotice(closeNotice(e.code, phaseRef.current));
      goTo("idle");
    };

    // Un error siempre llega seguido de onclose, que decide qué mostrar.
    socket.onerror = () => {
      stopTimer();
    };
  }, [courseId, token]);

  const sendAnswer = useCallback((itemId: string, selected: string) => {
    ws.current?.send(JSON.stringify({ type: "answer", item_id: itemId, selected }));
  }, []);

  const disconnect = useCallback(() => {
    stopTimer();
    clearFeedback();
    const socket = ws.current;
    ws.current = null;
    socket?.close();
    setNotice(null);
    goTo("idle");
  }, []);

  useEffect(() => () => {
    stopTimer();
    clearFeedback();
    const socket = ws.current;
    ws.current = null;
    socket?.close();
  }, []);

  const currentItem = items[currentIndex] ?? null;
  const totalItems = items.length;

  return {
    phase, connect, disconnect, sendAnswer,
    currentItem, currentIndex, totalItems,
    myScore, oppScore, opponent,
    result, timeLeft, feedback, notice,
  };
}
