/** Pure observations shared by the live sweep and its deliberate fault probes. */
const checks = {
  "flow-step": (s) => s.visible && s.enabled && s.changed,
  "lesson-completed": (s) => ["available", "current"].includes(s.before) && s.after === "completed" && s.persisted,
  "lesson-next": (s) => s.before === "blocked" && ["available", "current"].includes(s.after) && s.opened,
  "exam-result": (s) => s.total > 0 && s.studentCount === s.total && s.teacherCount === s.total &&
    s.studentScore === s.expectedScore && s.teacherScore === s.expectedScore &&
    s.studentVisible && s.teacherVisible && s.answersMatch && s.persisted,
  "procedure-grade": (s) => s.pending && s.image && s.studentScore === s.grade &&
    s.teacherScore === s.grade && s.commentMatch && s.studentVisible && s.teacherVisible,
  "ai-degraded": (s) => s.available === false && s.notice && s.directEnabled && !s.analyzeVisible && s.sent,
  "league-result": (s) => s.sameMatch && s.allAnswered && s.mirroredScores && s.outcome &&
    s.persisted && s.visible && s.deltasMatch && !s.abandoned && !s.forfeit,
  "league-close": (s) => s.unexpected.length === 0,
};

function finding(check, state, detail) {
  if (!checks[check]) throw new Error(`Unknown flow check: ${check}`);
  return checks[check](state) ? [] : [{ check, detail }];
}

module.exports = { checks, finding };
