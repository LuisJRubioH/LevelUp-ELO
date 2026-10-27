/**
 * pages/Student/League.tsx
 * =========================
 * Liga PvP — carrera libre 1v1 en tiempo real. Identidad Oulad (.lue-dx).
 * ELO se mueve por resultado de partida (no por respuesta individual).
 */

import { useEffect, useState } from "react";
import { useInfiniteQuery, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { motion, animate } from "framer-motion";
import { useTranslation } from "react-i18next";
import { MathText } from "../../components/Math/MathContent";
import { QuestionImage } from "../../components/Question/QuestionImage";
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

/** Why a finished match left the rating where it was (spec 001, FR-029c): keys of `league.reasons`. */
const ELO_REASONS = new Set(["no_rated_topics", "not_applied", "daily_cap"]);

/** Spec 007 FR-031 (O-M6): the notice for a match the server will not rate, by its reason. */
const UNRATED_NOTICES: Record<string, string> = { daily_cap: "league.unrated.dailyCap" };

/** Why a match closed without a winner (spec 004 FR-051): no rating moved for either player. */
/** Why a match ended with no winner (spec 004 FR-052): keys of `league.abandonReasons`. */
const ABANDON_REASONS = new Set(["account_expired"]);

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
    opponentAway, reconnectLeft, unratedReason,
  } = usePvpMatch(selectedCourse || null);
  const reconnecting = phase === "reconnecting";

  // The choice belongs to its item: it stays marked until the next item appears, and its colour
  // is the server's verdict on THAT item, never the previous answer's.
  const currentId = currentItem?.id;
  const picked = choice && choice.itemId === currentId ? choice.option : null;
  const verdict = feedback && feedback.itemId === currentId ? feedback : null;

  // A finished match belongs in the history right away — one lost by not coming back too.
  useEffect(() => {
    if (phase === "finished" || notice === "league.closeNotices.matchOver") {
      queryClient.invalidateQueries({ queryKey: ["pvp-history"] });
    }
  }, [phase, notice, queryClient]);

  const handleAnswer = (opt: string) => {
    if (!currentItem || picked || timeLeft === 0 || reconnecting) return;
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
              <span className="dx-eyebrow">{t("league.eyebrow")}</span>
              <h1 className="pv-title">{t("league.title")}</h1>
              <p className="pv-sub">
                {t("league.introBefore")}
                <b style={{ color: "var(--text)" }}>{t("league.introStrong")}</b>
                {t("league.introAfter")}
              </p>

              <label className="pv-field-label">{t("league.pickCourse")}</label>
              <select
                className="pv-select"
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
              >
                <option value="">{t("league.pickPlaceholder")}</option>
                {enrolled.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>

              {notice && <p className="pv-notice" role="alert">{t(notice)}</p>}
              {/* Spec 007 FR-020 (O-G9): no rating in the subject — its diagnostic is the way in. */}
              {notice === "league.closeNotices.noRating" && selectedCourse && (
                <Link
                  className="dx-btn pv-cta pv-diagnostic"
                  to={`/student/course/${encodeURIComponent(selectedCourse)}`}
                >
                  {t("league.goToDiagnostic")}
                </Link>
              )}

              <button className="dx-btn pv-cta" disabled={!selectedCourse} onClick={connect}>
                {t("league.findOpponent")}
              </button>

              <HistoryPanel userId={user?.user_id} />
            </>
          )}

          {/* ── Conectando ────────────────────────────────── */}
          {phase === "connecting" && (
            <div className="pv-center"><p className="pv-sub">{t("league.connecting")}</p></div>
          )}

          {/* ── Esperando rival ───────────────────────────── */}
          {phase === "waiting" && (
            <div className="pv-center">
              <div className="pv-radar" />
              <h2 className="pv-title" style={{ justifyContent: "center" }}>{t("league.searching")}</h2>
              <p className="pv-sub" style={{ marginBottom: 8 }}>
                {t("league.searchingHint")}
              </p>
              <button className="dx-link" onClick={disconnect}>{t("league.cancel")}</button>
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
                  ? t("league.cancelled")
                  : result.draw
                    ? t("league.draw")
                    : result.won
                      ? t("league.won")
                      : t("league.lost")}
              </h2>
              <div className="pv-board">
                <div className="pv-board-col">
                  <span className="pv-board-num">{result.my_score}</span>
                  <span className="pv-board-lbl">{t("league.you")}</span>
                </div>
                <span className="pv-board-vs">{t("league.vs")}</span>
                <div className="pv-board-col">
                  <span className="pv-board-num">{result.opp_score}</span>
                  <span className="pv-board-lbl">{opponent?.name ?? t("league.opponent")}</span>
                </div>
              </div>
              <p className={"pv-elo-delta " + (result.elo_delta_display > 0 ? "up" : result.elo_delta_display < 0 ? "down" : "flat")}>
                <span className="lbl">{t("league.yourElo")}</span>
                {/* The server's rounded number (survey 007 V14): never rounded here. */}
                <EloCount value={result.elo_delta_display} />
              </p>
              {result.abandoned ? (
                <p className="pv-sub pv-reason" role="status">
                  {result.reason && ABANDON_REASONS.has(result.reason)
                    ? t(`league.abandonReasons.${result.reason}`)
                    : t("league.abandonedFallback")}
                </p>
              ) : (
                <>
                  {/* Spec 007 F: why the match ended this way (FR-041 speed, FR-042 abandonment). */}
                  {result.forfeit && result.won && (
                    <p className="pv-sub pv-reason">{t("league.opponentForfeited")}</p>
                  )}
                  {result.tiebreak && (
                    <p className="pv-sub pv-reason">
                      {result.won ? t("league.wonBySpeed") : t("league.lostBySpeed")}
                    </p>
                  )}
                  {result.elo_reason && ELO_REASONS.has(result.elo_reason) && (
                    <p className="pv-sub pv-reason">{t(`league.reasons.${result.elo_reason}`)}</p>
                  )}
                </>
              )}
              <button className="dx-btn pv-cta" onClick={disconnect}>{t("league.playAgain")}</button>
            </motion.div>
          )}

          {/* ── Partida activa ────────────────────────────── */}
          {(phase === "playing" || reconnecting) && (
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

              {/* Spec 007 FR-031 (O-M6): said before the first item, kept for the whole match. */}
              {unratedReason && UNRATED_NOTICES[unratedReason] && (
                <motion.p
                  className="pv-notice pv-unrated"
                  role="status"
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  {t(UNRATED_NOTICES[unratedReason])}
                </motion.p>
              )}

              {/* Spec 007 FR-042: the connection is being recovered, or the rival's is. */}
              {reconnecting ? (
                <p className="pv-notice" role="status">
                  {t("league.reconnecting", { seconds: reconnectLeft })}
                </p>
              ) : opponentAway != null ? (
                <p className="pv-notice" role="status">
                  {t("league.opponentAway", { seconds: opponentAway })}
                </p>
              ) : null}

              <div className="dx-progress" style={{ marginBottom: 14 }}>
                <i style={{ width: pct + "%" }} />
              </div>

              <p className="pv-opp-line">
                {t("league.vs")} <b>{opponent?.name ?? t("league.opponent")}</b> ·{" "}
                {opponent?.elo == null ? t("rating.pending") : `${t("league.eloShort")} ${opponent.elo}`}
              </p>

              {currentItem ? (
                <div className="dx-qcard">
                  <div className="dx-qmeta"><span className="dx-qtopic">{currentItem.topic}</span></div>
                  <p className="dx-prompt"><MathText text={currentItem.content} /></p>
                  {/* Spec 007 FR-032: the item's figure, as Practice and Exam show it. */}
                  <QuestionImage imageUrl={currentItem.image_url} />
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
                          disabled={!!picked || timeLeft === 0 || reconnecting}
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
                    {t("league.doneTitle", { count: totalItems })}
                  </h2>
                  <p className="pv-sub">
                    {t("league.doneHint", { score: myScore })}
                  </p>
                </div>
              ) : (
                <div className="pv-center"><p className="pv-sub">{t("league.loading")}</p></div>
              )}
            </>
          )}

        </div>
      </div>
    </div>
  );
}

