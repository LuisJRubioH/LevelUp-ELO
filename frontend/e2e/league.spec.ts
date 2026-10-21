import { test, expect } from "./fixtures";
import type { Page, WebSocketRoute } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * The league screen tells the student what happened: an answer is coloured with its own result,
 * a +0 says why, a closed connection says why, and the history shows whole rating changes.
 * The PvP server is simulated on the page's WebSocket.
 */

const ITEMS = [
  { id: "i1", content: "¿Cuánto es $2+2$?", options: ["3", "4"], topic: "Suma", difficulty: 900 },
  { id: "i2", content: "¿Cuánto es $3+3$?", options: ["4", "6"], topic: "Suma", difficulty: 900 },
];
const KEY: Record<string, string> = { i1: "4", i2: "6" };

type Server = (ws: WebSocketRoute, message: Record<string, unknown>) => void;
type Row = { match_id: number };

async function openLeague(page: Page, server: Server, history: object[] = []) {
  await mockStudentApi(page);
  // Spec 007 FR-060: one page of five; `before` asks for the next one.
  await page.route("**/api/student/pvp/history**", (route) => {
    const before = Number(new URL(route.request().url()).searchParams.get("before") ?? 0);
    const rest = before ? history.slice(history.findIndex((r) => (r as Row).match_id === before) + 1) : history;
    return route.fulfill({ status: 200, json: { matches: rest.slice(0, 5), has_more: rest.length > 5 } });
  });
  await page.routeWebSocket("**/api/ws/pvp/**", (ws) => {
    ws.onMessage((raw) => server(ws, JSON.parse(String(raw))));
  });
  await injectAuth(page);
  await page.goto("/student/league");
}

async function startMatch(page: Page) {
  await page.locator("select.pv-select").selectOption("calculo");
  await page.getByRole("button", { name: "Buscar rival →" }).click();
}

/** A finished match in the history (spec 007 FR-060 shape). */
const ROW = {
  status: "finished",
  reason: null,
  course_id: "calculo",
  course_name: "Cálculo",
  won: true,
  draw: false,
  my_score: 6,
  opp_score: 4,
  opponent: "rival",
  finished_at: "2026-10-10 12:00",
};

const START = {
  type: "game_start",
  match_id: 7,
  items: ITEMS,
  opponent: { name: "rival", elo: 1010 },
  duration_seconds: 180,
};

/** A match where every answer is judged against KEY; `end`, if any, closes it after the last
 * answer. */
function match(end: object | null): Server {
  let answered = 0;
  return (ws, msg) => {
    if ("token" in msg) {
      ws.send(JSON.stringify(START));
      return;
    }
    const correct = msg.selected === KEY[msg.item_id as string];
    answered += 1;
    setTimeout(() => {
      ws.send(
        JSON.stringify({
          type: "answer_result",
          item_id: msg.item_id,
          is_correct: correct,
          your_score: correct ? 1 : 0,
          opp_score: 0,
        }),
      );
      if (end && answered === ITEMS.length) ws.send(JSON.stringify({ type: "game_end", ...end }));
    }, 150);
  };
}

const option = (page: Page, text: string) =>
  page.locator(".dx-opt").filter({ has: page.getByText(text, { exact: true }) });

