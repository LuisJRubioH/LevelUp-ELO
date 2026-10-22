# Image prompts — ALG-N2 and ALG-N3 · Baghdad, the House of Wisdom

Closes the art gap for the two new Algebra levels. **There is not a single Baghdad PNG in
`frontend/public/`:** the nine rooms currently render the placeholder "KatIA image here".

**10 required images** (1 hub header + 9 KatIA openings, one per room) and **9 optional**
(the trap card of each node).

**The two levels share a hub**, `ALG-S00-CASA-DE-LA-SABIDURIA`, because they share an idea:
the workshop stamps and the warehouse opens what was stamped. It is the same operation in two
directions, so the hub has two doors, not nine.

Destination: `frontend/public/leccion/06-alg-n2-troqueles/` and `…/07-alg-n3-caravana/`. The
hub header goes with the dies.

---

## Continuity with Kemet

Same world, same KatIA, third place. Greece (agora, city, factory, port) → Kemet (the four
houses) → **Baghdad, 9th century**. KatIA has followed the caravan route. The visual line
does NOT change: the architecture, light and materials change.

**Required visual line (`Implementacion/image-prompts/referencias/`):** use as direct references
`step-naturales.png`, `step-enteros.png`, `escalera-conjuntos.png`,
`katia-primer-plano-enteros.png` and `caso-enteros-recta.jpg`. Before generating, attach them
as visual references if the tool allows it; otherwise, copy the whole visual line into the
final prompt.

**Base style (copy verbatim into every prompt):**

`refined educational pixel art, high-quality narrative 16/32-bit style, with visible pixel
clusters, clean pixelated edges, block shading and subtle dithering; NO hyperrealistic
digital painting or smooth illustration. Keep the visual language of the existing assets:
KatIA readable in the foreground/mid-ground, contained scene, few secondary characters, clear
teaching objects on a table/bench/counter, night-blue shadows, warm oil-lamp light, small
teal accents on KatIA's ocular and on mechanical instruments. KatIA keeps her identity: white
cat with an orange/black patch on her head, visible green eye, teal mechanical ocular,
segmented mechanical arm and ear piercings; she wears an ivory linen tunic under a muted plum
Abbasid-style overgarment, sleeves adapted so the mechanical arm stays exposed, ears
uncovered. The space must read as the INTERIOR of a 9th-century Abbasid building — fired
brick and carved stucco, pointed arches, recessed niches, turned-wood lattices, wool rugs,
cupboards of paper and parchment, hanging bronze lamps —, with the background architecture
always secondary.`

**KatIA canonical block (required whenever she appears):** use
`katia-primer-plano-enteros.png` as an IDENTITY reference, not just a style reference. An
adult cyborg cat, serene and Socratic, not a childlike mascot: white face with a rounded adult
muzzle, calm and observant expression, visible green almond-shaped eye, asymmetric
orange/black marking on the forehead and ear, teal mechanical ocular with grey plates over
the other eye, segmented mechanical paw/arm, ear piercings, Abbasid-context tunic and
overgarment (see contextual wardrobe below). If the frame is tight, simplify the environment
before simplifying KatIA.

**Contextual wardrobe (user instruction, 2026-09-16):** KatIA wears a tunic and overgarment
suited to the Abbasid setting, adapted so the mechanical arm stays recognizable. Keep her
face, markings, green eye, teal ocular and ear piercings; do not cover the ears. This rule
replaces the earlier references to the Greek tunic. See
[IDENTIDAD-KATIA.md](IDENTIDAD-KATIA.md).

**Secondary characters:** every role mentioned (apprentice, porter, cooper, muleteer) is an
**anthropomorphic animal**, preferably bipedal cats in a short linen tunic, leather apron or
padded vest; varied coats (tabby, black, grey, calico, Siamese, orange, spotted white). The
two guides look the same across their rooms:

| Guide | Level | Appearance |
|---|---|---|
| **Rayhana** | The Stamping-Die Room (N2) | Siamese cat with an upright bearing, leather apron with forge burns, linen sleeve cuffs, awl behind the ear |
| **Salim** | The Caravan Warehouse (N3) | stocky, older orange cat, padded travel vest, bunch of keys at the belt, reed pen and delivery-note tablet under the arm |

