import { test, expect } from "./fixtures";
import type { Page, WebSocketRoute } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * The league screen tells the student what happened: an answer is coloured with its own result,
 * a +0 says why, a closed connection says why, and the history shows whole rating changes.
 * The PvP server is simulated on the page's WebSocket.
 */

const ITEMS = [
  // Spec 007 FR-032: an item reaches the browser without its difficulty.
  { id: "i1", content: "¿Cuánto es $2+2$?", options: ["3", "4"], topic: "Suma" },
  { id: "i2", content: "¿Cuánto es $3+3$?", options: ["4", "6"], topic: "Suma" },
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

/** Spec 007 F: the server's clock, the speed tiebreak and the grace (US4). */
test.describe("Liga PvP — la partida la decide el servidor (spec 007 F)", () => {
  /** A `game_start` that ends `seconds` after the server's `now`. */
  const startAt = (now: number, seconds = 180, extra: object = {}) => ({
    ...START,
    resume: "r1",
    server_now: new Date(now).toISOString(),
    ends_at: new Date(now + seconds * 1000).toISOString(),
    ...extra,
  });

  test("la cuenta atrás sigue la hora del servidor aunque la pestaña duerma (spec 007 US4-AS1)", async ({ page }) => {
    // The page's clock is not the server's: the countdown corrects it with `server_now`.
    await page.clock.install({ time: new Date("2026-10-21T15:00:00Z") });
    await openLeague(page, (ws, msg) => {
      if ("token" in msg) ws.send(JSON.stringify(startAt(Date.now())));
    });
    await startMatch(page);
    const timer = page.locator(".pv-timer");
    await expect(timer).toHaveText(/⏱ (3:00|2:5\d)/);

    // The tab sleeps for a minute: no timer fires meanwhile; the next tick reads the end time.
    const now = await page.evaluate(() => Date.now());
    await page.clock.setSystemTime(now + 61_000);
    await expect(timer).toHaveText(/⏱ 1:5\d/);
  });

  test("un empate se decide por velocidad (spec 007 US4-AS2)", async ({ page }) => {
    await openLeague(page, (ws, msg) => {
      if ("token" in msg) {
        ws.send(JSON.stringify(startAt(Date.now())));
        ws.send(
          JSON.stringify({
            type: "game_end", your_score: 4, opp_score: 4, won: true, draw: false, tiebreak: true,
            forfeit: false, elo_delta: 12, elo_delta_display: 12, elo_reason: null,
          }),
        );
      }
    });
    await startMatch(page);

    await expect(page.getByText("¡Ganaste!")).toBeVisible();
    await expect(page.getByText("Ganaste por velocidad")).toBeVisible();
  });

  test("una caída reconecta y retoma la partida (spec 007 US4-AS3)", async ({ page }) => {
    const resumes: unknown[] = [];
    let connections = 0;
    await openLeague(page, (ws, msg) => {
      if ("token" in msg) {
        connections += 1;
        if (connections === 1) {
          ws.send(JSON.stringify(startAt(Date.now())));
          return;
        }
        resumes.push(msg.resume);
        setTimeout(() => {
          ws.send(
            JSON.stringify({
              type: "game_resume", match_id: 7, items: ITEMS, answered: ["i1"], your_score: 1,
              opp_score: 0, opponent: { name: "rival", elo: 1010 }, resume: "r1",
              server_now: new Date().toISOString(),
              ends_at: new Date(Date.now() + 150_000).toISOString(),
            }),
          );
        }, 600);
        return;
      }
      // The first answer is judged, then the connection drops (not a 4xxx close).
      ws.send(
        JSON.stringify({ type: "answer_result", item_id: msg.item_id, is_correct: true, your_score: 1, opp_score: 0 }),
      );
      setTimeout(() => ws.close({ code: 1011, reason: "network" }), 900);
    });
    await startMatch(page);
    await option(page, "4").click();

    await expect(page.getByText("Reconectando")).toBeVisible();
    await expect(page.locator(".dx-prompt")).toContainText("3+3");
    expect(resumes).toEqual(["r1"]);
    await expect(page.locator(".pv-scorepill .me")).toHaveText("1");
    await expect(page.locator(".pv-timer")).toHaveText(/⏱ 2:(2|3)\d/);
  });

  test("el rival abandona y ganas al instante (spec 007 US4-AS3)", async ({ page }) => {
    await openLeague(page, (ws, msg) => {
      if (!("token" in msg)) return;
      ws.send(JSON.stringify(startAt(Date.now())));
      ws.send(JSON.stringify({ type: "opponent_away", grace_seconds: 20 }));
      setTimeout(() => {
        ws.send(
          JSON.stringify({
            type: "game_end", your_score: 1, opp_score: 3, won: true, draw: false, tiebreak: false,
            forfeit: true, elo_delta: 12, elo_delta_display: 12, elo_reason: "forfeit",
          }),
        );
      }, 1200);
    });
    await startMatch(page);

    await expect(page.getByText("Tu rival se desconectó")).toBeVisible();
    await expect(page.getByText("¡Ganaste!")).toBeVisible();
    await expect(page.getByText("Tu rival abandonó la partida")).toBeVisible();
  });

  test("volver tarde dice que la partida terminó (spec 007 US4-AS3)", async ({ page }) => {
    let connections = 0;
    await openLeague(page, (ws, msg) => {
      if (!("token" in msg)) return;
      connections += 1;
      if (connections === 1) {
        ws.send(JSON.stringify(startAt(Date.now())));
        setTimeout(() => ws.close({ code: 1011, reason: "network" }), 300);
      } else {
        ws.close({ code: 4410, reason: "Match over" });
      }
    });
    await startMatch(page);

    await expect(page.getByRole("alert")).toContainText("La partida ya terminó");
    await expect(page.getByRole("button", { name: "Buscar rival →" })).toBeVisible();
  });

  test("una partida perdida por abandono lo dice en el historial (spec 007 FR-042)", async ({ page }) => {
    await openLeague(page, () => {}, [
      { ...ROW, match_id: 2, won: false, reason: "forfeit", elo_delta: -12, elo_delta_display: -12 },
    ]);

    await expect(page.locator(".pv-hrow").first()).toContainText("Perdida");
    await expect(page.locator(".pv-hrow").first()).toContainText("Cálculo · por abandono");
  });
});

/** Spec 007 M: fair matches (US3). */
test.describe("Liga PvP — partidas parejas (spec 007 M)", () => {
  test("una partida fuera del cupo diario avisa que no cuenta (spec 007 US3-AS2)", async ({ page }) => {
    await openLeague(
      page,
      (ws, msg) => {
        if (!("token" in msg)) return;
        ws.send(JSON.stringify({ ...START, rated: false, unrated_reason: "daily_cap" }));
        setTimeout(() => {
          ws.send(
            JSON.stringify({
              type: "game_end", your_score: 2, opp_score: 1, won: true, draw: false, tiebreak: false,
              forfeit: false, elo_delta: 0, elo_delta_display: 0, elo_reason: "daily_cap",
            }),
          );
        }, 1500);
      },
    );
    await startMatch(page);

    // Before the first answer, and kept in the match header.
    const notice = "Esta partida no cuenta para tu ELO: ya jugaron 3 partidas hoy";
    await expect(page.getByText(notice)).toBeVisible();
    await expect(page.locator(".dx-prompt")).toContainText("2+2");

    await expect(page.getByText("¡Ganaste!")).toBeVisible();
    await expect(page.getByText("Tu ELO no cambió: esta partida no contaba")).toBeVisible();
  });

  test("el historial dice que una partida fuera del cupo no contó (spec 007 US3-AS2)", async ({ page }) => {
    await openLeague(page, () => {}, [
      { ...ROW, match_id: 4, reason: "daily_cap", elo_delta: 0, elo_delta_display: 0 },
    ]);

    await expect(page.locator(".pv-hrow").first()).toContainText("Cálculo · sin ELO: ya habían jugado 3 hoy");
  });

  test("una partida que cuenta no muestra el aviso (spec 007 US3-AS2)", async ({ page }) => {
    await openLeague(page, (ws, msg) => {
      if ("token" in msg) ws.send(JSON.stringify({ ...START, rated: true, unrated_reason: null }));
    });
    await startMatch(page);

    await expect(page.locator(".dx-prompt")).toContainText("2+2");
    await expect(page.getByText("no cuenta para tu ELO")).toHaveCount(0);
  });

  test("el ítem de la Liga muestra su imagen (spec 007 US3-AS3)", async ({ page }) => {
    await page.route("**/items/images/**", (route) =>
      route.fulfill({
        status: 200,
        contentType: "image/png",
        body: Buffer.from(
          "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
          "base64",
        ),
      }),
    );
    await openLeague(page, (ws, msg) => {
      if (!("token" in msg)) return;
      const items = [{ ...ITEMS[0], image_url: "items/images/figura.png" }, ITEMS[1]];
      ws.send(JSON.stringify({ ...START, items }));
    });
    await startMatch(page);

    const image = page.locator(".dx-qcard img");
    await expect(image).toBeVisible();
    await expect(image).toHaveAttribute("src", /items\/images\/figura\.png$/);
  });
});

test.describe("Liga PvP — quién puede entrar (spec 007 G)", () => {
  /** The server refuses the entry with `codes[n]` on the n-th connection. */
  const refusing = (...codes: number[]): Server => {
    let n = 0;
    return (ws, msg) => {
      if ("token" in msg) ws.close({ code: codes[Math.min(n++, codes.length - 1)], reason: "refused" });
    };
  };

  test("sin diagnóstico la Liga ofrece el diagnóstico (spec 007 US2-AS1)", async ({ page }) => {
    await openLeague(page, refusing(4413));
    await startMatch(page);

    await expect(page.getByRole("alert")).toContainText("primero haz su diagnóstico");
    const go = page.getByRole("link", { name: "Hacer el diagnóstico" });
    await expect(go).toBeVisible();
    await go.click();
    await expect(page).toHaveURL(/\/student\/course\/calculo$/);
  });

  test("una partida en curso impide otra búsqueda y dice por qué (spec 007 US2-AS4)", async ({ page }) => {
    await openLeague(page, refusing(4412));
    await startMatch(page);

    await expect(page.getByRole("alert")).toContainText("Ya tienes una búsqueda o una partida en curso");
    await expect(page.getByRole("link", { name: "Hacer el diagnóstico" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Buscar rival →" })).toBeVisible();
  });

  test("sin institución la Liga dice qué falta (spec 007 FR-022)", async ({ page }) => {
    await openLeague(page, refusing(4414));
    await startMatch(page);

    await expect(page.getByRole("alert")).toContainText("Tu grupo aún no tiene institución registrada");
    await expect(page.getByRole("link", { name: "Hacer el diagnóstico" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Buscar rival →" })).toBeVisible();
  });

  test("cada rechazo muestra su motivo (spec 007 US2-AS5)", async ({ page }) => {
    await openLeague(page, refusing(4001, 4004, 4500, 4002, 4414));
    await page.locator("select.pv-select").selectOption("calculo");
    const texts: string[] = [];
    for (const expected of [
      "Tu sesión expiró",
      "No estás inscrito en esta materia",
      "Hubo un problema en el servidor",
      "La Liga es solo para estudiantes",
      "Tu grupo aún no tiene institución registrada",
    ]) {
      await page.getByRole("button", { name: "Buscar rival →" }).click();
      await expect(page.getByRole("alert")).toContainText(expected);
      texts.push((await page.getByRole("alert").textContent()) ?? "");
    }
    expect(new Set(texts).size).toBe(5);
  });
});
