# Prompt for Claude Code — Implementing Level 2 "Operaciones básicas" (*Basic operations*) (LevelUpElo)

> Paste this prompt into Claude Code with the 7 `F2_nodo_*.md` files in the repo's `docs/specs/nivel-2/`.
>
> **Defaults (confirm and adjust if your stack differs):**
> - **Specs path:** `docs/specs/nivel-2/`
> - **Assumed stack:** React + TypeScript (`.tsx` components, KaTeX for formulas, Framer Motion for animations).
> - **Commands:** `npm run lint` · `npm run typecheck` (or `npx tsc --noEmit`) · `npm test`. If you use pnpm/yarn, replace `npm run`/`npm` with `pnpm`/`yarn`.
>
> Student-facing content stays in Spanish (es-CO). Quoted Spanish text is literal copy from the specs, with an English gloss in italics.

---

## Role and goal

Implement **Level 2 — Basic operations** (Pre-algebra module) of LevelUpElo in this repository: a **3D city (hub)** with **6 buildings**, one per operation. You work from 7 node specifications. Since the level may not exist yet or may exist partially, **audit first** whatever is there and reconcile; do not duplicate or blindly overwrite.

## Important notice about where the content comes from

Unlike Level 1 (whose material arrived mature), Level 2 was developed from an **early draft**. In each spec, the content is tagged:
- **verbatim** = text that came in the draft (Katia's dialogue, situations, formalizations). Respect it exactly.
- **[NUEVO]** (*new*) = authoring added to reach formative quality (differentiated feedback, definition + base examples, storyboards, differentiation by band, accessibility, JSON). **Implement the [NUEVO] content as it is, but leave a marker/annotation** (e.g. a comment or content flag) so the pedagogy team can validate it before publishing. Do not treat it as firmly approved content.

## Product context

- Gamified math platform, 8th grade, Colombia. **es-CO** format (decimal comma, thousands dot). Guide mascot: **Katia**. Situation characters per building: Felipe, Manuel, Andrea, Pablo, Juan.
- Three proficiency bands: **Básico, Intermedio, Avanzado** (*Basic, Intermediate, Advanced*) (`level_presentation` field in each spec).
- Each spec has **PARTE A** (*Part A*: readable script; A2 is the source of truth for visible text) and **PARTE B** (*Part B*: JSON — source of truth for the data model, interactions, events, alerts, per-band presentation and handoff).

## File → node_id map (route order)

| Order | Spec file | node_id | Type |
|---|---|---|---|
| E00 | `F2_nodo_ciudad_hub.md` | `PREALG-N2-E00-CIUDAD` | 3D hub (gating: open 6 signs) |
| E01 | `F2_nodo_suma.md` | `PREALG-N2-E01-SUMA-JUNTAR` | Building — manipulative (basket) |
| E02 | `F2_nodo_resta.md` | `PREALG-N2-E02-RESTA-QUITAR` | Building — situations |
| E03 | `F2_nodo_multiplicacion.md` | `PREALG-N2-E03-MULTIPLICACION-AGRUPAR` | Building — progressive construction |
| E04 | `F2_nodo_division.md` | `PREALG-N2-E04-DIVISION-REPARTIR` | Building — manipulative (pizza) |
| E05 | `F2_nodo_potenciacion.md` | `PREALG-N2-E05-POTENCIACION-CRECER` | Building — growth table |
| E06 | `F2_nodo_radicacion.md` | `PREALG-N2-E06-RADICACION-RAIZ` | Building — geometric (closes the level) |

## PHASE 1 — Audit and reconciliation (do NOT write code yet)

1. Read the 7 specs in full.
2. Scan the repo: do any Level 2 structure, the hub, any building, routes, events or `prealgebra.n2.*` i18n already exist?
3. Classify each node: **EXISTS-MATCHES / EXISTS-NEEDS-CHANGES / MISSING**. (Most will probably be MISSING, but check for scaffolding and reusable shared components from Level 1.)
4. Deliver a **reconciliation table** + a **per-node plan** and **stop for confirmation** before coding.
5. On a structural conflict (a `node_id`, an `unlock_rule`, a route, an event already consumed by analytics), **flag it and ask**; do not change it silently.

## PHASE 2 — Implementation (after approval, in route order E00 → E06)

For each node:

- **Hub E00:** 3D city with 6 buildings; each building unfolds a sign (a real-world problem). **Gating:** opening the 6 signs unlocks entry to the buildings (no penalty). Reuse an existing 3D scene or provide an accessible 2D alternative.
- **Data:** materialize PARTE B (interactions, `expected`/`answer`, per-case `feedback`, `misconception_tags`, `level_presentation`). Keep the `node_id` and wiring; update in place.
- **Definition + base examples (required pattern):** each building shows, **before** practice, a screen with the **definition of the operation** and **1–2 worked examples** (`definition_and_worked_examples` block in the JSON; `definition_and_examples_viewed` event). It goes before the situations/manipulation; the **formalization with properties** goes at the end as consolidation.
- **UI / text:** use the A2 script **verbatim** for visible text; respect the [NUEVO] tagging. Reuse shared components (Katia dialogue, feedback modal, numeric field, drag-and-drop, number line, etc.).
- **Mechanics per building:** Addition = drag fruit into a basket with a counter; Subtraction = situations with a numeric field + number line (includes debt/negatives); Multiplication = situations with Katia interventions (repeated addition → commutativity → bridge to division); Division = drag pizza slices onto plates, with remainder and inverses; Exponentiation = fill in a growth table by the hour + curve; Roots = geometric situations (area/volume) with exact and non-exact roots.
- **Events and persistence:** record `events_to_register`; respect `persistence_required`/`persistence_excluded`. **Never persist `elo_score`** (these nodes do not affect ELO).
- **Differentiation:** implement `level_presentation` (Básico/Intermedio/Avanzado).
- **Accessibility:** KaTeX with MathML/`aria-label`; drag-and-drop with a tap-to-place and keyboard alternative; states that do not depend on color alone (✓/⚠ icons); contrast ≥ 4.5:1 in light and dark mode.
- **i18n:** strings in es-CO resources with the spec's `i18n_prefix` (`prealgebra.n2.e00` … `e06`).
- **Tests:** evaluation logic, feedback routing by error, hub gating, differentiation by band, and the remainder/inverse in division.

## Corrections ALREADY applied in the specs (do not reintroduce them from the original PDF)

If you compare with the original draft/PDF, **these corrections are already in the specs and must be kept**:
- **Hub:** the draft's internal title "Nivel 1" (*Level 1*) → **Nivel 2**.
- **Subtraction:** Texto 1 said "edificio de la suma" (*addition building*) → **resta** (*subtraction*).
- **Exponentiation:** "crecimiento lineal/lineal exponencial" (*linear/linear exponential growth*) → **exponencial** (*exponential*); the character "pablo/repartición" (*pablo/sharing*) → **Juan/crecimiento** (*Juan/growth*); explicit modeling **population(hour n) = base^(n+1)** (you start from "base" individuals that multiply by "base" every hour). *(If you prefer pure powers, population = baseⁿ, the statement would have to be reworded to "starts with 1"; pedagogical decision pending — respect what the spec says unless told otherwise.)*
- **Roots:** area 16 m² → side **4 m** (not 4 cm); **es-CO** "√20 ≈ 4,4721" (comma); Texto 1 completed to "último edificio" (*last building*).
- **es-CO** across the whole level (decimal comma).

## Invariants that must NOT break

- **es-CO notation** (decimal comma, thousands dot).
- **All nodes are formative:** `safe_zone = true`, `affects_elo = false`, `skip_penalty = false`. Do not connect them to ELO.
- **Definition + base examples before practice** (required pattern, see above).
- **Three-level alerts:** `observation → reinforcement_suggested → teacher_intervention` (the last one requires persistence / ≥3 occurrences). Configurable design hypotheses, not calibrated thresholds.
- **KaTeX rendering required:** respect every `render_blocker`. **High risk in E05 (superscripts/exponents) and E06 (radical indices/radicands)** — verify them explicitly; do not leave exponents or radicals empty.
- **Growth-oriented language** in feedback; nothing punitive.
- **Minors' data (Law 1581 / data minimization):** do not persist the student's raw free text as conditioning data.
- **No complex-number gating** (does not apply at this level). Roots link to Level 1's Irrationals/Reals (non-exact roots), but do not introduce optional branches.

## Expected output of this session

1. Reconciliation table (exists-matches / needs-changes / missing) + diffs.
2. Per-node plan in order E00 → E06.
3. After approval: node-by-node implementation, with a summary of what was created vs. updated, and **[NUEVO]** content markers pending pedagogical validation.
4. Lint/typecheck/tests green: `npm run lint`, `npm run typecheck` (or `npx tsc --noEmit`) and `npm test` (adjust to the repo's package manager if it is not npm).
5. List of conflicts or pending decisions (including the one about modeling exponentiation, if applicable).

**Do not assume everything is new without auditing, do not reintroduce the errors already fixed, and respect the definition→practice→consolidation pattern in every building.**
