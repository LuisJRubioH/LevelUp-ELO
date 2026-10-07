/**
 * pages/Student/League.tsx
 * =========================
 * Liga PvP — carrera libre 1v1 en tiempo real. Identidad Oulad (.lue-dx).
 * ELO se mueve por resultado de partida (no por respuesta individual).
 */

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
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

export function League() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const [selectedCourse, setSelectedCourse] = useState<string>("");
  const [picked, setPicked] = useState<string | null>(null);

  const { data: courses } = useQuery({ queryKey: ["courses"], queryFn: () => studentApi.courses() });
  const enrolled = courses?.filter((c) => c.enrolled) ?? [];

  const {
    phase, connect, disconnect, sendAnswer,
    currentItem, currentIndex, totalItems,
    myScore, oppScore, opponent,
    result, timeLeft, lastCorrect,
  } = usePvpMatch(selectedCourse || null);

  const handleAnswer = (opt: string) => {
    if (!currentItem || picked) return;
    setPicked(opt);
    sendAnswer(currentItem.id, opt);
    setTimeout(() => setPicked(null), 600);
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
                {result.draw ? "🤝" : result.won ? "🏆" : "💔"}
              </motion.div>
              <h2 className={"pv-result-title " + (result.draw ? "draw" : result.won ? "win" : "loss")}>
                {result.draw ? "Empate" : result.won ? "¡Ganaste!" : "Perdiste"}
              </h2>
              <div className="pv-board">
                <div className="pv-board-col">
                  <span className="pv-board-num">{result.my_score}</span>
                  <span className="pv-board-lbl">Tú</span>
                </div>
                <span className="pv-board-vs">vs</span>
                <div className="pv-board-col">
                  <span className="pv-board-num">{result.opp_score}</span>
                  <span className="pv-board-lbl">{opponent?.username ?? "Rival"}</span>
                </div>
              </div>
              <p className={"pv-elo-delta " + (result.elo_delta > 0 ? "up" : result.elo_delta < 0 ? "down" : "flat")}>
                <span className="lbl">Tu ELO</span>
                <EloCount value={result.elo_delta} />
              </p>
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
                vs <b>{opponent?.username ?? "Rival"}</b> ·{" "}
                {opponent?.elo == null ? t("rating.pending") : `ELO ${opponent.elo}`}
              </p>

              {currentItem ? (
                <div className="dx-qcard">
                  <div className="dx-qmeta"><span className="dx-qtopic">{currentItem.topic}</span></div>
                  <p className="dx-prompt"><MathText text={currentItem.content} /></p>
                  <div className="dx-options">
                    {currentItem.options.map((opt, i) => {
                      const isPicked = picked === opt;
                      const cls = "dx-opt" + (isPicked ? (lastCorrect ? " ok" : " bad") : "");
                      return (
                        <button
                          key={i}
                          className={cls}
                          onClick={() => handleAnswer(opt)}
                          disabled={!!picked}
                          style={isPicked ? {
                            borderColor: lastCorrect ? "#34d399" : "#f87171",
                            background: lastCorrect ? "color-mix(in srgb, #34d399 14%, transparent)"
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
        return (
          <div key={i} className="pv-hrow">
            <span className={"pv-tag " + cls}>{label}</span>
            <span className="pv-hopp">vs {m.opponent}</span>
            <span className="pv-hscore">{m.my_score}–{m.opp_score}</span>
            <span className={"pv-hdelta " + (m.elo_delta >= 0 ? "up" : "down")}>
              {m.elo_delta >= 0 ? "+" : ""}{m.elo_delta}
            </span>
          </div>
        );
      })}
    </div>
  );
}
