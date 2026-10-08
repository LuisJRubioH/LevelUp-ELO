"""Generates `05-alg-n1-kemet-PEGABLE.md`: the 36 Kemet prompts, each one self-contained.

The style block, the characters and the negatives are identical in all 36 and live
here only once. If the visual line needs fixing —it already happened with N2, which started
out as a market and ended up as buildings— edit THIS file and regenerate:

    python Implementacion/image-prompts/_gen_kemet_prompts.py

`05-alg-n1-kemet.md` is the design sheet (why each scene is the one it is). This script
produces the pasteable file.
"""
import io
import os

ESTILO = (
    "STYLE — refined educational pixel art, high-quality narrative 16/32-bit style, with "
    "visible pixel clusters, clean pixelated edges, block shading and subtle dithering. NO "
    "hyperrealistic digital painting, no 3D render, no flat vector. Contained mid-distance "
    "scene, few characters, clear and readable teaching objects on a table, floor or "
    "workbench. Night-blue shadows, warm oil-lamp light, limestone and whitewashed adobe. The "
    "space reads as the INTERIOR of an Ancient Egyptian compound: adobe walls, papyriform "
    "columns, stone lintels, reed mats, storage jars; the background architecture always "
    "secondary."
)

KATIA = (
    "KATIA — white cat with an orange and black patch on her head, visible green eye, teal "
    "mechanical ocular, segmented mechanical arm and ear piercings preserved. She wears "
    "sleeveless ivory Egyptian linen, a teal/purple bead collar and a narrow purple sash. "
    "No nemes headdress or pharaoh attire. Keep the adult face and proportions. Readable in the "
    "foreground or mid-ground. Do not turn her into a fully metal cat."
)

SECUNDARIOS = (
    "SECONDARY CHARACTERS — all are anthropomorphic animals, preferably bipedal cats with a "
    "linen kilt, apron or broad Egyptian collar; varied coats (tabby, black, grey, calico, "
    "Siamese, orange, spotted white). Never realistic humans."
)

GUIAS = {
    "meritka": (
        "GUIDE — Meritka: slender black cat, broad collar of blue beads, reed pen behind the "
        "ear. Same appearance in all four rooms of her house."
    ),
    "bakenra": (
        "GUIDE — Bakenra: stocky tabby cat, short leather kilt, rope over the shoulder. "
        "Same appearance in all four rooms of his house."
    ),
    "tabiry": (
        "GUIDE — Tabiry: calico cat, woven reed hat, bare muddy feet. "
        "Same appearance in all four rooms of her house."
    ),
    "iuty": (
        "GUIDE — Iuty: short-haired grey cat, pigment-stained apron, plumb bob at the belt. "
        "Same appearance in all four rooms of his house."
    ),
    None: "",
}

PALETAS = {
    "vida": "PALETTE — dominant turquoise and ochre, ink-black accent.",
    "obra": "PALETTE — dominant sand and terracotta, cool blue shadow accent.",
    "campos": "PALETTE — dominant fertile green and silt, turquoise water accent.",
    "canon": "PALETTE — dominant Egyptian blue and lime white, restrained gold accent.",
}

# Added only when KatIA is in the scene: a still life has no purple to keep.
PALETA_KATIA = " KatIA's purple sash stays as an accent over that dominant."

# Still lifes must stay empty: without this negative the generator adds a cat.
SIN_FIGURAS = (
    "NO FIGURES — pure still life: no KatIA, no guides, no secondary characters, no silhouettes "
    "or hands entering the frame. Only objects and architecture."
)

REGLAS = (
    "HARD RULES — the image shows the SITUATION, never the solution: no figures, no result, "
    "no quantity of objects arranged so that the exercise can be solved by counting in the "
    "image. Any written text (papyri, tablets) is illegible: ink strokes, no recognizable signs, "
    "and never Latin letters or numbers. Hieroglyphs are only acceptable as wall or column "
    "texture, never legible, never prominent and never on the surface where the action "
    "happens. If a staircase or step appears, it is completely clean: no symbols, letters, "
    "numbers, runes, marks, medallions, arrows or reliefs."
)

