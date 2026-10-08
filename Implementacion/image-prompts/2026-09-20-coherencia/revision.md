# Revisión de coherencia con N2 — 2026-09-20

Inventario: 67 PNG anteriores a la renovación de N2. Inspección visual completa; B02 se visualizó mediante copia JPEG y su PNG antiguo con error CRC fue reemplazado durante la renovación.

Actualización: el usuario pide una renovación integral de color, intensidad, estilo y detalle de las imágenes antiguas. Ver renovacion-agora.md. La corrección anatómica forma parte de esa renovación.

Correcciones anatómicas instaladas y revisadas en Kemet: A00, L01, L02, L03, L04, O01, O02, F04, R01 y R02. La primera propuesta de L03 se rechazó; la nueva corrección del 2026-09-28 respeta la oclusión tras el aprendiz. Ver kemet-2026-09-28-revision.md. Los estados de la tabla siguiente corresponden al diagnóstico inicial.

Referencia: rostro original `referencias/katia-primer-plano-enteros.png` y nueva cabecera N2. Izquierdo anatómico completamente metálico, derecho orgánico; ocular en el lado opuesto al brazo metálico. Vestuario contextual, pixel art, proporciones adultas. Las diferencias de luz diurna/nocturna y de arquitectura entre culturas son intencionales.

## Estado actualizado 2026-09-28 — completado

- Ágora: 13/13 renovadas e instaladas; ver renovacion-agora.md.
- Comunes: 6/6 renovadas e instaladas; ver comunes-revision.md.
- B02: inspección visual completada mediante copia JPEG de visualización. Se confirmó error CRC del PNG antiguo al enviarlo al generador; fue sustituido por la nueva generación revisada. Auditoría visual completa de las 67 anteriores.
- Fábrica: 11/11 renovadas e instaladas; ver fabrica-revision.md.
- Puerto: 10/10 renovadas e instaladas; ver puerto-revision.md.
- Kemet: diez correcciones anatómicas completadas; siete imágenes recientes compatibles conservadas.
- Bagdad: diez imágenes recientes compatibles conservadas tras revisión visual.
- Total anterior a N2: 40 renovadas, 10 corregidas, 17 conservadas compatibles = 67 revisadas. N2 ya estaba renovado (15/15).
- Verificación final: las 40 renovadas se decodifican correctamente y sus hashes difieren de los originales respaldados. No se cambió código ni contenido matemático.

La tabla siguiente conserva el diagnóstico inicial, anterior a las correcciones y renovaciones indicadas arriba.

| Grupo | Hallazgos | Estado |
|---|---|---|
| Kemet, A00, L01–L04, O01–O02 | Brazo mecánico derecho anatómico; intercambiar materiales de ambos brazos sin reflejar rostro | Pendiente de corrección |
| Kemet, F04, R01, R02 | Mano de pelo al final del antebrazo robótico izquierdo | Pendiente de corrección |
| Kemet, F01–F03, O03–O04, R03–R04 | Identidad y estilo compatibles; barro en F01/F02 corresponde al campo inundado, F03 seco limpio | Conservar |
| Bagdad, P01–P04, S00, G01–G05 | Laterales, manos, rostro y vestuario contextual coherentes | Conservar |
| Comunes, seis imágenes | Brazo derecho mecánico, pendientes y acabado anteriores; menor definición en sprites | Pendiente de armonización |
| Ágora B01, B04–B07, B09–B12 | Brazo derecho mecánico; B10 además termina en mano orgánica | Pendiente de corrección |
| Ágora B08 | Vista posterior: brazo mecánico a la derecha anatómica | Pendiente de corrección |
| Ágora B03, B13 | Pose girada: revisar conexión de hombros al armonizar; rostro y proporciones antiguos | Pendiente de armonización |
| Ágora B02 | No decodificable con view_image | Pendiente de revisión visual |
| Fábrica, once imágenes | Ocular y mancha frontal difieren del original, pendientes dorados largos; contraste demasiado oscuro frente a N2. Hub más próximo al rostro canónico | Pendiente de armonización |
| Fábrica ICE1, ICE3, opuesto, recíproco | Además mano derecha metálica sobre antebrazo orgánico | Pendiente de corrección |
| Puerto, diez imágenes | Mismo rostro/ocular/mancha frontal/pendientes alternativos de Fábrica; sombras muy cerradas | Pendiente de armonización |
| Puerto ICE2 | Además mano derecha metálica sobre antebrazo orgánico | Pendiente de corrección |

No se modifican diagramas ni contenido matemático al corregir identidad. No uniformar la iluminación de todas las culturas ni eliminar el barro de campos inundados.
