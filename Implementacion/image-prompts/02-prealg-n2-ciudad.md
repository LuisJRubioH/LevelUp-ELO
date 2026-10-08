# Image prompts — N2 · The City of Operations

**Replaces `n2-mercado.md`.** The level stopped being a market of stalls: it is SIX
BUILDINGS with proper names, and you enter one per node. The current art
(`frontend/public/leccion/02-prealg-n2-mercado/*-v4.png`) shows cloth stalls and counters —
it must be regenerated. The file names are kept so the content paths do not break.

| Node | Building | Trade · what you see inside |
|---|---|---|
| E01 Addition | **The Public Granary** (*El Granero Público*) | two floors of sacks, floor scale, tablet of incoming and outgoing loads next to the door |
| E02 Subtraction | **The Counting House** (*La Casa de Cuentas*) | hall with strongboxes, a wall of tablets crossed by an engraved line (zero) |
| E03 Multiplication | **The Mosaic Workshop** (*El Taller de Mosaicos*) | long tables, drawers of tesserae sorted by color, storeroom at the back |
| E04 Division | **The Communal Dining Hall** (*El Comedor Comunal*) | long communal tables, a big cauldron, a ladle, sliced loaves |
| E05 Exponentiation | **The Greenhouse** (*El Invernadero*) | glass roof, germination trays in rows, a log hanging on the door |
| E06 Roots | **The Quarry** (*La Cantera*) | open-air stone cut, pulleys, chisels, a hanging plumb line |

**Visual vocabulary of the level:** everyday Greek civic architecture — ashlar walls, wooden
lintels, double-leaf doors, inner courtyards, service stairs, pulleys, trade tools. **Zero
market vocabulary**: no stalls, cloth awnings, merchants behind a counter or displayed fruit
baskets. Each building must be recognizable by its TRADE, not by a sign with the operation
symbol.

**Required visual line (`Implementacion/image-prompts/referencias/`):** use as direct references
`step-naturales.png`, `step-enteros.png`, `step-racionales.png`, `step-reales.png`,
`escalera-conjuntos.png`, `katia-primer-plano-enteros.png` and `caso-enteros-recta.jpg`.
Before generating, open/attach those images as visual references if the tool allows it;
otherwise, copy this whole visual line into the final prompt.

**Base style:** `refined educational pixel art, high-quality narrative 16/32-bit style,
with visible pixel clusters, clean pixelated edges, block shading and subtle dithering; NO
hyperrealistic digital painting. Keep the visual language of the existing assets: KatIA
readable in the foreground/mid-ground, contained scene, few secondary characters, clear
teaching objects on a table/floor/workbench, night-blue shadows, golden lamplight, warm
stone, small teal accents on KatIA's ocular and on mechanical instruments. KatIA must keep
her identity: white cat with an orange/black patch on her head, visible green eye, teal
mechanical ocular, mechanical paw/arm, purple tunic and gold ornaments. The space must read
as the INTERIOR of a trade building in a Greek city; if background architecture appears, it
is secondary.`

**Secondary characters:** any role mentioned (scribe, accountant, apprentice, stonecutter,
gardener, cook, customer) is depicted as an anthropomorphic animal. Preference: bipedal cats
in Greek tunics or aprons, varied coats (tabby, black, grey, calico, Siamese, orange,
spotted white) and distinct textures. No realistic humans.

**Stairs and steps:** if a staircase or step appears, it is completely clean: no symbols,
letters, numbers, runes, marks, medallions, arrows or mathematical reliefs.

**Style negatives:** no tourist panorama, no market or stalls, no crowds, no public square
as the focus, no smooth digital painting, no saturated neon, no hard sci-fi, no anime/chibi,
no realistic humans, no turning KatIA into a fully metal cat.

**Hard rule:** every prompt describes the SITUATION, never the SOLUTION. No prompt shows the
numeric result of an exercise, or a quantity of objects arranged so that it could be counted
to solve the exercise by looking at the image.

---

## E00 — Hub: The City of Operations (*La Ciudad de las Operaciones*)

`e00-hub-mercado-v4.png` → regenerate as a **city of buildings** (keep the file name).

**Level header** (`.level-presentation-header` + `.level-presentation-media`, full width,
16:9).

> A sloping street in a Greek city at dusk, seen in a contained mid-distance view: on both
> sides rise six stone buildings, each different from the others, recognizable by their
> trade and not by signs — a two-story granary with a high hatch and pulleys; a counting
> house with a double-leaf door and a barred window; a workshop with tables visible through
> the doorway and drawers of colored tesserae; a dining hall with its doors thrown wide open
> and smoke rising from a vent; a greenhouse with a fogged glass roof; and in the
> background, where the street opens up, the cut of a quarry with a pulley silhouetted
> against the sky. KatIA in the foreground on the cobblestones, waist-up, pointing up the
> street as if inviting a walk through it. No market stalls, no hanging cloth, nobody
> selling.

**Icebreakers** (keep `e00-ice1-ladrillos-v4.png`, `e00-ice2-tejas-v4.png`,
`e00-ice3-puestos-v4.png`): they are street construction scenes, before entering any
building. The third one (`ice3`) must stop showing "stalls in the square" and instead show
**the gates of the six buildings, some open and some closed**.

---

## E01 — The Public Granary (*El Granero Público*)

`e01-suma-katia-v4.png` — opening.

