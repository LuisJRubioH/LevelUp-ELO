# Image prompts — ALG-N1 · The Papyrus of the Four Houses (Kemet)

**There is not a single Egypt PNG in `frontend/public/`.** The 16 nodes render the
placeholder "KatIA image here" and the hub points to a file that does not exist yet. This
document covers the **17 required images** (1 hub header + 16 KatIA openings) and lists the
**16 optional** trap images.

Destination: `frontend/public/leccion/05-alg-n1-kemet/`. The file names in this document are
final — the hub already declares `a00-hub-papiro-katia.png`.

---

## Continuity with Pre-algebra

It is the same world and the same KatIA, in another place. Pre-algebra takes place in Greece
(agora, city, factory, port); here KatIA has traveled up the river to **Kemet**. The visual
line does NOT change: the architecture, light and materials change.

**Required visual line (`Implementacion/image-prompts/referencias/`):** use as direct references
`step-naturales.png`, `step-enteros.png`, `escalera-conjuntos.png`,
`katia-primer-plano-enteros.png` and `caso-enteros-recta.jpg`. Before generating, attach them
as visual references if the tool allows it; otherwise, copy the whole visual line into the
final prompt.

**Base style (copy verbatim into every prompt):**

`refined educational pixel art, high-quality narrative 16/32-bit style, with visible pixel
clusters, clean pixelated edges, block shading and subtle dithering; NO hyperrealistic
digital painting. Keep the visual language of the existing assets: KatIA readable in the
foreground/mid-ground, contained scene, few secondary characters, clear teaching objects on
a table/floor/workbench, night-blue shadows, warm oil-lamp light, limestone and adobe, small
teal accents on KatIA's ocular and on mechanical instruments. KatIA keeps her identity: white
cat with an orange/black patch on her head, visible green eye, teal mechanical ocular,
segmented mechanical arm and ear piercings; she wears sleeveless ivory Egyptian linen, a
teal/purple bead collar and a narrow purple waist sash. The space must read as the INTERIOR
of an Ancient Egyptian compound — whitewashed adobe walls, papyriform columns, stone lintels,
reed mats, storage jars — with the background architecture always secondary.`

**Contextual wardrobe (user instruction, 2026-09-16):** KatIA wears Egyptian linen, a bead
collar and a belt suited to the Kemet setting. Her identity stays: face, markings, green eye,
teal ocular, mechanical arm and ear piercings. Purple can remain as an accent on the belt. No
nemes headdress or royal attire. This rule replaces the references to the Greek tunic in
earlier prompts. See [IDENTIDAD-KATIA.md](IDENTIDAD-KATIA.md).

**Secondary characters:** every role mentioned (scribe, foreman, dyer, gold beater, water
carrier, apprentice) is an **anthropomorphic animal**, preferably bipedal cats with a linen
kilt, apron or broad Egyptian collar; varied coats (tabby, black, grey, calico, Siamese,
orange, spotted white). The four guides look the same across their four rooms:

| Guide | House | Appearance |
|---|---|---|
| **Meritka** | The House of Life | slender black cat, broad collar of blue beads, reed pen behind the ear |
| **Bakenra** | The Pyramid Works | stocky tabby cat, short leather kilt, rope over the shoulder |
| **Tabiry** | The Fields After the Flood | calico cat, bare muddy feet, woven reed hat |
| **Iuty** | The Canon Workshop | short-haired grey cat, pigment-stained apron, plumb bob at the belt |

**Stairs and steps:** if a staircase or step appears, it is completely clean: no symbols,
letters, numbers, runes, marks, medallions, arrows or mathematical reliefs.

**Hieroglyphs:** allowed as ambient texture on walls and columns, **never legible or
prominent**, and never on the surface where the teaching action happens (the tablet, the
working papyrus, the grid). No cartouches with the node's name.

**Style negatives:** no tourist panorama, no postcard pyramids at sunset, no Sphinx, no
pharaoh or royalty, no mummies or tombs, no anthropomorphic Egyptian gods (Anubis, Thoth) —
the anthropomorphic animals here are neighbors, not deities —, no crowds, no smooth digital
painting, no saturated neon, no hard sci-fi, no anime/chibi, no realistic humans, no turning
KatIA into a fully metal cat.

**Hard rule:** every prompt describes the SITUATION, never the SOLUTION. No image shows the
numeric result of the exercise, or a quantity of objects arranged so that the exercise could
be solved by counting in the image. When the story is about a mistake already made, show
**the consequence** (dull skeins, empty threshing floor, dry jar), never the correct
calculation.