NEGATIVOS = (
    "NEGATIVES — no tourist panorama, no postcard pyramids at sunset, no Sphinx, no pharaoh or "
    "royalty, no mummies or tombs, no anthropomorphic Egyptian gods (Anubis, Thoth: the animals "
    "here are neighbors, not deities), no crowds, no public square as the focus, no smooth "
    "digital painting, no saturated neon, no hard sci-fi, no anime or chibi, no realistic "
    "humans, no watermarks or signatures."
)

# (file, ratio, house, guide, title, scene)
IMAGENES = [
    # ── Hub ──────────────────────────────────────────────────────────────────
    ("a00-hub-papiro-katia.png", "16:9 (level header, full width)", "vida", "meritka",
     "A00 · Hub — The Papyrus of the Four Houses",
     "Dim interior of an Ancient Egyptian archive room, at dawn. On a long wooden table, "
     "Meritka spreads out a large, visibly damaged papyrus: four sections are missing, four torn "
     "holes with irregular edges, completely empty. On the other side of the table, KatIA has "
     "just arrived and still carries the dust of the journey. Through the open doorway at the "
     "back, very secondary and without detail, four different buildings stand silhouetted "
     "against the sky: a whitewashed compound, a construction ramp, flooded fields and a "
     "workshop with scaffolding. Low oil-lamp light concentrated on the table; cool blue in the "
     "rest of the room."),
    ("a00-ice1-cestos.png", "1:1", "vida", None,
     "A00 · Icebreaker 1 — The grain baskets",
     "Tight still life, no characters: several wicker baskets full of grain stacked next to a "
     "two-pan floor scale, on a packed-earth floor. One basket is tipped on its side, empty. "
     "Whitewashed adobe wall behind. The number of baskets must not be clearly countable: some "
     "fall outside the frame and others are in shadow."),
    ("a00-ice2-registro.png", "1:1", "vida", None,
     "A00 · Icebreaker 2 — The two tablets",
     "Tight still life, no characters: two clay tablets leaning against a whitewashed adobe "
     "wall, side by side, with notes in illegible strokes. One is full of repeated short lines; "
     "the other has a single long line. A reed pen on the floor between the two."),
    ("a00-ice3-hueco.png", "1:1", "vida", None,
     "A00 · Icebreaker 3 — The missing piece of data",
     "Top-down close-up of an unrolled papyrus on a table. No characters. Lines of notes in "
     "illegible strokes and, in the middle of one of them, a deliberately blank space the size "
     "of a word. A reed pen resting on the edge of the papyrus, pointing at that gap without "
     "touching it."),

    # ── House I · The House of Life ───────────────────────────────────────────
    ("l01-variables-katia.png", "4:3", "vida", "meritka",
     "L01 · The Reed-Pen Room — Variables",
     "Interior of a scribes' office: niche shelves full of scrolls, a bowl of black ink, reed "
     "pens in a ceramic cup. Meritka holds up an unrolled papyrus in front of KatIA; on the "
     "papyrus the same short note is repeated many times in columns, in illegible strokes. In "
     "the background, a basket full of identical scrolls waiting to be copied. Turquoise "
     "morning light coming through a high window."),
    ("l02-constantes-katia.png", "4:3", "vida", "meritka",
     "L02 · The Sealed Shelf — Constants",
     "Meritka pulls a broken clay seal off the small door of a low shelf. Inside, on a folded "
     "cloth, three standard measuring objects: a wooden rod, a rope with evenly spaced knots and "
     "a polished stone weight with an engraved mark. KatIA leans in to look without touching. "
     "The rest of the room is an everyday workspace and is messy; only that shelf is clean and "
     "set apart. Contrast between the cool turquoise of the niche and the warm ochre of the "
     "room."),
    ("l03-traduccion-katia.png", "4:3", "vida", "meritka",
     "L03 · The Dictation Table — Translation",
     "A low dictation table. A messenger (a Siamese cat in travel sandals, still wearing his "
     "cloak) speaks standing up and in a hurry, one hand raised. Sitting in front of him, two "
     "young scribes write at the same time on two different tablets; the tablets are turned "
     "toward the viewer just enough to look busy, with illegible ink strokes that are clearly "
     "DIFFERENT from each other. Meritka watches standing, without intervening. KatIA in the "
     "foreground, looking from one tablet to the other."),
    ("l04-valor-numerico-katia.png", "4:3", "vida", "meritka",
     "L04 · The Tally Chamber — Numerical value",
     "A half-underground tally chamber with a low ceiling. Clay tokens stacked in columns and a "
     "knotted counting cord hanging on the wall. Meritka holds a tablet; next to her, on the "
     "floor, a long row of EMPTY wooden handcarts, far more than needed, waiting for a load that "
     "never arrived. KatIA looks at the empty carts. Grazing oil-lamp light and dust hanging in "
     "the air. No grain anywhere in sight."),

    # ── House II · The Pyramid Works ──────────────────────────────────────────
    ("o01-semejantes-katia.png", "4:3", "obra", "bakenra",
     "O01 · The Ramp — Like terms",
     "At the foot of an adobe construction ramp, mid-morning. Bakenra holds two shift tablets, "
     "one in each hand, looking from one to the other. Behind him, a crew of worker cats waits "
     "standing next to a loaded wooden sledge, not moving forward. On one side of the frame, "
     "coiled ropes; on the other, mallets and stacked tools — two clearly separate piles, not "
     "mixed. KatIA in the foreground between the two piles, looking at Bakenra's tablets. Sand "
     "dust in the air and cool blue shadow under the ramp."),
    ("o02-signos-katia.png", "4:3", "obra", "bakenra",
     "O02 · The Rigging Yard — Signs and parentheses",
     "An enclosed rigging storehouse yard: wooden pulleys hanging from a beam, ropes coiled on "
     "the floor, stone counterweights lined up against the wall. Bakenra holds a return-voucher "
     "tablet. On the back wall, a row of wooden racks for counterweights with several obvious "
     "empty slots. In the exit doorway, a crew walks away empty-handed. KatIA in the foreground "
     "next to the pulleys. Harsh midday light, short shadows."),
    ("o03-producto-katia.png", "4:3", "obra", "bakenra",
     "O03 · The Chisel Workshop — Product of monomials",
     "Inside the carving workshop: a long bench with chisels lined up by size, whetstones, "
     "stone chips on the floor, wooden templates hanging on the wall. Bakenra has left an order "
     "tablet on the bench and looks out through the doorway, where —very secondary and without "
     "detail— an almost empty stockyard with a few loose ashlar blocks can be seen. KatIA "
     "examines a chisel. White stone dust in the air."),
    ("o04-cociente-katia.png", "4:3", "obra", "bakenra",
     "O04 · The Foreman's Hut — Quotient of monomials",
     "A small, shaded site hut with reed mats and a shutterless window. On a shelf, the site "
     "census on tablets. Bakenra points at a line on one of them. Outside, seen through the "
     "window, a group of water carriers standing with their jars on their shoulders STILL FULL, "
     "undistributed, looking toward the hut. KatIA follows Bakenra's finger with her eyes. "
     "Mid-afternoon heat outside, deep shadow inside."),

    # ── House III · The Fields After the Flood ────────────────────────────────
    ("f01-simplificar-katia.png", "4:3", "campos", "tabiry",
     "F01 · The Divided Plot — Simplification",
     "A field freshly drained after the flood, shiny mud and the first green shoots. Tabiry "
     "holds a surveyor's rope stretched over the ground; the boundary stones have fallen over or "
     "disappeared and the field looks like a single continuous expanse, with no divisions. In "
     "the background, a small group of cat families waiting on their feet with their "
     "belongings. KatIA next to Tabiry, with her paws in the mud. Morning light and turquoise "
     "reflections in the puddles."),
    ("f02-suma-katia.png", "4:3", "campos", "tabiry",
     "F02 · The Mother Canal — Adding fractions",
     "Beside a main irrigation canal, with two ditches branching off it in different directions "
     "and a weir made of wooden planks. Tabiry has crouched down and plunged a hand into the "
     "canal water. On the bank, leaning against a stone, a tablet of irrigation turns. One of "
     "the two ditches runs visibly drier than the other. KatIA standing at the edge, looking at "
     "the water. High sky and dense greens on the banks."),
    ("f03-producto-katia.png", "4:3", "campos", "tabiry",
     "F03 · The Threshing Floor — Multiplying fractions",
     "A circular threshing floor of packed earth, with a wooden threshing sledge leaning at the "
     "edge and loose straw swirled by the wind. The threshing floor is practically EMPTY: hardly "
     "any grain is left to thresh. Tabiry holds a tablet and looks at the swept floor. In the "
     "background, the door of an adobe granary, open and dark. KatIA next to the threshing "
     "sledge. Very white midday light and short shadows."),
    ("f04-division-katia.png", "4:3", "campos", "tabiry",
     "F04 · The Seed Silo — Dividing fractions",
     "Inside a round adobe silo, with the seed forming a tall heap up to the middle of the wall. "
     "Against the wall, a stack of EMPTY, folded cloth sacks, unfilled. Tabiry holds a record "
     "tablet and points at the full heap with her other hand. KatIA looks at the empty sacks. "
     "Clear contrast between the abundance of the heap and the stack of unused sacks. A beam of "
     "light entering through a high slit window."),

    # ── House IV · The Canon Workshop ─────────────────────────────────────────
    ("r01-razones-katia.png", "4:3", "canon", "iuty",
     "R01 · The Canon Grid — Ratios and proportions",
     "A painters' workshop facing a whitewashed wall with a grid of taut string. On a table in "
     "the foreground, the small sketch of a motif; on the wall, the enlarged version of the same "
     "motif, visibly DISTORTED: stretched on one side and squashed on the other. Iuty looks at "
     "the wall with his arms crossed. KatIA compares the sketch with the wall. Secondary wooden "
     "scaffolding to one side."),
    ("r02-regla-de-tres-katia.png", "4:3", "canon", "iuty",
     "R02 · The Linen Dye — Rule of three",
     "The dye room: a large clay vat with dark liquid and a bench with skeins of linen. Skeins "
     "hang from the ceiling to dry; the first ones have full color and the last ones in the row "
     "are clearly dull and uneven. Iuty holds a tablet with the recipe. KatIA touches one of the "
     "faded skeins. Faint steam over the vat and a damp, reflective floor."),
    ("r03-porcentajes-katia.png", "4:3", "canon", "iuty",
     "R03 · The Gold Leaf — Percentages",
     "A gold beater's workroom: a polished stone table, a small mallet, stacks of ultra-thin gold "
     "leaves separated by parchment, fine tweezers. A gold beater (a spotted white cat, hands "
     "wrapped in cloth) has stepped back from the table with open, empty hands, in a gesture "
     "that he cannot go on. Iuty holds the commission tablet. On the table there is an obvious "
     "gap where the stack of leaves should continue. KatIA looks at the gap. Intense but "
     "restrained golds, no exaggerated metallic shine."),
    ("r04-variacion-katia.png", "4:3", "canon", "iuty",
     "R04 · The Lamp Room — Direct and inverse variation",
     "The workshop's night workroom. Six oil lamps spread around the room, all out except one "
     "that is burning down, its wick almost spent. In the center, a large oil jar tipped over on "
     "its side, empty. Iuty points at the jar. The wall frieze is half finished, in shadow. "
     "KatIA inside the circle of light of the last flame. A predominantly dark scene with a "
     "single small warm light source."),

    # ── Optionals · the traps ─────────────────────────────────────────────────
    ("l01-trampa-etiqueta.png", "1:1", "vida", None,
     "L01 · Trap — The rewritten note",
     "Top-down close-up, no characters: a reed pen resting on a papyrus where a short note "
     "appears struck through with a line and rewritten just below. Illegible ink strokes. A "
     "drop of dried ink next to the crossing-out."),
    ("l02-trampa-pozo.png", "1:1", "vida", None,
     "L02 · Trap — The well rim",
     "Tight top-down view of the circular rim of a stone well, with a rope crossing it from side "
     "to side through the center and dark water at the bottom. No characters. The circle of the "
     "rim fills almost the whole frame; no marks or measurements carved into the stone."),
    ("l03-trampa-tablillas.png", "1:1", "vida", None,
     "L03 · Trap — The two versions",
     "Two clay tablets of the same size, leaning side by side on a reed mat, with illegible ink "
     "strokes that are clearly different from each other. No characters. Side light that brings "
     "out the relief of the clay."),
    ("l04-trampa-carros.png", "1:1", "vida", None,
     "L04 · Trap — The extra carts",
     "A long row of empty wooden handcarts, seen in perspective and receding into the "
     "background, next to a noticeably small heap of grain in the foreground. No characters. "
     "Packed-earth floor, grazing light."),
    ("o01-trampa-monton.png", "1:1", "obra", None,
     "O01 · Trap — What does not mix",
     "Two separate piles on the sand: coiled ropes on one side, mallets and tools on the other, "
     "with a line drawn in the sand between them. No characters. Mid-height view, cool blue "
     "shadow."),
    ("o02-trampa-huecos.png", "1:1", "obra", None,
     "O02 · Trap — The empty racks",
     "Detail of an adobe wall with a row of wooden racks for stone counterweights: half occupied "
     "and half empty, alternating irregularly. No characters. Harsh midday light that picks out "
     "the gaps."),
    ("o03-trampa-acopio.png", "1:1", "obra", None,
     "O03 · Trap — The stockyard",
     "An ashlar stockyard seen from mid-distance, almost empty: a few loose blocks and the marks "
     "in the dust where the others used to be. No characters. Low horizon and a big sky."),
    ("o04-trampa-cantaros.png", "1:1", "obra", None,
     "O04 · Trap — The sharing that never happened",
     "Several full clay jars lined up against a shaded wall, with an upside-down sharing bowl on "
     "the floor next to them. No characters. Close detail, mid-afternoon light."),
    ("f01-trampa-mojon.png", "1:1", "campos", None,
     "F01 · Trap — The fallen boundary stone",
     "A stone boundary marker fallen in the mud and half sunk, with the flood line still wet "
     "around it. No characters. Low close-up, green and silt."),
    ("f02-trampa-acequias.png", "1:1", "campos", None,
     "F02 · Trap — The two ditches",
     "Two ditches branching off the same canal at an angle, one with a good flow and the other "
     "almost dry, its cracked bed exposed. No characters. Diagonal view from above."),
    ("f03-trampa-era.png", "1:1", "campos", None,
     "F03 · Trap — The swept threshing floor",
     "The circular threshing floor seen from the edge, swept and practically empty, with the "
     "door of the adobe granary open and dark in the background. No characters. Loose straw "
     "stirred by the wind."),
    ("f04-trampa-sacos.png", "1:1", "campos", None,
     "F04 · Trap — The unfilled sack",
     "A single empty cloth sack hanging from a wooden peg, in the foreground, with the full heap "
     "of seed behind it, blurred by the half-light. No characters. A beam of light from a high "
     "slit window."),
    ("r01-trampa-boceto.png", "1:1", "canon", None,
     "R01 · Trap — The sketch and its copy",
     "The small sketch of a motif and its enlarged, distorted copy, side by side on a workshop "
     "table. No characters. Top-down view, grid string coiled to one side."),
    ("r02-trampa-madejas.png", "1:1", "canon", None,
     "R02 · Trap — The uneven skeins",
     "A row of linen skeins hanging from a rod, fading from full color at one end to clearly "
     "washed out at the other. No characters. Whitewashed wall background and drips on the "
     "floor."),
    ("r03-trampa-pila.png", "1:1", "canon", None,
     "R03 · Trap — The gap in the stack",
     "Tight detail of a stack of ultra-thin gold leaves separated by parchment, on a polished "
     "stone table, with an obvious gap where the stack should continue. No characters. A pair of "
     "tweezers resting beside it."),
    ("r04-trampa-lampara.png", "1:1", "canon", None,
     "R04 · Trap — The last wick",
     "A single clay oil lamp in the foreground with its wick burning down, the flame tiny, "
     "against an almost black background. No characters. The only light source in the whole "
     "image."),
]

