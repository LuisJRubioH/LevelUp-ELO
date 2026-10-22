# Nodo: Las remesas salen sin etiqueta, y hay un orden para abrirlas — ALG-N3-G05-EXPEDICION

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N3-G05-EXPEDICION` |
| `concept_slug` | `factorizacion_completa` |
| Error focal | `se_queda_en_el_primer_caso` |
| Sala / edificio | La sala de expedición |
| Guía | Salim |
| Entra después de | `ALG-N3-G04-CUBOS` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La sala de expedición · Factorización completa

**Título:** Las remesas salen sin etiqueta, y hay un orden para abrirlas

Hasta ahora cada sala te decía qué molde usar: en el cotejo se cotejaba, en la mesa se despiezaba. Aquí llegan remesas mezcladas y sin etiqueta. Lo único que hay que decidir es por dónde empezar — y cuándo parar.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de firmar la primera guía. Sin nota.

**D1**

¿Qué tienen en común los términos de $12mx^{2}-12m$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `both` | Un 12 y una $m$ | — |
| 　 | `num` | Solo el 12 | `factor_comun_incompleto` |
| 　 | `none` | Nada | `factor_comun_incompleto` |

**D2**

¿Cuál es la factorización de $x^{2}-1$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $(x+1)(x-1)$ | — |
| 　 | `sq` | $(x-1)^{2}$ | `confunde_diferencia_con_cuadrado_perfecto` |
| 　 | `none` | No se puede | `suma_de_cuadrados_es_factorizable` |

**D3**

¿En cuántos factores queda $x^{2}-9$ una vez abierto del todo?

Respuesta: `2`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la sala de expedición* — **La guía que se firmó con la carga a medias**

En la sala de expedición se precinta lo que sale. Cada remesa lleva una guía de carga donde se anota en cuántos bultos quedó dividida, y una vez sellada no se vuelve a abrir.

Salim deja una guía sobre el mostrador:

«Salía la remesa $12mx^{2}-12m$. El mozo vio dos términos que restaban, aplicó el cotejo de huellas y anotó dos bultos. Firmó y precintó.»

«Antes había un 12 y una eme en los dos términos que nadie sacó. La remesa llegó a destino en dos bultos cuando eran tres, y hubo que romper el precinto.»

**Pregunta:** Si la factorización que anotó el mozo era correcta, ¿por qué la guía estaba mal?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `orden` | Porque había que empezar por otro molde | — |
| 　 | `falsa` | Porque la factorización que anotó era falsa | — |
| 　 | `parar` | Porque paró antes de tiempo, aunque no se equivocara | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Siempre se empieza por lo mismo**

Cuando una remesa admite varios moldes, el orden no da igual: hay uno que conviene siempre primero, porque simplifica todo lo que viene detrás.

- **Empezando por el molde llamativo** — Los términos no son cuadrados exactos —12m no lo es—, así que el molde ni siquiera aplicaba tal cual.
- **Empezando por el factor común** — Al sacar el 12m, lo que queda dentro es limpio y el molde se reconoce de un vistazo.

**Resolución:** El factor común va SIEMPRE primero. Después se mira cuántos términos quedan: con dos, diferencia de cuadrados o de cubos; con tres, cuadrado perfecto o trinomio general; con cuatro, agrupación. Y al terminar cada paso se vuelve a mirar cada trozo, porque un trozo puede volver a abrirse.

**Definición — Factorización completa**

$$\text{común}\ \rightarrow\ \text{contar términos}\ \rightarrow\ \text{molde}\ \rightarrow\ \text{repetir en cada trozo}$$

Factorizar COMPLETAMENTE es repetir el proceso hasta que ningún factor se pueda abrir más. La ruta:

1. Sacar el factor común, si lo hay.
2. Contar los términos de lo que queda: 2 → cuadrados o cubos · 3 → cuadrado perfecto o trinomio general · 4 → agrupación.
3. Volver al paso 1 con cada factor obtenido.

Se para cuando todos los factores son irreducibles. El resultado no depende del camino elegido.

| Símbolo | Se lee | Significa |
|---|---|---|
| `12m(x+1)(x-1)` | doce eme, por equis más uno, por equis menos uno | tres bultos: el común y los dos del molde |
| `5m^{4}+5m=5m(m^{3}+1)` | cinco eme a la cuarta más cinco eme | sacar el común deja a la vista una suma de cubos |
| `5m(m+1)(m^{2}-m+1)` | cinco eme por eme más uno por eme cuadrado menos eme más uno | la misma remesa terminada: tres factores |
| `x^{2}+4` | equis cuadrado más cuatro | un factor irreducible: aquí se para |
| `1-n^{6}` | uno menos ene a la sexta | cuadrados y cubos a la vez: cuatro factores al final |

### A5. Ejemplos resueltos

#### Tres bultos, no dos · *resuelto*

Salim expide la remesa $12mx^{2}-12m$. ¿En cuántos bultos sale?

- Paso 1, factor común: MCD(12, 12) = 12 y la m está en los dos → 12m.
- Queda 12m(x² − 1).
- Paso 2, cuento términos dentro: dos, y restan.
- ¿Cuadrados exactos? x² y 1. Sí → (x + 1)(x − 1).
- Paso 3, reviso cada trozo: 12m es un monomio y los dos binomios no se abren. Tres bultos: 12m(x + 1)(x − 1).

**Autoexplicación (focal):** {'step_index': 0, 'prompt': '¿Por qué conviene sacar el factor común ANTES de mirar qué molde aplica, y no después?'}

#### Lo que aparece al quitar de encima · *resuelto*

Otra remesa: $5m^{4}+5m$. Tal como viene no encaja en ningún molde.

- Tal cual: dos términos que suman, pero m⁴ y m no son ni cuadrados ni cubos exactos.
- Paso 1, factor común: 5 y la menor potencia de m, o sea 5m.
- Queda 5m(m³ + 1).
- Ahora sí: m³ y 1 son cubos exactos. Suma de cubos → (m + 1)(m² − m + 1).
- Tres bultos: 5m(m + 1)(m² − m + 1). El común no era un trámite: era lo que dejaba ver el molde.

#### El mozo que precintó demasiado pronto · *TRAMPA*

Vuelve la remesa de la apertura. El mozo saca el común, aplica un molde y firma la guía:

- Dentro hay tres términos: m⁴ − 8m² + 16.
- Extremos: (m²)² y 4². Doble producto: 2 · m² · 4 = 8m² ✓. Es cuadrado perfecto: (m² − 4)².
- Y m² − 4 es diferencia de cuadrados: (m + 2)(m − 2).
- Queda 5m(m + 2)²(m − 2)². Regla: después de cada paso, vuelve a mirar cada trozo.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '5m(m^{4}-8m^{2}+16)', 'right_latex': '5m(m+2)^{2}(m-2)^{2}', 'rows': [{'wrong': 'Saqué el común: ya está', 'right': 'Después del común hay que contar términos y volver a mirar'}, {'wrong': 'Dos bultos', 'right': 'Tres, y dos de ellos van al cuadrado'}]}
**¿Por qué falla?:** Sigue abriendo el paréntesis y di en cuántos bultos sale la remesa de verdad.


### A6. Puente — parcialmente resueltos

La guía de carga va empezada; completa los huecos.

**P1** (*falta: last*) — Factoriza completamente $3x^{2}-27$.

- dado: $\text{común}: 3$
- dado: $3(x^{2}-9)$
- hueco `P1-b1`: $\text{número de factores al terminar}=$ → `3`

**P2** (*falta: middle*) — Factoriza completamente $2x^{3}+16$.

- dado: $\text{común}: 2\ \Rightarrow\ 2(x^{3}+8)$
- hueco `P2-b1`: $\sqrt[3]{8}=$ → `2`
- hueco `P2-b2`: $\text{términos del segundo factor}=$ → `3`

**P3** (*falta: statement_only*) — Solo el planteamiento: $1-n^{6}$. Decide por qué molde empezar y di cuántos factores quedan al final.

- hueco `P3-b1`: $\text{número de factores finales}=$ → `4`


### A7. Comparación de métodos

**Dos órdenes para abrir la misma remesa**

$3x^{2}-27$. Los dos llegan a lo mismo; uno cuesta más.

- **Método 1 · Molde primero** — 
- **Método 2 · Común primero** — 

**Pregunta:** ¿Por qué el factor común va siempre primero, aunque no sea obligatorio?

**Insight:** Porque los moldes exigen formas exactas —cuadrados, cubos— y un coeficiente de más las estropea. 3x² − 27 no es diferencia de cuadrados; x² − 9 sí lo es, y es la misma remesa con el 3 fuera. Sacar el común no es un trámite previo: es lo que hace visible el molde. Por eso el orden no es una costumbre, es lo que evita descartar un caso que sí aplicaba.

### A8. Práctica independiente (7 ítems)

**E1**

Para factorizar $18x^{3}-2x$, ¿por qué molde hay que EMPEZAR?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `comun` | Factor común | — |
| 　 | `cuadrados` | Diferencia de cuadrados | `no_saca_el_factor_comun_primero` |
| 　 | `cubos` | Diferencia de cubos | `no_saca_el_factor_comun_primero` |
| 　 | `trinomio` | Trinomio general | `cuenta_mal_los_terminos` |

Escalera de pistas:
1. Antes de mirar la forma, mira si los términos comparten algo.
2. 18 y 2 comparten un 2; x³ y x comparten una x.
3. Sacando 2x queda 2x(9x² − 1), y ahí sí se ve el molde.

**E2**

Al factorizar completamente $12mx^{2}-12m$, ¿en cuántos factores queda?

Respuesta: `3`

Escalera de pistas:
1. Primero el factor común.
2. Queda 12m(x² − 1), y lo de dentro se vuelve a abrir.
3. El común cuenta como uno de los factores.

**E3**

Sin factorizar: $x^{6}-1$ es a la vez diferencia de cuadrados y de cubos. ¿En cuántos factores queda al abrirlo del todo?

Respuesta: `4`

Escalera de pistas:
1. Empieza por cuadrados: (x³ + 1)(x³ − 1).
2. Cada uno de esos dos es una suma o diferencia de cubos.
3. Cada uno se parte en dos: 2 × 2.

**E4**

Sin hacer ninguna cuenta: ¿cuál de estas remesas NO se puede abrir más?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `irred` | $x^{2}+4$ | — |
| 　 | `dif` | $x^{2}-4$ | `suma_de_cuadrados_es_factorizable` |
| 　 | `comun` | $2x^{2}+8x$ | `no_saca_el_factor_comun_primero` |
| 　 | `cubo` | $x^{3}+8$ | `cree_que_ninguna_suma_se_factoriza` |

Escalera de pistas:
1. Mira una por una: ¿tiene factor común? ¿cae en algún molde?
2. La suma de cuadrados es el hueco del catálogo.
3. La suma de CUBOS sí se abre; la de cuadrados no.

**E5**

Un mozo anota $5m^{5}-40m^{3}+80m=5m(m^{4}-8m^{2}+16)$ y precinta. ¿Está terminado?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: lo de dentro es cuadrado perfecto y se abre dos veces más | — |
| 　 | `yes` | Sí: el factor común está completo | `se_queda_en_el_primer_caso` |
| 　 | `wrong` | No: el factor común debería ser 5m³ | `factor_comun_incompleto` |
| 　 | `err` | No: la igualdad es falsa | `se_queda_en_el_primer_caso` |

Escalera de pistas:
1. El factor común está bien. Cuenta los términos de lo que quedó dentro.
2. Son tres: extremos cuadrados y doble producto 2 · m² · 4 = 8m² ✓.
3. (m² − 4)², y m² − 4 todavía se abre.

**E6**

¿Verdadera o falsa? «Si al multiplicar los factores vuelve a salir la remesa original, la guía se puede precintar.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: $5m(m^{4}-8m^{2}+16)$ lo cumple y no está terminada | — |
| 　 | `true` | Verdadera: si la igualdad es cierta, está terminada | `se_queda_en_el_primer_caso` |
| 　 | `true_comun` | Verdadera siempre que se haya sacado el factor común | `se_queda_en_el_primer_caso` |
| 　 | `false_never` | Falsa: multiplicar de vuelta nunca sirve de nada | `cuenta_mal_los_terminos` |

Escalera de pistas:
1. Es la misma lección del pesaje de entrada, ahora sobre toda la cadena.
2. Una factorización incompleta también cumple la igualdad.
3. La señal de parar no es que multiplique bien: es que ningún factor se abra.

**E7**

Cuatro remesas sin etiqueta. ¿En cuáles hay que sacar factor común ANTES de aplicar ningún molde? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok1` | $3x^{2}-27$ | — |
| ✅ | `ok2` | $2x^{3}+16$ | — |
| 　 | `no1` | $x^{2}-49$ | `cuenta_mal_los_terminos` |
| 　 | `no2` | $x^{2}+10x+25$ | `cuenta_mal_los_terminos` |

