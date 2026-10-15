/**
 * pages/Student/League.tsx
 * =========================
 * Liga PvP — carrera libre 1v1 en tiempo real. Identidad Oulad (.lue-dx).
 * ELO se mueve por resultado de partida (no por respuesta individual).
 */

import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, animate } from "framer-motion";
import { useTranslation } from "react-i18next";
import { MathText } from "../../components/Math/MathContent";
import { studentApi } from "../../api/student";
import { usePvpMatch } from "../../hooks/usePvpMatch";
import { useAuthStore } from "../../stores/authStore";
import "./CourseEntry.css";
import "./League.css";

const KEYS = ["A", "B", "C", "D", "E"];

/** Número ELO que cuenta desde 0 hasta `value` (D2 — animación con función). */
function EloCount({ value }: { value: number }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    const controls = animate(0, value, {
      duration: 0.9,
      ease: "easeOut",
      onUpdate: (v) => setN(Math.round(v)),
    });
    return () => controls.stop();
  }, [value]);
  return <>{n >= 0 ? `+${n}` : n}</>;
}

/** Why a finished match left the rating where it was (spec 001, FR-029c). */
const ELO_REASONS: Record<string, string> = {
  no_rated_topics:
    "Tu ELO no cambió: aún no tienes nota en esta materia. Haz su diagnóstico para que las partidas cuenten.",
  not_applied: "Tu ELO no cambió: no pudimos guardar el resultado de esta partida.",
};

/** Why a match closed without a winner (spec 004 FR-051): no rating moved for either player. */
const ABANDON_REASONS: Record<string, string> = {
  account_expired:
    "La partida terminó sin ganador porque el período de acceso de una de las cuentas terminó. Ningún ELO cambió y tus respuestas quedaron guardadas.",
};
const ABANDONED_FALLBACK = "La partida terminó sin ganador. Ningún ELO cambió.";