**Arabic script:** allowed as ambient texture on friezes, book spines and stucco, **never
legible or prominent**, and never on the surface where the teaching action happens (the
sheet, the working delivery note, the breakdown table). No cartouches with the node's name.
No legible text in any language, in any image.

**Style negatives:** no Orientalist postcard (no flying carpets, magic lamps, genies, harems,
fairy-tale bazaar), no tourist panorama of domes at sunset, no minaret as the focus, no
religious calligraphy or worship scene, no camels at sunset, no royalty or caliph, no crowds,
no smooth digital painting, no smoothed render, no saturated neon, no hard sci-fi, no
anime/chibi, no realistic humans, no turning KatIA into a fully metal cat.

**Hard rule:** every prompt describes the SITUATION, never the SOLUTION. No image shows the
result of the exercise, or a quantity of objects arranged so that it could be solved by
counting in the image. When the story is about a mistake already made, show **the
consequence** (the sheet with an unstamped edge, the jammed stamp, the hollow block, the
broken seal), never the correct calculation.

**Palette per level** (dominant + accent; KatIA's purple accent stays in both):

| Level | Dominant | Accent |
|---|---|---|
| N2 · The Stamping-Die Room | copper and fired brick | verdigris green |
| N3 · The Caravan Warehouse | indigo and raw wool | lamp amber |

---

## S00 — Hub: The House of Wisdom (*La Casa de la Sabiduría*)
`s00-hub-patio-katia.png` · **16:9**, level header (`.level-presentation-media`).

> The inner courtyard of an Abbasid house of study in the late afternoon, contained
> mid-distance view, slightly elevated. The courtyard is rectangular, of fired brick, with a
> low fountain, not running, in the center and a grapevine giving shade on one side. **Two
> facing doors** in the long walls, different from each other: the one on the left is the
> mouth of a workshop — the orange glow of a forge and the arm of a screw press can be seen —
> and next to it waits a Siamese cat with an upright bearing, a scorched leather apron and an
> awl behind her ear (Rayhana). The one on the right is a warehouse gate, wider and of
> reinforced wood, with burlap bales stacked to one side; next to it, a stocky, older orange
> cat with a padded vest and keys at his belt (Salim). Between the two doors, in the center of
> the courtyard and still undecided, **KatIA has just arrived** — white cat with orange and
> black markings, green eye, teal mechanical ocular, mechanical arm and ear piercings, in an
> ivory linen tunic under a muted plum Abbasid overgarment, ears uncovered —, with the dust of
> the road on her and a saddlebag over her shoulder. In the background, very secondary and
> without detail, the entrance arch through which the last mule of a caravan is leaving.
> Slanting afternoon light, warm amber on the brick and cool blue shadow under the vine. No
> legible text, number or symbol anywhere in the image; the bales are stacked irregularly and
> cannot be counted.

**Hub optionals** (1:1, same pattern as N2's `e00-ice*`): `s00-ice1-sacos.png` (three
identical burlap sacks leaning against a brick wall, next to a steelyard scale) ·
`s00-ice2-fardo-cerrado.png` (a tied and sealed bale on a stone slab, with no label) ·
`s00-ice3-dos-puertas.png` (the two courtyard doors seen head-on, one with a forge glow and the
other in shadow, no characters).

# ALG-N2 · The Stamping-Die Room (*La sala de los troqueles*) — Rayhana · copper and brick

A stamping workshop inside the House of Wisdom. The four rooms share space and forge light,
but **do not share vocabulary**: matrix/sheet/rim (P01) · stamp/frieze band/fret (P02) ·
mold/layer/clay (P03) · tray/slot/pair (P04). Do not mix the lanes across images.

## P01 · The Square Matrix (*La matriz cuadrada*)
`p01-cuadrado-katia.png` · **4:3**

> Interior of a stamping workshop in warm half-light. On a thick wooden bench rest several
> square copper plates of different sizes, stacked with felt separators. A Siamese cat with
> an upright bearing and a scorched leather apron (Rayhana) holds up a freshly stamped copper
> sheet and tilts it toward the light: the relief comes out crisp in the center but **a strip
> along the edge came out smooth, unstamped**, with the die mark cut off halfway across the
> rim. KatIA, standing on the other side of the bench, looks at the strip without touching
> it. In the background, an iron screw press and the mouth of a forge with low embers. Orange
> ember light from the right, cool blue shadow everywhere else. No numbers or letters visible
> anywhere; the sheets carry no grid or countable marks.

## P02 · The Frieze Stamp (*El cuño de la cenefa*)
`p02-conjugados-katia.png` · **4:3**

> A long table for stamping frieze bands: long, narrow copper strips laid across the width
> of the frame, held down by battens. Rayhana leans over an elongated stamp that **has jammed
> halfway through its stroke**, twisted in its guide, with a blob of black ink spilling over
> one side of the strip and the fret pattern broken off on the other. A stained rag and a
> tipped-over ink pot by her elbow. KatIA crouches to table height to look at the stamp from
> the side, her teal ocular lit. In the background, a turned-wood lattice panel filters the
> street light into stripes. The fret pattern on the copper is ornamental and geometric, with
> no signs or figures.

## P03 · The Three-Layer Mold (*El molde de tres capas*)
`p03-cubo-katia.png` · **4:3**

> A molding corner at the back of the workshop, darker and damper. On a stone slab stand
> tall fired-clay molds, opened into two halves, and a heap of clay covered with a wet cloth.
> A tabby apprentice cat holds in both hands a freshly unmolded cubic block that **has cracked
> open and shows it is hollow inside**, with thin walls and an empty interior. Rayhana points
> at the hollow without scolding. KatIA, in the side foreground, studies the broken section of
> the block. Brick floor, mud splatters, a bronze lamp hanging at the top left. Nothing
> written, no numbered molds.

## P04 · The Pairs Tray (*La bandeja de parejas*)
`p04-termino-comun-katia.png` · **4:3**

> The last table in the room, tidier than the previous ones. On it, wooden trays divided into
> rectangular slots, like movable-type cases. A set of identical copper tokens waits in a
> bowl. Rayhana holds an open leather-bound ledger and frowns at the tray like someone who
> has just found that the count does not add up; **an entire strip of slots was left empty**
> while the rest are full. KatIA stands opposite, resting a hand on the edge of the tray. In
> the background, shelves with more stacked trays and, very secondary, the press from the
> front of the room. The tokens in the bowl are heaped up in no order, impossible to count;
> the empty slots do not form a shape that could be read as a quantity.

---

# ALG-N3 · The Caravan Warehouse (*El almacén de la caravana*) — Salim · indigo and wool

The other end of the building: where the dies stamped, here things get opened. A caravan
warehouse with a scale at the door, a catalog of tracings, a breakdown bench, a cellar below
and a shipping room at the exit. Vocabulary lanes: bale/scale/delivery note (G01) ·
imprint/tracing/catalog (G02) · breakdown/slat/notch (G03) · barrel/stave/hoop (G04) ·
waybill/seal/consignment (G05).

## G01 · The Intake Weighing (*El pesaje de entrada*)
`g01-factor-comun-katia.png` · **4:3**

> The inner door of a caravan warehouse, seen from inside. A steelyard scale hangs from the
> lintel and a worn wooden counter crosses the frame. On the counter, **a burlap bale already
> opened and half untied**, with the cord still tangled and the bundles inside poking out,
> not fully separated. A stocky, older orange cat with a padded travel vest and keys at his
> belt (Salim) holds a delivery-note tablet with a crossed-out note, visibly illegible. KatIA
> stands next to the bale, with one hand on the open burlap. In the background, more bales
> stacked against a brick wall and the bright opening of the courtyard. No legible figures on
> the tablet or on the bale tags; the bundles inside are half hidden and cannot be counted.

## G02 · The Imprint Check (*El cotejo de huellas*)
`g02-cuadrados-katia.png` · **4:3**

> A narrow matching room, with lamplight over a single table. On the wall, a panel of
> tracings hung from strings: paper sheets with embossed die impressions, all different and
> none legible. On the table, a thick catalog open to the middle and, next to it, **a bale
> that arrived sealed and that someone forced open**: the burlap torn, the wax seal broken in
> two halves. Salim has one finger resting on a catalog page and his eyes on the broken bale.
> KatIA holds a tracing against the light, comparing it with the panel. **An empty gap between
> two sheets hanging from the string**, with the string visible and no sheet. Dominant indigo,
> lamp amber over the table. None of the imprints on the panel is a symbol, letter or number:
> they are geometric relief textures.

## G03 · The Breakdown Table (*La mesa de despiece*)
`g03-trinomio-katia.png` · **4:3**

> A long workbench at the back of the warehouse, with a row of notches carved into its edge
> for checking measurements. On the bench, **two already cut wooden slats that do not fit the
> notch**: one falls short and the other sticks out, resting unevenly on the edge. Next to
> them, a bow saw and a pile of wood shavings. A calico porter cat stands staring at the slat
> that sticks out, ears flattened back. Salim, behind, does not intervene. KatIA has crouched
> to the height of the bench edge to look at the notch in profile. Cool side light from a
> small high window, lamp amber over the bench. No written measurements, no legible graduated
> ruler, no slat marked with figures.

## G04 · The Barrel Cellar (*La bodega de los toneles*)
`g04-cubos-katia.png` · **4:3**

> A vaulted cellar under the warehouse, bare brick and cold air. Wooden barrels with iron
> hoops rest on chocks at mid-height. Salim comes down the last steps holding an oil lamp up
> high, and the circle of light falls on **an overfilled barrel: a dark trickle runs down the
> stave and pools on the floor under the badly fitted bung**. On the wall, a chalk note
> crossed out and smudged, illegible. KatIA stands next to the leaking barrel, looking up at
> the bung. In the background, the vault fades into dark blue. The barrels at the back are in
> shadow and do not form a countable row; no mark on the wall is a legible number.

## G05 · The Shipping Room (*La sala de expedición*)
`g05-expedicion-katia.png` · **4:3**

> The warehouse's outgoing room, with the gate ajar onto the loading yard and afternoon light
> slanting in. On a high counter, a paper waybill with a wax seal, and next to it **a seal
> already broken**: the wax split and the cord cut, lying on the table. Behind, a consignment
> of bundles ready to leave, with **one loose bundle set to one side, left out of the tied
> load**. Salim looks at the broken seal with his hands resting on the counter. KatIA stands
> with her back to the gate, her eyes on the loose bundle. At the far end of the yard, very
> secondary and without detail, two different routes leading out of the compound. The waybill
> is written in illegible strokes; the bundles are stacked irregularly and cannot be counted.

---

# Optionals · the nine traps

Same style, **1:1** format, for the trap card (`worked_examples` with `trap: True`). They all
show an apprentice or porter **in the moment before realizing**, never the correction. None
has visible numbers or formulas.

| File | Scene |
|---|---|
| `p01-trampa-orla.png` | An apprentice cat sets two small copper pieces on the bench and walks away, satisfied, leaving the rest of the bench empty. |
| `p02-trampa-suma.png` | An apprentice presses the stamp down with both hands on a strip that is already crooked in the guide. |
| `p03-trampa-capas.png` | An apprentice closes the two halves of a tall mold having poured clay only into the bottom and the lid. |
| `p04-trampa-fila.png` | An apprentice seals a tray that still has a strip of empty slots, without looking at it. |
| `g01-trampa-albaran.png` | A porter signs a delivery note with the bale still half tied behind him. |
| `g02-trampa-catalogo.png` | A porter slashes open the burlap of a bale with the catalog closed under his elbow. |
| `g03-trampa-corte.png` | A porter puts the saw down after cutting, with the two slats on the bench and the notch in view, without having tried them. |
| `g04-trampa-arqueo.png` | A porter closes up a barrel, taking the gauging as good, with the measuring rod still leaning against the wall. |
| `g05-trampa-precinto.png` | A porter presses the wax seal onto the waybill with a loose bundle visible at the back of the room. |

---

## Checklist before accepting an image

1. Is KatIA recognizable as the same KatIA from `katia-primer-plano-enteros.png`, in Abbasid-context clothing (not the Greek toga), with the mechanical arm, ears and piercings visible?
2. Does the space read as an Abbasid interior and **not** as an Orientalist postcard?
3. Is there any legible text, figure or symbol? If so, reject it.
4. Can the exercise be solved by counting objects in the image? If so, reject it.
5. Does the scene show the **consequence** of the mistake and not the correct calculation?
6. Does the visual vocabulary step into another room's lane (a frieze band in P01, a barrel in G03)? If so, reject it.
