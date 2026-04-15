/**
 * components/ui/PWAPrompt.tsx
 * ============================
 * Prompt de instalación PWA. Aparece una sola vez si el navegador expone
 * `beforeinstallprompt` y el usuario no ha rechazado antes.
 */

import { useEffect, useState } from "react";
import { Button } from "./Button";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

const DISMISS_KEY = "pwa-prompt-dismissed";

export function PWAPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (localStorage.getItem(DISMISS_KEY) === "1") return;

    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setVisible(true);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const install = async () => {
    if (!deferredPrompt) return;
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      localStorage.setItem(DISMISS_KEY, "1");
    }
    setVisible(false);
    setDeferredPrompt(null);
  };

  const dismiss = () => {
    localStorage.setItem(DISMISS_KEY, "1");
    setVisible(false);
  };

  if (!visible || !deferredPrompt) return null;

  return (
    <div className="fixed bottom-20 md:bottom-4 right-4 z-40 max-w-sm bg-slate-800 border border-violet-600/40 rounded-xl shadow-xl p-4 space-y-3">
      <div className="flex items-start gap-3">
        <span className="text-2xl">📱</span>
        <div className="flex-1">
          <p className="text-sm font-medium text-white">Instalar LevelUp ELO</p>
          <p className="text-xs text-slate-400 mt-0.5">
            Accede más rápido desde tu pantalla de inicio y úsalo offline.
          </p>
        </div>
      </div>
      <div className="flex gap-2 justify-end">
        <Button size="sm" variant="ghost" onClick={dismiss}>
          Ahora no
        </Button>
        <Button size="sm" onClick={install}>
          Instalar
        </Button>
      </div>
    </div>
  );
}
