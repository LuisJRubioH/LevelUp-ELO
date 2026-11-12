/**
 * QA only: open every screen of the app, for every role, and run the shared DOM checks
 * (scripts/qa/lib.js) on each; then answer a few practice questions per course.
 *
 * Needs the API (with PUBLIC_REGISTRATION_ENABLED=true for the sign-up screen and
 * ADMIN_PASSWORD set) and the frontend running locally, and `scripts/qa/seed_lesson_access.py`:
 *
 *   node scripts/qa/screen_sweep.js --out <dir> [--width 375] [--roles anon,student,teacher,admin]
 *        [--practice 5] [--lang es] [--shots]
 *
 * Practice answers the first option of each question, so it writes attempts and moves the
 * ratings of the local test student. Never point it at production.
 *
 * Besides the shared checks, per screen:
 *   load          the screen never settled
 *   wrong-route   the app sent the user somewhere else (a guard or a crash)
 *   no-feedback   a practice answer got nothing back
 */
const { chromium } = require("playwright");
const { arg, common, login, token, collect, inspect, shoot, writeReport, summary } = require("./lib");

const cfg = common();
const ROLES = String(arg("roles", "anon,student,teacher,admin")).split(",");
const PRACTICE = Number(arg("practice", 5));
const LANG = arg("lang", "es");
const STUDENT = arg("student", "estudiante_colegio_2");
const ADMIN_PASSWORD = arg("admin-password", process.env.ADMIN_PASSWORD || "testadmin123");

const USERS = {
  student: [STUDENT, "test1234"],
  teacher: ["profesor1", "demo1234"],
  admin: ["admin", ADMIN_PASSWORD],
};

// 401 before sign-in and the refresh probe are how the app finds out it has no session.
const EXPECTED_HTTP = [/^401 POST \/api\/auth\/refresh/, /^401 GET \/api\/auth\/me/];

async function settle(page) {
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  await page.waitForTimeout(400);
}

async function check(page, errors, report, name, expectPath) {
  await settle(page);
  const findings = [...(await page.evaluate(inspect))];
  const here = new URL(page.url()).pathname;
  if (expectPath && here !== expectPath) findings.push({ check: "wrong-route", detail: `${expectPath} → ${here}` });
  findings.push(...(await errors.take()));
  if (cfg.shots) await shoot(page, findings, cfg.out, name);
  report.push({ name, findings });
  summary(name, findings);
}

async function visit(page, errors, report, name, path) {
  try {
    await page.goto(`${cfg.web}${path}`);
  } catch (e) {
    report.push({ name, findings: [{ check: "load", detail: String(e).slice(0, 200) }] });
    return;
  }
  await check(page, errors, report, name, path);
}

async function practice(page, errors, report, course) {
  const name = `practice · ${course.id}`;
  const findings = [];
  let answered = 0;
  await page.goto(`${cfg.web}/student/course/${course.id}`);
  await settle(page);
  const start = page.getByRole("button", { name: /Practicar/ }).first();
  if (!(await start.count())) {
    report.push({ name, findings: [{ check: "no-practice", detail: "no «Practicar» on the course screen" }] });
    return;
  }
  await start.click();
  for (let i = 1; i <= PRACTICE; i++) {
    const options = page.getByRole("group", { name: "Opciones de respuesta" }).getByRole("button");
    try {
      await options.first().waitFor({ state: "visible", timeout: 12000 });
    } catch {
      const body = (await page.locator("body").innerText()).slice(0, 160).replace(/\s+/g, " ");
      if (!/completado todas las preguntas/.test(body)) findings.push({ check: "no-question", detail: `question ${i}: ${body}` });
      break;
    }
    findings.push(...(await page.evaluate(inspect)).map((f) => ({ ...f, detail: `q${i}: ${f.detail}` })));
    await options.first().click();
    await page.getByRole("button", { name: "Enviar respuesta" }).click();
    const next = page.getByRole("button", { name: /Siguiente pregunta/ }).first();
    try {
      await next.waitFor({ state: "visible", timeout: 10000 });
    } catch {
      findings.push({ check: "no-feedback", detail: `question ${i}` });
      break;
    }
    findings.push(...(await page.evaluate(inspect)).map((f) => ({ ...f, detail: `q${i} answered: ${f.detail}` })));
    answered++;
    await next.click();
  }
  if (answered < PRACTICE && !findings.length) findings.push({ check: "practice-short", detail: `${answered} of ${PRACTICE} answered` });
  findings.push(...(await errors.take()));
  if (cfg.shots) await shoot(page, findings, cfg.out, name);
  report.push({ name: `${name} (${answered} answered)`, findings });
  summary(`${name} (${answered} answered)`, findings);
}

