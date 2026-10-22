# PROMPT — Replicate the unified format + closure ladder across the 5 remaining N2 operations

> Student-facing content stays in Spanish (es-CO). Quoted Spanish text is literal copy, with an English gloss in italics.

## Goal
The **Division (E04)** node is already the reference for the "operation extended across the number sets" pattern. Replicate that pattern for **Addition (E01), Subtraction (E02), Multiplication (E03), Exponentiation (E05) and Roots (E06)**, each with its own closure ladder and examples that walk through the sets.

## What is ALREADY built — DO NOT redo (reuse as-is)
- **Renderer**: `LevelTwoOperation` in `frontend/src/pages/Student/lessons/LevelTwoLesson.tsx`. It detects `content.story_contract.type === "unified_set_extension"` and automatically renders: `KatiaStorySlot` → `[discovery | formal definition]` → worked examples in 2 columns → trap in a wide column → closure ladder → practice → footer. Mark the trap with `trap: true` (the renderer moves it down to the wide column).
- **CSS**: `LevelTwoLesson.css` (`.n2-closure`, `.n2-closure-ladder/-row/-badge`, `.n2-examples-2col`, `.n2-example-wide`, `.n2-image-slot`, `.n2-example-latex`).
- **Types**: `frontend/src/api/student.ts` (`katia`, `discovery`, `closure`, `worked_examples` with `latex/eyebrow/title/image_slot/trap`, `situations.set_label`).
- **Component** `KatiaStorySlot` (props `question`, `formulas`).

⇒ The work is ONLY **content**: edit each operation's dict in `_N2_OPERATION_CONTENT[<NODE_ID>]` inside `src/domain/learning/prealgebra.py`, copying the EXACT shape of `N2_DIVISION_NODE_ID` as the template.

## Structure to put in each dict (same as Division)
```
story_contract = {"type": "unified_set_extension", "practice_position": "after_definition_plus_examples", "is_integrated": True}
katia          = {eyebrow, title, body, question}          # Greek opening + trigger question
discovery      = {eyebrow, title, body}                    # guided discovery
definition, definition_title, definition_katex             # formal definition (explicit LaTeX)
worked_examples = [ ...examples per set..., {trap: True, ...} ]  # N normal (2 col) + 1 trap (wide)
closure        = {title, intro, rows: [6 rows: ℕ ℤ ℚ 𝕀 ℝ ℂ]}        # ALWAYS the 6 sets
situations     = [ ...per set, set_label, typeable answer... ]
validation_status = "F2_<EXX>_unified_set_extension"
```
Each `worked_example`: `eyebrow="Ejemplo N · <Conjunto>"` (*Example N · <Set>*), `title`, `statement`, `latex` (explicit KaTeX), `steps` (complete steps), `image_slot: True` wherever there is an image.
Each `closure.row`: `{symbol, name, closed: "yes"|"no", latex, note}`.

## NON-negotiable rules
1. **KatIA is a GREEK cyborg cat.** Agora contexts: amphorae, olives, figs, drachmas, loaves, columns, disciples, Greek market. Pizza and other non-Greek contexts are **forbidden**. The opening must **not** repeat the exact exercise from the practice.
2. **Minimum differentiation in every exercise (posed or solved).** No concrete case is repeated: the opening, the discovery, each worked example and each practice item use numbers and/or contexts that are **different** from one another. No showing `12÷4` as an example and then asking for `12÷4` again in practice. Vary the Greek object (olives/figs/amphorae/drachmas/loaves) and the quantities.
3. **Explicit LaTeX that COMPILES in KaTeX** (verify 0 `.katex-error` elements in the real render). Use `\dfrac`, `\tfrac`, `\sqrt`, `\cdot`, `\div`, `\neq`, `\notin`, `\in`, `\mathbb{}`. **es-CO decimal comma** wrapped in braces: `2{,}5`. Do not use `mathFromText` (the unified renderer already passes the LaTeX straight through).
3. **Complete steps, nothing skipped.** Every example and every closure row with its justification.
4. **The ladder ALWAYS carries the 6 sets** (ℕ, ℤ, ℚ, 𝕀, ℝ, ℂ), with ℂ as "desvío opcional avanzado" (*optional advanced detour*).
5. **Recurring theme — 𝕀 (irrationals) is NOT closed under ANY arithmetic operation**: the result can always "fall" into ℚ. It is the deep trap that repeats in addition, subtraction, multiplication, exponentiation and division (it reinforces why we need ℝ = ℚ ∪ 𝕀). For roots the axis is inverted (taking roots *produces* irrationals and motivates ℂ).
6. **Practice with typeable numeric answers**: the backend validates with the regex `-?\d{1,6}(,\d{1,4})?`. Only integers or decimals with ≤4 decimal digits (`2,5`, `1,75`, `-3`). `0,333…` and non-terminating answers are **forbidden**. If a calculation gives a repeating/irrational result, choose numbers that give a finite result (e.g. `√8÷√2=2`, `9^{1/2}=3`).
7. Worked examples in **2 columns**; the **trap** in a **wide column below** (automatic with `trap: True`).

## Closure analysis per operation — USE THIS (already verified)

### E01 Addition (closed except in 𝕀)
| Set | closed | suggested latex |
|---|---|---|
| ℕ | yes | `3+5=8` |
| ℤ | yes | `-3+5=2` |
| ℚ | yes | `\dfrac{1}{2}+\dfrac{1}{3}=\dfrac{5}{6}` |
| 𝕀 | **no** | `\sqrt{2}+(-\sqrt{2})=0` (∈ ℚ) |
| ℝ | yes | `\sqrt{2}+\pi\in\mathbb{R}` |
| ℂ | yes | `(2+i)+(3+2i)=5+3i` |
Trap = 𝕀. Question: "¿Juntar dos cantidades siempre da una cantidad del mismo tipo?" (*Does joining two quantities always give a quantity of the same kind?*)

