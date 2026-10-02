# Image prompts — index

All image-generation prompts for the platform, **numbered by order of appearance in the
student's route**. The prompt number matches the art folder number in
`frontend/public/leccion/`.

| # | Level | Prompt | Served art | Done | Missing |
|---|---|---|---|---:|---:|
| 00 | — (global style) | [00-estilo-base.md](00-estilo-base.md) | `leccion/00-comunes/` | 6 | 0 |
| 01 | PREALG-N1 · The Agora | [01-prealg-n1-agora.md](01-prealg-n1-agora.md) | `leccion/01-prealg-n1-agora/` | 13 | 0 |
| 02 | PREALG-N2 · The City of Operations | [02-prealg-n2-ciudad.md](02-prealg-n2-ciudad.md) | `leccion/02-prealg-n2-mercado/` | 15 | 0 |
| 03 | PREALG-N3 · The Factory of Properties | [03-prealg-n3-fabrica.md](03-prealg-n3-fabrica.md) | `leccion/03-prealg-n3-fabrica/` | 11 | 0 |
| 04 | PREALG-N4 · The Port of the Polis | [04-prealg-n4-puerto.md](04-prealg-n4-puerto.md) | `leccion/04-prealg-n4-puerto/` | 10 | 0 |
| 05 | ALG-N1 · The Papyrus of the Four Houses (Kemet) | [05-alg-n1-kemet.md](05-alg-n1-kemet.md) · [pasteable](05-alg-n1-kemet-PEGABLE.md) | `leccion/05-alg-n1-kemet/` | 17 | 0 required (+16 optional) |
| 06 | ALG-N2 · The Stamping-Die Room (Baghdad) | [06-alg-n2-n3-bagdad.md](06-alg-n2-n3-bagdad.md) | `leccion/06-alg-n2-troqueles/` | 5 | 0 required (+4 optional) |
| 07 | ALG-N3 · The Caravan Warehouse (Baghdad) | [06-alg-n2-n3-bagdad.md](06-alg-n2-n3-bagdad.md) | `leccion/07-alg-n3-caravana/` | 5 | 0 required (+5 optional) |

**Verified 2026-09-20: all 27 required Kemet/Baghdad images are saved and referenced.**
The 15 N2 replacements are also complete (2026-09-20), preserving existing served paths.
Remaining separate work: 25 optional trap images.
N2 generation prompts: [2026-09-20-n2-ciudad/prompts.json](2026-09-20-n2-ciudad/prompts.json).
Use [IDENTIDAD-KATIA.md](IDENTIDAD-KATIA.md) for the corrected arm laterality; older prompts
may contain superseded wording. Exact generation and correction prompts are saved in
`2026-09-16-kemet-identidad/`.

The two Baghdad levels **share a hub** (`ALG-S00-CASA-DE-LA-SABIDURIA`): its header lives with
the dies, at `leccion/06-alg-n2-troqueles/s00-hub-patio-katia.png`.

## Known debts

- **N2 art renewed.** All 15 images now depict the City of Operations and its civic trades.
  The folder and file names retain `mercado` for compatibility with existing references.
  Previous assets are backed up outside public in `arte/descartes/n2-mercado-antes-ciudad/`.
- **The Kemet hub image is now present.** `05-alg-n1-kemet/a00-hub-papiro-katia.png`
  exists at the path referenced by `a00_hub.py`.
- The N4 hub pointed to `c00-hub-puerto-katia-canon-v10.png`, a composition that was never
  saved; it now points to `c00-hub-puerto-v4.png`, which does exist. If v10 turns up, change
  the reference in `prealgebra.py` and in `LevelFourLesson.tsx`.

## What is in each folder

- **`referencias/`** — the images the prompts cite as identity and style references
  (`katia-primer-plano-enteros.png`, the canonical sprites, `caso-enteros-recta.jpg`). The app
  does not serve them: they are generation material. Attach them to the tool before
  generating.
- **`correcciones/`** — the per-image correction sheets. They used to live inside
  `frontend/public/`, i.e. published on the web; now they are not served.
- **`_gen_kemet_prompts.py`** — generates `05-alg-n1-kemet-PEGABLE.md` from
  `05-alg-n1-kemet.md`, inlining the style block into every prompt. Only Kemet needs it
  (36 images); the other levels declare the style once.

## Where the rest is

- **Art served by the platform:** `frontend/public/leccion/NN-<level>/`, same numbering.
- **Discards:** `arte/descartes/` — superseded versions, KatIA-free backgrounds from the N4
  compositing method, and the N1 `amarillas/` set. Outside `public/`, so they are no longer
  shipped in the build.
