/**
 * pages/Student/CourseMap.tsx — Mapa de contenido (P3)
 * ====================================================
 * Sendero serpenteante de nodos (un nodo por tópico) sobre un fondo de
 * grilla + glow. El sendero usa la trama de "piedras" del diseño original
 * (cinta tenue + perlas), portada de docs/redesign/source (map.css).
 * El rail derecho vive ahora en StudentLayout (CourseRail, cajón con hover),
 * compartido entre el mapa y las lecciones.
 * Vive dentro del shell de StudentLayout (sidebar a la izquierda).
 */

import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { studentApi, type MapNode } from "../../api/student";
import { usePracticeStore } from "../../stores/practiceStore";
import "./CourseMap.css";

// geometría del lienzo (igual que el prototipo, sin banners de unidad)
const MAP_W = 402;
const LANES: Record<string, number> = { C: 50, R: 71, L: 29 };
const LANE_SEQ = ["C", "R", "C", "L"];
const TOP = 86; // ~1cm más abajo para calzar con el PNG del camino
const GAP = 92;
const BOTTOM = 120;

interface Laid extends MapNode {
  i: number;
  lane: string;
  xPct: number;
  x: number;
  y: number;
}

function shortTopic(t: string): string {
  return t.length > 26 ? t.slice(0, 24) + "…" : t;
}

/** Quita el prefijo redundante del nombre del curso ("Aritmética Básica · Fundamentos" → "Fundamentos"). */
function cleanLabel(label: string, courseName: string): string {
  const parts = label.split(/\s[·\-–]\s/);
  if (parts.length > 1 && parts[0].trim() === courseName.trim()) {
    return parts.slice(1).join(" · ").trim();
  }
  return label;
}

// glifos (SVG geométrico, consistente con la marca)
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
const Chevron = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 5l-7 7 7 7" />
  </svg>
);

