# Image prompts — N3 · The Retrofuturist Factory

Phase 7 of the unified script plan (`~/.claude/plans/effervescent-scribbling-goblet.md`).
Visual vocabulary of the space (Phase 0 / skill `prealgebra-narrative-style`): industrial
machines, gears, blocks, laboratory balance, levers, test benches. It is the most
"futuristic" space in the catalog — technological by default, not an occasional touch. Zero
agora/market vocabulary (no public-square columns or awning-covered stalls).

**Required visual line (`Implementacion/image-prompts/referencias/`):** use as direct references
`step-naturales.png`, `step-enteros.png`, `step-racionales.png`, `step-reales.png`,
`escalera-conjuntos.png`, `katia-primer-plano-enteros.png` and `caso-enteros-recta.jpg`.
Before generating, open/attach those images as visual references if the tool allows it;
otherwise, copy this whole visual line into the final prompt.

**Approved method for KatIA in N3:** do not regenerate KatIA from a free prompt. For a scene
with KatIA, first generate a background WITHOUT KatIA, without cats/main characters and with
free space to place her; then composite `Implementacion/image-prompts/referencias/katia-canon-sprite-hard.png`
on top. The canonical block below is used to validate identity, not to ask the model to
invent a new version of the character.

**KatIA canonical block (required for any image where she appears):** use
`katia-primer-plano-enteros.png` as an identity reference, not just a style reference. KatIA
is an adult cyborg cat, serene and Socratic, not a childlike mascot. Keep the proportions of
the original character: white face with a rounded adult muzzle, calm and observant
expression, large but not cartoonish ears, visible green almond-shaped eye, asymmetric
orange/black marking on the forehead and ear, teal mechanical ocular over the other eye with
grey metal plates, segmented mechanical paw/arm, purple Greek tunic with gold ornaments and
the silhouette of a tutor/teacher. If the frame is small, simplify the environment before
simplifying KatIA. She must still be recognizable as the same KatIA from the close-up.

**Base style:** `refined educational pixel art, high-quality narrative 16/32-bit style,
with visible pixel clusters, clean pixelated edges, block shading and subtle dithering, a
silhouette with visible pixel steps and little soft blending; NO hyperrealistic digital
painting or smooth illustration. Keep the visual language of the existing assets: KatIA
readable in the foreground/mid-ground, contained classroom/workshop-like scene, few helpers
or secondary characters, clear teaching objects on a workbench, night-blue shadows, golden
lamplight and small teal accents. KatIA must keep her identity: white cat with an
orange/black patch on her head, visible green eye, teal mechanical ocular, mechanical
paw/arm, purple tunic and gold ornaments; in N3 she may add a discreet work apron/harness
without hiding her silhouette or replacing the tunic. The factory is imagined Greek
machinery with bronze, brass gears, levers and steam pipes, not generic science fiction.`

**Secondary characters:** any human role mentioned in the prompts (helper, technician,
operator, etc.) must be depicted as an anthropomorphic animal. Preference: other bipedal
cats in Greek workshop aprons or harnesses, varied coats (tabby, black, grey, calico,
Siamese, orange, spotted white) and distinct fur textures. No realistic humans.

**Stairs and steps:** if a staircase, stairway or step appears in any image, it must be
completely clean: no symbols, letters, numbers, runes, marks, medallions, arrows, labels or
mathematical reliefs.

**Style negatives:** no hard sci-fi, no cyberpunk laboratory, no smooth digital painting,
no smoothed render, no airbrushed skin/fur, no soft antialiased edges, no saturated neon, no
giant machines hiding KatIA, no crowds, no anime/chibi, no kawaii, no baby kitten, no
oversized head, no childlike shiny eyes, no simplified sticker-style mascot, no realistic
humans, no turning KatIA into a fully metal cat or dressing her in full overalls.

**Hard rule:** every prompt describes the SITUATION, never the SOLUTION. No prompt shows the
numeric result of an exercise or a final value on a machine's display/scale.