(async () => {
  const browser = await chromium.launch();
  const report = [];
  for (const role of ROLES) {
    const context = await browser.newContext({ viewport: { width: cfg.width, height: cfg.height }, locale: LANG === "en" ? "en-US" : "es-CO" });
    await context.addInitScript((lang) => {
      try {
        localStorage.setItem("levelup-lang", lang);
      } catch {}
    }, LANG);
    const page = await context.newPage();
    const errors = collect(page, cfg, EXPECTED_HTTP);
    console.log(`── ${role}, ${cfg.width}px, ${LANG}`);

    if (role === "anon") {
      await visit(page, errors, report, "anon · home", "/");
      await visit(page, errors, report, "anon · login", "/login");
      const signup = page.getByRole("tab", { name: /Crear cuenta|Sign up/ }).or(page.getByRole("button", { name: /^(Crear cuenta|Sign up)$/ })).first();
      if (await signup.count()) {
        await signup.click();
        await check(page, errors, report, "anon · signup", "/login");
        for (const level of ["Colegio", "Semillero", "Universidad", "Concursos"]) {
          const pick = page.getByRole("button", { name: new RegExp(`\\b${level}\\b`) }).first();
          if (!(await pick.count())) continue;
          await pick.click();
          await check(page, errors, report, `anon · signup · ${level}`, "/login");
        }
      } else {
        report.push({ name: "anon · signup", findings: [{ check: "no-signup", detail: "no «Crear cuenta» (is PUBLIC_REGISTRATION_ENABLED on?)" }] });
      }
      await context.close();
      continue;
    }

    try {
      await login(page, cfg.web, ...USERS[role]);
    } catch (e) {
      report.push({ name: `${role} · login`, findings: [{ check: "login", detail: String(e).slice(0, 200) }] });
      await context.close();
      continue;
    }
    await errors.take();

    if (role === "student") {
      const auth = { Authorization: `Bearer ${await token(page)}` };
      const courses = await (await page.request.get(`${cfg.api}/api/student/courses`, { headers: auth })).json();
      const enrolled = (Array.isArray(courses) ? courses : []).filter((c) => c.enrolled);
      for (const [name, path] of [
        ["courses", "/student/courses"],
        ["stats", "/student/stats"],
        ["league", "/student/league"],
        ["exam", "/student/exam"],
        ["procedure", "/student/procedure"],
        ["feedback", "/student/feedback"],
        ["display name", "/mi-nombre"],
        ["change password", "/cambiar-contrasena"],
      ]) {
        await visit(page, errors, report, `student · ${name}`, path);
      }
      for (const course of enrolled) {
        await visit(page, errors, report, `student · course · ${course.id}`, `/student/course/${course.id}`);
        await visit(page, errors, report, `student · map · ${course.id}`, `/student/course/${course.id}/map`);
      }
      for (const course of enrolled.filter((c) => c.diagnostic_done)) await practice(page, errors, report, course);
    }

    if (role === "teacher") {
      for (const name of ["", "groups", "procedures", "export", "exams"]) {
        await visit(page, errors, report, `teacher · ${name || "dashboard"}`, `/teacher${name ? `/${name}` : ""}`);
      }
    }

    if (role === "admin") {
      for (const name of ["", "groups", "reports", "audit", "import"]) {
        await visit(page, errors, report, `admin · ${name || "users"}`, `/admin${name ? `/${name}` : ""}`);
      }
    }
    await context.close();
  }
  await browser.close();
  writeReport(cfg.out, `Screen sweep — ${cfg.width}px, ${LANG}, ${ROLES.join(", ")}`, report);
})();