Escalera de pistas:
1. Mira si los términos comparten un número o una letra.
2. En x² − 49 los coeficientes son 1 y 49: no comparten nada.
3. Son dos de las cuatro.


### A9. Cierre

*¿Por dónde se empieza?* — **La ruta de expedición**

Cada fila es una remesa sin etiqueta. La pregunta no es en qué se factoriza: es qué se hace PRIMERO.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Común primero, siempre. Sin el 3 fuera no hay cuadrados exactos. |
|  | ✅ | Tal cual no encajaba en nada; con 5m fuera aparece una suma de cubos. |
|  | ✅ | Tres términos → cuadrado perfecto o trinomio general. Se decide ahí. |
|  | ✅ | Cuatro términos y sin común → agrupación. |
|  | ~ (ámbar) | Cuadrados y cubos a la vez. Los dos caminos llegan al mismo sitio —la factorización completa es única— pero empezando por cuadrados se llega antes. |
|  | ✗ | Sin común, dos términos que suman y son cuadrados: aquí se precinta. |

La ruta en una línea: **común primero, después cuenta los términos, y al terminar vuelve a mirar cada trozo.** Se precinta cuando ningún factor se abre, no cuando la multiplicación cuadra.

#### Pregunta de abstracción

Las tres remesas se abren con moldes distintos. ¿Qué tienen en común los tres primeros pasos?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `comun` | En las tres se saca primero el factor común, y solo después se decide el molde | — |
| 　 | `dos` | En las tres el resultado tiene exactamente dos factores | — |
| 　 | `cuadrados` | En las tres se aplica diferencia de cuadrados | — |

