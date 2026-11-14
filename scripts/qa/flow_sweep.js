/** Real local end-to-end QA. No product fixes, response stubs, AI or browser installation.
 * node scripts/qa/flow_sweep.js --out tmp/qa-flow [--shots] [--browser <chromium executable>]
 * See docs/qa/README.md for setup, exit codes and the separate deliberate-fault probes.
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
let playwright;
try { playwright = require("playwright"); }
catch { playwright = require("../../frontend/node_modules/playwright"); }
const { arg, common, token, collect, inspect, shoot, writeReport, summary } = require("./lib");
const { finding } = require("./flow_checks");

function procedurePNG(seed) {
  // Build a valid 16x16 RGB PNG, with run-specific pixels to avoid the copy detector.
  const hash = require("crypto").createHash("sha256").update(seed).digest();
  const chunk = (type, data) => {
    const body = Buffer.concat([Buffer.from(type), data]);
    let crc = 0xffffffff;
    for (const byte of body) {
      crc ^= byte;
      for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
    }
    const size = Buffer.alloc(4); size.writeUInt32BE(data.length);
    const checksum = Buffer.alloc(4); checksum.writeUInt32BE((crc ^ 0xffffffff) >>> 0);
    return Buffer.concat([size, body, checksum]);
  };
  const header = Buffer.alloc(13); header.writeUInt32BE(16); header.writeUInt32BE(16, 4);
  header[8] = 8; header[9] = 2;
  const pixels = Buffer.alloc(16 * 49);
  for (let row = 0; row < 16; row++) {
    for (let col = 1; col < 49; col++) pixels[row * 49 + col] = hash[(row + col) % hash.length];
  }
  return Buffer.concat([Buffer.from("89504e470d0a1a0a", "hex"), chunk("IHDR", header),
    chunk("IDAT", require("zlib").deflateSync(pixels)), chunk("IEND", Buffer.alloc(0))]);
}

function localURL(value) {
  const url = new URL(value);
  if (!["http:", "ws:"].includes(url.protocol) ||
      !["localhost", "127.0.0.1", "[::1]"].includes(url.hostname) || url.username || url.password) {
    throw new Error("Only HTTP/WS loopback URLs without credentials are allowed");
  }
  return url;
}

class FlowStop extends Error {}

async function main() {
  const cfg = common();
  const report = [];
  const results = [];
  let browser;
  let request;
  const actors = [];
  const course = "algebra_basica";
  const stamp = `${Date.now()}${process.pid}`;
  const username = `qa_flow_${stamp}`;
  const password = "QaLocal1234";
  const displayName = `Ana Prueba ${stamp.replace(/\d/g, (n) => "abcdefghij"[Number(n)])}`;
  let answers;
  let student;
  let teacher;
  let group;

  async function screen(actor, name, extra = []) {
    await actor.page.waitForTimeout(180); // allow layout/animations to settle, not an outcome oracle
    const findings = [...await actor.page.evaluate(inspect), ...extra, ...await actor.errors.take()];
    if (cfg.shots) {
      await shoot(actor.page, findings, cfg.out, name);
      if (extra.length) {
        const shot = path.join(cfg.out, `${name.replace(/[^\w.-]+/g, "_")}.png`);
        await actor.page.screenshot({ path: shot });
        extra.forEach((f) => { f.shot = shot; });
      }
    }
    report.push({ name, findings });
    summary(name, findings);
    return findings;
  }

  async function eventually(predicate, timeout = 15000) {
    const deadline = Date.now() + timeout;
    do {
      if (await predicate()) return true;
      await new Promise((resolve) => setTimeout(resolve, 100));
    } while (Date.now() < deadline);
    return false;
  }

  async function api(actor, method, endpoint, data) {
    const url = `${cfg.api}${endpoint}`;
    localURL(url);
    let r;
    try {
      r = await request.fetch(url, { method, data, maxRedirects: 0,
        headers: actor ? { Authorization: `Bearer ${await token(actor.page)}` } : {} });
    } catch {
      // Playwright's request error includes its headers: never copy a bearer into the report.
      throw new Error(`${method} ${endpoint}: local request failed`);
    }
    if (!r.ok()) throw new Error(`${method} ${endpoint}: HTTP ${r.status()}`);
    return r.status() === 204 ? null : r.json();
  }

  function watchResponse(page, endpoint) {
    // Attach the rejection handler immediately: a dead button must not crash the other flows
    // or prevent report generation while this response is still being awaited.
    return page.waitForResponse((r) => new URL(r.url()).pathname === endpoint && r.request().method() === "POST",
      { timeout: 20000 }).catch(() => null);
  }

  async function responseJSON(promise) {
    const response = await promise;
    if (!response) throw new Error("Expected POST response did not arrive");
    if (!response.ok()) throw new Error(`Flow POST returned HTTP ${response.status()}`);
    return response.json();
  }

  async function actor(user, pass) {
    const context = await browser.newContext({ viewport: { width: cfg.width, height: cfg.height },
      locale: "es-CO", serviceWorkers: "block" });
    const allowed = new Set([new URL(cfg.api).origin, new URL(cfg.web).origin]);
    await context.route("**/*", (route) => {
      const url = new URL(route.request().url());
      return allowed.has(url.origin) || ["data:", "blob:"].includes(url.protocol)
        ? route.continue() : route.abort("blockedbyclient");
    });
    await context.addInitScript(() => {
      const Native = window.WebSocket;
      window.WebSocket = class extends Native {
        constructor(url, protocols) {
          const parsed = new URL(url, location.href);
          if (parsed.protocol !== "ws:" || !["localhost", "127.0.0.1", "[::1]"].includes(parsed.hostname) || parsed.username || parsed.password) {
            throw new Error("QA refuses non-local WebSockets");
          }
          super(parsed.href, protocols);
        }
      };
    });
    await context.addInitScript(() => localStorage.setItem("levelup-lang", "es"));
    const page = await context.newPage();
    page.setDefaultTimeout(10000);
    const a = { context, page, errors: collect(page, cfg,
      [/^401 POST \/api\/auth\/refresh/, /^401 GET \/api\/auth\/me/]) };
    actors.push(a);
    await page.goto(`${cfg.web}/login`);
    await page.locator('input[autocomplete="username"]').waitFor();
    await screen(a, `${user} · login`);
    await page.fill('input[autocomplete="username"]', user);
    await page.fill('input[autocomplete="current-password"]', pass);
    await step(a, `${user} · signed in`, page.locator('button[type="submit"]'),
      () => Promise.resolve(!new URL(page.url()).pathname.startsWith("/login")));
    return a;
  }

  async function visit(a, name, route, selector) {
    await a.page.goto(`${cfg.web}${route}`);
    try { await a.page.locator(selector).first().waitFor(); }
    catch (e) {
      await screen(a, name, [{ check: "flow-step", detail: `Expected screen ${route}: ${e.message.slice(0, 200)}` }]);
      throw new FlowStop(name);
    }
    await screen(a, name, finding("flow-step", { visible: true, enabled: true,
      changed: new URL(a.page.url()).pathname === route.split("?")[0] }, `Wrong route: ${a.page.url()}`));
  }

  async function step(a, name, button, changed) {
    const state = { visible: false, enabled: false, changed: false };
    let detail = name;
    try {
      await button.waitFor({ state: "visible" });
      state.visible = true;
      state.enabled = await button.isEnabled();
      if (state.enabled) {
        await button.click();
        state.changed = await eventually(changed);
      }
    } catch (e) { detail += `: ${e.message.slice(0, 220)}`; }
    const found = finding("flow-step", state, `${detail}; ${JSON.stringify(state)}`);
    await screen(a, name, found);
    if (found.length) throw new FlowStop(detail);
  }

  async function contract(a, name, check, state) {
    const found = finding(check, state, JSON.stringify(state));
    await screen(a, name, found);
    report.at(-1).observation = state;
    if (found.length) throw new FlowStop(`${name}: ${check}`);
  }

  async function flow(name, work) {
    console.log(`── ${name}`);
    const start = report.length;
    let status = "completed";
    try { await work(); }
    catch (e) {
      status = "failed";
      if (!(e instanceof FlowStop)) {
        const findings = [{ check: "flow-error", detail: e.message.slice(0, 400) }];
        await screen(name === "exam" ? teacher : student, `${name} · stopped`, findings);
      }
      if (name === "league") for (const a of actors.filter((a) => a.messages)) {
        const unexpected = await a.page.evaluate(() => (window.__qaCloses || []).filter((c) => c !== 1000));
        await screen(a, "league · stopped socket", finding("league-close", { unexpected }, `Close codes: ${unexpected.join(", ")}`));
      }
    }
    results.push({ flow: name, status, findings: report.slice(start).reduce((n, r) => n + r.findings.length, 0) });
    console.log(`${name}: ${status}`);
  }

  async function lessonFlow() {
    const nodes = Object.values(answers.nodes);
    const node = nodes.find((n) => n.content?.kind === "eleven_block_node");
    if (!node) throw new Error("No eleven-block node in domain export");
    // Open only its predecessors through the app, preserving the next node's locked state.
    const predecessors = [];
    let previous = node.unlock_after;
    while (previous) {
      const n = answers.nodes[previous];
      if (!n) throw new Error(`Unknown prerequisite ${previous}`);
      predecessors.unshift(n);
      previous = n.unlock_after;
    }
    for (const n of predecessors) {
      const base = `/api/student/lessons/${course}/${n.node_id}`;
      await api(student, "POST", `${base}/events`, { event: "node_viewed" });
      for (const item of n.interactions) await api(student, "POST", `${base}/interactions`, {
        interaction_id: item.interaction_id, selected_option: n.answers[item.interaction_id] });
      await api(student, "POST", `${base}/events`, { event: "node_completed" });
    }
    const next = nodes.find((n) => n.unlock_after === node.node_id);
    if (!next) throw new Error("No successor declared by domain");
    const map = async () => (await api(student, "GET", `/api/student/map/${course}`)).nodes;
    const before = await map();
    const beforeNode = before.find((n) => n.node_id === node.node_id);
    const beforeNext = before.find((n) => n.node_id === next.node_id);
    const base = `/api/student/lessons/${course}/${node.node_id}`;
    await visit(student, "lesson · opened", `/student/course/${course}/lesson/${node.node_id}`, ".eleven-block-page");
    await step(student, "lesson · genuine attempt", student.page.locator(".block-attempt button").first(),
      () => student.page.locator(".block-attempt-response").isVisible());
    for (const [index, item] of node.content.practice.entries()) {
      const unit = student.page.locator(".blk-practice article.block-item").nth(index);
      await answerLesson(unit, item, node, `lesson · practice ${item.id}`);
    }
    for (let i = 0; i < 4; i++) {
      const button = student.page.locator(".block-polya > button");
      await step(student, `lesson · Pólya ${i + 1}`, button,
        () => i === 3 ? student.page.locator(".block-polya article.block-item").isVisible()
          : student.page.locator(".block-polya-steps li").count().then((n) => n === i + 1));
    }
    await answerLesson(student.page.locator(".block-polya article.block-item"),
      { ...node.content.closing_item, kind: "numeric" }, node, "lesson · closing answer");
    await step(student, "lesson · finish", student.page.locator(".block-footer button"),
      () => Promise.resolve(new URL(student.page.url()).pathname.endsWith("/map")));
    const after = await map();
    const saved = await api(student, "GET", base);
    await contract(student, "lesson · persisted completion", "lesson-completed", {
      before: beforeNode?.state, after: after.find((n) => n.node_id === node.node_id)?.state,
      persisted: saved.state === "completed" && node.interactions.every((i) => saved.progress.responses[i.interaction_id]?.is_expected),
    });
    const nextState = after.find((n) => n.node_id === next.node_id)?.state;
    const nextRow = after.find((n) => n.node_id === next.node_id);
    await step(student, "lesson · open successor", student.page.locator("button.node").filter({ has: student.page.locator(".disc") }).and(student.page.getByRole("button", { name: new RegExp(`^${nextRow?.label || "__missing__"}:`) })),
      () => Promise.resolve(student.page.url().includes(`/lesson/${next.node_id}`)));
    await contract(student, "lesson · next unlocked", "lesson-next", {
      before: beforeNext?.state, after: nextState, opened: await student.page.locator(".eleven-block-page").isVisible(),
    });
  }

  async function answerLesson(unit, item, node, name) {
    const answer = node.answers[`${node.node_id}-${item.id}`];
    if (answer === undefined) throw new Error(`No server answer for ${item.id}`);
    if (["numeric", "text_exact"].includes(item.kind)) {
      await unit.locator("input:not([type=range])").fill(answer);
    } else {
      for (const id of answer.split(",")) {
        const index = item.options.findIndex((o) => o.id === id);
        if (index < 0) throw new Error(`Answer ${id} absent from domain options`);
        await unit.locator(".block-options button").nth(index).click();
      }
    }
    const check = unit.getByRole("button", { name: "Comprobar", exact: true });
    if (await check.count()) await step(student, name, check, () => unit.locator(".block-feedback.is-ok").isVisible());
    else {
      const ok = await eventually(() => unit.locator(".block-feedback.is-ok").isVisible());
      await contract(student, name, "flow-step", { visible: true, enabled: true, changed: ok });
    }
  }

  async function examFlow() {
    const p = teacher.page;
    const title = `QA flow ${stamp}`;
    await visit(teacher, "exam · teacher list", "/teacher/exams", ".ex-toolbar select");
    await p.locator(".ex-toolbar select").selectOption(course);
    await step(teacher, "exam · create form", p.locator(".ex-toolbar button"), () => p.locator(".ex-form").isVisible());
    await p.locator(".ex-config select").selectOption(course);
    await p.locator('.ex-config input:not([type=range])').fill(title);
    await p.locator(".ex-item").first().waitFor();
    // Pick real catalogue items in the UI. The server grading data stays in this Node process.
    await p.locator(".ex-item").nth(0).click();
    await p.locator(".ex-item").nth(1).click();
    await screen(teacher, "exam · selected items");
    await step(teacher, "exam · created", p.getByRole("button", { name: "Crear examen", exact: true }),
      () => p.locator(".ex-card").filter({ hasText: title }).isVisible());
    const templates = await api(teacher, "GET", `/api/teacher/exam-templates?course_id=${course}`);
    const template = templates.find((t) => t.title === title);
    if (!template) throw new Error("Created template absent from server");
    const card = p.locator(".ex-card").filter({ hasText: title });
    await step(teacher, "exam · assignment dialog", card.getByRole("button", { name: "Asignar", exact: true }),
      () => p.getByRole("dialog", { name: "Asignar examen" }).isVisible());
    const dialog = p.getByRole("dialog", { name: "Asignar examen" });
    await dialog.locator("label.ex-grp-opt").filter({ hasText: group.name }).locator("input").check();
    await step(teacher, "exam · assigned", dialog.getByRole("button", { name: "Guardar asignación" }),
      async () => (await api(teacher, "GET", `/api/teacher/exam-templates/${template.id}/assignments`)).some((a) => a.group_id === group.group_id));
    await visit(student, "exam · student assignment", "/student/exam", "main select");
    await step(student, "exam · selected assignment", student.page.getByRole("button", { name: new RegExp(title) }),
      () => student.page.locator("select").nth(1).inputValue().then((v) => v === String(template.id)));
    const started = watchResponse(student.page, "/api/student/exam/start");
    await step(student, "exam · started", student.page.getByRole("button", { name: "Iniciar examen →", exact: true }),
      () => student.page.getByRole("timer").isVisible());
    const run = await responseJSON(started);
    let correct = 0;
    const selected = {};
    for (const [i, item] of run.items.entries()) {
      const index = item.options.indexOf(answers.bank[item.id]);
      if (index < 0) throw new Error(`Missing bank answer ${item.id}`);
      selected[item.id] = item.options[index];
      correct++;
      // The options container is the sibling immediately after the question statement/image.
      const options = student.page.locator("div.space-y-3 > button.w-full");
      await step(student, `exam · answer ${i + 1}`, options.nth(index),
        () => options.nth(index).getAttribute("class").then((c) => c.includes("ring-1")));
      if (i < run.items.length - 1) await step(student, `exam · next ${i + 1}`,
        student.page.getByRole("button", { name: "Siguiente →", exact: true }),
        () => options.nth(index).getAttribute("class").then((c) => !c.includes("ring-1")));
    }
    await step(student, "exam · confirm screen", student.page.getByRole("button", { name: "Finalizar examen", exact: true }),
      () => student.page.getByRole("button", { name: "Sí, finalizar", exact: true }).isVisible());
    const submitted = watchResponse(student.page, "/api/student/exam/submit");
    await step(student, "exam · submitted", student.page.getByRole("button", { name: "Sí, finalizar", exact: true }),
      () => student.page.getByRole("button", { name: "Nuevo examen", exact: true }).isVisible());
    const result = await responseJSON(submitted);
    await visit(teacher, "exam · teacher refreshed", "/teacher/exams", ".ex-toolbar select");
    await p.locator(".ex-toolbar select").selectOption(course);
    await step(teacher, "exam · teacher results", p.locator(".ex-card").filter({ hasText: title }).getByRole("button", { name: "Resultados" }),
      () => p.locator(".ex-stu").isVisible());
    const data = await api(teacher, "GET", `/api/teacher/exam-templates/${template.id}/results`);
    const theirs = data.students.find((s) => s.user_id === run.user_id || s.name === displayName);
    const row = p.locator(".ex-stu").filter({ hasText: displayName });
    const score = Math.round(correct / run.items.length * 1000) / 10;
    const history = await api(student, "GET", "/api/student/exam/history");
    await contract(teacher, "exam · role agreement", "exam-result", {
      total: run.items.length, studentCount: result.results?.length, teacherCount: theirs?.answers.length,
      studentScore: result.score_pct, teacherScore: theirs?.score_pct, expectedScore: score,
      studentVisible: (await student.page.locator("main").innerText()).includes(`${score}%`),
      teacherVisible: (await row.innerText()).includes(`${score}%`),
      answersMatch: theirs?.answers.every((a) => selected[a.item_id] === a.selected_option && a.is_correct),
      persisted: history.some((h) => h.course_id === course && h.n_questions === run.items.length && h.score_pct === score),
    });
  }

  async function procedureFlow() {
    const ai = await api(student, "GET", "/api/student/ai-status");
    await visit(student, "procedure · upload screen", "/student/procedure", 'input[type="file"]');
    const p = student.page;
    await p.locator('input[type="text"]').fill("alb1");
    const png = procedurePNG(stamp);
    await p.locator('input[type="file"]').setInputFiles({ name: "qa-procedure.png", mimeType: "image/png", buffer: png });
    const direct = p.getByRole("button", { name: /Enviar al docente/ });
    const aiState = { available: ai.available, notice: await p.getByText("La revisión automática con IA no está disponible en este momento.", { exact: true }).isVisible(),
      directEnabled: await direct.isEnabled(), analyzeVisible: await p.getByRole("button", { name: /Analizar con IA/ }).isVisible(), sent: false };
    const uploaded = watchResponse(p, "/api/student/procedure");
    await step(student, "procedure · sent", direct, () => p.getByRole("heading", { name: "Procedimiento enviado" }).isVisible());
    const upload = await responseJSON(uploaded);
    aiState.sent = upload.submission_id > 0 && upload.ai_score == null && !upload.is_copy;
    await contract(student, "procedure · no-key degradation", "ai-degraded", aiState);
    await visit(teacher, "procedure · teacher queue", "/teacher/procedures", ".pq-card");
    const queue = teacher.page.locator(".pq-card").filter({ hasText: displayName });
    await queue.click();
    const image = teacher.page.locator(".proc-detail img").first();
    await image.waitFor();
    const imageLoaded = await eventually(() => image.evaluate((img) => img.complete && img.naturalWidth > 0));
    await screen(teacher, "procedure · teacher image");
    const grade = 80;
    const comment = `QA reviewed ${stamp}`;
    await teacher.page.getByRole("slider", { name: "Calificación" }).fill(String(grade));
    await teacher.page.locator("textarea.pd-note").fill(comment);
    const graded = watchResponse(teacher.page, "/api/teacher/procedures/grade");
    await step(teacher, "procedure · teacher graded", teacher.page.getByRole("button", { name: `Guardar calificación · ${grade}`, exact: true }),
      () => teacher.page.locator(".proc-graded-note").isVisible());
    const gradingResponse = await responseJSON(graded);
    const gradings = await api(teacher, "GET", `/api/teacher/procedures/${upload.submission_id}/gradings`);
    await visit(student, "procedure · student feedback", "/student/feedback", "article.sp-card");
    const row = student.page.locator("article.sp-card").filter({ hasText: comment });
    await row.waitFor();
    const data = await api(student, "GET", "/api/student/procedures");
    const saved = data.submissions.find((s) => s.item_id === "alb1");
    await contract(student, "procedure · role agreement", "procedure-grade", {
      pending: upload.status === "pending", image: imageLoaded,
      studentScore: saved.teacher_score, teacherScore: gradings.at(-1)?.grade ?? gradings.at(-1)?.teacher_score,
      grade, commentMatch: saved.teacher_feedback === comment,
      studentVisible: (await row.innerText()).includes(String(grade)),
      teacherVisible: gradingResponse.elo_delta !== undefined && await teacher.page.locator(".proc-graded-note").isVisible(),
    });
  }

  async function leagueFlow() {
    const players = [];
    for (const user of ["estudiante_colegio_1", "estudiante_colegio_2"]) {
      const a = await actor(user, "test1234");
      // These seeded accounts are test-only (AGENTS R18/R19); no institution required.
      // The app's diagnostic is the sole preparation of rating state. Never write rating SQL.
      await api(a, "POST", `/api/student/diagnostic/${course}/submit`, {
        answers: [{ item_id: "alb1", selected_option: answers.bank.alb1 }] });
      a.messages = [];
      a.closes = [];
      await a.page.addInitScript(() => {
        window.__qaCloses = [];
        const Native = window.WebSocket;
        window.WebSocket = class extends Native {
          constructor(...args) {
            super(...args);
            this.addEventListener("close", (e) => window.__qaCloses.push(e.code));
          }
        };
      });
      a.page.on("websocket", (socket) => socket.on("framereceived", ({ payload }) => {
        try { a.messages.push(JSON.parse(payload.toString())); }
        catch { /* Non-JSON frames are not game events. */ }
      }));
      await visit(a, `league · ${user} lobby`, "/student/league", ".pv-select");
      await a.page.locator(".pv-select").selectOption(course);
      players.push(a);
    }
    const [a, b] = players;
    await step(a, "league · player 1 queued", a.page.getByRole("button", { name: "Buscar rival →", exact: true }),
      () => a.page.locator(".pv-radar").isVisible());
    await step(b, "league · player 2 paired", b.page.getByRole("button", { name: "Buscar rival →", exact: true }),
      () => b.page.locator(".dx-options").isVisible());
    await screen(a, "league · player 1 paired");
    const starts = players.map((p) => p.messages.find((m) => m.type === "game_start"));
    if (starts.some((s) => !s)) throw new Error("Missing game_start for a player");
    for (const [who, player] of players.entries()) {
      for (const item of starts[who].items) {
        const options = player.page.locator(".dx-options button");
        await options.first().waitFor();
        await eventually(() => options.first().isEnabled());
        const judgedBefore = player.messages.filter((m) => m.type === "answer_result").length;
        await step(player, `league · player ${who + 1} · ${item.id}`, options.first(),
          () => Promise.resolve(player.messages.filter((m) => m.type === "answer_result").length === judgedBefore + 1));
        if (item !== starts[who].items.at(-1)) {
          const advanced = await eventually(() => options.first().isEnabled());
          if (!advanced) throw new Error("No next League question");
        }
      }
      await screen(player, `league · player ${who + 1} all answers`);
    }
    const finished = await eventually(() => Promise.resolve(players.every((p) => p.messages.some((m) => m.type === "game_end"))));
    const ends = players.map((p) => p.messages.find((m) => m.type === "game_end"));
    if (!finished) throw new Error("Both players answered, no game_end");
    const histories = [];
    for (const [i, player] of players.entries()) {
      await player.page.locator(".pv-result").waitFor();
      await screen(player, `league · player ${i + 1} result`);
      histories.push(await api(player, "GET", "/api/student/pvp/history"));
      const unexpected = (await player.page.evaluate(() => window.__qaCloses)).filter((c) => c !== 1000);
      await screen(player, `league · player ${i + 1} socket`, finding("league-close", { unexpected }, `Close codes: ${unexpected.join(", ")}`));
    }
    const rows = histories.map((h, i) => (h.matches || h.items || h).find((m) => m.id === starts[i].match_id || m.match_id === starts[i].match_id));
    const boards = await Promise.all(players.map((p) => p.page.locator(".pv-board-num").allTextContents()));
    await contract(a, "league · role agreement", "league-result", {
      sameMatch: starts[0].match_id === starts[1].match_id,
      allAnswered: players.every((p, i) => p.messages.filter((m) => m.type === "answer_result").length === starts[i].items.length),
      mirroredScores: ends[0].your_score === ends[1].opp_score && ends[1].your_score === ends[0].opp_score,
      outcome: ends[0].draw === ends[1].draw && (ends[0].draw
        ? !ends[0].won && !ends[1].won : ends[0].won !== ends[1].won),
      persisted: rows.every((r, i) => r?.status === "finished" && r.my_score === ends[i].your_score &&
        r.opp_score === ends[i].opp_score && r.won === ends[i].won && r.draw === ends[i].draw),
      visible: boards.every((v, i) => Number(v[0]) === ends[i].your_score && Number(v[1]) === ends[i].opp_score),
      deltasMatch: rows.every((r, i) => r?.elo_delta === ends[i].elo_delta),
      abandoned: ends.some((e) => e.abandoned), forfeit: ends.some((e) => e.forfeit),
    });
  }

  try {
    if (Object.hasOwn(process.env, "DATABASE_URL")) throw new Error("DATABASE_URL is defined: local sweep refused");
    localURL(cfg.web); localURL(cfg.api);
    answers = JSON.parse(execFileSync(arg("python", "python"), [path.join(__dirname, "dump_flow_answers.py")],
      { encoding: "utf8", env: { ...process.env, PYTHONIOENCODING: "utf-8" }, maxBuffer: 20 * 1024 * 1024 }));
    browser = await playwright.chromium.launch({ executablePath: arg("browser", undefined) });
    request = await playwright.request.newContext({ timeout: 15000 });
    await api(null, "GET", "/api/health");
    teacher = await actor("profesor1", "demo1234");
    await api(null, "POST", "/api/auth/register", { username, password, display_name: displayName,
      education_level: "colegio", role: "student" });
    student = await actor(username, password);
    group = await api(teacher, "POST", "/api/teacher/groups", { course_id: course, group_name: `QA ${stamp}` });
    const invitation = await api(teacher, "POST", `/api/teacher/groups/${group.group_id}/invitations`, { count: 1 });
    await api(student, "POST", "/api/student/enroll-by-code", { invite_code: invitation.tokens[0] });
    await flow("lesson", lessonFlow);
    await flow("exam", examFlow);
    await flow("procedure", procedureFlow);
    await flow("league", leagueFlow);
  } catch (e) {
    report.push({ name: "setup", findings: [{ check: "flow-setup", detail: e.message.slice(0, 500) }] });
    for (const flow of ["lesson", "exam", "procedure", "league"]) {
      if (!results.some((r) => r.flow === flow)) results.push({ flow, status: "blocked", reason: "setup failed" });
    }
    console.error(`setup: ${e.message}`);
  } finally {
    for (const dispose of [...actors.map((a) => () => a.context.close()),
      ...(request ? [() => request.dispose()] : []), ...(browser ? [() => browser.close()] : [])]) {
      try { await dispose(); }
      catch (e) { report.push({ name: "cleanup", findings: [{ check: "flow-error", detail: e.message.slice(0, 300) }] }); }
    }
    writeReport(cfg.out, `Flow sweep — ${cfg.width}px, es-CO`, report);
    const jsonPath = path.join(cfg.out, "report.json");
    const json = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
    json.flows = results;
    fs.writeFileSync(jsonPath, JSON.stringify(json, null, 2));
    fs.appendFileSync(path.join(cfg.out, "report.md"), `\n## Flow outcomes\n\n| Flow | Outcome | Findings |\n|---|---|---|\n${results.map((r) => `| ${r.flow} | ${r.status} | ${r.findings ?? r.reason} |`).join("\n")}\n`);
    console.log(JSON.stringify(results));
    process.exitCode = results.some((r) => r.status === "blocked") ? 2
      : results.some((r) => r.status !== "completed") || report.some((r) => r.findings.length) ? 1 : 0;
  }
}

if (require.main === module) main().catch((e) => { console.error(e.message); process.exitCode = 2; });
module.exports = { localURL };
