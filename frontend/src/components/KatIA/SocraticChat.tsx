/**
 * components/KatIA/SocraticChat.tsx
 * ===================================
 * Chat socrático con KatIA usando SSE streaming desde /api/ai/socratic.
 * El estudiante escribe su pregunta y ve la respuesta token a token.
 */

import { useCallback, useRef, useState } from "react";
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
  apiKey: string;
  provider?: string;
}

export function SocraticChat({
  itemId,
  itemContent,
  courseId,
  apiKey,
  provider = "groq",
}: SocraticChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "katia",
      text: "¡Hola! Soy KatIA 🐱 ¿En qué parte de este problema necesitas ayuda?",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { accessToken } = useAuthStore();

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const sendMessage = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      const text = input.trim();
      if (!text || sending) return;

      setInput("");
      setSending(true);
      setMessages((prev) => [...prev, { role: "student", text }]);

      // Agregar mensaje vacío de KatIA que se irá llenando
      setMessages((prev) => [...prev, { role: "katia", text: "", streaming: true }]);

      try {
        const res = await fetch("/api/ai/socratic", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
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
        setMessages((prev) =>
          prev.map((m, i) =>
            i === prev.length - 1
              ? { role: "katia", text: "Lo siento, ocurrió un error. ¿Puedes intentarlo de nuevo?" }
              : m,
          ),
        );
      } finally {
        setSending(false);
        scrollToBottom();
      }
    },
    [input, sending, itemId, itemContent, courseId, apiKey, provider, accessToken, scrollToBottom],
  );

  return (
    <div className="flex flex-col h-80 bg-slate-900 rounded-2xl border border-slate-700">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-2">
        <span className="text-violet-400 font-medium text-sm">🐱 Chat con KatIA</span>
        <span className="text-xs text-slate-500">(socrático — no da la respuesta)</span>
      </div>

      {/* Mensajes */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "student" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={[
                "max-w-[80%] px-3 py-2 rounded-xl text-sm",
                msg.role === "student"
                  ? "bg-violet-700 text-white"
                  : "bg-slate-800 text-slate-200 border border-slate-700",
              ].join(" ")}
            >
              {msg.text}
              {msg.streaming && (
                <span className="inline-block w-1 h-4 bg-violet-400 animate-pulse ml-1" />
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="px-4 py-3 border-t border-slate-700 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="¿Qué no entiendes del problema?"
          className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-500"
          disabled={sending}
        />
        <Button type="submit" size="sm" loading={sending} disabled={!input.trim()}>
          Enviar
        </Button>
      </form>
    </div>
  );
}
