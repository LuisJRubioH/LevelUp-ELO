# Spot corrections - Pre-algebra images

Base path: `Implementacion/image-prompts/referencias/generated`

Use this file when the corrections are small and specific.
Do not fill in a sheet for every image: record only the images you are actually going to correct.

## How to use it

1. Pick the image from the compact catalog.
2. Add a row under `Active corrections`.
3. Copy the minimal block into the generation session.
4. Generate only that image.
5. Mark the row as `Approved` when it is done.

## Active corrections

| Status | Image | Target version | Specific change | Keep | Do not |
|---|---|---|---|---|---|
| Approved | n3-fabrica: m00-hub-fabrica-v5.png, m01-conmutativa-katia-canon-v10.png, m02-asociativa-katia-canon-v10.png, m03-distributiva-katia-canon-v10.png, m04-elemento-neutro-katia-canon-v10.png, m05-inversos-katia-canon-v10.png | v5 / canon-v10 | Regenerating KatIA from a free prompt was ruled out. New character-free backgrounds were used, composited with `Implementacion/image-prompts/referencias/katia-canon-sprite-hard.png` to preserve the original identity. | Teaching composition, factory machines, night bronze/purple/teal palette, the objects of each scene. | Do not use the v4 images as a character reference again; no chibi/kawaii/baby kitten; do not soften into digital painting; do not change the tunic or the ocular. |
| Approved | n4-puerto: c00-hub-puerto-katia-canon-v10.png, c01-divisibilidad-katia-canon-v10.png, c02-multiplos-katia-canon-v10.png, c03-primos-katia-canon-v10.png, c04-factorizacion-katia-canon-v10.png, c05-mcd-katia-canon-v10.png, c06-mcm-katia-canon-v10.png | canon-v10 | Regenerating KatIA from a free prompt was ruled out. New character-free backgrounds were used, composited with `Implementacion/image-prompts/referencias/katia-canon-sprite-hard.png` to preserve the original identity. | Teaching composition, close-up Greek port, cargo/routes/tablets, night lantern/purple/teal palette. | Do not use the v4 images as a character reference again; no chibi/kawaii/baby kitten; do not soften into digital painting; no tourist port or epic panorama. |

## Minimal block to paste

```text
Image:
Target version:

Specific change:

Keep:

Do not:
```

## Control prompt

```text
Work only on the indicated image.
Do not redesign the whole set.
Do not change images that are already approved.
Apply only the specific change described.
Generate a single new version with the name given in Target version.
```

## Approved global changes

Use only when a decision applies to several images.

| Scope | Decision | Exceptions |
|---|---|---|
| N3/N4 with KatIA | The v4 images are rejected as KatIA identity references. The approved solution for scenes with KatIA is to generate character-free backgrounds and composite the canonical sprite `Implementacion/image-prompts/referencias/katia-canon-sprite-hard.png` on top. | The v4 images may be used only as a rough composition/environment reference, never for KatIA's face, body proportions or finish. |

## Compact catalog

### n1-agora

```text
b01-bienvenida-v4.png
b02-pregunta-detonadora-v4.png
b03-escalera-necesidad-v4.png
b04-naturales-v4.png
b05-enteros-v2.png
b05-enteros-v4.png
b06-racionales-v4.png
b07-irracionales-v4.png
b08-reales-v4.png
b09-complejos-v4.png
b10-clasificador-i-v4.png
b11-clasificador-ii-v4.png
b12-detective-falsedades-v4.png
b13-diagnostico-v4.png
```

### n2-mercado

```text
e00-hub-mercado-v4.png
e00-ice1-ladrillos-v4.png
e00-ice2-tejas-v4.png
e00-ice3-puestos-v4.png
e01-deuda-pago-v4.png
e01-higos-reunidos-v4.png
e01-suma-katia-v4.png
e02-ceramica-vendida-v4.png
e02-dracmas-deuda-v4.png
e02-resta-katia-v4.png
e03-deuda-repetida-v4.png
e03-filas-tinajas-v4.png
e03-multiplicacion-katia-v4.png
e04-division-katia-v4.png
e04-reparto-exacto-v4.png
e04-reparto-residuo-v4.png
e05-crecimiento-niveles-v4.png
e05-exponente-negativo-v4.png
e05-potenciacion-katia-v4.png
e06-cuadrado-perfecto-v4.png
e06-radicacion-katia-v4.png
e06-raiz-no-entera-v4.png
```

### n3-fabrica

```text
m00-hub-fabrica-v4.png
m00-ice1-balanza-bloques-v4.png
m00-ice2-balanzas-orden-v4.png
m00-ice3-retirar-pieza-v4.png
m01-conmutativa-katia-v4.png
m01-suma-conmuta-negativos-v4.png
m02-asociativa-katia-v4.png
m02-suma-asocia-negativos-v4.png
m03-distributiva-katia-v4.png
m03-distribuye-factor-negativo-v4.png
m04-cero-deja-negativo-v4.png
m04-elemento-neutro-katia-v4.png
m05-inversos-katia-v4.png
m05-opuesto-descargar-prensa-v4.png
m05-reciproco-recomponer-plancha-v4.png
```

### n4-puerto

```text
c00-hub-puerto-v4.png
c00-ice1-naranjas-reparto-v4.png
c00-ice2-postes-primos-v4.png
c00-ice3-carretas-tela-v4.png
c01-canicas-amigos-v4.png
c01-divisibilidad-katia-v4.png
c01-entradas-feria-v4.png
c02-corredor-completo-v4.png
c02-multiplos-katia-v4.png
c03-compuesto-vecinos-v4.png
c03-contar-divisores-v4.png
c03-primos-katia-v4.png
c04-cadena-larga-v4.png
c04-division-sucesiva-v4.png
c04-factorizacion-katia-v4.png
c05-mcd-factores-comunes-v4.png
c05-mcd-katia-v4.png
c06-mcm-factores-v4.png
c06-mcm-katia-v4.png
```
