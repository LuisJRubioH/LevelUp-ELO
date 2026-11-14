/**
 * QA only: render every formula a student can see — the whole item bank and every lesson node —
 * with the frontend's own KaTeX, offline, in seconds. No browser, no server, no model tokens.
 *
 *   node scripts/qa/math_check.js --out <dir> [--only bank|lessons]
 *
 * It mirrors frontend/src/components/Math/MathContent.tsx: `MathText` splits prose on $…$,
 * $$…$$, \(…\) and \[…\]; `MathFormula` takes a whole field as LaTeX (and falls back to
 * MathText when it carries a `$`). Keep the two in step: a change there is a change here.
 *
 * Findings:
 *   parse-error   KaTeX refuses the formula: the student sees the raw source in a grey box
 *   bare-latex    a LaTeX command or `{,}` in prose, outside any delimiters: shown as text
 *   prose-in-math two `$` that were meant as money paired up into a formula: the words between
 *                 them are typeset as math, run together in italics ($500 y $300)
 *   katex-strict  KaTeX renders it but warns (unicode in math mode, …); informational
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..", "..");
const katex = require(path.join(ROOT, "frontend", "node_modules", "katex"));
// KaTeX prints a console warning per glyph it has no metrics for («, ✓, …); the strict
// callback already records what matters.
console.warn = () => {};

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? fallback : process.argv[i + 1];
}
const OUT = arg("out", null);
const ONLY = arg("only", null);
if (!OUT) {
  console.error("--out <dir> is required");
  process.exit(2);
}
fs.mkdirSync(OUT, { recursive: true });

// ── Mirror of MathContent.tsx ──────────────────────────────────────────────
function normalizeLatex(source) {
  let value = source.trim();
  if (value.startsWith("$$") && value.endsWith("$$")) value = value.slice(2, -2);
  else if (value.startsWith("$") && value.endsWith("$")) value = value.slice(1, -1);
  else if (
    (value.startsWith("\\(") && value.endsWith("\\)")) ||
    (value.startsWith("\\[") && value.endsWith("\\]"))
  ) {
    value = value.slice(2, -2);
  }
  return value
    .replace(/\\\\(?=[A-Za-z])/g, "\\")
    .replace(/\\(mathbb|mathbf|mathrm)([A-Z0-9])\b/g, "\\$1{$2}")
    .replace(/\\text\{✸\}|✸/g, "\\star")
    .replace(/○/g, "\\bigcirc");
}
const TOKENS =
  /(\$\$(?:\\\$|[\s\S])*?\$\$|\\\[[\s\S]+?\\\]|(?<!\\)\$(?:\\\$|[^$\n])+?(?<!\\)\$|\\\([\s\S]+?\\\))/g;

function render(math, display) {
  const warnings = [];
  try {
    katex.renderToString(normalizeLatex(math), {
      displayMode: display,
      throwOnError: true,
      strict: (code, msg) => {
        warnings.push(`${code}: ${msg}`);
        return "ignore";
      },
      trust: false,
    });
    return { error: null, warnings };
  } catch (e) {
    return { error: String(e.message || e).replace(/^KaTeX parse error: /, ""), warnings };
  }
}

function checkText(text) {
  const found = [];
  for (const token of text.split(TOKENS)) {
    let math = null;
    let display = false;
    if (token.startsWith("$$") && token.endsWith("$$") && token.length >= 4) [math, display] = [token.slice(2, -2), true];
    else if (token.startsWith("\\[") && token.endsWith("\\]")) [math, display] = [token.slice(2, -2), true];
    else if (token.startsWith("$") && token.endsWith("$") && token.length >= 2) math = token.slice(1, -1);
    else if (token.startsWith("\\(") && token.endsWith("\\)")) math = token.slice(2, -2);
    if (math !== null) {
      const r = render(math, display);
      if (r.error) found.push({ check: "parse-error", detail: `${r.error} ← ${token}` });
      const words = math.replace(/\\(text|mathrm|textbf|operatorname)\{[^}]*\}/g, "");
      if (/[A-Za-zÁÉÍÓÚáéíóúñÑ]{3,}\s+[A-Za-zÁÉÍÓÚáéíóúñÑ]{3,}/.test(words) && !/\\[a-zA-Z]/.test(words)) {
        found.push({ check: "prose-in-math", detail: token });
      }
      for (const w of r.warnings) found.push({ check: "katex-strict", detail: `${w} ← ${token}` });
      continue;
    }
    const bare = token.match(/\\[a-zA-Z]{2,}|\{,\}/);
    if (bare) found.push({ check: "bare-latex", detail: `«${bare[0]}» in: ${token.trim()}` });
  }
  return found;
}

function checkFormula(text) {
  if (/(?<!\\)\$/.test(normalizeLatex(text))) return checkText(text);
  const r = render(text, false);
  const found = [];
  if (r.error) found.push({ check: "parse-error", detail: `${r.error} ← ${text}` });
  for (const w of r.warnings) found.push({ check: "katex-strict", detail: `${w} ← ${text}` });
  return found;
}

// ── Sources ────────────────────────────────────────────────────────────────
const results = []; // { source, where, check, detail }

function bank() {
  const dir = path.join(ROOT, "items", "bank");
  const files = [];
  const walk = (d) => {
    for (const f of fs.readdirSync(d)) {
      const p = path.join(d, f);
      if (fs.statSync(p).isDirectory()) walk(p);
      else if (f.endsWith(".json")) files.push(p);
    }
  };
  walk(dir);
  let count = 0;
  for (const file of files) {
    const items = JSON.parse(fs.readFileSync(file, "utf8"));
    for (const item of Array.isArray(items) ? items : items.items || []) {
      if (item.retired === true) continue;
      count++;
      const where = `${path.relative(ROOT, file)} · ${item.id}`;
      for (const f of checkText(String(item.content ?? ""))) results.push({ source: "bank", where: `${where} · content`, ...f });
      (item.options || []).forEach((o, i) => {
        for (const f of checkText(String(o))) results.push({ source: "bank", where: `${where} · option ${i + 1}`, ...f });
      });
    }
  }
  return count;
}

// Fields the eleven-block renderer passes to MathFormula (grep `<MathFormula` in
// frontend/src/pages/Student/lessons/blocks/); every other string goes through MathText.
const FORMULA_KEYS = new Set([
  "latex", "error_latex", "wrong_latex", "right_latex", "symbol", "expr", "chain",
  "definition_katex", "fraction", "division", "label",
]);
const FORMULA_LISTS = new Set(["thumbnails", "given_steps"]); // lists of formulas
// Not shown to the student, or not prose.
const SKIP_KEYS = new Set([
  "id", "kind", "node_id", "image", "scene", "expected", "valid_options", "trap_options",
  "misconception", "misconception_tag", "focal_misconception", "closed", "accept", "answer",
  "regex", "unlock_after", "next_node_id", "presentation", "outcome_gain", "outcome_flat",
]);

function lessons() {
  const json = execFileSync("python3", [path.join(ROOT, "scripts", "qa", "dump_lesson_content.py")], {
    cwd: ROOT,
    maxBuffer: 64 * 1024 * 1024,
  }).toString();
  const nodes = JSON.parse(json);
  const visit = (value, keyPath, node, formula) => {
    if (typeof value === "string") {
      const key = keyPath[keyPath.length - 1];
      if (SKIP_KEYS.has(key)) return;
      // method_comparison.methods[].steps are formulas; worked_examples[].steps are prose.
      const isFormula = formula || FORMULA_KEYS.has(key) || (key === "steps[]" && keyPath.includes("methods[]"));
      for (const f of isFormula ? checkFormula(value) : checkText(value)) {
        results.push({ source: "lessons", where: `${node} · ${keyPath.join(".")}`, ...f });
      }
    } else if (Array.isArray(value)) {
      const key = keyPath[keyPath.length - 1];
      value.forEach((v) => visit(v, [...keyPath.slice(0, -1), `${key}[]`], node, formula || FORMULA_LISTS.has(key)));
    } else if (value && typeof value === "object") {
      for (const [k, v] of Object.entries(value)) visit(v, [...keyPath, k], node, false);
    }
  };
  for (const [node, content] of Object.entries(nodes)) visit(content, ["content"], node, false);
  return Object.keys(nodes).length;
}

const counts = {};
if (ONLY !== "lessons") counts.items = bank();
if (ONLY !== "bank") counts.nodes = lessons();

// ── Report ─────────────────────────────────────────────────────────────────
fs.writeFileSync(path.join(OUT, "math_report.json"), JSON.stringify({ counts, results }, null, 2));
const byCheck = {};
for (const r of results) {
  const k = `${r.source} · ${r.check}`;
  byCheck[k] = (byCheck[k] || 0) + 1;
}
const lines = [
  "# Math check",
  "",
  `${counts.items ?? 0} items in circulation, ${counts.nodes ?? 0} lesson nodes.`,
  "",
  "| Source · check | Findings |",
  "|---|---|",
  ...Object.entries(byCheck).sort().map(([k, v]) => `| ${k} | ${v} |`),
  "",
];
for (const check of ["parse-error", "bare-latex", "prose-in-math"]) {
  const rows = results.filter((r) => r.check === check);
  if (!rows.length) continue;
  lines.push(`## ${check}`, "");
  for (const r of rows) lines.push(`- \`${r.where}\` — ${r.detail.replace(/\n/g, " ").slice(0, 300)}`);
  lines.push("");
}
fs.writeFileSync(path.join(OUT, "math_report.md"), lines.join("\n"));
for (const [k, v] of Object.entries(byCheck).sort()) console.log(`${k.padEnd(32)} ${v}`);
console.log(`report: ${path.join(OUT, "math_report.md")}`);
process.exitCode = results.some((r) => r.check !== "katex-strict") ? 1 : 0;
