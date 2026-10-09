# La ruta de aprendizaje — 60 nodos, y cómo se añade uno más

Documento operativo del contenido guiado de Oulad: qué es un nodo, cómo se
encadenan, qué forma tiene por dentro y qué hay que tocar para crear el
siguiente. Verificado contra el repo el **2026-08-14**.

> Esto documenta la **ruta de lecciones**, que es contenido escrito a mano y
> **no mueve el ELO**. El banco adaptativo de 2.031 ítems (que sí lo mueve) se
> documenta en el [README](../README.md#banco-de-preguntas).

---

## 1 · Qué es un nodo

Un nodo es **una pantalla de lección completa**: abre con un diagnóstico corto,
enseña un concepto, deja cometer el error típico a propósito y cierra midiendo
si algo cambió. No es un ejercicio ni un tema — es una sesión.

Los 60 nodos viven bajo un solo curso, `algebra_basica`, y se sirven por tres
endpoints que **nunca tocan el motor ELO**:

```
GET  /api/student/lessons/{course_id}/{node_id}               → contenido + progreso
POST /api/student/lessons/{course_id}/{node_id}/events        → progreso idempotente
POST /api/student/lessons/{course_id}/{node_id}/interactions  → evalúa UNA selección cerrada
```

Los tres viven en [api/routers/student.py](../api/routers/student.py). El
contenido sale de [src/domain/learning/](../src/domain/learning/): un módulo por
nodo en `nodes/`, y `prealgebra.py` como registro que los engancha.

**Decisión cerrada (2026-08-13):** los 60 nodos van con `affects_elo: False`.
Álgebra guiada no mueve el rating; el rating se mueve practicando.

---

## 2 · Cómo se encadena la ruta

Cada nodo declara `unlock_after` (el nodo anterior). **El mapa se deriva de esa
cadena** — no hay una lista de orden mantenida a mano:

```python
# src/domain/learning/prealgebra.py
curriculum_map_rows(state_of, complex_visible=True)  # deriva el mapa de unlock_after
```

Consecuencias prácticas:

- Insertar un nodo en medio = cambiar dos `unlock_after`, nada más.
- El nivel al que pertenece un nodo lo fija su `unlock_after`, **no su prefijo**.
  `ALG-N2-P01` está en Bagdad porque cuelga del hub de Bagdad, no porque se
  llame `N2`.
- Un test (`test_map_states_come_from_unlock_after`) falla si alguien vuelve a
  cablear el orden a mano.

El desbloqueo es **secuencial estricto** salvo una excepción deliberada: los
complejos (`PREALG-N1-B09`) son un callejón opcional y nunca son «el siguiente
paso» (`test_the_optional_complex_detour_is_never_the_next_step`).

---

## 3 · Los siete mundos

KatIA —gata cyborg, la tutora— recorre siete escenarios. El mundo es **telón de
fondo**: nunca decide qué se enseña ni en qué orden.

| Mundo | Nodos | Escenario | Guía |
|---|---|---|---|
| **PREALG-N1** · Conjuntos numéricos | B01–B13 (13) | La escalera de la necesidad | KatIA |
| **PREALG-N2** · Operaciones | E00–E06 (7) | La ciudad de las seis operaciones (Grecia) | KatIA |
| **PREALG-N3** · Propiedades | M00–M05 (6) | La fábrica de propiedades | KatIA |
| **PREALG-N4** · Divisibilidad | C00–C06 (7) | El Puerto de la Polis | KatIA |
| **ALG-N1** · Fundamentos del álgebra | A00 + 16 salas (17) | El Papiro de las Cuatro Casas (Kemet) | Meritka · Bakenra · Tabiry · Iuty |
| **ALG-N2** · Productos notables | S00 + P01–P04 (5) | La sala de los troqueles (Bagdad) | Rayhana |
| **ALG-N3** · Factorización | G01–G05 (5) | El almacén de la caravana (Bagdad) | Salim |

ALG-N2 y ALG-N3 **comparten el hub** `ALG-S00-CASA-DE-LA-SABIDURIA`: son la
misma operación en dos direcciones —el taller estampa, el almacén abre lo
estampado— así que comparten antesala, con una tarjeta por ala.

**Regla dura, con test:** dos nodos no pueden compartir nombre de sala en toda
la ruta (`test_no_two_nodes_share_a_room_name`). Fue lo que obligó a renombrar
el «patio de los mosaicos» de Bagdad — chocaba con El Taller de Mosaicos de N2.

---

## 4 · La arquitectura de 11 bloques

**52 de los 60 nodos** declaran `content["kind"] == "eleven_block_node"` y se
pintan con un renderer **genérico** que no conoce ningún `node_id`:
[ElevenBlockLesson.tsx](../frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx).

Los 8 restantes son 5 hubs de nivel y 3 pantallas de N1 con renderer propio
(bienvenida, pregunta detonadora y cierre diagnóstico).

Una sola ventana, cinco zonas por color, once bloques:

| # | Bloque | Clave en `CONTENT` | Zona | ¿Bloquea el cierre? |
|---|---|---|---|---|
| 1 | Mini-diagnóstico | `diagnostic` | Explorar | No (`required=False`) |
| 2 | Apertura de KatIA + intento genuino | `katia` (+ `katia.attempt`) | Explorar | No |
| 3 | Descubrimiento guiado | `discovery` | Construir | No |
| 4 | Definición formal | `definition_katex`, `definition`, `definition_symbols` | Construir | No |
| 5 | Dos ejemplos resueltos | `worked_examples[0..1]` | Construir | No |
| 6 | **La trampa** | `worked_examples[2]` (`trap: True`) | ⚠ Error (color reservado) | No |
| 7 | Puente | `bridge` | Tu turno | No |
| 8 | Comparación de métodos | `method_comparison` | Tu turno | No |
| 9 | Práctica (7 ítems con escalera de pistas) | `practice` | Tu turno | **Sí** |
| 10 | Cierre + abstracción + Pólya | `closure`, `abstraction_question`, `closing_item` | Cerrar | **Sí** |
| 11 | Post-diagnóstico | `post_diagnostic` | Cerrar | No |

### Invariantes que el código exige

Cada uno tiene su test en
[tests/unit/domain/test_prealgebra_lessons.py](../tests/unit/domain/test_prealgebra_lessons.py):

- **Los once bloques existen** en todo nodo `eleven_block_node`.
- **Solo práctica y cierre bloquean** `node_completed`. El resto es exploración.
- **El mini-diagnóstico no corrige**: acusa recibo con «Anotado. Seguimos.» — es
  la línea base contra la que se compara el post-diagnóstico. Corregirlo lo
  destruiría como medida.
- **La última tarjeta de `worked_examples` es la trampa**: lleva `trap: True`,
  `confidence_prompt`, `correct_version` y `explain_prompt`.
- **Exactamente una `self_explanation` focal** por nodo.
- **Toda práctica trae escalera** `hints.n1/n2/n3`, y sus respuestas son
  alcanzables (`test_eleven_block_practice_answers_are_reachable`).
- **`method_comparison` es obligatorio**. Si un nodo no tiene dos métodos de
  resolver, compara dos formas de **comprobar**.
- **`valid_options`/`expected`/`trap_options` son listas**, nunca `set()` — el
  dict se serializa a JSON.
- **Respuestas tecleadas en formato es-CO**: coma decimal, regex
  `-?\d{1,6}(,\d{1,4})?`.
- **Cada símbolo de la definición trae su lectura hablada** (`reads`) — es lo
  que oye un lector de pantalla en vez de deletrear LaTeX.

### El `closure` no se copia

Cada nodo define **su propio eje** de cierre. La escalera de los seis conjuntos
(ℕ ℤ ℚ 𝕀 ℝ ℂ) aplica a N2 y a los inversos de N3; en divisibilidad y en álgebra
no significa nada y usar la misma tabla sería relleno. Ejes reales en uso:
«¿el exponente se puede repartir?», «¿se anula el término del medio?»,
«¿cumple las DOS condiciones?», «¿por dónde se empieza?».

Los tres valores de `closed` son `yes` / `no` / **`partial`**. El `partial` es el
sitio donde va el matiz honesto — el caso que salva al nodo de ser una regla
memorizada. Ejemplos vivos: acertar por casualidad al repartir sobre un sumando
nulo, el coeficiente que sobrevive a la cancelación completa, los conjugados al
revés (que sí se anulan, pero invierten el resultado).

---

## 5 · Añadir un nodo — la lista completa

Son **tres archivos**. No se toca el renderer, ni `Lesson.tsx`, ni el router.

**1 · Escribir el módulo** en `src/domain/learning/nodes/xNN_nombre.py`.
Expone tres cosas:

```python
NODE_ID = "ALG-N3-G06-LO-QUE-SEA"
CONCEPT_SLUG = "concepto_en_snake_case"
CONTENT = {
    "kind": "eleven_block_node",
    "concept_slug": CONCEPT_SLUG,
    "misconception": "sintoma_operacion",     # el error focal — ver §6
    "kicker": "La sala tal · Concepto",
    "house": "La sala tal",                   # o building / station / destination
    "guide": "Salim",
    "title": "...", "intro": "...",
    "diagnostic": {...}, "katia": {...}, "discovery": {...},
    "definition_katex": r"...", "definition_symbols": [...],
    "worked_examples": [ejemplo, ejemplo, trampa],
    "bridge": {...}, "method_comparison": {...},
    "practice": [7 items con hints.n1/n2/n3],
    "closure": {...}, "abstraction_question": {...}, "closing_item": {...},
    "post_diagnostic": {...}, "footer": {...}, "feedback": {...},
}
```

**2 · Listarlo** en `nodes/__init__.py` — en el `from . import (...)` y en
`NODE_MODULES`.

**3 · Encadenarlo** en `prealgebra.py`: una fila en la secuencia del nivel
(`_ALG_N3_SEQUENCE`) con `(NODE_ID, node_type, topic, prefijo_i18n, unlock_after)`.

Después:

```bash
python -m pytest tests/unit/domain/test_prealgebra_lessons.py -q
```

Los tests parametrizados recorren `NODE_MODULES` entero: un nodo mal formado
falla sin que nadie escriba un test nuevo para él.

**El nodo de referencia para copiar** depende del nivel: `b06_racionales.py`
(N1), `e05_potenciacion.py` (N2), `c06_mcm.py` (N4), `o04_cociente.py` (ALG-N1).

### Un hub de nivel

Distinto: `kind: "level_hub_cards"`, y se despacha por `node_type` —
`Lesson.tsx` **no lleva lista blanca de node_id**. Un hub nuevo no toca el
frontend. Los textos del hub (`card_cta`, `finish_label`, `gating_label`,
`cards_aria`) son parámetros; el respaldo son los del Puerto.

---

## 6 · Taxonomía de errores — el tag dice DÓNDE, no solo QUÉ

Cada interacción equivocada emite un `misconception_tag`, y de esos tags sale la
**ruta de repaso**: qué nodo se le recomienda al estudiante volver a ver.

Un tag genérico (`signo_perdido`, `distribucion_parcial`) es inservible para
enrutar: si lo emiten seis nodos, la ruta cae en «el primero que pueda emitirlo»
y acierta por accidente. La regla es **`<síntoma>_<operación>`** — el prefijo
agrupa por fenómeno, el sufijo enruta.

Hay **dos clases de tag**, y solo una necesita dueño:

- **Error de contenido** → el nodo que enseña el concepto es su pantalla de
  repaso. Que lo emitan muchos nodos está bien: se enseña una vez y se detecta
  en todas partes (`magnitud_sin_signo` vive en B05 y salta en tres nodos más).
- **Hábito de proceso** (`habito_*`) → no verificar, no decidir, no simplificar.
  **No tiene dueño ni debe tenerlo**: no hay un nodo que enseñe «verificar». El
  prefijo lo deja fuera de la regla.

Dos tests lo sostienen: `test_no_misconception_the_engine_can_emit_is_left_without_a_route`
(cero tags huérfanos) y `test_a_content_error_seen_in_many_nodes_has_a_node_that_teaches_it`.

> **Ojo:** `test_every_focal_misconception_is_distinct` solo atrapa colisiones
> **literales** de cadena. Dos nodos que enseñan el mismo error con nombres
> distintos pasan el test y siguen siendo un duplicado. Eso se revisa a mano.

---

## 7 · Catálogo de nodos

Los 5 hubs y las 3 pantallas propias de N1 se omiten; van los 52 de once bloques.

### PREALG-N1 · Conjuntos numéricos

| Nodo | Error focal |
|---|---|
| `B03-ESCALERA-NECESIDAD` | `conjuntos_se_reemplazan` |
| `B04-NATURALES-CONTAR` | `cero_no_es_numero` |
| `B05-ENTEROS-DEUDA` | `magnitud_sin_signo` |
| `B06-RACIONALES-FRACCION-DIVISION` | `decimal_truncado_es_el_numero` |
| `B07-IRRACIONALES-DECIMALES` | `decimal_infinito_es_irracional` |
| `B08-REALES-RECTA` | `existe_el_siguiente` |
| `B09-COMPLEJOS-PLANO` *(opcional)* | `cuadrado_siempre_positivo` |
| `B10-CLASIFICADOR-BASICO` | `clasifica_por_apariencia` |
| `B11-CLASIFICADOR-RIGUROSO` | `pertenencia_unica` |
| `B12-DETECTIVE-FALSEDADES` | `error_del_reciproco` |

### PREALG-N2 · La ciudad de las operaciones

| Nodo | Edificio | Error focal |
|---|---|---|
| `E01-SUMA-JUNTAR` | El Granero Público | `sumar_siempre_agranda` |
| `E02-RESTA-QUITAR` | La Casa de Cuentas | `resta_es_conmutativa` |
| `E03-MULTIPLICACION-AGRUPAR` | El Taller de Mosaicos | `multiplicar_siempre_agranda` |
| `E04-DIVISION-REPARTIR` | El Comedor Comunal | `dividir_siempre_achica` |
| `E05-POTENCIACION-CRECER` | El Invernadero | `potencia_es_multiplicar_por_el_exponente` |
| `E06-RADICACION-RAIZ` | La Cantera | `raiz_de_suma_es_suma_de_raices` |

### PREALG-N3 · La fábrica de propiedades

| Nodo | Estación | Error focal |
|---|---|---|
| `M01-CONMUTATIVA` | La Prensa de Intercambio | `todas_las_operaciones_son_conmutativas` |
| `M02-ASOCIATIVA` | El Horno de Fundición | `parentesis_son_decorativos` |
| `M03-DISTRIBUTIVA` | La Cinta Repartidora | `distribuye_sobre_el_producto` |
| `M04-ELEMENTO-NEUTRO` | El Calibre Cero | `neutro_es_el_mismo_para_toda_operacion` |
| `M05-INVERSOS` | La Prensa de Contrapesos | `inverso_es_solo_cambiar_el_signo` |

### PREALG-N4 · El Puerto de la Polis

| Nodo | Destino | Error focal |
|---|---|---|
| `C01-DIVISIBILIDAD` | Corinto — el reparto exacto | `invierte_la_direccion_de_la_divisibilidad` |
| `C02-MULTIPLOS` | Rodas — lo que se repite | `los_multiplos_se_acaban` |
| `C03-PRIMOS` | Delos — la isla indivisible | `uno_es_primo` |
| `C04-FACTORIZACION-PRIMA` | Mileto — piezas fundamentales | `deja_factores_compuestos` |
| `C05-MCD` | Atenas — lo más grande en común | `mcd_es_el_mayor_de_los_numeros` |
| `C06-MCM` | Esparta — donde coinciden las rutas | `mcm_es_el_producto_de_los_numeros` |

### ALG-N1 · El Papiro de las Cuatro Casas (Kemet)

**La Casa de la Vida** · guía Meritka — nombrar → distinguir → escribir → evaluar

| Nodo | Sala | Error focal |
|---|---|---|
| `L01-VARIABLES` | La sala de los cálamos | `variable_como_etiqueta` |
| `L02-CONSTANTES` | El estante sellado | `toda_letra_es_variable` |
| `L03-TRADUCCION` | La mesa de dictado | `traduce_en_el_orden_de_las_palabras` |
| `L04-VALOR-NUMERICO` | La cámara del recuento | `yuxtapone_en_vez_de_multiplicar` |

**La obra de la pirámide** · guía Bakenra — juntar → restar → repartir → dividir

| Nodo | Sala | Error focal |
|---|---|---|
| `O01-SEMEJANTES` | La rampa | `combina_no_semejantes` |
| `O02-SIGNOS` | El patio de aparejos | `el_menos_solo_afecta_al_primero` |
| `O03-PRODUCTO` | El taller de cinceles | `multiplica_los_exponentes_al_multiplicar` |
| `O04-COCIENTE` | La caseta del capataz | `cancelar_completo_da_cero` |

**Los campos tras la crecida** · guía Tabiry — sin factorizar polinomios

| Nodo | Sala | Error focal |
|---|---|---|
| `F01-SIMPLIFICAR` | La parcela partida | `cancelacion_en_suma` |
| `F02-SUMA` | El canal madre | `suma_numeradores_y_denominadores` |
| `F03-PRODUCTO` | La era de trilla | `busca_comun_denominador_para_multiplicar` |
| `F04-DIVISION` | El silo de simiente | `invierte_la_primera_fraccion` |

**El taller del canon** · guía Iuty

| Nodo | Sala | Error focal |
|---|---|---|
| `R01-RAZONES` | La cuadrícula del canon | `escalado_aditivo` |
| `R02-REGLA-DE-TRES` | El tinte de lino | `invierte_la_razon_en_la_regla_de_tres` |
| `R03-PORCENTAJES` | El pan de oro | `descuento_y_recargo_se_cancelan` |
| `R04-VARIACION` | La sala de las lámparas | `toda_relacion_es_directa` |

> Los datos históricos de Kemet son **ambientación**. No se afirma una función
> exacta de Per-Ankh ni una razón concreta del canon egipcio, y la cuerda de 12
> nudos 3-4-5 —mito moderno, Cantor 1882— no aparece en ningún ejercicio.

### ALG-N2 · La sala de los troqueles (Bagdad) · guía Rayhana

| Nodo | Sala | Error focal |
|---|---|---|
| `P01-CUADRADO` | La matriz cuadrada | `binomio_cuadrado_falta_2ab` |
| `P02-CONJUGADOS` | El cuño de la cenefa | `conjugado_da_suma_de_cuadrados` |
| `P03-CUBO` | El molde de tres capas | `binomio_cubo_falta_terminos` |
| `P04-TERMINO-COMUN` | La bandeja de parejas | `termino_comun_falta_suma` |

P04 cierra el nivel **recogiéndolo**: P01 y P02 son casos particulares suyos —
cuando los dos términos no comunes son iguales sale el cuadrado, cuando son
opuestos se anula la suma y sale la diferencia de cuadrados. No son cuatro
troqueles: es uno con distintos ajustes.

### ALG-N3 · El almacén de la caravana (Bagdad) · guía Salim

| Nodo | Sala | Error focal |
|---|---|---|
| `G01-FACTOR-COMUN` | El pesaje de entrada | `factor_comun_incompleto` |
| `G02-CUADRADOS` | El cotejo de huellas | `suma_de_cuadrados_es_factorizable` |
| `G03-TRINOMIO` | La mesa de despiece | `pares_sin_verificar` |
| `G04-CUBOS` | La bodega de los toneles | `suma_de_cubos_es_cubo_de_binomio` |
| `G05-EXPEDICION` | La sala de expedición | `se_queda_en_el_primer_caso` |

Dos hilos deliberados: **«cierto ≠ terminado»** (G01 lo instala, G02 lo
reengancha, G05 lo cierra sobre la cadena entera) y el contraste **G02 ↔ G04**
—la suma de cuadrados no se factoriza, la de cubos sí.

**G05 existe para llenar un hueco medido, no por simetría.** Sobre los 4.656
enunciados extraídos de los libros hay **cero** ítems de decisión de método,
y es estructural: el índice del libro ya responde qué método toca, así que el
estudiante nunca elige. Conteo en
[MAPA_ITEMS_A_NODOS_N6_N10.md](../Implementacion/MAPA_ITEMS_A_NODOS_N6_N10.md) §5.

---

## 8 · Qué queda pendiente

El inventario vivo está en
[Implementacion/CABOS_SUELTOS.md](../Implementacion/CABOS_SUELTOS.md). Los que
afectan a quien escriba un nodo:

- **Contenido solo en español.** 47 nodos llevan el texto en dicts de Python;
  solo B01, B02 y B13 son bilingües vía i18n. Falta decidir si el inglés sigue
  en alcance.
- **Faltan los cierres diagnósticos** de N2, N3, N4 y ALG-N1. Solo N1 tiene el
  suyo (B13), así que la ruta de repaso no llega al estudiante fuera de N1.
- **El arte de N2 y de Kemet está aplazado a propósito.** Los prompts están
  escritos en [Implementacion/image-prompts/](../Implementacion/image-prompts/);
  los PNG de N2 todavía dibujan puestos de mercado (descartado) y los de Kemet
  no existen.
- **Los 4.656 ítems extraídos de los libros no alimentan los nodos.** Aportaron
  lo caro —enunciado, respuesta, dificultad calibrada— y falta lo que ningún
  libro trae: los distractores.

---

## 9 · Ver el contenido sin leer Python

```bash
python scripts/generar_specs.py
```

Genera una spec de ~400 líneas por nodo en `Implementacion/specs/generadas/`
desde su módulo. Tres secciones no salen del código y quedan marcadas
`PENDIENTE`: estándares DBA/ICFES (A0), citas (A13) y notas de handoff a
Design (A14). **Al rellenar una a mano hay que sacar el archivo de
`generadas/`** — regenerar pisa la carpeta entera.