#### Ítem final con protocolo de Pólya

**C1**

¿En cuántos factores queda?
¿En cuántos factores queda?

Respuesta: `4`

Escalera de pistas:
1. Saca el 2 primero.
2. Queda x⁴ − 16, que es diferencia de cuadrados.
3. De los dos trozos, solo x² − 4 se vuelve a abrir; x² + 4 no.

Pólya: Entender: hay que factorizar completamente y contar los factores. → Planear: común primero, después contar términos y repetir en cada trozo. → Ejecutar: 2(x⁴ − 16) = 2(x² + 4)(x² − 4) = 2(x² + 4)(x + 2)(x − 2). → Comprobar: x² + 4 es suma de cuadrados, irreducible. Cuatro factores.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que tienes la ruta.

- **Mejoró:** Avance: ya decides el orden y sabes cuándo se puede precintar.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el orden de los moldes antes de cerrar el almacén.

**Q1**

En $8ax^{2}-8a$, ¿qué se hace primero?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `comun` | Sacar el factor común 8a | — |
| 　 | `cuad` | Aplicar diferencia de cuadrados | `no_saca_el_factor_comun_primero` |
| 　 | `nada` | No se puede factorizar | `se_queda_en_el_primer_caso` |

**Q2**

¿Cuál de estas NO se puede abrir más?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `irred` | $x^{2}+9$ | — |
| 　 | `dif` | $x^{2}-9$ | `suma_de_cuadrados_es_factorizable` |
| 　 | `cubo` | $x^{3}+27$ | `cree_que_ninguna_suma_se_factoriza` |

