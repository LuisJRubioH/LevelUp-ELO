/**
 * Spec 001, delivery INV (User Story 10; FR-028p, FR-028r, FR-028t): single-use invitations on
 * the teacher's Groups screen and on the student's access-code tab. The API is mocked: these
 * check what the screens send and show, not the backend.
 */
import type { Page } from "@playwright/test";
import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi, MOCK_TEACHER } from "./helpers/auth";

interface Invitation {
  id: number;
  token: string;
  status: "unused" | "used" | "expired" | "revoked";
  created_at: string;
  expires_at: string;
  used_at: string | null;
  used_by_name: string | null;
}

const row = (over: Partial<Invitation> & Pick<Invitation, "id" | "token" | "status">) => ({
  created_at: "2026-10-01 14:00:00",
  expires_at: "2026-10-31 14:00:00",
  used_at: null,
  used_by_name: null,
  ...over,
});

async function teacherGroups(page: Page, invitations: Invitation[]) {
  const posted: unknown[] = [];
  const revoked: string[] = [];
  // Every teacher call answers empty unless routed again below (later routes win).
  await page.route("**/api/teacher/**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
  );
  await page.route("**/api/teacher/dashboard", (route) =>
    route.fulfill({ status: 200, json: { students: [], groups: [] } }),
  );
  await page.route("**/api/student/exam/pending", (route) => route.fulfill({ json: [] }));
  await page.route("**/api/teacher/groups", (route) =>
    route.fulfill({
      json: [{ group_id: 7, name: "10A", course_id: "algebra_basica", student_count: 1 }],
    }),
  );
  await page.route("**/api/teacher/groups/7/invitations", async (route) => {
    if (route.request().method() === "POST") {
      posted.push(route.request().postDataJSON());
      const fresh = [
        row({ id: 11, token: "K7M2P-QX9RT", status: "unused", created_at: "2026-10-15 13:00:00", expires_at: "2026-11-14 13:00:00" }),
        row({ id: 12, token: "HN4WD-8ZC3F", status: "unused", created_at: "2026-10-15 13:00:00", expires_at: "2026-11-14 13:00:00" }),
      ];
      invitations.unshift(...fresh);
      await route.fulfill({
        status: 201,
        json: { tokens: fresh.map((i) => i.token), ttl_days: 30 },
      });
      return;
    }
    await route.fulfill({ json: { ttl_days: 30, invitations } });
  });
  await page.route("**/api/teacher/invitations/*", async (route) => {
    const id = Number(new URL(route.request().url()).pathname.split("/").pop());
    revoked.push(`${route.request().method()} ${id}`);
    const target = invitations.find((i) => i.id === id);
    if (target) target.status = "revoked";
    await route.fulfill({ status: 204, body: "" });
  });
  await injectAuth(page, MOCK_TEACHER);
  await page.goto("/teacher/groups");
  await page.getByRole("heading", { name: "10A" }).click();
  return { posted, revoked };
}

test.describe("Invitaciones de un solo uso (spec 001 INV)", () => {
  test("El docente genera invitaciones, ve sus estados, copia y anula (US10-AS1, FR-028t)", async ({
    page,
    context,
  }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    const invitations: Invitation[] = [
      row({ id: 3, token: "ABCDE-FGHJK", status: "used", used_at: "2026-10-02 09:00:00", used_by_name: "Ana Pérez" }),
      row({ id: 2, token: "MNPQR-STUVW", status: "expired" }),
      row({ id: 1, token: "XYZ23-45678", status: "revoked" }),
    ];
    const { posted, revoked } = await teacherGroups(page, invitations);

    const panel = page.getByRole("region", { name: "Invitaciones" });
    await expect(
      panel.getByText("Cada código sirve para un solo estudiante y vence a los 30 días si nadie lo usa."),
    ).toBeVisible();
    const item = (token: string) => panel.getByRole("listitem").filter({ hasText: token });
    await expect(item("ABCDE-FGHJK")).toContainText("Usada por Ana Pérez");
    await expect(item("MNPQR-STUVW")).toContainText("Vencida");
    await expect(item("XYZ23-45678")).toContainText("Anulada");
    for (const token of ["ABCDE-FGHJK", "MNPQR-STUVW", "XYZ23-45678"]) {
      await expect(item(token).getByRole("button")).toHaveCount(0);
    }

    await panel.getByLabel("Cantidad de invitaciones").fill("2");
    await panel.getByRole("button", { name: "Generar invitaciones" }).click();

    await expect(item("K7M2P-QX9RT")).toContainText("Sin usar · vence 14/11/2026");
    await expect(item("HN4WD-8ZC3F")).toContainText("Sin usar · vence 14/11/2026");
    expect(posted).toEqual([{ count: 2 }]);

    await item("K7M2P-QX9RT").getByRole("button", { name: "Copiar" }).click();
    await expect(item("K7M2P-QX9RT").getByRole("button", { name: "✓ Copiado" })).toBeVisible();
    expect(await page.evaluate(() => navigator.clipboard.readText())).toBe("K7M2P-QX9RT");

    await item("K7M2P-QX9RT").getByRole("button", { name: "Anular" }).click();
    await expect(item("K7M2P-QX9RT")).toContainText("Anulada");
    await expect(item("K7M2P-QX9RT").getByRole("button")).toHaveCount(0);
    await expect(item("HN4WD-8ZC3F").getByRole("button", { name: "Anular" })).toBeVisible();
    expect(revoked).toEqual(["DELETE 11"]);
  });

  test("El estudiante usa un código con o sin guion; uno ya usado muestra el aviso (US10-AS2, US10-AS3)", async ({
    page,
  }) => {
    const sent: string[] = [];
    await mockStudentApi(page);
    await page.route("**/api/student/enroll-by-code", async (route) => {
      const code = (route.request().postDataJSON() as { invite_code: string }).invite_code;
      sent.push(code);
      if (sent.length === 1) {
        await route.fulfill({
          status: 201,
          json: { message: "Acceso especial activado correctamente.", course_id: "algebra_basica" },
        });
        return;
      }
      await route.fulfill({
        status: 409,
        json: { detail: "Este código ya fue usado. Pide uno nuevo a tu docente." },
      });
    });
    await injectAuth(page);
    await page.goto("/student/courses");
    await page.getByRole("button", { name: "Código de acceso" }).click();

    const input = page.getByPlaceholder("Ej: K7M2P-QX9RT");
    await input.fill("k7m2pqx9rt");
    await page.getByRole("button", { name: "Acceder" }).click();
    await expect(page.getByText("Acceso especial activado para algebra_basica")).toBeVisible();

    await input.fill("K7M2P-QX9RT");
    await page.getByRole("button", { name: "Acceder" }).click();
    await expect(page.getByText("Este código ya fue usado. Pide uno nuevo a tu docente.")).toBeVisible();
    expect(sent).toEqual(["K7M2PQX9RT", "K7M2P-QX9RT"]);
  });
});
