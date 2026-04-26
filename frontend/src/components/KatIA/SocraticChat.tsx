/**
 * components/KatIA/SocraticChat.tsx
 * ===================================
 * Chat socrático con KatIA usando SSE streaming desde /api/ai/socratic.
 * Muestra el avatar de KatIA (gata cyborg) junto a cada mensaje.
 * Personalidad: metáforas felinas + tecnológicas, socrática, nunca revela respuestas.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { useAuthStore } from "../../stores/authStore";
import { Button } from "../ui/Button";

interface Message {
  role: "student" | "katia";
  text: string;
  streaming?: boolean;
}

interface SocraticChatProps {
  itemId: string;
  itemContent: string;
  courseId: string;
  apiKey?: string;
  provider?: string;
}

/** Mensajes de bienvenida con personalidad KatIA (selección del banco domain). */
const WELCOME_MESSAGES = [
  "Mis sensores detectan que tienes una duda interesante. Desenredemos este ovillo juntos... ¿qué parte del problema te tiene pensando?",
  "Mis bigotes vibran de emoción al verte aquí. Como decía Sócrates, la sabiduría comienza con buenas preguntas. ¿Cuál es la tuya?",
  "Purrr... acabo de calibrar mis circuitos para este tema. ¿En qué parte del problema necesitas que afilemos las garras?",
  "Bip, bip. Protocolos de tutoría activados. Estoy aquí para guiarte, no para darte la respuesta. ¿Qué te tiene atrapado?",
  "Mis procesadores están listos y mi curiosidad felina al máximo. ¿Qué parte de este problema quieres explorar conmigo?",
];

function randomWelcome() {
  return WELCOME_MESSAGES[Math.floor(Math.random() * WELCOME_MESSAGES.length)];
}

export function SocraticChat({
  itemId,
  itemContent,
  courseId,
  apiKey = "",
  provider = "groq",
}: SocraticChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "katia", text: randomWelcome() },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { accessToken } = useAuthStore();

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
        const res = await fetch("/api/ai/socratic", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          credentials: "include",
          body: JSON.stringify({
            item_id: itemId,
            item_content: itemContent,
            student_message: text,
            course_id: courseId,
            api_key: apiKey,
            provider,
          }),
        });

        if (!res.ok || !res.body) {
          throw new Error("Error en streaming");
        }

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
                          text: "Miau... mis circuitos tuvieron un cortocircuito. ¿Puedes intentarlo de nuevo?",
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
      } catch {
        setMessages((prev) =>
          prev.map((m, i) =>
            i === prev.length - 1
              ? {
                  role: "katia",
                  text: "Purrr... parece que perdí la conexión. ¿Puedes intentarlo de nuevo?",
                  streaming: false,
                }
              : m,
          ),
        );
      } finally {
        setSending(false);
        scrollToBottom();
        inputRef.current?.focus();
      }
    },
    [input, sending, itemId, itemContent, courseId, apiKey, provider, accessToken, scrollToBottom],
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
            Tutora socrática — te guía sin dar la respuesta
          </span>
        </div>
        {sending && (
          <span className="ml-auto text-[10px] text-violet-400 animate-pulse">
            pensando...
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
                  ? "bg-violet-600/80 text-slate-100 rounded-br-sm"
                  : "bg-slate-800/80 text-slate-200 border border-slate-700/60 rounded-bl-sm",
              ].join(" ")}
            >
              {msg.text || (msg.streaming ? "" : "...")}
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
          placeholder="Escribe tu pregunta a KatIA..."
          className="flex-1 bg-slate-800/60 border border-slate-600/50 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-500/70 transition-colors"
          disabled={sending}
        />
        <Button type="submit" size="sm" loading={sending} disabled={!input.trim()}>
          Enviar
        </Button>
      </form>
    </div>
  );
}