**Q3**

¿En cuántos factores queda $5x^{2}-45$ al abrirla del todo?

Respuesta: `3`

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N3-G05-EXPEDICION-D1` | `num` | `factor_comun_incompleto` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-D1` | `none` | `factor_comun_incompleto` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-D2` | `sq` | `confunde_diferencia_con_cuadrado_perfecto` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-D2` | `none` | `suma_de_cuadrados_es_factorizable` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E1` | `cuadrados` | `no_saca_el_factor_comun_primero` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E1` | `cubos` | `no_saca_el_factor_comun_primero` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E1` | `trinomio` | `cuenta_mal_los_terminos` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E4` | `dif` | `suma_de_cuadrados_es_factorizable` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E4` | `comun` | `no_saca_el_factor_comun_primero` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E4` | `cubo` | `cree_que_ninguna_suma_se_factoriza` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E5` | `yes` | `se_queda_en_el_primer_caso` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E5` | `wrong` | `factor_comun_incompleto` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E5` | `err` | `se_queda_en_el_primer_caso` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E6` | `true` | `se_queda_en_el_primer_caso` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E6` | `true_comun` | `se_queda_en_el_primer_caso` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-E6` | `false_never` | `cuenta_mal_los_terminos` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-Q1` | `cuad` | `no_saca_el_factor_comun_primero` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-Q1` | `nada` | `se_queda_en_el_primer_caso` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-Q2` | `dif` | `suma_de_cuadrados_es_factorizable` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |
| `ALG-N3-G05-EXPEDICION-Q2` | `cubo` | `cree_que_ninguna_suma_se_factoriza` | La ruta es siempre la misma: factor común, contar los términos de lo que queda, aplicar el molde, y volver a mirar cada  |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
