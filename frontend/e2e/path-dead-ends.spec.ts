import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Places where a student walking the learning path got stuck without knowing why:
 * - B13 closes pre-algebra level 1 (N2 opens only once it is completed). Its footer had two
 *   buttons both reading "Volver al mapa"; only one completes the level.
 * - A hub's cards each offered "Zarpar" once opened, but destinations open in order (V2-R14) and
 *   the hub itself locks them until it is finished: most led to a 403.
 * - That 403 read "No pudimos cargar esta lección", which looks like a failure, with no way back.
 */
const COURSE = "algebra_basica";

function lesson(node_id: string, node_type: string, content?: Record<string, unknown>) {
  return {
    node_id,
    node_type,
    course_id: COURSE,
    i18n_prefix: "",
    next_node_id: null,
    state: "current",
    presentation: "basico",
    explored_complex_branch: false,
    affects_elo: false,
    is_safe_zone: true,
    optional_branch: false,
    objectives: [],
    optional_objectives: [],
    unlock_after: null,
    interactions: [],
    progress: {
      state: "current",
      objectives_viewed: false,
      math_convention_viewed: false,
      viewed_at: null,
      completed_at: null,
      responses: {},
    },
    ...(content ? { content } : {}),
  };
}

async function mockLesson(page: Page, data: ReturnType<typeof lesson>, events: string[] = []) {
  await page.route(`**/api/student/lessons/${COURSE}/${data.node_id}`, (route) => route.fulfill({ json: data }));
  await page.route(`**/api/student/lessons/${COURSE}/${data.node_id}/events`, async (route) => {
    const { event } = route.request().postDataJSON();
    events.push(event);
    await route.fulfill({ json: { ...data, state: event === "node_completed" ? "completed" : data.state } });
  });
}

test.describe("Ruta de aprendizaje — callejones sin salida", () => {
  test.beforeEach(async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
  });

  test("cierre del nivel 1: el botón que termina el nivel no se llama igual que el que sale", async ({ page }) => {
    const events: string[] = [];
    await mockLesson(page, lesson("PREALG-N1-B13-CIERRE-DIAGNOSTICO", "diagnostic_summary"), events);
    await page.route(`**/api/student/prealgebra-summary/${COURSE}`, (route) =>
      route.fulfill({
        json: { course_id: COURSE, completed_nodes: 8, total_nodes: 8, overall_status: "strong", review: [] },
      }),
    );
    await page.goto(`/student/course/${COURSE}/lesson/PREALG-N1-B13-CIERRE-DIAGNOSTICO`);

    const footer = page.locator(".lesson-footer-actions");
    await expect(footer.getByRole("button")).toHaveCount(2);
    const names = await footer.getByRole("button").allInnerTexts();
    expect(new Set(names.map((n) => n.trim())).size).toBe(2);

    await footer.getByRole("button", { name: "Terminar el nivel 1" }).click();
    await expect(page).toHaveURL(`/student/course/${COURSE}/map`);
    expect(events).toContain("node_completed");
  });

  test("hub: con todas las tarjetas abiertas, «Zarpar» solo aparece donde el mapa deja entrar", async ({ page }) => {
    const hub = lesson("HUB-PRUEBA", "level_hub_cards", {
      kind: "level_hub_cards",
      title: "El puerto de prueba",
      cards: [
        { id: "uno", destination: "Corinto", symbol: "1", teaser: "Primera ruta.", node_id: "DEST-UNO" },
        { id: "dos", destination: "Rodas", symbol: "2", teaser: "Segunda ruta.", node_id: "DEST-DOS" },
      ],
      card_cta: "Zarpar",
    });
    await mockLesson(page, hub);
    await page.route(`**/api/student/lessons/${COURSE}/HUB-PRUEBA/interactions`, async (route) => {
      const { interaction_id } = route.request().postDataJSON();
      await route.fulfill({
        json: { interaction_id, selected_option: "opened", is_expected: true, misconception_tag: null, feedback_key: "ok" },
      });
    });
    await page.route(`**/api/student/map/${COURSE}`, (route) =>
      route.fulfill({
        json: {
          course_id: COURSE,
          course_name: "Álgebra",
          diagnostic_done: true,
          nodes: [
            ["HUB-PRUEBA", "level_hub_cards", "current", "El puerto de prueba"],
            ["DEST-UNO", "concept", "available", "Corinto"],
            ["DEST-DOS", "concept", "blocked", "Rodas"],
          ].map(([node_id, node_type, state, label]) => ({
            node_id, node_type, state, label, topic: label, elo: null, rd: null, item_count: 0,
          })),
        },
      }),
    );
    await page.goto(`/student/course/${COURSE}/lesson/HUB-PRUEBA`);

    for (const name of ["Explorar Corinto", "Explorar Rodas"]) await page.getByRole("button", { name }).click();
    await expect(page.getByText("Primera ruta.")).toBeVisible();
    await expect(page.getByText("Segunda ruta.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Zarpar" })).toHaveCount(1);
    await expect(page.locator(".n4-card", { hasText: "Corinto" }).getByRole("button", { name: "Zarpar" })).toBeVisible();
  });

  test("una lección bloqueada lo dice y deja volver al mapa", async ({ page }) => {
    await page.route(`**/api/student/lessons/${COURSE}/DEST-DOS`, (route) =>
      route.fulfill({ status: 403, json: { detail: "Completa el nodo anterior primero" } }),
    );
    await page.goto(`/student/course/${COURSE}/lesson/DEST-DOS`);

    await expect(page.getByText(/todavía está bloqueada/)).toBeVisible();
    await expect(page.getByText("No pudimos cargar esta lección.")).toBeHidden();
    await page.getByRole("button", { name: "Volver al mapa" }).click();
    await expect(page).toHaveURL(`/student/course/${COURSE}/map`);
  });
});