### E02 Subtraction (breaks in ℕ → motivates ℤ; and 𝕀 is not closed)
| Set | closed | latex |
|---|---|---|
| ℕ | **no** | `3-5=-2\notin\mathbb{N}` |
| ℤ | yes | `3-5=-2` |
| ℚ | yes | `\dfrac{1}{2}-\dfrac{1}{3}=\dfrac{1}{6}` |
| 𝕀 | **no** | `\sqrt{2}-\sqrt{2}=0` (∈ ℚ) |
| ℝ | yes | `\pi-\sqrt{2}\in\mathbb{R}` |
| ℂ | yes | `(3+2i)-(1+i)=2+i` |
Star example: `3-5=-2` enters ℤ (motivates B05). Trap = 𝕀. Question: "¿Restar dos naturales siempre da un natural?" (*Does subtracting two naturals always give a natural?*)

### E03 Multiplication (closed except in 𝕀)
| Set | closed | latex |
|---|---|---|
| ℕ | yes | `3\times 4=12` |
| ℤ | yes | `(-3)\times 4=-12` |
| ℚ | yes | `\dfrac{2}{3}\times\dfrac{3}{4}=\dfrac{1}{2}` |
| 𝕀 | **no** | `\sqrt{2}\times\sqrt{2}=2` (∈ ℚ) |
| ℝ | yes | `\sqrt{2}\cdot\pi\in\mathbb{R}` |
| ℂ | yes | `(1+i)(1-i)=2` |
Trap = 𝕀. Question: "¿Multiplicar dos irracionales da siempre un irracional?" (*Does multiplying two irrationals always give an irrational?*)

### E05 Exponentiation (axis = extending the EXPONENT; `closed` = "does the result stay in the base's set?")
| Case | closed | latex | note |
|---|---|---|---|
| natural exponent (ℕ) | yes | `2^{3}=8` | natural base and exponent → natural |
| negative integer exponent (ℤ) | **no** | `2^{-2}=\dfrac{1}{4}` | the negative exponent leads to ℚ |
| fractional exponent (ℚ) | **no** | `2^{1/2}=\sqrt{2}` | fractional exponent = root → ℝ (irrational) |
| power of an irrational (𝕀) | **no** | `(\sqrt{2})^{2}=2` | back to ℚ |
| real base (ℝ) | yes | `2^{\pi}\in\mathbb{R}` | |
| negative base, fractional exponent (ℂ) | yes | `(-1)^{1/2}=i` | optional detour |
Frequent traps to debunk in the steps: `2^{3}\neq 2\times 3`; `2^{0}=1`; `2^{-1}=\dfrac{1}{2}` (not `-2`). Question: "Si subimos el exponente por debajo de cero o entre enteros, ¿el resultado sigue siendo natural?" (*If we push the exponent below zero or between integers, is the result still natural?*)

### E06 Roots (inverse axis: PRODUCES irrationals → motivates ℝ and ℂ)
| Set | closed | latex | note |
|---|---|---|---|
| ℕ | **no** | `\sqrt{16}=4` but `\sqrt{2}\notin\mathbb{N}` | only perfect squares |
| ℤ | **no** | `\sqrt{2}\notin\mathbb{Z}` | |
| ℚ | **no** | `\sqrt{2}\notin\mathbb{Q}` | root of a non-square = irrational → motivates 𝕀 (B07) |
| 𝕀 | (produces) | `\sqrt{2}\in\mathbb{R}\setminus\mathbb{Q}` | taking roots CREATES irrationals |
| ℝ | yes | `\sqrt{20}\approx 4{,}4721` (radicand ≥ 0) | |
| ℂ | yes | `\sqrt{-1}=i` | negative radicand → motivates ℂ (B09) |
Trap = ℂ (`\sqrt{-1}=i`) or the ℚ→𝕀 jump. Question: "¿Toda raíz de un número entero es otro entero?" (*Is every root of an integer another integer?*)

## Worked examples and practice — guide
- Worked examples: 1 per set where the operation is interesting (min. 4: cover ℕ, ℤ, ℚ and the trap). Include the explicit **fraction⊕fraction** case in ℚ (as in Division Ex. 5).
- Practice (`situations`): walk ℕ → ℤ → ℚ → 𝕀, with `set_label` and finite typeable answers. Examples of valid answers: addition `\frac{1}{4}+\frac{1}{4}` → `0,5`; exponentiation `2^{-2}` → `0,25`; roots `\sqrt{16}` → `4`; `\sqrt{8}\div\sqrt{2}` does not apply here, but `9^{1/2}` → `3`.
- Mark `image_slot: True` on 2 concrete examples per node (the ones with a physical context, e.g. olives/amphorae/figs/drachmas).

## Verification (required per node)
1. `python -c "import src.domain.learning.prealgebra"` loads without errors (watch out for UTF-8; the file allows accents).
2. `cd frontend && ./node_modules/.bin/tsc --noEmit` (no errors; validates types).
3. **Restart the backend** (it runs without `--reload`) to load the new content.
4. Live render of each node, checking via the DOM: `0` `.katex-error` elements; ladder with 6 rows; examples in 2 columns; trap in a wide column below; practice with `set_label` crossing sets. (Preview screenshots tend to time out on these KaTeX-heavy pages: verify via the DOM, not via image.)

## Suggested order
Subtraction (E02) → Multiplication (E03) → Addition (E01) → Exponentiation (E05) → Roots (E06).
Reason: subtraction and multiplication are the closest to Division; addition consolidates the "closed except in 𝕀" pattern; exponentiation and roots have a special axis (exponent / produces irrationals) and are best done last, once the pattern is refined.
