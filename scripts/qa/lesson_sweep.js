/**
 * QA only: walk every lesson of the learning path in a real browser and report what a person
 * would see broken — without a person, and without spending model tokens on screenshots.
 *
 * Needs the API and the frontend running locally, and the lessons opened for the test students:
 *
 *   python scripts/qa/seed_lesson_access.py
 *   node scripts/qa/lesson_sweep.js --out <dir> [--user estudiante_colegio_2] [--width 1366]
 *        [--node PREALG-N1-B03-ESCALERA-NECESIDAD] [--shots]
 *
 * For each node it opens every step that opens on a click (worked-example steps, the trap's
 * calibration and contrast, hints, Pólya) and runs the checks below. It writes `report.json`
 * and `report.md` to --out; with --shots, one viewport picture per finding (the first offending
 * element centred), to look at only where a check fired.
 *
 * Checks (each a class of defect, not one bug):
 *   katex-broken      a rendered formula whose pieces are forced out of their inline layout
 *                     (a descendant `span { display: block }` rule; QA Q1)
 *   latex-unrendered  LaTeX commands left as plain text outside any formula
 *   katex-error       KaTeX could not parse a formula
 *   faded-no-input    a «Complétalo tú» step with nothing to complete (QA Q4)
 *   multi-no-hint     a multiple-answer question that does not say several may be right (QA Q2)
 *   overflow-x        an element that sticks out of the viewport horizontally
 *   image-broken      a picture that did not load
 *   console-error     an error in the browser console
 *   http-error        a request answered with 4xx/5xx
 */
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return fallback;
  const next = process.argv[i + 1];
  return next === undefined || next.startsWith("--") ? true : next;
}

const WEB = arg("web", "http://localhost:5173");
const API = arg("api", "http://localhost:8000");
const USER = arg("user", "estudiante_colegio_2");
const PASSWORD = arg("password", "test1234");
const COURSE = arg("course", "algebra_basica");
const WIDTH = Number(arg("width", 1366));
const HEIGHT = WIDTH < 600 ? 812 : 768;
const ONLY = arg("node", null);
const SHOTS = Boolean(arg("shots", false));
const OUT = arg("out", null);
if (!OUT) {
  console.error("--out <dir> is required");
  process.exit(2);
}
fs.mkdirSync(OUT, { recursive: true });

// Buttons that reveal more of a lesson without answering anything.
const REVEAL = /^(Ver el siguiente paso|Fijar y ver dónde falla|Comparar con la versión correcta|Pedir una pista|Pista \d de 3|Empezar por comprender|Siguiente: )/;

