/**
 * hooks/useNotifications.ts
 * ==========================
 * Hook que conecta al WebSocket de notificaciones en tiempo real.
 * Maneja reconexión automática y cleanup en desmontaje.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuthStore } from "../stores/authStore";

export type NotificationEvent = {
  type: string;
  [key: string]: unknown;
};

interface UseNotificationsOptions {
  room: string; // ej: "teacher_42", "student_7"
  onEvent?: (event: NotificationEvent) => void;
  enabled?: boolean;
}

const MAX_RETRIES = 8;
const BASE_DELAY_MS = 2000;

export function useNotifications({ room, onEvent, enabled = true }: UseNotificationsOptions) {
  const { accessToken } = useAuthStore();
  const wsRef = useRef<WebSocket | null>(null);
  const retryCountRef = useRef(0);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [connected, setConnected] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  // Stable ref for onEvent — avoids recreating connect on every parent render
  const onEventRef = useRef(onEvent);
  useEffect(() => { onEventRef.current = onEvent; }, [onEvent]);

  const connect = useCallback(() => {
    if (!accessToken || !enabled) return;

    // En producción (Vercel + Render separados) VITE_API_URL = "https://levelup-elo.onrender.com"
    // → wsBase = "wss://levelup-elo.onrender.com"
    // En dev (proxy Vite a localhost:8000), VITE_API_URL="" → usa el mismo host
    const apiBase = import.meta.env.VITE_API_URL as string | undefined;
    const wsBase = apiBase
      ? apiBase.replace(/^https/, "wss").replace(/^http(?!s)/, "ws")
      : `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`;
    const wsUrl = `${wsBase}/api/ws/notifications/${room}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      retryCountRef.current = 0; // reset backoff on successful open
      ws.send(JSON.stringify({ token: accessToken }));
    };

    ws.onmessage = (e) => {
      try {
        const msg: NotificationEvent = JSON.parse(e.data);
        if (msg.type === "connected") {
          setConnected(true);
        } else if (msg.type === "ping") {
          ws.send(JSON.stringify({ type: "pong" }));
        } else {
          setUnreadCount((n) => n + 1);
          onEventRef.current?.(msg);
        }
      } catch {
        /* ignorar mensajes malformados */
      }
    };

    ws.onclose = () => {
      setConnected(false);
      if (retryCountRef.current >= MAX_RETRIES) return; // stop retrying
      // Exponential backoff: 2s, 4s, 8s, 16s, 32s, 60s cap
      const delay = Math.min(BASE_DELAY_MS * Math.pow(2, retryCountRef.current), 60000);
      retryCountRef.current += 1;
      retryTimerRef.current = setTimeout(() => connect(), delay);
    };

    ws.onerror = () => ws.close();
  }, [accessToken, room, enabled]); // onEvent removed — use ref instead

  useEffect(() => {
    retryCountRef.current = 0;
    connect();
    return () => {
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const clearUnread = () => setUnreadCount(0);

  return { connected, unreadCount, clearUnread };
}