---

## M00 — Hub: The Laboratory of Mysterious Properties (*El Laboratorio de las Propiedades Misteriosas*)

**Level header** (`.level-presentation-header` + `.level-presentation-media`, full width,
16:9) — from `welcome_text`/`scene_text`: "The laboratory has five industrial machines... a
demonstration, a guided series and a formalization."

> Interior of a retrofuturist Greek laboratory-workshop, contained like the assets in
> `Implementacion/image-prompts/referencias/`, with five different machines arranged in the
> space (a press, a smelting furnace, a conveyor belt, a bench gauge and a counterweight
> press — recognizable silhouettes but none with foreground detail), bronze pipes running
> along the ceiling, teal light coming from simple control panels. KatIA appears in the
> foreground/mid-ground in her purple tunic and a discreet work apron/harness, looking
> toward the five machines with a notebook in her paw.
> Base style + aspect ratio 16:9.

**Icebreaker ICE1** (numeric, square ~1:1) — from `icebreaker.items.ICE1.prompt`: "A
laboratory machine weighs 3 blocks of 4 kg each on the left pan."

> A bronze laboratory balance with articulated arms, with three identical metal blocks
> stacked on the left pan and the right pan empty, the pointer tilted to the left. No
> numeric marker visible on the scale.
> Base style + aspect ratio 1:1.

**Icebreaker ICE2** (single_select, square ~1:1) — from `icebreaker.items.ICE2.story` +
`support_objects`: "2 identical laboratory balances" with "one 5 kg gear and one 3 kg gear
per balance", placed in a different order.

> Two identical laboratory balances side by side. On the first, a mechanical helper places a
> large gear on the pan and then a small one on top; on the second, another helper places the
> small one first and then the large one on top. Both balances must show the pointer in the
> same tilted position, without marking the total weight.
> Base style + aspect ratio 1:1.

**Icebreaker ICE3** (numeric, square ~1:1) — from `icebreaker.items.ICE3.prompt`: "The
balance reads 9 kg with a test piece on it. When that piece is removed..."