**Palette per house** (dominant + accent; KatIA's purple accent stays in all four):

| House | Dominant | Accent |
|---|---|---|
| The House of Life | turquoise and ochre | ink black |
| The Pyramid Works | sand and terracotta | cool blue shadow |
| The Fields After the Flood | fertile green and silt | turquoise water |
| The Canon Workshop | Egyptian blue and lime white | gold |

---

## A00 — Hub: The Papyrus of the Four Houses (*El Papiro de las Cuatro Casas*)

`a00-hub-papiro-katia.png` · **16:9**, level header (`.level-presentation-media`).

> Dim interior of an Ancient Egyptian archive room at dawn, contained mid-distance view. On a
> long wooden table, a slender black cat with a broad collar of blue beads (Meritka) spreads
> out a large, visibly damaged papyrus: four sections are missing, four torn holes with
> irregular edges. On the other side of the table, KatIA — white cat with orange and black
> markings, green eye, teal mechanical ocular, mechanical arm and ear piercings, in
> sleeveless ivory Egyptian linen with a bead collar and a narrow purple sash — has just
> arrived and still carries the dust of the journey. Through the open doorway at the back,
> very secondary and without detail, four different buildings stand against the sky: a
> whitewashed compound, a construction ramp, flooded fields and a workshop with scaffolding.
> Low oil-lamp light on the table, cool blue in the rest of the room. The holes in the
> papyrus are empty: nothing written in them, no legible letter or number anywhere in the
> image.

**Hub optionals** (1:1, same pattern as N2's `e00-ice*`): `a00-ice1-cestos.png` (grain
baskets stacked next to a floor scale) · `a00-ice2-registro.png` (two clay tablets leaning
against a whitewashed wall) · `a00-ice3-hueco.png` (a papyrus with a deliberately blank space
in the middle of a line of illegible notes).

---

## House I · The House of Life (*La Casa de la Vida*) — Meritka · turquoise and ochre

### L01 · The Reed-Pen Room (*la sala de los cálamos*)
`l01-variables-katia.png` · **4:3**

> Interior of a scribes' office: niche shelves with scrolls, a bowl of black ink, reed pens
> in a ceramic cup. Meritka holds up an unrolled papyrus in front of KatIA; on the papyrus
> the same short note is repeated many times in columns, deliberately illegible (ink
> strokes, no recognizable signs). In the background, a basket full of identical scrolls
> waiting to be copied. Turquoise morning light coming through a high window; warm ochres on
> the shelves.

### L02 · The Sealed Shelf (*el estante sellado*)
`l02-constantes-katia.png` · **4:3**

> Meritka pulls a broken clay seal off the small door of a low shelf. Inside, on a cloth,
> three standard measuring objects: a wooden rod, a rope with evenly spaced knots and a
> polished stone weight with an engraved mark. KatIA leans in to look without touching. The
> rest of the room is an everyday workspace and is messy; only that shelf is clean and set
> apart. Contrast between the cool turquoise of the sealed niche and the warm ochre of the
> room.

### L03 · The Dictation Table (*la mesa de dictado*)
`l03-traduccion-katia.png` · **4:3**

> A low dictation table. A messenger (a Siamese cat in travel sandals, still wearing his
> cloak) speaks standing up and in a hurry, one hand raised. Sitting in front of him, two
> young scribes write at the same time on two different tablets; the tablets are turned
> toward the viewer just enough to look busy, with illegible ink strokes that are clearly
> DIFFERENT from each other. Meritka watches standing, without intervening. KatIA in the
> foreground, looking from one tablet to the other. Nothing legible on either of them.

### L04 · The Tally Chamber (*la cámara del recuento*)
`l04-valor-numerico-katia.png` · **4:3**

> A half-underground tally chamber with a low ceiling. Clay tokens stacked in columns and a
> knotted counting cord hanging on the wall. Meritka holds a tablet; next to her, on the
> floor, a row of empty wooden handcarts, far more than needed, waiting for a load that never
> arrived. KatIA looks at the empty carts. Grazing oil-lamp light; dust hanging in the air.
> No grain in sight, no figures anywhere.

---

## House II · The Pyramid Works (*La obra de la pirámide*) — Bakenra · sand and terracotta

### O01 · The Ramp (*la rampa*)
`o01-semejantes-katia.png` · **4:3**

> At the foot of an adobe construction ramp, mid-morning. Bakenra, a stocky tabby cat with a
> leather kilt and a rope over his shoulder, holds two shift tablets, one in each hand,
> looking from one to the other. Behind him, a crew of worker cats waits standing next to a
> loaded wooden sledge, not moving forward. On one side, coiled ropes; on the other, mallets
> and stacked tools — two clearly separate piles. Sand dust in the air, cool blue shadow
> under the ramp.

### O02 · The Rigging Yard (*el patio de aparejos*)
`o02-signos-katia.png` · **4:3**

> An enclosed rigging storehouse yard: wooden pulleys hanging from a beam, ropes coiled on
> the floor, stone counterweights lined up against the wall. Bakenra holds a return-voucher
> tablet. On the back wall, a row of wooden racks for counterweights with several obviously
> empty slots. In the exit doorway, a crew walks away empty-handed. KatIA in the foreground
> next to the pulleys. Harsh midday light, short blue shadows.

### O03 · The Chisel Workshop (*el taller de cinceles*)
`o03-producto-katia.png` · **4:3**

> Inside the carving workshop: a long bench with chisels lined up by size, whetstones, stone
> chips, wooden templates hanging up. Bakenra has left an order tablet on the bench and looks
> out through the doorway, where — very secondary, without detail — an almost empty stockyard
> with a few ashlar blocks can be seen. KatIA examines a chisel. Terracotta atmosphere, white
> stone dust, a teal accent on the ocular.

### O04 · The Foreman's Hut (*la caseta del capataz*)
`o04-cociente-katia.png` · **4:3**

> A small, shaded site hut with reed mats and a shutterless window. On a shelf, the site
> census on tablets. Bakenra points at a line on a tablet. Outside, seen through the window,
> a group of water carriers standing with their jars on their shoulders, still full,
> undistributed, looking toward the hut. KatIA follows Bakenra's finger. Mid-afternoon heat,
> sand and terracotta, deep shadow inside the hut.

---

## House III · The Fields After the Flood (*Los campos tras la crecida*) — Tabiry · fertile green and silt

### F01 · The Divided Plot (*la parcela partida*)
`f01-simplificar-katia.png` · **4:3**

> A field freshly drained after the flood, shiny mud and green shoots. Tabiry, a calico cat
> with a reed hat and muddy feet, holds a surveyor's rope stretched over the ground; the
> boundary stones have fallen over or disappeared and the field looks like a single expanse
> with no divisions. In the background, a small group of cat families waiting on their feet
> with their belongings. KatIA next to Tabiry, with her paws in the mud. Morning light, greens
> and silt ochres, turquoise reflections in the puddles.

### F02 · The Mother Canal (*el canal madre*)
`f02-suma-katia.png` · **4:3**

> Beside a main irrigation canal, with two ditches branching off it in different directions
> and a weir made of wooden planks. Tabiry has crouched down and plunged a hand into the
> canal water. On the bank, leaning against a stone, a tablet of irrigation turns. One of the
> two ditches runs visibly drier than the other. KatIA standing at the edge, looking at the
> water. Fertile green on the banks, turquoise in the water, high sky.

### F03 · The Threshing Floor (*la era de trilla*)
`f03-producto-katia.png` · **4:3**

> A circular threshing floor of packed earth, with a wooden threshing sledge leaning at the
> edge and loose straw swirled by the wind. The threshing floor is practically empty: hardly
> any grain is left to thresh. Tabiry holds a tablet and looks at the swept floor. In the
> background, the door of an adobe granary, open. KatIA next to the threshing sledge. Very
> white midday light, straw golds, short shadow.

### F04 · The Seed Silo (*el silo de simiente*)
`f04-division-katia.png` · **4:3**

> Inside a round adobe silo, with the seed forming a tall heap up to the middle of the wall.
> Against the wall, a stack of empty, folded cloth sacks, unfilled. Tabiry holds a record
> tablet and points at the full heap with her other hand. KatIA looks at the empty sacks.
> Clear contrast between the abundance of the heap and the stack of unused sacks. Light
> entering as a beam through a high slit window; muted greens and earth tones.

---

## House IV · The Canon Workshop (*El taller del canon*) — Iuty · Egyptian blue and lime white

### R01 · The Canon Grid (*la cuadrícula del canon*)
`r01-razones-katia.png` · **4:3**

> A painters' workshop facing a whitewashed wall with a grid of taut string. On a table, the
> small sketch of a motif; on the wall, the enlarged version of the same motif, visibly
> distorted — stretched on one side and squashed on the other. Iuty, a grey cat with a
> pigment-stained apron and a plumb bob at his belt, looks at the wall with his arms crossed.
> KatIA compares the sketch with the wall. Egyptian blue and lime white, secondary wooden
> scaffolding.

### R02 · The Linen Dye (*el tinte de lino*)
`r02-regla-de-tres-katia.png` · **4:3**

> The dye room: a large clay vat with dark liquid and a bench with skeins of linen. Skeins
> hang from the ceiling to dry; some have full color and the last ones in the row are clearly
> dull and uneven. Iuty holds a tablet with the recipe. KatIA touches one of the faded skeins.
> Faint steam over the vat, damp floor, deep blues and lime white.

### R03 · The Gold Leaf (*el pan de oro*)
`r03-porcentajes-katia.png` · **4:3**

> A gold beater's workroom: a polished stone table, a small mallet, stacks of ultra-thin gold
> leaves separated by parchment, tweezers. A gold beater (a spotted white cat, hands wrapped
> in cloth) has stepped back from the table with open, empty hands, in a gesture that he
> cannot go on. Iuty holds the commission tablet. On the table there is a gap where the stack
> of leaves should continue. KatIA looks at the gap. Intense but restrained golds over
> Egyptian blue; no exaggerated metallic shine.

### R04 · The Lamp Room (*la sala de las lámparas*)
`r04-variacion-katia.png` · **4:3**

> The workshop's night workroom. Six oil lamps spread around the room, all out except one
> that is burning down, its wick almost spent. In the center, a large oil jar tipped over on
> its side, empty. Iuty points at the jar. The wall frieze is half finished, in shadow. KatIA
> in the circle of light of the last flame. A predominantly dark scene, night blue, a single
> small warm light source.

---

## Optionals — the traps (1:1)

One per room, for the `trap` card in `worked_examples`. Same visual line, tight framing on
the object, with no characters or just one. Priority: the four marked with ★ gain the most
from an image.

| File | What you see |
|---|---|
| `l01-trampa-etiqueta.png` | a reed pen resting on a note that is crossed out and rewritten |
| `l02-trampa-pozo.png` ★ | the circular rim of a well seen from above, with a rope crossing it through the center |
| `l03-trampa-tablillas.png` | two tablets of identical size, leaning side by side, with different strokes |
| `l04-trampa-carros.png` ★ | a long row of empty handcarts, in perspective, next to a small heap of grain |
| `o01-trampa-monton.png` | two separate piles: ropes on one side, mallets on the other, with a line drawn in the sand between them |
| `o02-trampa-huecos.png` | counterweight racks on a wall, half occupied and half empty |
| `o03-trampa-acopio.png` ★ | an ashlar stockyard seen from mid-distance, almost empty |
| `o04-trampa-cantaros.png` | full jars lined up and an upside-down sharing bowl next to them |
| `f01-trampa-mojon.png` | a boundary stone fallen in the mud, half sunk |
| `f02-trampa-acequias.png` | two ditches branching off the same canal, one with water and the other almost dry |
| `f03-trampa-era.png` | the swept threshing floor, with the granary door open in the background |
| `f04-trampa-sacos.png` ★ | a single empty cloth sack hanging from a peg in front of a heap of seed |
| `r01-trampa-boceto.png` | the small sketch and its distorted copy, side by side on the table |
| `r02-trampa-madejas.png` | a row of hanging skeins, fading from full color to washed out |
| `r03-trampa-pila.png` | a stack of gold leaves with a visible gap where it should continue |
| `r04-trampa-lampara.png` | a single oil lamp with its wick burning down, black background |

---

## When the PNGs arrive

The node modules do **not declare** the paths yet: they must be added by hand, one line per
room, inside `CONTENT["katia"]`:

```python
"katia": {
    "eyebrow": "...",
    "image": "/leccion/05-alg-n1-kemet/l01-variables-katia.png",
    ...
}
```

And on the trap card in `worked_examples`, `"image_slot": True` plus `"image": "..."` (see
`nodes/e05_potenciacion.py` as an already wired reference).

The hub is the exception: `a00_hub.py` already declares its `image`, so as soon as the file
exists it shows up on its own. Until then that path **returns 404 in the browser** — it is the
only known broken asset in the module.