function HistoryPanel({ userId }: { userId?: number }) {
  const { t } = useTranslation();
  // Spec 007 FR-060 (O-H1): five at a time; «Ver más» asks for the five after the last shown.
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ["pvp-history", userId],
    queryFn: ({ pageParam }) => studentApi.pvpHistory(pageParam),
    initialPageParam: undefined as number | undefined,
    getNextPageParam: (last) =>
      last.has_more ? last.matches[last.matches.length - 1]?.match_id : undefined,
    enabled: !!userId,
    staleTime: 30_000,
  });
  const rows = data?.pages.flatMap((p) => p.matches) ?? [];
  if (!rows.length) return null;

  return (
    <div className="pv-history">
      <p className="pv-history-h">{t("league.historyTitle")}</p>
      {rows.map((m) => {
        const abandoned = m.status === "abandoned";
        // Spec 007 FR-042 (O-F3): a forfeit is a finished match that says why.
        // Spec 007 FR-031: a match over the daily cap says it did not count.
        const showReason = abandoned || m.reason === "forfeit" || m.reason === "daily_cap";
        const cls = abandoned ? "void" : m.draw ? "draw" : m.won ? "win" : "loss";
        const label = abandoned
          ? t("league.historyAbandoned")
          : m.draw
            ? t("league.draw")
            : m.won
              ? t("league.historyWon")
              : t("league.historyLost");
        // The server's rounded number (survey 007 V14); a match with no recorded change shows «—».
        const delta = abandoned ? null : m.elo_delta_display;
        const deltaCls = delta == null || delta === 0 ? "flat" : delta > 0 ? "up" : "down";
        return (
          <div key={m.match_id} className="pv-hrow">
            <span className={"pv-tag " + cls}>{label}</span>
            <span className="pv-hopp">
              {t("league.vs")} {m.opponent}
              <span className="pv-hsub">
                {m.course_name}
                {showReason &&
                  ` · ${t(`league.historyReasons.${m.reason ?? "unknown"}`, {
                    defaultValue: t("league.historyReasons.unknown"),
                  })}`}
              </span>
            </span>
            <span className="pv-hscore">{m.my_score}–{m.opp_score}</span>
            <span className={"pv-hdelta " + deltaCls}>
              {delta == null ? "—" : delta >= 0 ? `+${delta}` : delta}
            </span>
          </div>
        );
      })}
      {hasNextPage && (
        <button
          type="button"
          className="pv-more"
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          {t("league.historyMore")}
        </button>
      )}
    </div>
  );
}
