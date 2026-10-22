/**
 * hooks/usePvpMatch.ts
 * ====================
 * Maneja la conexión WebSocket a la liga PvP.
 * Estados: idle → connecting → waiting → playing (⇄ reconnecting) → finished
 *
 * Spec 007 delivery F: the countdown runs to the server's end time (`ends_at`, corrected by
 * `server_now`), so a tab that slept shows the right time on its first tick back; the screen never
 * ends the match itself (FR-040). A connection that drops during a match reconnects on its own for
 * up to the server's grace, presenting the `resume` token the server sent, which the tab keeps in
 * sessionStorage so a reload can come back too (FR-042, O-F1).
 *
 * Spec 007 delivery M: an item arrives with its image and without its difficulty (FR-032); a
 * match the server will not rate says so in `game_start` (`rated: false`, `unrated_reason`), and
 * the screen shows it as given (FR-031, O-M6).
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuthStore } from "../stores/authStore";
import { refreshAccessToken } from "../api/client";
import { wsBase } from "../api/wsBase";

export type PvpPhase = "idle" | "connecting" | "waiting" | "playing" | "reconnecting" | "finished";

export interface PvpItem {
  id: string;
  content: string;
  options: string[];
  topic: string;
  /** Spec 007 FR-032: the item's figure, a path the API serves; null when it has none. */
  image_url?: string | null;
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
  /** Spec 007 FR-041: equal scores, decided by total answer time. */
  tiebreak: boolean;
  /** Spec 007 FR-042: a player left and did not come back within the grace. */
  forfeit: boolean;
}

/** The server's verdict on the last answer, shown on that item before the next one appears. */
export interface PvpFeedback {
  itemId: string;
  correct: boolean;
}

const FEEDBACK_MS = 700;
/** Spec 007 FR-042: retry at once, then every 2 s, for as long as the server keeps the place. */
const RECONNECT_EVERY_MS = 2000;
const RECONNECT_WINDOW_MS = 20_000; // the server's grace (O2)

/** Why the server closed the League socket: a key under `league.closeNotices` (i18n). */
const CLOSE_NOTICES: Record<number, string> = {
  4001: "authFailed",
  4404: "noItems",
  4409: "secondTab", // spec 007 FR-050
  4410: "matchOver", // spec 007 FR-042: the grace ended before the reconnect
  4411: "resumedElsewhere", // spec 007 FR-042: another tab took the match over
  4429: "tooManyMessages", // spec 007 FR-051
  4500: "serverError",
};

function closeNotice(code: number, phase: PvpPhase): string {
  const key =
    CLOSE_NOTICES[code] ??
    (phase === "playing" || phase === "reconnecting"
      ? "lostMatch"
      : phase === "waiting"
        ? "noRival"
        : "cannotConnect");
  return `league.closeNotices.${key}`;
}

/** This browser's clock, read when a reconnect is scheduled (never during render). */
const wallClock = () => Date.now();

/** A dropped connection, not a close the server chose (1000) or explained (4xxx). */
const isDrop = (code: number) => code !== 1000 && code < 4000;

/** The server's reason for not rating a match, as it sent it; null for a rated match. */
const unratedOf = (msg: { rated?: boolean; unrated_reason?: string | null }) =>
  msg.rated === false ? (msg.unrated_reason ?? "daily_cap") : null;

const resumeKey = (courseId: string) => `oulad.pvp.resume.${courseId}`;

function readResume(courseId: string): string | null {
  try {
    return sessionStorage.getItem(resumeKey(courseId));
  } catch {
    return null;
  }
}

function writeResume(courseId: string, token: unknown) {
  if (typeof token !== "string") return;
  try {
    sessionStorage.setItem(resumeKey(courseId), token);
  } catch {
    /* storage unavailable: a drop can still be resumed while this page lives */
  }
}

