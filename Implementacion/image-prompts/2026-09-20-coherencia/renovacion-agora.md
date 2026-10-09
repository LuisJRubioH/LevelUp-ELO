# Renovación integral de las imágenes antiguas

El usuario amplió el alcance: renovar color, intensidad, estilo y detalle con el generador actual, tomando N2 como referencia. Conservar narrativa y contenido matemático. No limitar el trabajo a corregir brazos.

Primer lote: B01, B04, B05, B06 de Ágora. Originales guardados en arte/descartes/antes-coherencia-2026-09-20/01-prealg-n1-agora. Generador integrado image_gen.

## Prompt base

Use case: style-transfer. Completely repaint and upgrade image 1, an older lesson illustration, to the rendering quality, rich controlled color saturation, luminous highlights, clean readable cool shadows, precise material detail and sophisticated crisp pixel art of image 2. Image 1 supplies the exact narrative, characters, framing and props; image 2 supplies art direction and adult KatIA body proportions; image 3 supplies canonical face only. Preserve original Greek night scene, no daytime conversion. Raise midtone clarity and color separation, rich plum fabric, amber lamp light, blue stone shadows, finely constructed marble/mosaic/wood/metal textures with deliberate visible pixel clusters. No blurry smoothing, photorealism, chibi or excessive grain. KatIA must be adult white feline, teal ocular viewer LEFT with full silver plate, natural green eye viewer RIGHT, orange/black patch near viewer RIGHT ear, silver ear piercings. CRITICAL correction: image 1 has the wrong robotic side. In final, the arm on viewer LEFT must be entirely organic WHITE FUR shoulder through fingers; the arm on viewer RIGHT must be entirely articulated SILVER ROBOTIC METAL shoulder through fingers. Keep poses; exchange materials not body positions. No mirrored face, extra arms or mixed furry/metal limb. All other cats organic. Retain all original story objects and their counts, no new writing, symbols or answers. This is a full quality renewal, not merely an arm correction. 

Referencias por llamada: imagen antigua correspondiente; frontend/public/leccion/02-prealg-n2-mercado/e00-hub-mercado-v4.png; Implementacion/image-prompts/referencias/katia-primer-plano-enteros.png.

Estado: B01, B04, B05 y B06 generadas, revisadas visualmente e instaladas en sus rutas originales. Conservan relato, props y ambiente nocturno. Brazos completos con lateralidad correcta. Se mejoraron color, claridad de sombras, iluminación y detalle de materiales con el generador integrado.

## Resultados

| Archivo | Salida aprobada |
|---|---|
| b01-bienvenida-v4.png | exec-8225d3db-799a-4739-bd74-9675f71c12c4.png |
| b04-naturales-v4.png | exec-beba8fe7-4d0b-4f5d-b97e-aefa52f10075.png |
| b05-enteros-v4.png | exec-17a674b1-6bc0-44cf-9fdd-0cab457a7334.png |
| b06-racionales-v4.png | exec-dfbb78e2-3979-40fb-84f8-0db5b2f8adda.png |

Salidas en C:/Users/orian/.codex/generated_images/01a0acf2-0b1f-7e13-b8bc-c82bdea44950/. Copiadas a frontend/public/leccion/01-prealg-n1-agora/.

## Instrucciones adicionales por escena

B01: Welcome scene: raised presenting hand on viewer LEFT white fur; lower hand holding stylus on viewer RIGHT and its entire arm metal. Preserve broad stairway and scholarly cats.

B04: The hand holding the small tablet at viewer LEFT is WHITE FUR and whole arm organic. Hand lifting basket fabric at viewer RIGHT and whole arm METAL. Preserve open empty chest, covered basket and tablet.

B05: The hand touching chin at viewer LEFT and entire connecting arm WHITE FUR. Resting hand on table viewer RIGHT and entire connecting arm METAL. Preserve balance scale with tied purple bundle on left pan and empty right pan, cat mason and tools.

B06: The hand touching chin at viewer LEFT and its entire connecting arm WHITE FUR. Resting hand on table viewer RIGHT and its entire arm METAL. Preserve five student cats, ONE whole uncut round loaf, covered basket, knife and tablets. Do not slice the bread.

B07: Preserve rope stretched along stone slab diagonal, its other segment along slab edge, and scholar measuring circular rope behind. KatIA kneels with both hands on rope: viewer LEFT hand and entire arm WHITE FUR, viewer RIGHT hand and entire arm METAL.

B07 produjo exec-7721c413-a870-45c7-9183-dbf092688ff2.png: acabado mejorado, pero brazo incorrecto. RECHAZADA, no instalada. Su corrección recibió límite 429 (resets_at 1789972011). No se reintentó tras el límite.

## Continuación 2026-09-21

Instaladas y revisadas además: B07 (exec-954b89c6-1305-46d5-96ff-6c03425b45a1.png), B08 (exec-54841822-cc44-41bd-869f-67c30897a5c1.png), B10 (exec-23fbe8a7-4440-4761-8369-f8710436ef58.png), B11 (exec-fa53b5fa-7652-41a5-a93d-3841f5ce6064.png), B12 (exec-85e7f567-e37a-4bed-8949-cc06e2ff3517.png). Total instalado hasta aquí: 9/13.

B02: revisada visualmente mediante conversión de visualización a JPEG con System.Drawing, sin modificar el original. El generador confirmó error CRC en IDAT del PNG original: expected 0x9bdf05b7, have 0x2ba975c1. Su contenido se recuperó para referencia en b02-preview.jpg. Las afirmaciones previas de que era solamente un fallo del visor quedan superadas por este diagnóstico.

B09: dos propuestas de renovación descartadas por escala del plano complejo (exec-2ca171ca-9648-4dcd-9b9b-e0083109f075.png y exec-321ebe6c-2ace-41a5-930c-08ce30733f02.png). No instaladas.

Prompts de esta continuación: lote-2026-09-21.json, correcciones-2026-09-21.json, lote-2026-09-21-b.json, lote-2026-09-21-c.json. Corrección B07: intercambio de materiales de ambos brazos manteniendo pose y rostro, brazo hacia izquierda de pantalla blanco y hacia derecha de pantalla metálico.

## Cierre Ágora: 13/13 instaladas

B02 final: exec-20475c02-eee8-4733-9007-caaceda708ad.png. B03 final: exec-226ca0e1-ba2d-43e3-a767-aab2a457dac1.png. B13 final: exec-cbcac61f-2511-4794-a559-2e07472513e5.png. B09 final: exec-2b2cb711-01cb-495c-828d-9d962e6ba722.png.

En B03/B13 se giró el torso hacia el espectador para resolver la ambigüedad anatómica sin cambiar posición en la escena. B09 se reconstruyó en dos pasos: borrar diagrama defectuoso y dibujar ejes ortogonales con proyecciones correctas para 1+i, 2+i, 2-i y -1-2i. Los cuatro puntos y sus etiquetas quedaron revisados visualmente. El amanecer de B13 y la noche de las otras escenas se mantienen.

Pendiente: renovación de grupos antiguos fuera del Ágora. Se inicia 00-comunes con respaldo de originales.