CABECERA = """# ALG-N1 · Kemet — all 36 prompts

Generated by `_gen_kemet_prompts.py`. **Do not edit by hand**: if the style, the characters or
the negatives need to change, edit the script and regenerate — that way the 36 stay identical
in everything that must be identical.

Each block is self-contained and is pasted as-is into the image generator. Destination for
the files: `frontend/public/leccion/05-alg-n1-kemet/`.

**Visual references:** if the tool allows it, attach before generating
`Implementacion/image-prompts/referencias/step-naturales.png`, `step-enteros.png`, `escalera-conjuntos.png`,
`katia-primer-plano-enteros.png` and `caso-enteros-recta.jpg`. They are the visual line to
keep.

**Suggested order:** first `a00-hub-papiro-katia.png` and one room from each house (L01, O01,
F01, R01). With those five, validate the style and the four guides before running the
remaining 31.

The design sheet —why each scene is the one it is— is in `05-alg-n1-kemet.md`.

---
"""


def bloque(archivo, ratio, casa, guia, titulo, escena):
    """Builds the prompt. A still life ("No characters") gets neither KatIA nor secondary characters."""
    vacia = "no characters" in escena.lower()
    con_katia = "KatIA" in escena
    partes = [
        f"SCENE — {escena}",
        ESTILO,
        "" if vacia else (KATIA if con_katia else ""),
        "" if vacia else GUIAS[guia],
        "" if vacia else SECUNDARIOS,
        SIN_FIGURAS if vacia else "",
        PALETAS[casa] + (PALETA_KATIA if con_katia and not vacia else ""),
        f"FORMAT — {ratio}.",
        REGLAS,
        NEGATIVOS,
    ]
    cuerpo = "\n\n".join(p for p in partes if p)
    return f"## {titulo}\n\n`{archivo}` · {ratio}\n\n```text\n{cuerpo}\n```\n"


def revisar():
    """Each image is either a declared still life or a scene with KatIA. There is no third case."""
    for archivo, _ratio, _casa, _guia, _tit, escena in IMAGENES:
        vacia = "no characters" in escena.lower()
        if not vacia and "KatIA" not in escena:
            raise SystemExit(
                f"{archivo}: neither says 'No characters' nor puts KatIA in the scene. "
                "A room without KatIA is an oversight, not a decision."
            )


def main():
    revisar()
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "05-alg-n1-kemet-PEGABLE.md")
    partes = [CABECERA] + [bloque(*fila) for fila in IMAGENES]
    io.open(destino, "w", encoding="utf-8").write("\n".join(partes))
    print(f"{len(IMAGENES)} prompts written to {destino}")


if __name__ == "__main__":
    main()
