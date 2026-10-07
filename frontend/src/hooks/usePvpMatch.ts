/**
 * hooks/usePvpMatch.ts
 * ====================
 * Maneja la conexión WebSocket a la liga PvP.
 * Estados: idle → connecting → waiting → playing → finished
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuthStore } from "../stores/authStore";

const API_BASE = import.meta.env.VITE_API_URL ?? "";
const WS_BASE = API_BASE.replace(/^http/, "ws");

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
  /** null = applied; 'no_rated_topics' | 'not_applied' = 0 applied (spec 001). */
  elo_reason?: string | null;
}

export function usePvpMatch(courseId: string | null) {
  const token = useAuthStore((s) => s.accessToken);
  const [phase, setPhase] = useState<PvpPhase>("idle");
  const [items, setItems] = useState<PvpItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [myScore, setMyScore] = useState(0);
  const [oppScore, setOppScore] = useState(0);
  const [opponent, setOpponent] = useState<{ username: string; elo: number } | null>(null);
  const [result, setResult] = useState<PvpResult | null>(null);
  const [timeLeft, setTimeLeft] = useState(180);
  const [lastCorrect, setLastCorrect] = useState<boolean | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

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
    setPhase("connecting");
    setItems([]);
    setCurrentIndex(0);
    setMyScore(0);
    setOppScore(0);
    setResult(null);
    setLastCorrect(null);

    const socket = new WebSocket(`${WS_BASE}/api/ws/pvp/${courseId}`);
    ws.current = socket;

    socket.onopen = () => {
      socket.send(JSON.stringify({ token }));
    };

    socket.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      switch (msg.type) {
        case "waiting":
          setPhase("waiting");
          break;
        case "game_start":
          setItems(msg.items);
          setOpponent(msg.opponent);
          setPhase("playing");
          startTimer(msg.duration_seconds ?? 180);
          break;
        case "answer_result":
          setMyScore(msg.your_score);
          setOppScore(msg.opp_score);
          setLastCorrect(msg.is_correct);
          setCurrentIndex((i) => i + 1);
          break;
        case "opponent_update":
          setOppScore(msg.opp_score);
          break;
        case "game_end":
          stopTimer();
          setResult({
            won: msg.won, draw: msg.draw,
            my_score: msg.your_score, opp_score: msg.opp_score,
            elo_delta: msg.elo_delta,
            elo_reason: msg.elo_reason ?? null,
          });
          setPhase("finished");
          break;
      }
    };

    // Forma funcional: lee el phase ACTUAL, no el capturado en el closure.
    // Si el servidor cierra el socket tras game_end, NO debemos volver a "idle"
    // (eso devolvía al perdedor al lobby tras recibir su resultado).
    socket.onclose = () => {
      stopTimer();
      setPhase((p) => (p === "finished" ? "finished" : "idle"));
    };

    socket.onerror = () => {
      stopTimer();
      setPhase((p) => (p === "finished" ? "finished" : "idle"));
    };
  }, [courseId, token]);

  const sendAnswer = useCallback((itemId: string, selected: string) => {
    ws.current?.send(JSON.stringify({ type: "answer", item_id: itemId, selected }));
  }, []);

  const disconnect = useCallback(() => {
    stopTimer();
    ws.current?.close();
    ws.current = null;
    setPhase("idle");
  }, []);

  useEffect(() => () => { stopTimer(); ws.current?.close(); }, []);

  const currentItem = items[currentIndex] ?? null;
  const totalItems = items.length;

  return {
    phase, connect, disconnect, sendAnswer,
    currentItem, currentIndex, totalItems,
    myScore, oppScore, opponent,
    result, timeLeft, lastCorrect,
  };
}
