/**
 * components/KatIA/SocraticChat.tsx
 * ===================================
 * Chat socrático con KatIA usando SSE streaming desde /api/ai/socratic.
 * Muestra el avatar de KatIA (gata cyborg) junto a cada mensaje.
 *
 * Spec 005: the request carries the exercise's id, the message and the language — the server
 * reads the exercise from its store and the conversation from its own record (FR-018). A
 * provider is named only with the student's own key (FR-029). Every refusal arrives with a
 * code and is shown as a translated message, never as a raw status (FR-036).
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { authorizedFetch } from "../../api/client";
import { Button } from "../ui/Button";
import { MathText } from "../Math/MathContent";

interface Message {
  role: "student" | "katia";
  text: string;
  streaming?: boolean;
}

interface SocraticChatProps {
  itemId: string;
  apiKey?: string;
  provider?: string;
}

/** Refusal codes the API sends (spec 005 contracts/api.md); each has a translated message. */
const REFUSAL_CODES = [
  "item_not_found",
  "not_enrolled",
  "exam_active",
  "not_served",
  "message_too_long",
  "katia_not_configured",
  "unknown_provider",
  "katia_unavailable",
  "rate_limited",
] as const;

class KatiaRefusal extends Error {
  code: string;

  constructor(code: string) {
    super(code);
    this.code = code;
  }
}

async function refusalCode(res: Response): Promise<string> {
  if (res.status === 429) return "rate_limited";
  try {
    const body = await res.json();
    const code = body?.detail?.code;
    if ((REFUSAL_CODES as readonly string[]).includes(code)) return code;
  } catch {
    /* not JSON: the generic message */
  }
  return "generic";
}

export function SocraticChat({ itemId, apiKey = "", provider = "" }: SocraticChatProps) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language?.startsWith("en") ? "en" : "es";

  const randomWelcome = useCallback(() => {
    const bank = t("socratic.welcome", { returnObjects: true }) as Record<string, string>;
    const values = Object.values(bank);
    return values[Math.floor(Math.random() * values.length)];
  }, [t]);

  const [messages, setMessages] = useState<Message[]>([
    { role: "katia", text: randomWelcome() },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 50);
  }, []);

  // Auto-focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      const text = input.trim();
      if (!text || sending) return;

      setInput("");
      setSending(true);
      setMessages((prev) => [...prev, { role: "student", text }]);
      setMessages((prev) => [...prev, { role: "katia", text: "", streaming: true }]);
      scrollToBottom();

      try {
        // Como toda petición del API: si el token caducó (15 min), se renueva y se reintenta.
        const res = await authorizedFetch("/api/ai/socratic", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            item_id: itemId,
            student_message: text,
            lang,
            ...(apiKey ? { api_key: apiKey, provider } : {}),
          }),
        });

        if (!res.ok) throw new KatiaRefusal(await refusalCode(res));
        if (!res.body) throw new Error("Sin respuesta del servidor");

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let full = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const data = JSON.parse(line.slice(6));
              if (data.token) {
                full += data.token;
                setMessages((prev) =>
                  prev.map((m, i) =>
                    i === prev.length - 1 ? { ...m, text: full } : m,
                  ),
                );
                scrollToBottom();
              }
              if (data.error) {
                setMessages((prev) =>
                  prev.map((m, i) =>
                    i === prev.length - 1
                      ? {
                          role: "katia",
                          text: t("socratic.shortCircuit"),
                          streaming: false,
                        }
                      : m,
                  ),
                );
                break;
              }
              if (data.done) {
                setMessages((prev) =>
                  prev.map((m, i) =>
                    i === prev.length - 1 ? { ...m, streaming: false } : m,
                  ),
                );
              }
            } catch {
              /* ignorar líneas no-JSON */
            }
          }
        }
      } catch (err) {
        const text =
          err instanceof KatiaRefusal
            ? t(`socratic.errors.${err.code}`)
            : t("socratic.connectionLost");
        setMessages((prev) =>
          prev.map((m, i) =>
            i === prev.length - 1
              ? { role: "katia", text, streaming: false }
              : m,
          ),
        );
      } finally {
        setSending(false);
        scrollToBottom();
        inputRef.current?.focus();
      }
    },
    [input, sending, itemId, apiKey, provider, lang, scrollToBottom, t],
  );

  return (
    <div className="flex flex-col h-96 bg-[var(--canvas)] rounded-2xl border border-slate-700 overflow-hidden">
      {/* Header con avatar de KatIA */}
      <div className="px-4 py-2.5 border-b border-slate-700/80 flex items-center gap-3 bg-[var(--surface)]">
        <img
          src="/katia/katIA.png"
          alt="KatIA"
          className="w-8 h-8 rounded-full object-contain ring-2 ring-violet-500/40"
        />
        <div className="flex flex-col">
          <span className="text-violet-300 font-semibold text-sm leading-tight">
            KatIA
          </span>
          <span className="text-[10px] text-slate-500 leading-tight">
            {t("socratic.subtitle")}
          </span>
        </div>
        {sending && (
          <span className="ml-auto text-[10px] text-violet-400 animate-pulse">
            {t("socratic.thinking")}
          </span>
        )}
      </div>

      {/* Mensajes */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-2 ${msg.role === "student" ? "justify-end" : "justify-start"}`}
          >
            {/* Avatar de KatIA junto a sus mensajes */}
            {msg.role === "katia" && (
              <img
                src={msg.streaming ? "/katia/correcto_compressed.gif" : "/katia/katIA.png"}
                alt="KatIA"
                className="w-7 h-7 rounded-full object-contain flex-shrink-0 mt-0.5"
              />
            )}
            <div
              className={[
                "max-w-[80%] px-3 py-2 rounded-xl text-sm leading-relaxed",
                msg.role === "student"
                  ? "bg-violet-600/80 text-white rounded-br-sm"
                  : "bg-slate-800/80 text-slate-200 border border-slate-700/60 rounded-bl-sm",
              ].join(" ")}
            >
              {msg.text ? <MathText text={msg.text} /> : (msg.streaming ? "" : "...")}
              {msg.streaming && (
                <span className="inline-block w-1.5 h-4 bg-violet-400 animate-pulse ml-0.5 rounded-sm align-text-bottom" />
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={sendMessage}
        className="px-3 py-2.5 border-t border-slate-700/80 flex gap-2 bg-[var(--surface)]"
      >
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t("socratic.placeholder")}
          className="flex-1 bg-slate-800/60 border border-slate-600/50 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-500/70 transition-colors"
          disabled={sending}
        />
        <Button type="submit" size="sm" loading={sending} disabled={!input.trim()}>
          {t("socratic.send")}
        </Button>
      </form>
    </div>
  );
}
