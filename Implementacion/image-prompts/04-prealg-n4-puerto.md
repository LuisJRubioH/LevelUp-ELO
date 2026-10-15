# Image prompts — N4 · The Port of the Polis

Phase 7 of the unified script plan (`~/.claude/plans/effervescent-scribbling-goblet.md`).
Visual vocabulary of the space (Phase 0 / skill `prealgebra-narrative-style`): docks, ships,
cargo, routes, wax tablets. Retrofuturist touch allowed: navigation instruments with
occasional mechanical detail. Reference level (already validated, diverse, no overused
objects): oil amphorae, wheat sacks, cloth rolls, pottery, oranges, roof tiles, marble
columns, posts with route tablets.

**Required visual line (`Implementacion/image-prompts/referencias/`):** use as direct references
`step-naturales.png`, `step-enteros.png`, `step-racionales.png`, `step-reales.png`,
`escalera-conjuntos.png`, `katia-primer-plano-enteros.png` and `caso-enteros-recta.jpg`.
Before generating, open/attach those images as visual references if the tool allows it;
otherwise, copy this whole visual line into the final prompt.

**Approved method for KatIA in N4:** do not regenerate KatIA from a free prompt. For a scene
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
readable in the foreground/mid-ground, contained scene, few secondary characters, clear
teaching objects on a dock/control table, night-blue shadows, golden lantern light, warm
stone/wood and small teal accents on KatIA's ocular or on navigation instruments. KatIA must
keep her identity: white cat with an orange/black patch on her head, visible green eye, teal
mechanical ocular, mechanical paw/arm, purple tunic and gold ornaments. The space must read
as a close-up classical Greek port: docks, ships, cargo, routes, wax tablets and bronze
navigation instruments.`

**Secondary characters:** any human role mentioned in the prompts (merchant, scribe, child,
youth, porter, vendor, messenger, etc.) must be depicted as an anthropomorphic animal.
Preference: other bipedal cats in tunics, capes or Greek harbor clothing, varied coats
(tabby, black, grey, calico, Siamese, orange, spotted white) and distinct fur textures. No
realistic humans.

**Stairs and steps:** if a staircase, stairway or step appears in any image, it must be
completely clean: no symbols, letters, numbers, runes, marks, medallions, arrows, labels or
mathematical reliefs.

**Style negatives:** no epic port panorama, no huge fleet, no touristy coastal city, no
crowds, no hard sci-fi, no smooth digital painting, no smoothed render, no airbrushed
skin/fur, no soft antialiased edges, no saturated neon, no anime/chibi, no kawaii, no baby
kitten, no oversized head, no childlike shiny eyes, no simplified sticker-style mascot, no
realistic humans, no turning KatIA into a fully metal cat.

**Hard rule:** every prompt describes the SITUATION, never the SOLUTION. No prompt shows the
numeric result of an exercise, or a quantity of cargo arranged so that it could be counted to
solve the exercise by looking at the image.

---

## C00 — Hub: The Port of the Polis (*El Puerto de la Polis*)

**Level header** (`.level-presentation-header` + `.level-presentation-media`, full width,
16:9) — from `welcome_text`/`scene_text`: "here ships arrive and set sail... toward Athens,
Corinth, Delos, Miletus, Rhodes and Sparta... the port has six docks."

> Contained presentation framing from a dock control post, not a tourist panorama: KatIA in
> the foreground/mid-ground with a spyglass in her paw, next to a wooden table with route
> scrolls, wax tablets and a bronze astrolabe. Behind her, six wood-and-stone docks are
> suggested in depth, with a few sailing ships moored and posts with route tablets pointing
> to different destinations (city names, no numbers). Oil lanterns light the dock at
> nightfall.
> Base style + aspect ratio 16:9.

**Icebreaker ICE1** (multi_select, square ~1:1) — from `icebreaker.items.ICE1.prompt`: "A
merchant has 12 oranges and wants to share them equally."

> A merchant on the dock next to a basket of fresh oranges, with several smaller empty
> baskets arranged in a semicircle in front of him as sharing options, with no basket
> already holding shared-out oranges — only the original full basket and the empty ones
> waiting.
> Base style + aspect ratio 1:1.

**Icebreaker ICE2** (single_select, square ~1:1) — from `icebreaker.items.ICE2.story` +
`support_objects`: "5 wooden posts with tablets numbered 2, 3, 5, 7, 11" and "a measuring
rope trying to mark equal sections on each post".

> Five wooden posts driven into the dock, each with a route tablet engraved with a different
> number (2, 3, 5, 7, 11 — visible as numbers, since they are the exercise data, not the
> solution), and a harbor scribe with a measuring rope trying to mark equal sections on one
> of the posts, with a struggling expression. The rope must not be shown already divided into
> successful sections on any post.
> Base style + aspect ratio 1:1.

**Icebreaker ICE3** (numeric, square ~1:1) — from `icebreaker.items.ICE3.prompt`: "Each new
cart that arrives at the port brings 4 more cloth rolls than the previous one."

> A line of carts arriving at the port along a cobbled road, each cart with a visibly
> growing number of cloth rolls compared with the previous one (a visual progression, not
> exact/countable), the last cart still entering from the edge of the image without showing
> its full load.
> Base style + aspect ratio 1:1.

---

## C01 — Divisibility: the rule of exact sharing

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "a harbor scribe shares
out a ship's cargo... among the carts waiting on the dock... if the sharing does not come out
exact, some cart is left waiting or something is left over."

> A harbor scribe next to a newly moored ship, distributing cargo sacks toward several carts
> lined up on the dock, with some sacks still stacked on the dock stones, not assigned to any
> cart — suggesting the possibility of a leftover, without showing whether the sharing ends
> exactly or not.
> Base style + aspect ratio 4:3.

**Example 1 · Exact sharing — "Marbles among friends"** (square ~1:1) — from `statement`:
"36 marbles are shared equally among 4 friends."

> Four children sitting in a circle on the dock, each with a small empty cloth pouch in front
> of them, and a larger sack of colored glass marbles in the middle of the circle from which
> nothing has been shared out yet.
> Base style + aspect ratio 1:1.

**Example 2 · Sharing with a remainder — "Fair tickets"** (square ~1:1) — from `statement`:
"23 fair tickets are shared equally among 5 friends."

> Five youths in a line in front of a fair ticket booth on the dock, a vendor holding a deck
> of ceramic ticket-tablets, with one or two loose tablets set slightly apart from the main
> deck (suggesting a possible leftover) without it being possible to count them precisely.
> Base style + aspect ratio 1:1.

---

## C02 — Multiples: the numbers formed by repeating

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "A ship sets sail for
Rhodes every certain number of days. If it sailed today, on which future days will it sail
again?"

> A sailing ship leaving the dock toward the horizon, bound for Rhodes (route tablet visible
> on the dock), and in the foreground a circular stone calendar carved with regular marks and
> no written numbers, suggesting a repeated sailing cycle.
> Base style + aspect ratio 4:3.

**Example 2 — "The full runner"** (square ~1:1) — from `statement`: "A runner advances 4 km
every hour. What distance has he covered after 2, 3, 4, 6 and 9 hours?"

> A messenger running along a coastal road beside the port that recedes toward the horizon,
> with stone milestones evenly spaced along the road (no engraved numbers) marking the rhythm
> of his progress, the runner halfway between two milestones.
> Base style + aspect ratio 1:1.

---

## C03 — Prime numbers: the indivisibles

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "Some small poleis have
only one direct route: to the central port and no other."

> A bronze-and-parchment navigation map spread out on a dock table, showing several small
> islands connected to the central port by a single route line each (no routes crossing
> between them), while other, larger islands show multiple crisscrossing route lines. KatIA
> points at one of the single-route islands with a paw.
> Base style + aspect ratio 4:3.

**Example 1 — "Counting divisors"** (square ~1:1) — from `statement`: "11 has only the
divisors 1 and 11."

> A lone route post on the dock with a single tablet hanging from it, and a rope stretched
> directly from that post toward a single destination on the horizon, with no branches or
> intermediate posts.
> Base style + aspect ratio 1:1.

**Example 2 — "A composite with more neighbors"** (square ~1:1) — from `statement`: "18 has
more than two divisors: it is not prime."

> A route post on the dock with multiple ropes stretched toward several different
> destinations on the horizon, branching out from the same point, in clear visual contrast
> with the single-route scene of Example 1.
> Base style + aspect ratio 1:1.

---

## C04 — Prime factorization: the building blocks

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "Before storing the cargo
in the warehouse, it is best to break a large shipment down into its smallest indivisible
units."

> A dock porter taking apart a large cargo crate, pulling out ever smaller boxes nested
> inside one another (like Russian nesting dolls of packaging), with the smallest ones
> already lined up to one side, ready for the warehouse. KatIA supervises with an inventory
> tablet in her paw.
> Base style + aspect ratio 4:3.

**Example 1 — "Successive division"** (square ~1:1) — from `statement`: "Break 84 down by
dividing by primes until you reach 1."

> A series of cargo crates of decreasing size arranged as a descending staircase on the
> dock, each one open to show the next smaller crate inside, the last one still closed,
> without revealing how many times the process was repeated.
> Base style + aspect ratio 1:1.

**Example 2 — "A longer chain"** (square ~1:1) — from `statement`: "Break 72 down by dividing
by primes until you reach 1."

> A similar chain of nested crates, longer than the one in Example 1, stretching along the
> dock in perspective until it disappears into the background, without it being possible to
> count all the crates in the row.
> Base style + aspect ratio 1:1.

---

## C05 — Greatest common divisor: the largest sharing in common

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "Two shipments of
different sizes must be split into containers of the same size, with nothing left over in
either."

> Two cargo piles of clearly different sizes on the dock (one of wheat sacks, another of oil
> amphorae), and next to them a selection of empty containers in several possible sizes laid
> out in a row, as if evaluating which container would work for both piles with no leftover.
> No container should be shown already full.
> Base style + aspect ratio 4:3.

**Example 1 · Prime factorization — "GCD by common factors"** (square ~1:1) — from
`statement`: "Find the GCD of 225 and 180 by breaking both down at the same time."

> Two piles of cargo boxes of different sizes on the dock, each with a different route
> label, and between them a bronze comparison balance with the pointer aimed at the center,
> without marking any reference value.
> Base style + aspect ratio 1:1.

---

## C06 — Least common multiple: the first shared meeting point

**KatiaStorySlot** (image | copy column, ~4:3) — from `katia.body`: "A ship sails for Rhodes
every 4 days and another for Sparta every 6 days. Both sailed together today."

> Two different sailing ships leaving the same dock together at the same time, one on a
> course marked for Rhodes and the other for Sparta (route tablets visible), moving away in
> slightly different directions across the sea, with a circular stone calendar in the
> foreground marking the day of the joint departure and no other dates indicated.
> Base style + aspect ratio 4:3.

**Example 1 · Prime factorization — "LCM by factors"** (square ~1:1) — from `statement`:
"Find the LCM of 20 and 30."

> Two circular stone calendars partly overlapping in transparency, each with its own rhythm
> of sailing marks (different spacing between marks), suggesting the search for a point
> where both cycles coincide, without indicating which mark is the coincidence.
> Base style + aspect ratio 1:1.
