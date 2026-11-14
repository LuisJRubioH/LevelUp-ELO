/** Deliberate faults, separate from the live app. Each guard must be silent on the intact
 * observation, fire after each single-field mutation, then be silent after restoration.
 * The browser fixture supplies the UI observations; role/persistence observations are payloads.
 * node scripts/qa/flow_checks_probe.js --out tmp/qa-probes [--browser <executable>]
 */
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
let chromium;
try { ({ chromium } = require("playwright")); }
catch { ({ chromium } = require("../../frontend/node_modules/playwright")); }
const { arg, common, writeReport, summary } = require("./lib");
const { checks, finding } = require("./flow_checks");
const { localURL } = require("./flow_sweep");

const cases = {
  "flow-step": { visible: true, enabled: true, changed: true },
  "lesson-completed": { before: "available", after: "completed", persisted: true },
  "lesson-next": { before: "blocked", after: "available", opened: true },
  "exam-result": { total: 2, studentCount: 2, teacherCount: 2, studentScore: 100,
    teacherScore: 100, expectedScore: 100, studentVisible: true, teacherVisible: true,
    answersMatch: true, persisted: true },
  "procedure-grade": { pending: true, image: true, studentScore: 80, teacherScore: 80,
    grade: 80, commentMatch: true, studentVisible: true, teacherVisible: true },
  "ai-degraded": { available: false, notice: true, directEnabled: true, analyzeVisible: false, sent: true },
  "league-result": { sameMatch: true, allAnswered: true, mirroredScores: true, outcome: true,
    persisted: true, visible: true, deltasMatch: true, abandoned: false, forfeit: false },
  "league-close": { unexpected: [] },
};

async function main() {
  const cfg = common();
  const report = [];
  let browser;
  let failed = false;
  try {
    browser = await chromium.launch({ executablePath: arg("browser", undefined) });
    const page = await browser.newPage();
    await page.setContent('<button id="next">Next</button><section id="result" hidden>Done</section>');
    await page.locator("#next").evaluate((button) => {
      button.onclick = () => { document.querySelector("#result").hidden = false; };
    });
    const observeStep = async () => ({ visible: await page.locator("#next").isVisible(),
      enabled: await page.locator("#next").isEnabled(), changed: await page.locator("#result").isVisible() });
    await page.locator("#next").click();
    assert.deepEqual(finding("flow-step", await observeStep(), "intact"), []);
    for (const fault of ["hide", "disable", "dead"]) {
      await page.locator("#next").evaluate((button, fault) => {
        button.hidden = fault === "hide";
        button.disabled = fault === "disable";
        document.querySelector("#result").hidden = fault === "dead";
        if (fault === "dead") button.onclick = () => {};
      }, fault);
      if (fault === "dead") await page.locator("#next").click();
      assert.equal(finding("flow-step", await observeStep(), fault).length, 1);
      await page.locator("#next").evaluate((button) => {
        button.hidden = false; button.disabled = false;
        button.onclick = () => { document.querySelector("#result").hidden = false; };
      });
      await page.locator("#next").click();
      assert.deepEqual(finding("flow-step", await observeStep(), "restored"), []);
      report.push({ name: `DOM flow-step · ${fault} · intact/fault/restored`, findings: [] });
    }
    assert.deepEqual(Object.keys(checks).sort(), Object.keys(cases).sort());
    for (const [check, good] of Object.entries(cases)) {
      assert.deepEqual(finding(check, good, "intact"), []);
      for (const [key, value] of Object.entries(good)) {
        const broken = structuredClone(good);
        broken[key] = Array.isArray(value) ? [4413] : typeof value === "boolean" ? !value
          : typeof value === "number" ? (key === "total" ? 0 : value + 1)
          : key === "before" ? "completed" : "blocked";
        assert.equal(finding(check, broken, `mutated ${key}`).length, 1, `${check}.${key} did not fire`);
        assert.deepEqual(finding(check, good, "restored"), []);
        report.push({ name: `${check}.${key} · intact/fault/restored`, findings: [] });
      }
      summary(check, []);
    }
    // Admission and reconnect codes must remain visible as failures, never be ignored as normal.
    for (const code of [4001, 4002, 4004, 4403, 4409, 4410, 4411, 4412, 4413, 4414, 4429, 4500, 1006]) {
      assert.equal(finding("league-close", { unexpected: [code] }, `close ${code}`).length, 1);
      report.push({ name: `league-close · ${code}`, findings: [] });
    }
    for (const url of ["http://localhost:5173", "http://127.0.0.1:8000", "ws://[::1]:8000"]) localURL(url);
    for (const url of ["https://luislevelupelo.vercel.app", "http://localhost.evil.test", "http://127.1",
      "http://user:password@localhost", "https://localhost", "http://10.0.0.1"]) {
      // URL canonicalisation accepts 127.1 as 127.0.0.1: still loopback, hence safe.
      if (new URL(url).hostname === "127.0.0.1") continue;
      assert.throws(() => localURL(url));
    }
    for (const [name, args, env] of [
      ["remote", ["--web", "https://luislevelupelo.vercel.app"], {}],
      ["database", [], { DATABASE_URL: "" }],
      ["unreachable", ["--api", "http://127.0.0.1:1"], {}],
    ]) {
      const out = path.join(cfg.out, name);
      const run = spawnSync(process.execPath, [path.join(__dirname, "flow_sweep.js"), "--out", out,
        ...(arg("browser", null) ? ["--browser", arg("browser")] : []), ...args],
      { encoding: "utf8", env: { ...process.env, ...env }, timeout: 60000 });
      assert.equal(run.status, 2, `${name}: expected exit 2; ${run.stdout} ${run.stderr}`);
      const output = JSON.parse(fs.readFileSync(path.join(out, "report.json"), "utf8"));
      assert.equal(output.flows.length, 4);
      assert(output.flows.every((f) => f.status === "blocked"));
      assert(output.report.some((r) => r.findings.some((f) => f.check === "flow-setup")));
      report.push({ name: `safety/setup · ${name}`, findings: [] });
    }
    const launcher = spawnSync(arg("python", "python"), [path.join(__dirname, "serve_flow_app.py")],
      { encoding: "utf8", env: { ...process.env, DATABASE_URL: "" }, timeout: 10000 });
    assert.equal(launcher.status, 2);
    assert.match(launcher.stdout, /DATABASE_URL is defined/);
    report.push({ name: "safety/setup · launcher refuses DATABASE_URL", findings: [] });
  } catch (e) {
    failed = true;
    report.push({ name: "probe failure", findings: [{ check: "probe-failed", detail: e.stack }] });
    console.error(e.stack);
  } finally {
    if (browser) await browser.close();
    writeReport(cfg.out, "Flow guard deliberate-fault probes", report);
    console.log(`${report.length} probes; ${failed ? "FAILED" : "PASS"}`);
    process.exitCode = failed ? 1 : 0;
  }
}
main();