> A laboratory balance with a single metal test piece on the pan and a mechanical hand (the
> machine's own articulated arm) about to remove it, frozen halfway. The balance pointer
> must be in an ambiguous/intermediate position, not yet indicating the final result after
> removing the piece.
> Base style + aspect ratio 1:1.

---

## M01 — Commutative Machine: the Swap Press (*la Prensa de Intercambio*)

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "assembly bench... place
3 gears first and then 6 screws, or the other way around."

> A mechanical assembly bench with two parts trays: one with bronze gears and another with
> silver screws, and an articulated robotic arm hovering over both trays as if deciding
> which one to start with. KatIA watches from a side control panel with analog gauges
> (needles, not digits).
> Base style + aspect ratio 4:3.

**Example 1 · Integers — "Addition commutes with negatives"** (square ~1:1) — from
`statement`: "At the assembly bench, even with a negative-weight piece on the scale, the
order of the addition does not change the total."

> A mechanical bench scale with two loading slots, one receiving a counterweight piece
> marked with an engraved "minus" symbol (no number) and the other empty, with two twin
> robotic arms ready to insert the pieces in either order. The scale pointer in a neutral
> position, without marking the result.
> Base style + aspect ratio 1:1.

---

## M02 — Associative Machine: the Smelting Furnace (*el Horno de Fundición*)

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "Three different ingots
enter the smelting furnace... smelt the left pair first... or group them the other way."

> A retrofuturist smelting furnace with three metal ingots of different sizes laid out on a
> feed belt before the mouth of the furnace, with a mechanical gripper arm hovering between
> the first pair and the third ingot, as if deciding which pair to smelt first. A teal/violet
> glow coming out of the furnace mouth.
> Base style + aspect ratio 4:3.

**Example 1 · Integers — "Addition associates with negatives"** (square ~1:1) — from
`statement`: "In the furnace, with a negative-weight ingot in the trio, regrouping the
smelting does not change the total."

> Three ingots on the furnace feed belt, one of them marked with a "minus" symbol engraved
> on its surface (no number), with grouping lines projected by the control panel showing two
> different ways of grouping the trio (a different pair marked each time) without indicating
> the final result of the smelting.
> Base style + aspect ratio 1:1.

---

## M03 — Distributive Machine: the Distributor Belt (*la Cinta Repartidora*)

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "The distributor belt
sends 3 boxes to each bay... 6 bays with small parts and 4 with large parts."

> A long industrial conveyor belt with multiple unloading bays numbered with generic symbols
> (no figures), distributing identical boxes to several bays at once through mechanical
> gates. Some bays with small parts piled up, others with large parts, without totaling any
> quantity.
> Base style + aspect ratio 4:3.

**Example 1 · Integers — "Distributes with a negative factor"** (square ~1:1) — from
`statement`: "On the distributor belt, a negative factor is distributed to each bay, keeping
the signs."

> The distributor belt with a central gate marked with an engraved "minus" symbol,
> distributing simultaneously toward two side bays, each one receiving a piece also marked
> with the same "minus" symbol as it falls, showing the distribution in full motion, without
> marking the final total in any bay.
> Base style + aspect ratio 1:1.

---

## M04 — Identity Element Machine: the Zero Gauge (*el Calibre Cero*)

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "On the factory gauge,
adding 0 grams of adjustment does not change the weight... multiplying by 1 turn does not
alter how many units it produces."

> A mechanical bench gauge with an indicator needle pointing at the exact center of its
> scale ("no adjustment" position), next to a knob marked with a single notch at the neutral
> point, and an already calibrated metal piece waiting to one side with no visible change.
> KatIA turns the knob gently without moving it off center.
> Base style + aspect ratio 4:3.

**Example 1 · Integers — "0 leaves a negative unchanged"** (square ~1:1) — from `statement`:
"On the gauge, adding 0 grams of adjustment to a piece with negative weight does not change
it, from either side."

> A metal piece marked with an engraved "minus" symbol on the gauge tray, with the gauge
> needle in the central neutral position (a "0" mark engraved on the scale itself, no other
> figures) and a second, identical ghost piece superimposed in transparency suggesting that
> "it did not change", without showing any numeric weight value.
> Base style + aspect ratio 1:1.

---

## M05 — Inverses Machine: the Counterweight Press (*la Prensa de Contrapesos*)

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "every adjustment has its
counterweight. If the press adds... pressure, the scale returns to zero... splitting a plate
into equal rations, putting them back together rebuilds the whole plate."

> A retrofuturist hydraulic press with a needle pressure gauge in the center, an arm applying
> pressure from above onto a metal plate divided into equal sections marked with cut lines,
> and a set of bronze counterweights hanging to one side, ready to "undo" the pressure. The
> pressure gauge needle in an intermediate position, not at zero.
> Base style + aspect ratio 4:3.

**Example 1 · Integers — "Opposite: unloading the press"** (square ~1:1) — from `statement`:
"On the press, the opposite of 6 kg of pressure is −6 kg because together they return the
scale to the identity 0."

> Close-up of the press's pressure gauge with the needle tilted to one side by the applied
> pressure, and next to it a bronze counterweight marked with an engraved "minus" symbol,
> about to be placed on the opposite arm of the press. The needle must not be shown already
> in the neutral position — the counterweight is about to be applied, not applied.
> Base style + aspect ratio 1:1.

**Example 2 · Rationals — "Reciprocal: rebuilding the plate"** (square ~1:1) — from
`statement`: "The reciprocal of 4 turns of the machine is 1/4 because their product is the
identity 1."

> A circular metal plate divided into four equal sections by engraved cut lines, with a
> single section already separated and lifted by a mechanical arm, showing the gap it leaves
> — suggesting the idea of "one part out of four" without showing the plate already fully
> rebuilt or marking the fraction with numbers.
> Base style + aspect ratio 1:1.