export function CourseMap() {
  const { courseId = "" } = useParams();
  const navigate = useNavigate();
  const startSession = usePracticeStore((s) => s.startSession);
  const { t } = useTranslation();
  // FR-029a pending / FR-034a reconciled baseline: say why the number looks the way it does.
  const eloTitle = (n: MapNode) =>
    n.elo === null ? t("rating.pending") : n.approximate ? t("rating.approximateHint") : undefined;

  const { data, isLoading, isError } = useQuery({
    queryKey: ["course-map", courseId],
    queryFn: () => studentApi.courseMap(courseId),
    enabled: !!courseId,
  });

  const { laid, height, segments, completedCount, side } = useMemo(() => {
    let nodes = data?.nodes ?? [];
    // ponytail: solo en dev, relleno hasta 12 nodos para probar el scroll.
    // Nunca en prod (import.meta.env.DEV es false en build).
    const practiceNodes = nodes.filter((node) => !node.node_id);
    if (import.meta.env.DEV && practiceNodes.length > 0 && nodes.length < 12) {
      const pad: MapNode[] = [];
      for (let k = nodes.length; k < 12; k++) {
        const base = practiceNodes[k % practiceNodes.length];
        pad.push({
          ...base,
          topic: `${base.topic}#${k}`,
          label: `${base.label || base.topic} ${k + 1}`,
          label_key: null,
          node_id: null,
          node_type: "practice",
          state: "available",
        });
      }
      nodes = [...nodes, ...pad];
    }

    // Cursos guiados (prealgebra) mezclan lecciones (con node_id) y nodos de
    // práctica ELO (sin node_id). Separamos: el sendero muestra solo la ruta
    // guiada; la práctica adaptativa va aparte como refuerzo opcional. Cursos
    // 100% ELO (sin lecciones) siguen mostrando todo en el sendero.
    const guided = nodes.filter((n) => n.node_id);
    const trailNodes = guided.length > 0 ? guided : nodes;
    const laidNodes: Laid[] = trailNodes.map((n, i) => {
      const lane = LANE_SEQ[i % LANE_SEQ.length];
      const xPct = LANES[lane];
      return { ...n, i, lane, xPct, x: (xPct / 100) * MAP_W, y: TOP + i * GAP };
    });

    // cubic suave por par de nodos consecutivos; el sendero de "piedras"
    // (perlas) se pinta encima de una cinta tenue en el SVG (ver CSS).
    const segs = [];
    for (let i = 0; i < laidNodes.length - 1; i++) {
      const a = laidNodes[i];
      const b = laidNodes[i + 1];
      const dy = b.y - a.y;
      segs.push({
        d: `M ${a.x} ${a.y} C ${a.x} ${a.y + dy * 0.5}, ${b.x} ${b.y - dy * 0.5}, ${b.x} ${b.y}`,
        traveled: a.state === "completed",
      });
    }

    return {
      laid: laidNodes,
      height: laidNodes.length ? TOP + (laidNodes.length - 1) * GAP + BOTTOM : 400,
      segments: segs,
      completedCount: laidNodes.filter((n) => n.state === "completed").length,
      side: guided.length > 0 ? nodes.filter((n) => !n.node_id) : [],
    };
  }, [data]);

  const nodeLabel = (node: MapNode) =>
    node.label_key ? t(node.label_key) : cleanLabel(node.label || node.topic, data?.course_name ?? "");

  const openNode = (node?: MapNode) => {
    if (node?.state === "blocked") return;
    if (node?.node_id) {
      navigate(`/student/course/${courseId}/lesson/${encodeURIComponent(node.node_id)}`);
      return;
    }
    // Refuerzo desde un nodo: práctica filtrada a ese tópico (el ELO de ese
    // tópico avanza → el nodo progresa). Sin tópico = práctica del curso completo.
    startSession(courseId, undefined, node?.topic);
    navigate("/student");
  };

  if (isLoading)
    return (
      <div className="lue-map">
        <div className="lm-state">
          <div className="em-ic">🗺️</div>
          <h2>{t("courseMap.loading")}</h2>
        </div>
      </div>
    );
  if (isError || !data)
    return (
      <div className="lue-map">
        <div className="lm-state">
          <div className="em-ic">⚠️</div>
          <h2>{t("courseMap.errorTitle")}</h2>
          <p>{t("courseMap.errorBody")}</p>
        </div>
      </div>
    );
  if (laid.length === 0)
    return (
      <div className="lue-map">
        <div className="lm-state">
          <div className="em-ic">🧭</div>
          <h2>{t("courseMap.emptyTitle")}</h2>
          <p>{t("courseMap.emptyBody")}</p>
        </div>
      </div>
    );

  const total = laid.length;
  const pct = Math.round((completedCount / total) * 100);

  return (
    <div className="lue-map">
      {/* barra superior del curso (sticky) */}
      <header className="lm-bar">
        <button className="lm-iconbtn" onClick={() => navigate(`/student/course/${courseId}`)} aria-label={t("courseMap.backToCourse")}>
          <Chevron />
        </button>
        <div className="lm-title">
          <span className="lm-kicker">{t("courseMap.kicker")}</span>
          <span className="lm-h">{data.course_name}</span>
        </div>
        <div className="lm-prog">
          <div className="lm-prog-top">
            <span>{t("courseMap.progress", { done: completedCount, total })}</span>
            <b>{pct}%</b>
          </div>
          <div className="lm-bar-track">
            <i style={{ width: pct + "%" }} />
          </div>
        </div>
      </header>

      {/* columna central: sendero */}
      <div className="lm-stage">
        <div className="lm-canvas" style={{ height }}>
          {/* sendero de piedras: cinta tenue debajo + perlas coloreadas por avance */}
          <svg className="lm-trail" width={MAP_W} height={height} viewBox={`0 0 ${MAP_W} ${height}`} preserveAspectRatio="none" aria-hidden="true">
            {segments.map((s, i) => (
              <path key={"r" + i} className="trail-ribbon" d={s.d} />
            ))}
            {segments.map((s, i) => (
              <path key={"s" + i} className={"trail-stones " + (s.traveled ? "traveled" : "upcoming")} d={s.d} />
            ))}
          </svg>

          <div className="map-nodes">
            {laid.map((n) => {
              const side = n.lane === "R" ? "lbl-left" : "lbl-right";
              return (
                <div key={n.node_id || n.label || n.topic} className={`node-anchor ${side}`} style={{ left: n.x, top: n.y }}>
                  {n.state === "current" && <span className="here-flag">{t("courseMap.here")}</span>}
                  <button
                    className={`node ${n.state}`}
                    onClick={() => openNode(n)}
                    disabled={n.state === "blocked"}
                    aria-label={`${nodeLabel(n)}: ${t(`courseMap.state.${n.state}`)}`}
                    title={n.node_id ? nodeLabel(n) : t("courseMap.practiceTopic", { topic: n.topic })}
                  >
                    <span className="disc">
                      {n.state === "completed" ? (
                        <span className="glyph">
                          <Check />
                        </span>
                      ) : n.state === "current" ? (
                        <span className="glyph">
                          <Book />
                        </span>
                      ) : (
                        <span className="elo" title={eloTitle(n)}>
                          {n.elo === null ? "—" : Math.round(n.elo)}
                          {n.approximate && " ≈"}
                        </span>
                      )}
                    </span>
                  </button>
                  {n.state !== "current" && (
                    <span className="node-label">
                      <span className="nl-idx">{String(n.i + 1).padStart(2, "0")}</span>
                      {shortTopic(nodeLabel(n))}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Práctica adaptativa ELO: refuerzo opcional, separado del sendero guiado */}
      {side.length > 0 && (
        <section className="lm-practice" aria-label={t("courseMap.practice.title")}>
          <header className="lm-practice-head">
            <h2>{t("courseMap.practice.title")}</h2>
            <p>{t("courseMap.practice.subtitle")}</p>
          </header>
          <div className="lm-practice-grid">
            {side.map((n) => (
              <button
                key={n.label || n.topic}
                className={`lm-practice-card ${n.state}`}
                onClick={() => openNode(n)}
                disabled={n.state === "blocked"}
                title={t("courseMap.practiceTopic", { topic: n.topic })}
              >
                <span className="lm-practice-elo" title={eloTitle(n)}>
                  {n.elo === null ? "—" : Math.round(n.elo)}
                  {n.approximate && " ≈"}
                </span>
                <span className="lm-practice-label">
                  {cleanLabel(n.label || n.topic, data?.course_name ?? "")}
                </span>
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
