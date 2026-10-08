# Corrected implementation prompt — Levels 1 and 2

> Student-facing content stays in Spanish (es-CO); this prompt only governs structure and order.

Use this prompt when implementing or re-implementing Pre-algebra Level 1 nodes
`B04–B13` and Level 2 nodes `E00–E06`.

---

## Critical rules

### Rule 1: Do not interrupt the narrative with isolated definitions

Incorrect:

```markdown
[Narrative...]
[Isolated definition block]
[More narrative...]
[Examples...]
```

Correct:

```markdown
[Narrative opening]
[Guided discovery]
[Definition integrated into the prose]
[Worked examples immediately after]
[Narrative closing]
[Interactive practice]
```

The definition can be visually highlighted, but it must not break the flow or
appear as a disconnected box.

### Rule 2: Definition + examples always before practice

Required order:

1. Narrative opening: why the concept matters.
2. Guided discovery: examples, contrast and counterexample.
3. Formal definition in KaTeX integrated into the narration.
4. Two or three base examples with steps.
5. Narrative closing with Katia.
6. Interactive practice.

Do not implement:

- the definition as the first screen with no context,
- examples scattered after exercises,
- practice before the student understands the why,
- nodes without Katia in the narrative.

### Rule 3: Copy A2 in full

A2 is the source of truth for visible text.

- Do not summarize.
- Do not compress for readability.
- Do not move practice before the base examples.
- Do not remove Katia's dialogue.
- If A2 has fewer than 350 lines in Level 1, stop and ask for a correction.
- If A2 has fewer than 450 lines in Level 2, stop and ask for a correction.

### Rule 4: Visual hierarchy

- The narrative opening must feel like a scene.
- The guided discovery must show variation and contrast.
- The formal definition must render in KaTeX.
- The base examples must be numbered and show steps.
- Practice must start after a clear transition.
- Katia must summarize what was learned before moving on to practice or the closing.

---

## Minimal A2 template

```markdown
### A2. Screen script (full text per screen)

#### 2.1 Narrative opening

[3–5 paragraphs with context, Katia and a trigger question.]

---

#### 2.2 Guided discovery

[3–5 paragraphs showing a pattern, a second example and a counterexample.]

---

#### 2.3 Integrated formal definition + base examples

[Lead-in paragraph.]

$$\text{formal definition in KaTeX}$$

[Paragraph reading and interpreting the definition.]

##### Example 1 (basic)

**Statement:**
[Simple problem.]

**Step-by-step solution:**
[Visible steps.]

##### Example 2 (intermediate)

**Statement:**
[Problem with a subtlety.]

**Step-by-step solution:**
[Visible steps.]

##### Example 3 (common trap or edge case)

[Optional, but recommended if there is a frequent misconception.]

---

#### 2.4 Narrative closing

[Katia summarizes and connects to what comes next.]

---

#### 2.5 Interactive practice

[S1, S2, S3... or O1, O2, O3...]
```

---

## Required technical structure in PARTE B (*Part B*)

Each repaired node must expose in JSON a section equivalent to:

```json
{
  "type": "narrative_with_integrated_definition",
  "is_integrated": true,
  "sections": [
    {
      "type": "prose",
      "content_summary": "Narrative opening with Katia and a trigger question"
    },
    {
      "type": "guided_discovery",
      "content_summary": "Examples, variation and counterexample"
    },
    {
      "type": "definition_plus_examples",
      "definition_katex": "...",
      "is_integrated": true,
      "examples": [
        { "name": "Example 1 (basic)", "steps": [] },
        { "name": "Example 2 (intermediate)", "steps": [] }
      ]
    }
  ],
  "practice_position": "after_definition_plus_examples"
}
```

If the JSON still has `definition_block` with
`position = "interrupts_narrative"`, it must be fixed before implementing the UI.

---

## Checklist before delivering

- [ ] Katia appears by name in the narrative.
- [ ] There is an explicit trigger question.
- [ ] There is guided discovery with contrast or a counterexample.
- [ ] The formal definition is integrated and renders in KaTeX.
- [ ] There are at least 2 examples with steps before practice.
- [ ] Practice appears after the base examples.
- [ ] A2 meets the minimum length.
- [ ] PARTE B reflects `narrative_with_integrated_definition`.
- [ ] No ELO changes are introduced in these formative nodes.
- [ ] If UI is implemented, it is verified with before/after screenshots.

---

## Nodes already corrected with this prompt

- `Fase_1/F1_nodo_enteros.md` — B05 Integers.
- `Fase_2/F2_nodo_suma.md` — E01 Addition.
