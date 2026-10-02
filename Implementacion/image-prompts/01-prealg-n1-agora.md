# Image prompts — N1 · The Agora

Phase 7 of the unified script plan (`~/.claude/plans/effervescent-scribbling-goblet.md`).
Visual vocabulary of the space (Phase 0 / skill `prealgebra-narrative-style`): columns,
marble, tablets, public square, citizens, stone stairways. No forced mechanical touches —
KatIA (a cyborg cat) is the only technological note in the level.

**Required visual line (`Implementacion/image-prompts/referencias/`):** use as direct references
`escalera-conjuntos.png`, `step-naturales.png`, `step-enteros.png`, `step-racionales.png`,
`step-reales.png`, `katia-primer-plano-enteros.png` and `caso-enteros-recta.jpg`.
Before generating, open/attach those images as visual references if the tool allows it;
otherwise, copy this whole visual line into the final prompt.

**Base style (all 4 files share this tail):**
`refined educational pixel art, high-quality narrative 16/32-bit style, with visible pixel
clusters, clean pixelated edges, block shading and subtle dithering; NO hyperrealistic
digital painting. Contained composition like the existing assets: KatIA readable in the
foreground/mid-ground, stone stairways or a marble table as the anchor, Greek columns/arches
in the background, few blurred secondary characters, night-blue shadows, warm beige marble,
golden lamp/torch light and small teal accents. KatIA must keep the visual identity from
Implementacion/image-prompts/referencias: white cat with an orange/black patch on her head,
visible green eye, teal mechanical ocular over the other eye, mechanical paw/arm, purple
tunic and gold ornaments.`

**Secondary characters:** any human role mentioned in the prompts (citizen, scribe,
merchant, apprentice, bricklayer, youth, child, porter, vendor, messenger, etc.) must be
depicted as an anthropomorphic animal. Preference: other bipedal cats in Greek tunics,
varied coats (tabby, black, grey, calico, Siamese, orange, spotted white) and distinct fur
textures. No realistic humans.

**Stairs and steps:** if a staircase, stairway or step appears in any image, it must be
completely clean: no symbols, letters, numbers, runes, marks, medallions, arrows, labels or
mathematical reliefs.

**Style negatives:** no tourist panoramas of Athens, no heroic Acropolis in the background,
no crowds, no hyperrealistic cinematic composition, no smooth digital painting, no saturated
neon, no anime/chibi, no realistic humans, no swapping KatIA's identity for a fully metal
mascot.

**Hard rule:** every prompt describes the SITUATION, never the SOLUTION. No prompt includes
the numeric result of an exercise, or a quantity of objects that would let someone count it
and solve the exercise by looking at the image.

N1 does not use the `image_slot` field (it is i18n content in `es.ts`/`en.ts`, not Python
dicts) — the entries below cover the level header (B01, equivalent to a hub) and the opening
beat of each node (`KatiaStorySlot` or its bespoke equivalent in each TSX component).

---

## B01 — Welcome ("Every number has a place")

**Level header** (`.level-presentation-header` + `.level-presentation-media`, full width,
16:9) — taken from `body`: "The journey begins in the agora, the square where citizens
count, measure and share."

> Contained presentation framing, aligned with `escalera-conjuntos.png`: KatIA in the
> foreground/mid-ground on the right, next to a marble table with scrolls, wax tablets and a
> small basket. Behind her, the agora is suggested as an open gallery with columns, arches
> and stone stairways; a few anthropomorphic cats in tunics talk quietly in the background,
> without competing with KatIA. KatIA looks toward the viewer as if welcoming them to the
> journey. Golden lamplight on warm marble, night-blue shadows. No visible text or numbers.
> Base style + aspect ratio 16:9.

---

## B02 — Trigger question ("Is counting enough for everything?")

**Opening scene** (full width, 16:9) — B02 has no KatIA beat; the visual anchor is the 3
situations it presents (`situations.temperature/pizza/debt`), now implicitly relocated to
the agora of the journey.

> Three vignettes within the same marble square at dusk, without separating them with hard
> borders: (1) an antique mercury thermometer leaning against a column with the needle
> dropping below a central mark; (2) a whole, barely prepared wheat loaf on a stone table
> with anthropomorphic cats around it waiting for their share; (3) a wax tablet with
> abstract debt marks and an anthropomorphic cat checking a coin pouch without quite
> reaching the amount. KatIA watches the three scenes from a corner, thoughtful. Do not show
> the result of any operation or visually complete any sharing.
> Base style + aspect ratio 16:9.

---

## B03 — Staircase of need ("Each step is born from a need")

**Opening scene** (full width, 16:9) — anchored in `staircaseAria`: "Five-step staircase:
naturals, integers, rationals, irrationals and reals; with an optional detour toward the
complex numbers".

> A five-step marble stairway carved into the agora, completely clean, with no symbols,
> letters, numbers, runes, marks, medallions or mathematical reliefs. A sixth, smaller side
> step, somewhat apart from the main path, hints at an optional detour without any label.
> KatIA climbs the first step with one paw raised toward the second, looking up the stairs.
> Warm torchlight marking each step already climbed.
> Base style + aspect ratio 16:9.

---

## B04 — Naturals ("Counting whole quantities")

**KatiaStorySlot** (bespoke equivalent, image | copy column, ~4:3) — from
`story.katiaBody`: "KatIA... can count 1 tablet, 2 baskets, 3 citizens or 0 coins in an
empty chest" and from the `scenario`: "a basket of tablets... to complete the city census".