> Interior of the Public Granary at night: a tall ashlar hall with sacks stacked on two
> levels, a wooden ramp, a floor scale with large pans and, next to the door, a wax tablet
> hanging from a nail with two columns scored with a knife. KatIA in a medium shot next to
> the tablet, with her mechanical arm resting on it; to one side, a scribe cat in a grey
> tunic with a stylus, looking at the tablet with doubt. A cart unloading in the background,
> barely suggested. A hanging oil lamp as the only warm light. Do not show countable
> quantities of sacks.

`e01-higos-reunidos-v4.png` → mentally rename it **"grain coming in"**: close-up of the
granary ramp with sacks coming in, without it being possible to count them.

`e01-deuda-pago-v4.png` → **"the sack going out"**: the same ramp, a sack leaving through
the hatch and KatIA's mechanical hand marking the opposite sign on the tablet.

---

## E02 — The Counting House (*La Casa de Cuentas*)

`e02-resta-katia-v4.png` — opening.

> Interior of the Counting House: a narrow stone hall with two iron strongboxes at the back
> and a wall covered with hanging tablets, crossed from side to side by a HORIZONTAL LINE
> engraved into the wall. Some tablets hang above the line, others below it. An old tabby
> accountant cat in a dark tunic refuses to hang a tablet below the line and holds it in the
> air; in front of the counter, a young customer cat with a small pouch. KatIA in the side
> foreground, looking at the line on the wall. Oil lamp, blue shadows. The zero line must be
> the most readable graphic element in the scene. No numbers written on the tablets.

`e02-ceramica-vendida-v4.png` → **"the payment that rises"**: detail of a tablet moving from
below the line to above it.

`e02-dracmas-deuda-v4.png` → **"the tablet hanging below"**: detail of a single tablet
hanging below the engraved line, with a long shadow.

---

## E03 — The Mosaic Workshop (*El Taller de Mosaicos*)

`e03-multiplicacion-katia-v4.png` — opening.

> Interior of the Mosaic Workshop: long worktables with stone tesserae laid out in incomplete
> rows and columns, open drawers separating tesserae by color, and at the back the mouth of
> a storeroom with shelves. An apprentice cat in an apron going down to the storeroom with an
> empty basket; the master, an older calico cat, measuring a large mosaic with a template.
> KatIA in a medium shot next to the table, with her mechanical paw on a half-scale
> reduction template. Grazing lamplight that makes the tesserae shine. The rows of tesserae
> must look incomplete or partly covered so they cannot be counted.

`e03-filas-tinajas-v4.png` → **"the mosaic row by row"**: high-angle detail of a partly
assembled mosaic, with part of it covered by a cloth.

`e03-deuda-repetida-v4.png` → **"the broken tesserae"**: a small pile of split tesserae next
to the chisel, at the edge of the table.

---

## E04 — The Communal Dining Hall (*El Comedor Comunal*)

`e04-division-katia-v4.png` — opening.

> Interior of the Communal Dining Hall in the middle of a night service: long wooden tables,
> long benches, a big steaming cauldron over the fire at the back and a hanging ladle. On the
> front table, loaves of bread, some whole and others cut in half with a knife lying beside
> them. A cook cat in an apron signaling to cut; a young helper cat with an alarmed face
> holding a small slate. KatIA in a medium shot next to the loaves, with her mechanical paw
> on one of the halves. Steam, warm firelight, night-blue shadows. Do not show a countable
> number of loaves or diners.

`e04-reparto-exacto-v4.png` → **"equal rations"**: detail of a table where the portions look
equivalent, without it being possible to count them.

`e04-reparto-residuo-v4.png` → **"what is left over gets shared too"**: detail of a loose
loaf next to the knife, half cut, with hands around it.

---

## E05 — The Greenhouse (*El Invernadero*)

`e05-potenciacion-katia-v4.png` — opening.

> Interior of the Greenhouse: a hall with a fogged glass roof held up by wooden beams,
> germination trays in rows on stone benches, a copper watering can and a wooden log hanging
> next to the door with carved notches. The cuttings in the trays at the back clearly
> overflow their trays and have spilled onto the floor, while those in the foreground still
> fit — the scene must convey the overflow without it being possible to count it. A gardener
> cat in a stained apron looking at the overflow with drooping ears. KatIA in a medium shot
> next to the log by the door. Moonlight filtered through the glass plus a warm lamp.

`e05-crecimiento-niveles-v4.png` → **"two trays, two kinds of growth"**: two adjacent
benches, one with evenly spaced cuttings and the other overflowing, no figures.

`e05-exponente-negativo-v4.png` → **"the log running backwards"**: detail of the wooden log
with notches that get smaller toward the left.

---

## E06 — The Quarry (*La Cantera*)

`e06-radicacion-katia-v4.png` — opening.

> The open-air Quarry at nightfall: a cut of pale stone with cutting steps, a wooden pulley
> with a taut rope, chisels and mallets resting on a rock ledge, and a plumb line hanging
> still in the foreground. On the ground, two square slabs of different sizes already cut
> and a third, badly cut slab set aside, with a splintered edge. A burly stonecutter cat with
> grey fur, looking at the failed slab with the mallet lowered. KatIA in a medium shot next
> to the plumb line, with her mechanical paw holding a rope stretched diagonally across a
> slab. Deep blue sky, warm torchlight. The slabs must not carry measurements or numeric
> marks.

`e06-cuadrado-perfecto-v4.png` → **"the slab that fits"**: top-down detail of a square slab
seated in its hole.

`e06-raiz-no-entera-v4.png` → **"the diagonal with the rope"**: detail of a rope stretched
diagonally across a square slab, showing that the diagonal does not line up with any mark on
the ruler lying beside it.