/** Runs in the page: every check over the DOM as it stands. */
function inspect() {
  const findings = [];
  const add = (check, el, detail) => {
    if (el) el.setAttribute("data-qa-finding", check);
    findings.push({ check, detail: String(detail).slice(0, 240) });
  };
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none";
  };

  // katex-broken: KaTeX lays each base (a direct child of `.katex-html`) out inline-block; a
  // stray descendant rule turns it into a block and the formula falls apart, one piece a line.
  const broken = [...document.querySelectorAll(".katex-html > span:not(.newline)")].filter(
    (el) => getComputedStyle(el).display !== "inline-block",
  );
  const brokenFormulas = new Set(broken.map((el) => el.closest(".katex")));
  for (const f of brokenFormulas) {
    const holder = f.parentElement?.closest("[class]:not(.katex-display):not(.katex)");
    add("katex-broken", f, `in .${(holder?.className || "?").toString().split(" ")[0]}: ${f.querySelector("annotation")?.textContent ?? ""}`);
  }

  for (const el of document.querySelectorAll(".katex-error")) add("katex-error", el, el.textContent);

  // latex-unrendered: a text node outside any formula that still carries a LaTeX command.
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const latex = /\\(frac|dfrac|sqrt|cdot|times|div|in|notin|mathbb|le|ge|neq|left|right|text)\b|\$[^$\s][^$]*\$/;
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const parent = n.parentElement;
    if (!parent || parent.closest(".katex, script, style, textarea, code")) continue;
    if (latex.test(n.textContent) && visible(parent)) add("latex-unrendered", parent, n.textContent.trim());
  }

  for (const el of document.querySelectorAll(".block-step-faded")) {
    const li = el.closest("li");
    if (!li?.querySelector("input, textarea, select")) add("faded-no-input", el, li?.textContent ?? "");
  }

  for (const el of document.querySelectorAll(".block-abstraction")) {
    if (!el.querySelector("[data-multi-hint]")) add("multi-no-hint", el, el.querySelector("h3")?.textContent ?? "");
  }

  const vw = document.documentElement.clientWidth;
  const wide = [...document.querySelectorAll("body *")].filter((el) => {
    if (!visible(el) || el.closest(".katex-display, [data-qa-scroll-ok]")) return false;
    const r = el.getBoundingClientRect();
    // Only what straddles the edge: a box wholly off-screen (a closed drawer) is hidden on purpose.
    if (r.right <= vw + 1 || r.left >= vw) return false;
    // A child of a horizontally scrolling box is fine: the box scrolls.
    for (let p = el.parentElement; p; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX;
      if (o === "auto" || o === "scroll" || o === "hidden" || o === "clip") return false;
    }
    return true;
  });
  // Report the outermost offenders only.
  for (const el of wide.filter((el) => !wide.includes(el.parentElement)).slice(0, 5)) {
    add("overflow-x", el, `${el.tagName.toLowerCase()}.${el.className} right=${Math.round(el.getBoundingClientRect().right)} > ${vw}`);
  }

  for (const img of document.querySelectorAll("img")) {
    if (img.complete && img.naturalWidth === 0 && visible(img)) add("image-broken", img, img.getAttribute("src"));
  }
  return findings;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });
  let pageErrors = [];
  page.on("console", (m) => {
    if (m.type() === "error") pageErrors.push({ check: "console-error", detail: m.text().slice(0, 240) });
  });
  page.on("pageerror", (e) => pageErrors.push({ check: "console-error", detail: String(e).slice(0, 240) }));
  page.on("response", (r) => {
    if (r.status() >= 400) pageErrors.push({ check: "http-error", detail: `${r.status()} ${r.url().replace(API, "").replace(WEB, "")}` });
  });

  await page.goto(`${WEB}/login`);
  await page.fill('input[autocomplete="username"]', USER);
  await page.fill('input[autocomplete="current-password"]', PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/student\//, { timeout: 20000 });

  const token = await page.evaluate(() => JSON.parse(localStorage.getItem("levelup-auth") || "{}").state?.accessToken);
  const map = await (await page.request.get(`${API}/api/student/map/${COURSE}`, { headers: { Authorization: `Bearer ${token}` } })).json();
  const nodes = (map.nodes || []).map((n) => n.node_id).filter((id) => !ONLY || id === ONLY);
  console.log(`${nodes.length} nodes, ${USER}, ${WIDTH}px`);

  const report = [];
  for (const nodeId of nodes) {
    pageErrors = [];
    await page.goto(`${WEB}/student/course/${COURSE}/lesson/${nodeId}`);
    try {
      await page.waitForSelector("main h1, main h2, main h3", { timeout: 15000 });
      await page.waitForLoadState("networkidle", { timeout: 10000 });
    } catch {
      report.push({ node: nodeId, findings: [{ check: "load", detail: "the lesson did not render" }, ...pageErrors] });
      continue;
    }
    for (let i = 0; i < 80; i++) {
      const next = page.getByRole("button", { name: REVEAL }).first();
      if ((await next.count()) === 0) break;
      try {
        if (process.env.QA_DEBUG) console.log("  click:", await next.textContent());
        await next.click({ timeout: 2000 });
      } catch {
        break;
      }
    }
    await page.waitForTimeout(300);
    const findings = [...(await page.evaluate(inspect)), ...pageErrors];
    if (SHOTS) {
      const seen = new Set();
      for (const f of findings) {
        if (seen.has(f.check)) continue;
        seen.add(f.check);
        const el = page.locator(`[data-qa-finding="${f.check}"]`).first();
        if ((await el.count()) === 0) continue;
        await el.evaluate((e) => e.scrollIntoView({ block: "center" }));
        f.shot = path.join(OUT, `${nodeId}__${f.check}.png`);
        await page.screenshot({ path: f.shot });
      }
    }
    report.push({ node: nodeId, findings });
    const counts = {};
    for (const f of findings) counts[f.check] = (counts[f.check] || 0) + 1;
    console.log(nodeId.padEnd(40), Object.entries(counts).map(([k, v]) => `${k}:${v}`).join(" ") || "ok");
  }
  await browser.close();

  fs.writeFileSync(path.join(OUT, "report.json"), JSON.stringify({ user: USER, width: WIDTH, report }, null, 2));
  const totals = {};
  for (const r of report) for (const f of r.findings) totals[f.check] = (totals[f.check] || new Set()).add(r.node);
  const lines = [
    `# Lesson sweep — ${USER}, ${WIDTH}px`,
    "",
    `${report.length} nodes. Nodes with each finding:`,
    "",
    "| Check | Nodes |",
    "|---|---|",
    ...Object.entries(totals).map(([k, v]) => `| ${k} | ${v.size} |`),
    "",
  ];
  for (const r of report.filter((r) => r.findings.length)) {
    lines.push(`## ${r.node}`, "");
    for (const f of r.findings) lines.push(`- **${f.check}** ${f.detail.replace(/\n/g, " ")}`);
    lines.push("");
  }
  fs.writeFileSync(path.join(OUT, "report.md"), lines.join("\n"));
  console.log(`report: ${path.join(OUT, "report.md")}`);
})();
