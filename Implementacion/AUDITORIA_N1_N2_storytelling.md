# Auditoría y corrección de storytelling — Niveles 1 y 2

Fecha: 2026-06-28

Prompt aplicado: `PROMPT_auditoria_correccion_Niveles_1_y_2.md`

## Alcance

- Nivel 1: B04 a B13 en `Implementacion/Fase_1`.
- Nivel 2: E00 a E06 en `Implementacion/Fase_2`.
- Criterios revisados:
  - apertura narrativa con Katia y pregunta detonadora,
  - descubrimiento guiado,
  - definición formal integrada antes de práctica,
  - al menos 2 ejemplos trabajados antes de ejercicios,
  - práctica al final,
  - longitud mínima de A2.

## Tabla de auditoría

| Nodo | Archivo | Narrativa | Def+Ej | Arquit. | A2 líneas | Estado |
|---|---|---:|---:|---:|---:|---|
| B04 Naturales | `Fase_1/F1_nodo_naturales_reconstruido.md` | No | No | No | 267 | `[NARRATIVA FALTA] [DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |
| B05 Enteros | `Fase_1/F1_nodo_enteros.md` | Sí | Sí | Sí | 468 | `REPARADO` |
| B06 Racionales | `Fase_1/F1_nodo_racionales.md` | No | No | No | 406 | `[NARRATIVA FALTA] [DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA]` |
| B07 Irracionales | `Fase_1/F1_nodo_irracionales.md` | Sí | No | No | 386 | `[DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA]` |
| B08 Reales | `Fase_1/F1_nodo_reales.md` | Sí | No | No | 402 | `[DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA]` |
| B09 Complejos | `Fase_1/F1_nodo_complejos.md` | Sí | No | No | 475 | `[DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA]` |
| B10 Clasificador básico | `Fase_1/F1_nodo_clasificador_basico.md` | Sí | No | No | 295 | `[DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |
| B11 Clasificador riguroso | `Fase_1/F1_nodo_clasificador_riguroso.md` | Sí | No | No | 363 | `[DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA]` |
| B12 Detective falsedades | `Fase_1/F1_nodo_detective_falsedades.md` | No | No | No | 355 | `[NARRATIVA FALTA] [DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA]` |
| B13 Cierre diagnóstico | `Fase_1/F1_nodo_cierre_diagnostico.md` | Sí | No | No | 230 | `[DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |
| E00 Ciudad hub | `Fase_2/F2_nodo_ciudad_hub.md` | Sí | No | No | 39 | `[DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |
| E01 Suma | `Fase_2/F2_nodo_suma.md` | Sí | Sí | Sí | 450 | `CREADO / REPARADO` |
| E02 Resta | `Fase_2/F2_nodo_resta.md` | No | No | No | 121 | `[NARRATIVA FALTA] [DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |
| E03 Multiplicación | `Fase_2/F2_nodo_multiplicacion.md` | No | No | No | 125 | `[NARRATIVA FALTA] [DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |
| E04 División | `Fase_2/F2_nodo_division.md` | No | No | No | 102 | `[NARRATIVA FALTA] [DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |
| E05 Potenciación | `Fase_2/F2_nodo_potenciacion.md` | No | No | No | 134 | `[NARRATIVA FALTA] [DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |
| E06 Radicación | `Fase_2/F2_nodo_radicacion.md` | No | No | No | 143 | `[NARRATIVA FALTA] [DEF+EJ INCOMPLETO] [ARQUITECTURA ROTA] [A2 RESUMIDO]` |

## Correcciones aplicadas en esta pasada

### B05 Enteros

Archivo: `Implementacion/Fase_1/F1_nodo_enteros.md`

- Se insertó una apertura narrativa corregida antes de la primera práctica.
- Se agregó descubrimiento guiado con deuda, temperatura, recta numérica y contraejemplos.
- Se integró la definición formal de enteros en KaTeX antes de las interacciones.
- Se añadieron 3 ejemplos base con solución paso a paso.
- Se renumeraron las secciones A2 posteriores.
- Se añadió `phase_0_narrative_integrated_definition` en PARTE B.
- Resultado: A2 = 468 líneas; narrativa, definición+ejemplos y arquitectura quedan aprobadas.

### E01 Suma

Archivo creado: `Implementacion/Fase_2/F2_nodo_suma.md`

- El archivo no existía en `Fase_2`; se reconstruyó desde los recursos disponibles.
- Se creó PARTE A con narrativa, descubrimiento guiado, definición integrada y práctica de canasta.
- Se incorporaron los ejemplos base indicados en `VALIDACION_pedagogica_N2.md`.
- Se incluyó el caso `6 + 0 = 6` como trampa común.
- Se creó PARTE B con `interactividad.content.type = narrative_with_integrated_definition`.
- Resultado: A2 = 450 líneas; narrativa, definición+ejemplos y arquitectura quedan aprobadas.

## Pendiente recomendado

Orden sugerido para la siguiente tanda:

1. B04 Naturales, porque es el primer concepto numérico y quedó bajo de líneas.
2. E02 Resta, porque sigue inmediatamente a E01 y ya tiene material base reutilizable.
3. E03 a E06, porque todos los nodos N2 existentes tienen A2 resumido.
4. B06 a B13, priorizando los que tienen arquitectura rota aunque superen líneas.

## Comparación visual

No se generaron screenshots porque esta pasada trabajó sobre specs Markdown en `Implementacion`, no sobre una UI ejecutable. La comparación visual queda pendiente para cuando estos specs se implementen o se carguen en el frontend.