test.describe("Liga PvP", () => {
  test("la respuesta se colorea con su propio resultado", async ({ page }) => {
    await openLeague(page, match(null));
    await startMatch(page);

    // Both items offer a "4": read the question and the colour at the same moment.
    const judged = () =>
      page.evaluate(() => {
        const prompt = document.querySelector(".dx-prompt")?.textContent ?? "";
        const opt = [...document.querySelectorAll(".dx-opt")].find((b) => /\b(ok|bad)\b/.test(b.className));
        if (!opt) return "none";
        return `${prompt.includes("2+2") ? "i1" : "i2"}:${opt.className.includes("ok") ? "ok" : "bad"}`;
      });

    await option(page, "4").click();
    await expect(option(page, "4")).toHaveClass(/\bon\b/); // chosen, not judged yet
    await expect.poll(judged).toBe("i1:ok");

    await expect(page.locator(".dx-prompt")).toContainText("3+3");
    await option(page, "4").click();
    await expect.poll(judged).toBe("i2:bad");
  });

  test("un ELO sin cambio dice por qué", async ({ page }) => {
    await openLeague(
      page,
      match({ your_score: 2, opp_score: 0, won: true, draw: false, elo_delta: 0, elo_delta_display: 0, elo_reason: "no_rated_topics" }),
    );
    await startMatch(page);
    await option(page, "4").click();
    await expect(page.getByText("¿Cuánto es")).toContainText("3+3");
    await option(page, "6").click();

    await expect(page.getByText("¡Ganaste!")).toBeVisible();
    await expect(page.getByText("aún no tienes nota en esta materia")).toBeVisible();
  });

  test("si el servidor cierra la conexión, se dice el motivo", async ({ page }) => {
    await openLeague(page, (ws, msg) => {
      if ("token" in msg) ws.close({ code: 4404, reason: "No items" });
    });
    await startMatch(page);

    await expect(page.getByRole("alert")).toContainText("todavía no tiene preguntas");
    await expect(page.getByRole("button", { name: "Buscar rival →" })).toBeVisible();
  });

  test("una segunda pestaña dice por qué (spec 007 US5-AS1)", async ({ page }) => {
    await openLeague(page, (ws, msg) => {
      if ("token" in msg) ws.close({ code: 4409, reason: "Second tab" });
    });
    await startMatch(page);

    await expect(page.getByRole("alert")).toContainText("Ya tienes la Liga abierta en otra pestaña");
    await expect(page.getByRole("button", { name: "Buscar rival →" })).toBeVisible();
  });

  test("demasiados mensajes cierran la conexión con su motivo (spec 007 US5-AS2)", async ({ page }) => {
    await openLeague(page, (ws, msg) => {
      if ("token" in msg) ws.close({ code: 4429, reason: "Too many messages" });
    });
    await startMatch(page);

    await expect(page.getByRole("alert")).toContainText("Demasiados mensajes");
  });

  test("el historial muestra el número del servidor, sin redondear en el navegador", async ({ page }) => {
    // Survey 007 V14: -2.5 shows as -3 (half up on the value, as the server rounds it), where
    // Math.round in the browser gave -2.
    await openLeague(page, () => {}, [
      { ...ROW, match_id: 3, elo_delta: 11.52, elo_delta_display: 12 },
      { ...ROW, match_id: 2, won: false, elo_delta: -2.5, elo_delta_display: -3 },
      { ...ROW, match_id: 1, elo_delta: null, elo_delta_display: null },
    ]);

    const deltas = page.locator(".pv-hdelta");
    await expect(deltas).toHaveText(["+12", "-3", "—"]);
  });

  test("el historial muestra partidas abandonadas y no guardadas con su materia (spec 007 US6-AS1)", async ({ page }) => {
    await openLeague(page, () => {}, [
      { ...ROW, match_id: 3, elo_delta: 8, elo_delta_display: 8 },
      { ...ROW, match_id: 2, status: "abandoned", reason: "not_saved", elo_delta: 0, elo_delta_display: 0 },
      { ...ROW, match_id: 1, status: "abandoned", reason: "orphaned", course_name: "Álgebra", elo_delta: 0, elo_delta_display: 0 },
    ]);

    const rows = page.locator(".pv-hrow");
    await expect(rows).toHaveCount(3);
    await expect(rows.nth(0)).toContainText("Cálculo");
    await expect(rows.nth(1)).toContainText("Abandonada");
    await expect(rows.nth(1)).toContainText("no se pudo guardar el resultado");
    await expect(rows.nth(1).locator(".pv-hdelta")).toHaveText("—");
    await expect(rows.nth(2)).toContainText("Álgebra · se cerró sin terminar");
  });

  test("ver más carga la página siguiente del historial (spec 007 FR-060)", async ({ page }) => {
    const seven = [7, 6, 5, 4, 3, 2, 1].map((id) => ({ ...ROW, match_id: id, opponent: `rival ${id}`, elo_delta: 1, elo_delta_display: 1 }));
    await openLeague(page, () => {}, seven);

    await expect(page.locator(".pv-hrow")).toHaveCount(5);
    await page.getByRole("button", { name: "Ver más" }).click();

    await expect(page.locator(".pv-hrow")).toHaveCount(7);
    await expect(page.locator(".pv-hrow").last()).toContainText("rival 1");
    await expect(page.getByRole("button", { name: "Ver más" })).toHaveCount(0);
  });
});