function clearResume(courseId: string) {
  try {
    sessionStorage.removeItem(resumeKey(courseId));
  } catch {
    /* nothing stored */
  }
}

interface Reconnect {
  deadline: number;
  timer: ReturnType<typeof setTimeout> | null;
  refreshed: boolean;
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
  /** Seconds the rival has to come back; null = the rival is connected. */
  const [opponentAway, setOpponentAway] = useState<number | null>(null);
  /** Seconds left to reconnect while `reconnecting`. */
  const [reconnectLeft, setReconnectLeft] = useState(0);
  /** Spec 007 FR-031: why the server will not rate this match ("daily_cap"); null = rated. */
  const [unratedReason, setUnratedReason] = useState<string | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const feedbackRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const phaseRef = useRef<PvpPhase>("idle");
  const endsAtRef = useRef<number | null>(null); // the server's end time, ms since the epoch
  const offsetRef = useRef(0); // server clock − this browser's clock, ms
  const reconnectRef = useRef<Reconnect | null>(null);

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
    timerRef.current = null;
  };

  const endReconnect = () => {
    const r = reconnectRef.current;
    if (r?.timer) clearTimeout(r.timer);
    reconnectRef.current = null;
  };

  /** Every tick reads the clock again: a tab whose timers slept is right on its first tick. */
  const tick = useCallback(() => {
    const ends = endsAtRef.current;
    if (ends != null) {
      setTimeLeft(Math.max(0, Math.ceil((ends - (Date.now() + offsetRef.current)) / 1000)));
    }
    const r = reconnectRef.current;
    if (r) setReconnectLeft(Math.max(0, Math.ceil((r.deadline - Date.now()) / 1000)));
  }, []);

  /** FR-040: count down to the server's `ends_at`, corrected by its `server_now`. */
  const startClock = (msg: { ends_at?: string; server_now?: string; duration_seconds?: number }) => {
    const serverNow = msg.server_now ? Date.parse(msg.server_now) : NaN;
    offsetRef.current = Number.isFinite(serverNow) ? serverNow - Date.now() : 0;
    const ends = msg.ends_at ? Date.parse(msg.ends_at) : NaN;
    endsAtRef.current = Number.isFinite(ends)
      ? ends
      : Date.now() + offsetRef.current + (msg.duration_seconds ?? 180) * 1000;
    stopTimer();
    tick();
    timerRef.current = setInterval(tick, 1000);
  };

  useEffect(() => {
    document.addEventListener("visibilitychange", tick);
    return () => document.removeEventListener("visibilitychange", tick);
  }, [tick]);

  const giveUp = (noticeKey: string) => {
    stopTimer();
    clearFeedback();
    endReconnect();
    setOpponentAway(null);
    setNotice(noticeKey);
    goTo("idle");
  };

  const openSocket = (course: string, resume: string | null) => {
    const socket = new WebSocket(`${wsBase()}/api/ws/pvp/${course}`);
    ws.current = socket;

    socket.onopen = () => {
      // The store's token, read now: a refresh during a reconnect replaced it.
      const access = useAuthStore.getState().accessToken;
      socket.send(JSON.stringify(resume ? { token: access, resume } : { token: access }));
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
          writeResume(course, msg.resume);
          goTo("waiting");
          break;
        case "game_start":
          writeResume(course, msg.resume);
          endReconnect();
          setUnratedReason(unratedOf(msg));
          setItems(msg.items);
          setOpponent(msg.opponent);
          goTo("playing");
          startClock(msg);
          break;
        case "game_resume": {
          // FR-042: the same match, where it was — the first item not yet answered.
          endReconnect();
          clearFeedback();
          setFeedback(null);
          const answered = new Set<string>(msg.answered ?? []);
          const next = (msg.items as PvpItem[]).findIndex((item) => !answered.has(item.id));
          setUnratedReason(unratedOf(msg));
          setItems(msg.items);
          setCurrentIndex(next === -1 ? msg.items.length : next);
          setMyScore(msg.your_score);
          setOppScore(msg.opp_score);
          setOpponent(msg.opponent);
          setOpponentAway(null);
          goTo("playing");
          startClock(msg);
          break;
        }
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
        case "opponent_away":
          setOpponentAway(msg.grace_seconds ?? 20);
          break;
        case "opponent_back":
          setOpponentAway(null);
          break;
        case "game_end":
          clearResume(course);
          endReconnect();
          stopTimer();
          clearFeedback();
          setOpponentAway(null);
          setResult({
            won: msg.won, draw: msg.draw,
            my_score: msg.your_score, opp_score: msg.opp_score,
            elo_delta: msg.elo_delta,
            elo_delta_display: msg.elo_delta_display ?? 0,
            elo_reason: msg.elo_reason ?? null,
            tiebreak: !!msg.tiebreak,
            forfeit: !!msg.forfeit,
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
      if (phaseRef.current === "finished") return;
      const live = phaseRef.current === "playing" || phaseRef.current === "reconnecting";
      const stored = readResume(course);
      if (live && stored && isDrop(e.code)) {
        reconnect(course, stored);
        return;
      }
      // An access token that expired during the reconnect: refreshed once, then retried.
      if (phaseRef.current === "reconnecting" && stored && e.code === 4001) {
        const r = reconnectRef.current;
        if (r && !r.refreshed) {
          r.refreshed = true;
          void refreshAccessToken().then((renewed) => {
            if (ws.current !== socket) return;
            if (renewed) reconnect(course, stored);
            else giveUp(closeNotice(e.code, phaseRef.current));
          });
          return;
        }
      }
      if (e.code === 4410 || e.code === 4411) clearResume(course);
      giveUp(closeNotice(e.code, phaseRef.current));
    };

    // Un error siempre llega seguido de onclose, que decide qué mostrar.
    socket.onerror = () => {};
  };

  /** FR-042: try again at once, then every 2 s, until the server's grace is over. */
  function reconnect(course: string, resume: string) {
    const now = wallClock();
    if (reconnectRef.current === null) {
      reconnectRef.current = { deadline: now + RECONNECT_WINDOW_MS, timer: null, refreshed: false };
      clearFeedback();
      setFeedback(null);
      goTo("reconnecting");
      tick();
      reconnectRef.current.timer = setTimeout(() => openSocket(course, resume), 0);
      return;
    }
    if (now >= reconnectRef.current.deadline) {
      clearResume(course);
      giveUp("league.closeNotices.lostMatch");
      return;
    }
    reconnectRef.current.timer = setTimeout(() => openSocket(course, resume), RECONNECT_EVERY_MS);
  }

  const connect = useCallback(() => {
    if (!courseId || !token) return;
    goTo("connecting");
    clearFeedback();
    endReconnect();
    setNotice(null);
    setItems([]);
    setCurrentIndex(0);
    setMyScore(0);
    setOppScore(0);
    setResult(null);
    setFeedback(null);
    setOpponentAway(null);
    setUnratedReason(null);
    endsAtRef.current = null;
    // A reload during a match comes back to it with the tab's resume token (O-F1).
    openSocket(courseId, readResume(courseId));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId, token]);

  const sendAnswer = useCallback((itemId: string, selected: string) => {
    ws.current?.send(JSON.stringify({ type: "answer", item_id: itemId, selected }));
  }, []);

  const disconnect = useCallback(() => {
    stopTimer();
    clearFeedback();
    endReconnect();
    if (courseId) clearResume(courseId);
    const socket = ws.current;
    ws.current = null;
    socket?.close();
    setNotice(null);
    setOpponentAway(null);
    goTo("idle");
  }, [courseId]);

  useEffect(() => () => {
    stopTimer();
    clearFeedback();
    endReconnect();
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
    opponentAway, reconnectLeft, unratedReason,
  };
}
