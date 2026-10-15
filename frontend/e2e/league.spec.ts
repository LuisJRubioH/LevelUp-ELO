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

async function openLeague(page: Page, server: Server, history: object[] = []) {
  await mockStudentApi(page);
  await page.route("**/api/student/pvp/history", (route) =>
    route.fulfill({ status: 200, json: history }),
  );
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
      match({ your_score: 2, opp_score: 0, won: true, draw: false, elo_delta: 0, elo_reason: "no_rated_topics" }),
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

  test("el historial muestra cambios enteros y uno sin aplicar", async ({ page }) => {
    const row = { won: true, draw: false, my_score: 6, opp_score: 4, opponent: "rival", finished_at: "2026-10-10 12:00" };
    await openLeague(page, () => {}, [
      { ...row, elo_delta: 11.52 },
      { ...row, elo_delta: null },
    ]);

    const deltas = page.locator(".pv-hdelta");
    await expect(deltas).toHaveText(["+12", "—"]);
  });
});
