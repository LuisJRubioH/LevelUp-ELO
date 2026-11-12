/**
 * QA only: what the browser sweeps share — arguments, sign-in, the DOM checks, the error
 * collectors, screenshots and the report. See docs/qa/README.md.
 */
const fs = require("fs");
const path = require("path");

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return fallback;
  const next = process.argv[i + 1];
  return next === undefined || next.startsWith("--") ? true : next;
}

function common() {
  const width = Number(arg("width", 1366));
  const out = arg("out", null);
  if (!out) {
    console.error("--out <dir> is required");
    process.exit(2);
  }
  fs.mkdirSync(out, { recursive: true });
  return {
    web: arg("web", "http://localhost:5173"),
    api: arg("api", "http://localhost:8000"),
    width,
    height: width < 600 ? 812 : 768,
    shots: Boolean(arg("shots", false)),
    out,
  };
}

async function login(page, web, user, password) {
  await page.goto(`${web}/login`);
  await page.fill('input[autocomplete="username"]', user);
  await page.fill('input[autocomplete="current-password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL((url) => !url.pathname.startsWith("/login"), { timeout: 20000 });
}

async function token(page) {
  return page.evaluate(() => JSON.parse(localStorage.getItem("levelup-auth") || "{}").state?.accessToken);
}

/** Console errors (with React's %s filled in) and 4xx/5xx responses, per screen. */
function collect(page, { web, api }, ignore = []) {
  let pending = [];
  page.on("console", (m) => {
    if (m.type() !== "error") return;
    pending.push(
      Promise.all(m.args().map((a) => a.jsonValue().catch(() => "")))
        .then((vals) => {
          let text = m.text();
          if (vals.length > 1 && typeof vals[0] === "string" && vals[0].includes("%s")) {
            let i = 1;
            text = vals[0].replace(/%s/g, () => String(vals[i++] ?? ""));
          }
          return { check: "console-error", detail: text.slice(0, 240) };
        })
        .catch(() => ({ check: "console-error", detail: m.text().slice(0, 240) })),
    );
  });
  page.on("pageerror", (e) => pending.push(Promise.resolve({ check: "page-crash", detail: String(e).slice(0, 240) })));
  page.on("response", (r) => {
    if (r.status() < 400) return;
    const url = r.url().replace(api, "").replace(web, "");
    if (ignore.some((re) => re.test(`${r.status()} ${url}`))) return;
    pending.push(Promise.resolve({ check: "http-error", detail: `${r.status()} ${r.request().method()} ${url}` }));
  });
  return {
    async take() {
      const found = await Promise.all(pending);
      pending = [];
      // A failed request also logs «Failed to load resource»: the http-error already says it.
      return found.filter((f) => !(f.check === "console-error" && f.detail.startsWith("Failed to load resource")));
    },
  };
}

/** Runs in the page: every DOM check over the screen as it stands. */
function inspect() {
  const findings = [];
  const add = (check, el, detail) => {
    if (el && el.setAttribute) el.setAttribute("data-qa-finding", check);
    findings.push({ check, detail: String(detail).replace(/\s+/g, " ").trim().slice(0, 240) });
  };
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none";
  };

  // error-screen: the app's error boundary took the screen.
  for (const h of document.querySelectorAll("h1")) {
    if (/Algo salió mal|Something went wrong/.test(h.textContent || "")) add("error-screen", h, document.body.innerText.slice(0, 200));
  }

  // katex-broken: KaTeX lays each base (a direct child of `.katex-html`) out inline-block; a
  // stray descendant rule turns it into a block and the formula falls apart, one piece a line.
  const broken = [...document.querySelectorAll(".katex-html > span:not(.newline)")].filter(
    (el) => getComputedStyle(el).display !== "inline-block",
  );
  for (const f of new Set(broken.map((el) => el.closest(".katex")))) {
    const holder = f.parentElement?.closest("[class]:not(.katex-display):not(.katex)");
    add("katex-broken", f, `in .${(holder?.className || "?").toString().split(" ")[0]}: ${f.querySelector("annotation")?.textContent ?? ""}`);
  }

  // katex-error: MathContent shows a formula KaTeX refused as its source, marked data-math-error.
  for (const el of document.querySelectorAll("[data-math-error], .katex-error")) add("katex-error", el, el.textContent);

  // latex-unrendered: a text node outside any formula that still carries a LaTeX command.
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const latex = /\\[a-zA-Z]{2,}|\{,\}|\$[^$\s][^$]*\$/;
  // i18n-key: an untranslated key such as `practice.sendAnswer` shown as text.
  const i18nKey = /^\s*[a-z][a-zA-Z]+(\.[a-z][a-zA-Z0-9]+){1,4}\s*$/;
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const parent = n.parentElement;
    if (!parent || parent.closest(".katex, script, style, textarea, code, [data-math-error]")) continue;
    if (!visible(parent)) continue;
    if (latex.test(n.textContent)) add("latex-unrendered", parent, n.textContent);
    else if (i18nKey.test(n.textContent) && !/\.(com|co|org|net|app|json|png|webp)\b/.test(n.textContent)) add("i18n-key", parent, n.textContent);
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
  for (const el of wide.filter((el) => !wide.includes(el.parentElement)).slice(0, 5)) {
    const cls = typeof el.className === "string" ? el.className.split(" ").slice(0, 2).join(".") : "";
    add("overflow-x", el, `${el.tagName.toLowerCase()}.${cls} «${(el.textContent || "").trim().slice(0, 40)}» right=${Math.round(el.getBoundingClientRect().right)} > ${vw}`);
  }

  for (const img of document.querySelectorAll("img")) {
    if (img.complete && img.naturalWidth === 0 && visible(img)) add("image-broken", img, img.getAttribute("src"));
  }

  // clipped-control: a button or link whose text does not fit its box (cut off on screen).
  for (const el of document.querySelectorAll("button, a, [role=button], select")) {
    if (!visible(el) || el.closest("[data-qa-scroll-ok]")) continue;
    const s = getComputedStyle(el);
    if (s.overflow === "visible" && s.textOverflow !== "ellipsis") continue;
    if (el.scrollWidth > el.clientWidth + 2 && (el.textContent || "").trim()) {
      add("clipped-control", el, `«${el.textContent.trim().slice(0, 50)}» ${el.scrollWidth}px in ${el.clientWidth}px`);
    }
  }
  return findings;
}

