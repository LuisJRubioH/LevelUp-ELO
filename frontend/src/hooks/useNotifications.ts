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

export function useNotifications({ room, onEvent, enabled = true }: UseNotificationsOptions) {
  const { accessToken } = useAuthStore();
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

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
      // Autenticarse con el JWT como primer mensaje
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
          onEvent?.(msg);
        }
      } catch {
        /* ignorar mensajes malformados */
      }
    };

    ws.onclose = () => {
      setConnected(false);
      // Reconexión automática después de 5 s
      setTimeout(() => connect(), 5000);
    };

    ws.onerror = () => ws.close();
  }, [accessToken, room, enabled, onEvent]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const clearUnread = () => setUnreadCount(0);

  return { connected, unreadCount, clearUnread };
}
