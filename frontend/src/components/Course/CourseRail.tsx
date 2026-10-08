/**
 * components/Course/CourseRail.tsx
 * ================================
 * Cajón derecho del curso. Oculto por defecto: se revela al pasar el cursor
 * por el tirador del borde derecho, al enfocar con teclado (focus-within) o al
 * tocar el tirador (estado `open`, para móvil). Vive sobre el mapa Y dentro de
 * las lecciones (se monta una sola vez en StudentLayout), y permite saltar
 * entre lecciones del curso sin volver al mapa.
 *
 * Comparte la queryKey ["course-map", courseId] con CourseMap → una sola
 * petición de red para ambos.
 */
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { studentApi, type MapNode } from "../../api/student";
import { usePracticeStore } from "../../stores/practiceStore";
import { SocraticChat } from "../KatIA/SocraticChat";
import "./CourseRail.css";

const Check = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12.5l4.5 4.5L19 7" />
  </svg>
);
const Book = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 5a2 2 0 0 1 2-2h6v16H6a2 2 0 0 0-2 2V5z" />
    <path d="M20 5a2 2 0 0 0-2-2h-6v16h6a2 2 0 0 1 2 2V5z" />
  </svg>
);
const Arrow = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
);
const MapGlyph = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 4 4 6v14l5-2 6 2 5-2V4l-5 2-6-2z" />
    <path d="M9 4v14M15 6v14" />
  </svg>
);

function shortTopic(t: string): string {
  return t.length > 30 ? t.slice(0, 28) + "…" : t;
}
/** Quita el prefijo redundante del nombre del curso ("Aritmética · Fundamentos" → "Fundamentos"). */
function cleanLabel(label: string, courseName: string): string {
  const parts = label.split(/\s[·\-–]\s/);
  if (parts.length > 1 && parts[0].trim() === courseName.trim()) {
    return parts.slice(1).join(" · ").trim();
  }
  return label;
}

export function CourseRail({ courseId, currentNodeId }: { courseId: string; currentNodeId?: string }) {
  const navigate = useNavigate();
  const startSession = usePracticeStore((s) => s.startSession);
  const { t } = useTranslation();

  const [open, setOpen] = useState(false); // toggle por tap (móvil / sin hover)
  const [chatOpen, setChatOpen] = useState(false);
  const [anchor, setAnchor] = useState<{ id: string; content: string } | null>(null);
  const [anchorLoading, setAnchorLoading] = useState(false);

  const { data } = useQuery({
    queryKey: ["course-map", courseId],
    queryFn: () => studentApi.courseMap(courseId),
    enabled: !!courseId,
  });

  const nodes = data?.nodes ?? [];
  const nodeLabel = (n: MapNode) =>
    n.label_key ? t(n.label_key) : cleanLabel(n.label || n.topic, data?.course_name ?? "");

  const { focusNode, completedCount } = useMemo(() => {
    const byId = currentNodeId ? nodes.find((n) => n.node_id === currentNodeId) : undefined;
    const focus =
      byId ??
      nodes.find((n) => n.state === "current") ??
      nodes.find((n) => n.state === "available") ??
      (nodes.length ? nodes[nodes.length - 1] : null);
    return { focusNode: focus, completedCount: nodes.filter((n) => n.state === "completed").length };
  }, [nodes, currentNodeId]);

  const openNode = (node?: MapNode | null) => {
    if (!node || node.state === "blocked") return;
    setOpen(false);
    if (node.node_id) {
      navigate(`/student/course/${courseId}/lesson/${encodeURIComponent(node.node_id)}`);
      return;
    }
    // Refuerzo: práctica filtrada a ese tópico (sube el ELO → el nodo progresa).
    startSession(courseId, undefined, node.topic);
    navigate("/student");
  };

  const openKatia = async () => {
    setChatOpen(true);
    if (anchor || anchorLoading) return;
    setAnchorLoading(true);
    try {
      const res = await studentApi.nextQuestion({ course_id: courseId });
      if (res.item) setAnchor({ id: res.item.id, content: res.item.content });
    } catch {
      /* sin ítem → el chat muestra el estado de carga/fallback */
    } finally {
      setAnchorLoading(false);
    }
  };

  if (!courseId || nodes.length === 0) return null;

  const total = nodes.length;
  const allDone = completedCount === total;
  const katiaMsg = allDone ? t("courseMap.rail.katiaMsgDone") : t("courseMap.rail.katiaMsg");

  return (
    <aside className={"course-drawer" + (open ? " open" : "")} aria-label={t("courseMap.rail.ariaLabel")}>
      <button
        className="cd-handle"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label={open ? t("courseMap.rail.hide") : t("courseMap.rail.show")}
      >
        <MapGlyph />
      </button>

      <div className="cd-panel">
        <div className="rail-cont">
          <span className="rc-kicker">{allDone ? t("courseMap.rail.kickerDone") : t("courseMap.rail.kicker")}</span>
          <div className="rc-card">
            <div className="rc-ic">
              <Book />
            </div>
            <div className="rc-meta">
              <span className="rc-st">{allDone ? t("courseMap.rail.stDone") : t("courseMap.rail.stCurrent")}</span>
              <span className="rc-name">{focusNode ? nodeLabel(focusNode) : "—"}</span>
            </div>
          </div>
          <button className="rail-btn" onClick={() => openNode(focusNode)}>
            {allDone ? t("courseMap.rail.btnPractice") : t("courseMap.rail.btnLesson")} <Arrow />
          </button>
        </div>

        {!chatOpen ? (
          <button className="rail-katia" onClick={openKatia}>
            <div className="katia-av small">
              <img src="/katia/katIA.png" alt="KatIA" />
            </div>
            <div className="rk-bubble">
              <span className="nm">KatIA</span>
              {katiaMsg}
              <span className="rk-cta">{t("courseMap.rail.askCta")}</span>
            </div>
          </button>
        ) : (
          <div className="rail-chat">
            <div className="rail-chat-head">
              <span className="rch-nm">
                <span className="rch-dot" /> KatIA
              </span>
              <button className="rail-chat-close" onClick={() => setChatOpen(false)} aria-label={t("courseMap.rail.closeChat")}>
                ✕
              </button>
            </div>
            {anchor ? (
              <SocraticChat itemId={anchor.id} itemContent={anchor.content} courseId={courseId} />
            ) : (
              <p className="rail-chat-loading">
                {anchorLoading ? t("courseMap.rail.wakingKatia") : t("courseMap.rail.noQuestion")}
              </p>
            )}
          </div>
        )}

        <div className="rail-units">
          <span className="ru-title">{t("courseMap.rail.lessonsTitle")}</span>
          {nodes.map((n) => (
            <button
              key={n.node_id || n.label || n.topic}
              className={`ru-item ${n.state}${n.node_id && n.node_id === currentNodeId ? " here" : ""}`}
              onClick={() => openNode(n)}
              disabled={n.state === "blocked"}
              title={n.node_id ? nodeLabel(n) : t("courseMap.practiceTopic", { topic: n.topic })}
            >
              <span className="ru-badge">
                {n.state === "completed" ? <Check /> : <span className="ru-dot" />}
              </span>
              <span className="ru-name">{shortTopic(nodeLabel(n))}</span>
              <span className="ru-prog">
                {n.state === "completed" ? "✓" : n.state === "blocked" ? "—" : n.node_id ? "" : n.elo === null ? t("rating.pending") : `ELO ${Math.round(n.elo)}${n.approximate ? " ≈" : ""}`}
              </span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
