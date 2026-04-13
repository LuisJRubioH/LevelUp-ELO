/**
 * hooks/useTimer.ts
 * =================
 * Timer nativo React — sin JavaScript embebido vía iframe.
 * Actualiza cada segundo con useEffect + setInterval.
 */

import { useEffect, useRef, useState } from "react";

interface UseTimerOptions {
  autoStart?: boolean;
  onExpire?: () => void;
  limitSeconds?: number; // si se pasa, el timer cuenta regresiva
}

export function useTimer(options: UseTimerOptions = {}) {
  const { autoStart = true, onExpire, limitSeconds } = options;
  const [seconds, setSeconds] = useState(0);
  const [running, setRunning] = useState(autoStart);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!running) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    intervalRef.current = setInterval(() => {
      setSeconds((s) => {
        const next = s + 1;
        if (limitSeconds && next >= limitSeconds) {
          setRunning(false);
          onExpire?.();
        }
        return next;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [running, limitSeconds, onExpire]);

  const reset = () => setSeconds(0);
  const start = () => setRunning(true);
  const stop = () => setRunning(false);

  const formatted = () => {
    const m = Math.floor(seconds / 60)
      .toString()
      .padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  return { seconds, formatted: formatted(), running, start, stop, reset };
}
