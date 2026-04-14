/**
 * components/ui/StreakToast.tsx
 * ==============================
 * Toast de celebración para rachas de respuestas correctas consecutivas.
 * Se muestra durante 3 segundos y luego desaparece con fade-out.
 */

import { useEffect, useState } from "react";

interface StreakToastProps {
  streak: number; // 5, 10, 20 o cualquier hito
  onDismiss: () => void;
}

const STREAK_MESSAGES: Record<number, { emoji: string; title: string; subtitle: string }> = {
  5: {
    emoji: "🔥",
    title: "¡Racha de 5!",
    subtitle: "¡Llevas 5 respuestas correctas seguidas!",
  },
  10: {
    emoji: "⚡",
    title: "¡Racha imparable!",
    subtitle: "¡10 correctas consecutivas! KatIA está impresionada.",
  },
  20: {
    emoji: "🏆",
    title: "¡LEYENDA!",
    subtitle: "¡20 seguidas! Eres una máquina de aprender.",
  },
};

export function StreakToast({ streak, onDismiss }: StreakToastProps) {
  const [visible, setVisible] = useState(true);
  const data = STREAK_MESSAGES[streak] ?? {
    emoji: "🔥",
    title: `¡Racha de ${streak}!`,
    subtitle: `${streak} respuestas correctas seguidas`,
  };

  useEffect(() => {
    const hideTimer = setTimeout(() => setVisible(false), 2700);
    const dismissTimer = setTimeout(onDismiss, 3200);
    return () => {
      clearTimeout(hideTimer);
      clearTimeout(dismissTimer);
    };
  }, [onDismiss]);

  return (
    <div
      className={[
        "fixed top-4 left-1/2 -translate-x-1/2 z-50 transition-all duration-500",
        visible ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-4",
      ].join(" ")}
      role="status"
      aria-live="polite"
    >
      <div className="bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-2xl px-6 py-4 shadow-2xl border border-violet-400/30 flex items-center gap-4">
        <span className="text-3xl">{data.emoji}</span>
        <div>
          <div className="text-white font-bold text-base">{data.title}</div>
          <div className="text-violet-200 text-sm">{data.subtitle}</div>
        </div>
      </div>
    </div>
  );
}