/** One viewport picture per check, centred on its first offending element. */
async function shoot(page, findings, out, name) {
  const seen = new Set();
  for (const f of findings) {
    if (seen.has(f.check)) continue;
    seen.add(f.check);
    const el = page.locator(`[data-qa-finding="${f.check}"]`).first();
    if ((await el.count()) === 0) continue;
    await el.evaluate((e) => e.scrollIntoView({ block: "center" })).catch(() => {});
    f.shot = path.join(out, `${name.replace(/[^\w.-]+/g, "_")}__${f.check}.png`);
    await page.screenshot({ path: f.shot });
  }
}

function writeReport(out, title, report) {
  fs.writeFileSync(path.join(out, "report.json"), JSON.stringify({ title, report }, null, 2));
  const totals = {};
  for (const r of report) for (const f of r.findings) (totals[f.check] ||= new Set()).add(r.name);
  const lines = [
    `# ${title}`,
    "",
    `${report.length} screens. Screens with each finding:`,
    "",
    "| Check | Screens |",
    "|---|---|",
    ...Object.entries(totals).map(([k, v]) => `| ${k} | ${v.size} |`),
    "",
  ];
  for (const r of report.filter((r) => r.findings.length)) {
    lines.push(`## ${r.name}`, "");
    const seen = new Set();
    for (const f of r.findings) {
      const line = `- **${f.check}** ${f.detail}${f.shot ? ` ([shot](${path.basename(f.shot)}))` : ""}`;
      if (!seen.has(line)) lines.push(line);
      seen.add(line);
    }
    lines.push("");
  }
  fs.writeFileSync(path.join(out, "report.md"), lines.join("\n"));
  console.log(`report: ${path.join(out, "report.md")}`);
}

function summary(name, findings) {
  const counts = {};
  for (const f of findings) counts[f.check] = (counts[f.check] || 0) + 1;
  console.log(name.padEnd(44), Object.entries(counts).map(([k, v]) => `${k}:${v}`).join(" ") || "ok");
}

module.exports = { arg, common, login, token, collect, inspect, shoot, writeReport, summary };