> KatIA sitting at a marble table in the square, counting clay tablets she takes out one by
> one from a wicker basket. To one side, an empty, open offering chest. Behind, citizens
> talking next to a column. No tablet should appear stacked into an already added-up total —
> only the gesture of counting one by one, basket and chest kept separate.
> Base style + aspect ratio 4:3.

---

## B05 — Integers ("Crossing zero")

**KatiaStorySlot** (image | copy column, ~4:3) — from `story.katiaBody`: "city council...
marble and chisels on credit... to carve a monument in the square... public collection" and
from the example: "the stonecutter's workshop".

> A stonecutter's workshop in the agora: uncarved marble blocks stacked next to chisels
> hanging from a wooden panel. A city council scribe holds an accounts tablet with a
> balance scale drawn on it (no numbers), showing the gesture of "still owed" — the left pan
> lower than the right, without marking the exact amount. KatIA watches the scale with a paw
> on her chin. Public-square atmosphere in the background, columns and stairways.
> Base style + aspect ratio 4:3.

---

## B06 — Rationals ("Sharing a unit")

**KatiaStorySlot** (image | copy column, ~4:3) — from `scenario`: "Three loaves among four
citizens, in the agora" and `story.katiaBody`: "fruits/juice" (en-only parallel, see note).

> A stone table in the agora with whole wheat loaves, not yet cut, and four citizens
> standing around it waiting for their share with open hands. KatIA stands by the table with
> a stone knife in one paw, about to cut one of the loaves, looking at the four citizens as
> if working out how to share them equally. Do not show the loaves already cut or the
> portions handed out.
> Base style + aspect ratio 4:3.

---

## B07 — Irrationals ("Decimals that do not come from a fraction")

**KatiaStorySlot** (image | copy column, ~4:3) — from `story.katiaBody`: "KatIA measures the
diagonal of a paved square whose side measures exactly 1" and from the trap example: "draws
a circle in the square and divides its circumference by its diameter".

> KatIA kneeling on a courtyard of square tiles in the agora, with a measuring rope
> stretched diagonally from one corner to the other of a single square tile, looking at the
> rope with curiosity as if the length does not match any exact mark on the rope. In the
> background, a circle drawn on the ground in chalk and a citizen measuring its edge with
> the same rope. No figures or fractions visible on the rope or the ground.
> Base style + aspect ratio 4:3.

---

## B08 — Reals ("All together on the line")

**KatiaStorySlot** (image | copy column, ~4:3) — from `story.katiaBody`: "a tiled path
crosses the square from end to end... each tile is a real number" and `discoveryBody`: "from
the entrance of the square to the temple stairway".

> Elevated view of a long marble-tiled path crossing the whole agora square, from the
> entrance arch to the stairway of a temple in the background. The tiles have slightly
> different textures (some smooth, some with wavy veins) to suggest two families of numbers
> living together on the same path, without marking any of them with numbers or symbols.
> KatIA walks down the middle of the path looking toward the distant temple.
> Base style + aspect ratio 4:3.

---

## B09 — Complex numbers (optional detour, "Numbers on the plane")

**KatiaStorySlot** (image | copy column, ~4:3) — from `story.katiaBody`: "the agora's tiled
path... some situations need one more extension... a plane" (not a formal Cartesian plane,
but the idea of "stepping off the line").

> KatIA standing at the edge of the agora's tiled path, with one paw raised as if testing a
> step off the path, toward a new space barely suggested by a faint gridded teal glow that
> extends perpendicular to the path — a hint of a plane, not a Cartesian plane drawn with
> axes or numbers. Expression of curiosity, not confusion. The classical agora remains the
> dominant background.
> Base style + aspect ratio 4:3.

---

## B10 — The Classifier I ("Most specific set")

**KatiaStorySlot** — from `katiaAlt` (already written text, literal): "KatIA next to a
sorting area with number cards".

> KatIA standing next to a marble board divided into boxes labeled only with set symbols
> (ℕ, ℤ, ℚ, 𝕀, ℂ — no written numeric examples), holding a blank tablet in one paw as if about
> to place it in a box. Public-square atmosphere in the background. No card should be shown
> already placed in its correct box.
> Base style + aspect ratio 4:3.

---

## B11 — The Classifier II ("All the sets")

**KatiaStorySlot** — from `katiaAlt`: "KatIA next to a membership matrix".

> KatIA next to a large marble slab engraved with an empty grid (columns marked only with
> the symbols ℕ ℤ ℚ 𝕀 ℝ ℂ, blank rows with no numbers), pointing at the grid with one paw as
> if explaining that one row can be checked in several columns at once. No box checked yet.
> Base style + aspect ratio 4:3.

---

## B12 — The Falsehood Detective ("Catch the falsehood")

**KatiaStorySlot** — from `katiaAlt`: "KatIA with a detective's magnifying glass".

> KatIA with a bronze-and-glass magnifying glass in one paw, closely examining a marble
> tablet with an engraved sentence (the tablet must show illegible/abstract lines of text,
> never a real mathematical statement or a marked true/false), narrowing her eyes with
> suspicion. Night-time agora setting, torches casting long shadows.
> Base style + aspect ratio 4:3.

---

## B13 — Level diagnostic ("Your journey through the level")

**Closing header** (full width, 16:9) — from `title`: "Your journey through the level", a
closing/summary tone without revealing the result of the student's diagnostic.

> Contained closing framing inside the same marble gallery as the existing assets: the
> five-step stairway appears in the mid-background, the tiled path enters from the
> foreground and disappears toward a bright doorway. KatIA stands near the stairway, looking
> back in a closing pose of quiet celebration (not euphoric). Golden dawn light coming
> through the arches, with soft shadows and few secondary details. No score marker,
> percentage or badge visible in the scene.
> Base style + aspect ratio 16:9.
