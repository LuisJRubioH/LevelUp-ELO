/**
 * QA only: walk every lesson of the learning path in a real browser and report what a person
 * would see broken — without a person, and without spending model tokens on screenshots.
 *
 * Needs the API and the frontend running locally, and the lessons opened for the test students:
 *
 *   python scripts/qa/seed_lesson_access.py
 *   node scripts/qa/lesson_sweep.js --out <dir> [--user estudiante_colegio_2] [--width 1366]
 *        [--node PREALG-N1-B03-ESCALERA-NECESIDAD] [--answer] [--shots]
 *
 * For each node it opens every step that opens on a click (worked-example steps, the trap's
 * calibration and contrast, hints, Pólya) and runs the shared DOM checks (scripts/qa/lib.js):
 * broken or unrendered formulas, faded steps with nothing to fill, multiple-answer questions
 * without a hint, overflow, clipped controls, broken images, untranslated keys, console and
 * HTTP errors.
 *
 * With --answer it also answers every question once — the first option, or «1» in a number
 * field — and checks what follows (this writes answers for the local test student):
 *   no-feedback       nothing tells the student how the answer went
 *   dead-end          a wrong answer leaves nothing to try again with (QA Q2)
 *   generic-feedback  «Revisa el procedimiento paso a paso» on a question with no procedure (Q3)
 */
const { chromium } = require("playwright");
const { arg, common, login, token, collect, inspect, shoot, writeReport, summary } = require("./lib");

const cfg = common();
const USER = arg("user", "estudiante_colegio_2");
const PASSWORD = arg("password", "test1234");
const COURSE = arg("course", "algebra_basica");
const ONLY = arg("node", null);
const ANSWER = Boolean(arg("answer", false));

// Buttons that reveal more of a lesson without answering anything.
const REVEAL = /^(Ver el siguiente paso|Fijar y ver dónde falla|Comparar con la versión correcta|Pedir una pista|Pista \d de 3|Empezar por comprender|Siguiente: )/;
// What a student can answer, each with its own feedback.
const UNITS = "article.block-item, .block-abstraction, .block-bridge-blank";

async function answerAll(page) {
  const findings = [];
  const units = page.locator(UNITS);
  const total = await units.count();
  for (let i = 0; i < total; i++) {
    const unit = units.nth(i);
    if (!(await unit.isVisible().catch(() => false))) continue;
    const label = ((await unit.locator("h3, label").first().textContent().catch(() => "")) || "").trim().slice(0, 70);
    const input = unit.locator(".block-numeric input:enabled").first();
    // An option already pressed (an earlier answer, restored) would be toggled off, not chosen.
    const option = unit.locator('.block-options button:enabled:not([aria-pressed="true"])').first();
    const check = unit.getByRole("button", { name: "Comprobar" });
    try {
      if (await input.count()) {
        await input.fill("1");
        await check.first().click({ timeout: 2000 });
      } else if (await option.count()) {
        await unit.scrollIntoViewIfNeeded();
        await option.click({ timeout: 2000 });
        if (await check.count()) {
          if (await check.first().isEnabled()) await check.first().click({ timeout: 2000 });
        }
      } else {
        continue; // already answered right, or nothing to answer
      }
    } catch {
      findings.push({ check: "unanswerable", detail: label });
      continue;
    }
    const status = unit.locator('[role="status"]').first();
    try {
      await status.waitFor({ state: "visible", timeout: 4000 });
    } catch {
      findings.push({ check: "no-feedback", detail: label });
      continue;
    }
    const text = ((await status.textContent()) || "").trim();
    if (/procedimiento paso a paso/i.test(text)) findings.push({ check: "generic-feedback", detail: label });
    if ((await status.getAttribute("class"))?.includes("is-retry")) {
      // Something must remain to try again with.
      const retry =
        (await unit.locator(".block-numeric input:enabled").count()) +
        (await unit.locator(".block-options button:enabled").count());
      if (!retry) findings.push({ check: "dead-end", detail: label });
    }
  }
  return findings;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: cfg.width, height: cfg.height } });
  const errors = collect(page, cfg);
  await login(page, cfg.web, USER, PASSWORD);
  const auth = { Authorization: `Bearer ${await token(page)}` };
  const map = await (await page.request.get(`${cfg.api}/api/student/map/${COURSE}`, { headers: auth })).json();
  // Rows without a node_id are the map's section headers, not lessons.
  const nodes = (map.nodes || []).map((n) => n.node_id).filter((id) => id && (!ONLY || id === ONLY));
  console.log(`${nodes.length} nodes, ${USER}, ${cfg.width}px${ANSWER ? ", answering" : ""}`);
  await errors.take();

  const report = [];
  for (const nodeId of nodes) {
    await page.goto(`${cfg.web}/student/course/${COURSE}/lesson/${nodeId}`);
    try {
      await page.waitForSelector("main h1, main h2, main h3", { timeout: 15000 });
      await page.waitForLoadState("networkidle", { timeout: 10000 });
    } catch {
      report.push({ name: nodeId, findings: [{ check: "load", detail: "the lesson did not render" }, ...(await errors.take())] });
      continue;
    }
    for (let i = 0; i < 80; i++) {
      const next = page.getByRole("button", { name: REVEAL }).first();
      if ((await next.count()) === 0) break;
      try {
        await next.click({ timeout: 2000 });
      } catch {
        break;
      }
    }
    const answered = ANSWER ? await answerAll(page) : [];
    await page.waitForTimeout(300);
    const findings = [...(await page.evaluate(inspect)), ...answered, ...(await errors.take())];
    if (cfg.shots) await shoot(page, findings, cfg.out, nodeId);
    report.push({ name: nodeId, findings });
    summary(nodeId, findings);
  }
  await browser.close();
  writeReport(cfg.out, `Lesson sweep — ${USER}, ${cfg.width}px${ANSWER ? ", answering" : ""}`, report);
})();