export function League() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [selectedCourse, setSelectedCourse] = useState<string>("");
  const [choice, setChoice] = useState<{ itemId: string; option: string } | null>(null);

  const { data: courses } = useQuery({ queryKey: ["courses"], queryFn: () => studentApi.courses() });
  const enrolled = courses?.filter((c) => c.enrolled) ?? [];

  const {
    phase, connect, disconnect, sendAnswer,
    currentItem, currentIndex, totalItems,
    myScore, oppScore, opponent,
    result, timeLeft, feedback, notice,
  } = usePvpMatch(selectedCourse || null);

  // The choice belongs to its item: it stays marked until the next item appears, and its colour
  // is the server's verdict on THAT item, never the previous answer's.
  const currentId = currentItem?.id;
  const picked = choice && choice.itemId === currentId ? choice.option : null;
  const verdict = feedback && feedback.itemId === currentId ? feedback : null;

  // A finished match belongs in the history right away.
  useEffect(() => {
    if (phase === "finished") queryClient.invalidateQueries({ queryKey: ["pvp-history"] });
  }, [phase, queryClient]);

  const handleAnswer = (opt: string) => {
    if (!currentItem || picked || timeLeft === 0) return;
    setChoice({ itemId: currentItem.id, option: opt });
    sendAnswer(currentItem.id, opt);
  };

  const pct = totalItems > 0 ? Math.round((currentIndex / totalItems) * 100) : 0;
  const timerWarn = timeLeft <= 30;
  const mm = Math.floor(timeLeft / 60);
  const ss = String(timeLeft % 60).padStart(2, "0");

  return (
    <div className="lue-dx">
      <div className="dx-body" style={{ alignItems: "flex-start", paddingTop: 28 }}>
        <div className="dx-center">

          {/* ── Lobby ─────────────────────────────────────── */}
          {phase === "idle" && (
            <>
              <span className="dx-eyebrow">Liga · 1 contra 1</span>
              <h1 className="pv-title">⚔️ Arena PvP</h1>
              <p className="pv-sub">
                Reta a otro estudiante en una carrera de 10 preguntas. Cada acierto suma un punto;
                el <b style={{ color: "var(--text)" }}>ELO se mueve por el resultado final</b>.
              </p>

              <label className="pv-field-label">Elige una materia</label>
              <select
                className="pv-select"
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
              >
                <option value="">— selecciona —</option>
                {enrolled.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>

              {notice && <p className="pv-notice" role="alert">{notice}</p>}

              <button className="dx-btn pv-cta" disabled={!selectedCourse} onClick={connect}>
                Buscar rival →
              </button>

              <HistoryPanel userId={user?.user_id} />
            </>
          )}

          {/* ── Conectando ────────────────────────────────── */}
          {phase === "connecting" && (
            <div className="pv-center"><p className="pv-sub">Conectando a la arena…</p></div>
          )}

          {/* ── Esperando rival ───────────────────────────── */}
          {phase === "waiting" && (
            <div className="pv-center">
              <div className="pv-radar" />
              <h2 className="pv-title" style={{ justifyContent: "center" }}>Buscando rival…</h2>
              <p className="pv-sub" style={{ marginBottom: 8 }}>
                Esperando que otro estudiante entre a la misma materia.
              </p>
              <button className="dx-link" onClick={disconnect}>Cancelar</button>
            </div>
          )}

          {/* ── Resultado ─────────────────────────────────── */}
          {phase === "finished" && result && (
            <motion.div
              className="pv-result"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}
            >
              <motion.div
                className="pv-result-emoji"
                initial={{ scale: 0.4 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 320, damping: 16 }}
              >
                {result.abandoned ? "⏸" : result.draw ? "🤝" : result.won ? "🏆" : "💔"}
              </motion.div>
              <h2
                className={
                  "pv-result-title " +
                  (result.abandoned || result.draw ? "draw" : result.won ? "win" : "loss")
                }
              >
                {result.abandoned
                  ? "Partida cancelada"
                  : result.draw
                    ? "Empate"
                    : result.won
                      ? "¡Ganaste!"
                      : "Perdiste"}
              </h2>
              <div className="pv-board">
                <div className="pv-board-col">
                  <span className="pv-board-num">{result.my_score}</span>
                  <span className="pv-board-lbl">Tú</span>
                </div>
                <span className="pv-board-vs">vs</span>
                <div className="pv-board-col">
                  <span className="pv-board-num">{result.opp_score}</span>
                  <span className="pv-board-lbl">{opponent?.name ?? "Rival"}</span>
                </div>
              </div>
              <p className={"pv-elo-delta " + (result.elo_delta > 0 ? "up" : result.elo_delta < 0 ? "down" : "flat")}>
                <span className="lbl">Tu ELO</span>
                <EloCount value={result.elo_delta} />
              </p>
              {result.abandoned ? (
                <p className="pv-sub pv-reason" role="status">
                  {(result.reason && ABANDON_REASONS[result.reason]) || ABANDONED_FALLBACK}
                </p>
              ) : (
                result.elo_reason &&
                ELO_REASONS[result.elo_reason] && (
                  <p className="pv-sub pv-reason">{ELO_REASONS[result.elo_reason]}</p>
                )
              )}
              <button className="dx-btn pv-cta" onClick={disconnect}>Jugar de nuevo</button>
            </motion.div>
          )}

          {/* ── Partida activa ────────────────────────────── */}
          {phase === "playing" && (
            <>
              <div className="pv-hud">
                <span className="pv-scorepill">
                  <span className="me">{myScore}</span>
                  <span className="vs">VS</span>
                  <span className="opp">{oppScore}</span>
                </span>
                <span className={"pv-timer" + (timerWarn ? " warn" : "")}>⏱ {mm}:{ss}</span>
                <span className="pv-counter">{Math.min(currentIndex + 1, totalItems)}/{totalItems}</span>
              </div>

              <div className="dx-progress" style={{ marginBottom: 14 }}>
                <i style={{ width: pct + "%" }} />
              </div>

              <p className="pv-opp-line">
                vs <b>{opponent?.name ?? "Rival"}</b> ·{" "}
                {opponent?.elo == null ? t("rating.pending") : `ELO ${opponent.elo}`}
              </p>

              {currentItem ? (
                <div className="dx-qcard">
                  <div className="dx-qmeta"><span className="dx-qtopic">{currentItem.topic}</span></div>
                  <p className="dx-prompt"><MathText text={currentItem.content} /></p>
                  <div className="dx-options">
                    {currentItem.options.map((opt, i) => {
                      const isPicked = picked === opt;
                      const judged = isPicked && verdict ? verdict : null;
                      const cls = "dx-opt" + (judged ? (judged.correct ? " ok" : " bad") : isPicked ? " on" : "");
                      return (
                        <button
                          key={i}
                          className={cls}
                          onClick={() => handleAnswer(opt)}
                          disabled={!!picked || timeLeft === 0}
                          style={judged ? {
                            borderColor: judged.correct ? "#34d399" : "#f87171",
                            background: judged.correct ? "color-mix(in srgb, #34d399 14%, transparent)"
                                                       : "color-mix(in srgb, #f87171 14%, transparent)",
                          } : undefined}
                        >
                          <span className="dx-key">{KEYS[i] ?? i + 1}</span>
                          <span><MathText text={opt} /></span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ) : totalItems > 0 ? (
                <div className="pv-center">
                  <div className="pv-done-emoji">✅</div>
                  <h2 className="pv-title" style={{ justifyContent: "center" }}>
                    Terminaste tus {totalItems} preguntas
                  </h2>
                  <p className="pv-sub">
                    Acertaste {myScore}. Esperando a que el rival termine o se acabe el tiempo…
                  </p>
                </div>
              ) : (
                <div className="pv-center"><p className="pv-sub">Cargando preguntas…</p></div>
              )}
            </>
          )}

        </div>
      </div>
    </div>
  );
}

function HistoryPanel({ userId }: { userId?: number }) {
  const { data } = useQuery({
    queryKey: ["pvp-history", userId],
    queryFn: () => studentApi.pvpHistory(),
    enabled: !!userId,
    staleTime: 30_000,
  });

  if (!data?.length) return null;

  return (
    <div className="pv-history">
      <p className="pv-history-h">Últimas partidas</p>
      {data.slice(0, 5).map((m, i) => {
        const cls = m.draw ? "draw" : m.won ? "win" : "loss";
        const label = m.draw ? "Empate" : m.won ? "Ganada" : "Perdida";
        // Whole points, as the result screen shows them; a match with no recorded change shows «—».
        const delta = m.elo_delta == null ? null : Math.round(m.elo_delta);
        const deltaCls = delta == null || delta === 0 ? "flat" : delta > 0 ? "up" : "down";
        return (
          <div key={i} className="pv-hrow">
            <span className={"pv-tag " + cls}>{label}</span>
            <span className="pv-hopp">vs {m.opponent}</span>
            <span className="pv-hscore">{m.my_score}–{m.opp_score}</span>
            <span className={"pv-hdelta " + deltaCls}>
              {delta == null ? "—" : delta >= 0 ? `+${delta}` : delta}
            </span>
          </div>
        );
      })}
    </div>
  );
}
