# Documentación de Oulad

Índice de todo lo que hay escrito, y de qué sirve para qué. Actualizado el
**2026-08-14**.

Si solo vas a leer una cosa, que sea el [README de la raíz](../README.md).

---

## Empezar

| Documento | Para quién |
|---|---|
| [../README.md](../README.md) | Cualquiera que abra el repo: qué es, cómo se levanta, cómo se prueba |
| [guia-estudiante.md](guia-estudiante.md) | Estudiantes — qué es el ELO, el diagnóstico, el mapa, la liga, los procedimientos |
| [guia-docente.md](guia-docente.md) | Docentes — leer el dashboard sin malinterpretar el ELO, calificar procedimientos, exportar |
| [ruta-de-aprendizaje.md](ruta-de-aprendizaje.md) | Quien escriba contenido: los 60 nodos, los 11 bloques, cómo añadir uno |
| [arquitectura.md](arquitectura.md) | Quien toque el backend: decisiones, límites conocidos y the runtime contract a deployment must meet |
| [transfer.md](transfer.md) | The owner, before merging the redesign into `main` (which deploys): backup, migration rehearsal, host settings, verification |

> Los PDF de la raíz (`guia_estudiante.pdf`, `guia_docente.pdf`) son **de mayo de
> 2026 y están obsoletos**: no cubren el diagnóstico, el mapa, la ruta de
> lecciones ni la liga, y todavía dicen «LevelUp-ELO». Los genera
> `scripts/generate_user_guides.py` con el contenido escrito dentro del propio
> script. La fuente de verdad ahora son los dos `.md` de arriba.

---

## Reglas de trabajo en el repo

| Documento | Qué contiene |
|---|---|
| [../CLAUDE.md](../CLAUDE.md) | Las reglas duras: dual DB, capas, conexiones, LaTeX, y las reglas V2-R1…R18 (una por decisión de arquitectura de contenido) |
| [../AGENTS.md](../AGENTS.md) | Equivalente para otros agentes |
| [../PRODUCT.md](../PRODUCT.md) | Marca, audiencia, personalidad, anti-referencias |
| [../DESIGN.md](../DESIGN.md) | Sistema de diseño: paleta, tipografía, motion |

**Lo que más se olvida:** cualquier cambio en un repositorio va en **los dos**
(`sqlite_repository.py` y `postgres_repository.py`), y `python
scripts/db_sync_check.py` lo verifica antes del commit.

---

## Contenido pedagógico

Todo vive en [`Implementacion/`](../Implementacion/).

| Documento | Qué es |
|---|---|
| [CABOS_SUELTOS.md](../Implementacion/CABOS_SUELTOS.md) | **El inventario de pendientes.** Verificado contra el repo, no de memoria. Empieza por aquí |
| [GUION_MAESTRO_NARRATIVA_PREALGEBRA.md](../Implementacion/GUION_MAESTRO_NARRATIVA_PREALGEBRA.md) | El mundo narrativo de Preálgebra |
| [MAPA_NODOS_ALGEBRA8.md](../Implementacion/MAPA_NODOS_ALGEBRA8.md) | El mapa de los cinco niveles de Álgebra |
| [MAPA_ITEMS_A_NODOS_N6_N10.md](../Implementacion/MAPA_ITEMS_A_NODOS_N6_N10.md) | Qué ítem del libro alimenta qué nodo, con conteos |
| `Fase_1/`, `Fase_2/`, `Fase_3/` | Las fichas pedagógicas por nodo, previas a la implementación |
| `specs/generadas/` | Una spec de ~400 líneas por nodo, **generada** desde su módulo |
| `image-prompts/` | Los prompts de imagen, por nivel, con el estilo base |

**Las specs se regeneran, no se editan:**

```bash
python scripts/generar_specs.py
```

Tres secciones no salen del código y quedan `PENDIENTE` en cada archivo:
estándares DBA/ICFES (A0), citas (A13) y handoff a Design (A14). Al rellenar una
a mano, **sacar el archivo de `generadas/`** — regenerar pisa la carpeta entera.

> **Citas:** ninguna se da por buena todavía. Viven en
> [Fase_2/CITAS_EN_REMOJO.md](../Implementacion/Fase_2/CITAS_EN_REMOJO.md) y la
> regla es: **se pueden usar para diseñar contenido, no para respaldarlo por
> escrito**. Falta la lista de la biblioteca aprobada del proyecto.

---

## Rediseño y estado del V2

| Documento | Qué es |
|---|---|
| [redesign/README.md](redesign/README.md) | El bundle de diseño exportado, con el mapa pantalla → archivo |
| [v2-plan.md](v2-plan.md) | Checklist de los sprints 1–8 del V2 |
| [v2-tecnico.md](v2-tecnico.md) | Notas técnicas del V2 |

`v2-plan.md` y `v2-tecnico.md` son de **mayo de 2026**: describen el V2 tal como
se cerró en producción, antes del rediseño de este playground. Son historia útil,
no estado actual.

---

## Scripts

| Script | Qué hace |
|---|---|
| `validate_bank.py` | Integridad del banco (49 archivos, 2.031 ítems). Corre en CI y en pre-commit |
| `db_sync_check.py` | Paridad de API entre los dos repositorios. Obligatorio antes de commitear repos |
| `generar_specs.py` | Specs legibles desde los módulos de nodo |
| `generate_user_guides.py` | Los PDF de guía (contenido hardcodeado, desactualizado) |
| `generate_banners.py` | Banners de curso |
| `extract_math_exercises_to_latex.py`, `verificar_*.py`, `manifiesto_caminos8.py` | Extracción y verificación de los libros de 8.º |
| `scan_dollar_prices.py` | Caza precios `$N$` que rompen el render de LaTeX |
| `monthly_metrics.py`, `train_calibrator.py` | Métricas y calibración |

---

## Dónde NO buscar

- `Implementacion/FORMATO_nodo_conjuntos_numericos.md` describe el **molde
  anterior** a la arquitectura de 11 bloques. Ya no aplica.
- `GUIA_UNIFICADA_CREACION_NODOS.md` y `GUIA_APLICADA_ALGEBRA_N1_...md`, que
  CLAUDE.md cita como guías operativas, **no están en el repo**. Lo que cubrían
  está ahora en [ruta-de-aprendizaje.md](ruta-de-aprendizaje.md).
