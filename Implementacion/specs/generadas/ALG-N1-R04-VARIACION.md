# Nodo: Cuando una sube y la otra baja, lo que se conserva es el producto — ALG-N1-R04-VARIACION

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-R04-VARIACION` |
| `concept_slug` | `variacion_directa_e_inversa` |
| Error focal | `toda_relacion_es_directa` |
| Sala / edificio | La sala de las lámparas |
| Guía | Iuty |
| Entra después de | `ALG-N1-R03-PORCENTAJES` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La sala de las lámparas · Variación directa e inversa

**Título:** Cuando una sube y la otra baja, lo que se conserva es el producto

Hasta ahora, cuando una cantidad crecía la otra crecía con ella. Esta sala trata el caso contrario, y el peligro no es que sea difícil: es que la cuenta de la tina se puede aplicar igual y devuelve un número creíble.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de encender nada. Sin nota.

**D1**

Si 2 pintores tardan 6 días en un muro, ¿cuántos días tardan 4 pintores?

Respuesta: `3`

**D2**

Si se encienden MÁS lámparas, ¿cuánto dura la misma reserva de aceite?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `less` | Menos noches | — |
| 　 | `more` | Más noches | `toda_relacion_es_directa` |
| 　 | `same` | Las mismas noches | `ignora_la_proporcionalidad` |

**D3**

Cuatro lámparas encendidas durante 12 noches. ¿Cuántas noches de lámpara son en total?

Respuesta: `48`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la sala de las lámparas* — **La noche en que el taller se quedó a oscuras**

El taller trabaja de noche con lámparas de aceite. La reserva se guarda en una tinaja y se anota cuánto dura.

«Con cuatro lámparas encendidas, la reserva daba para doce noches», dice Iuty. «El maestro mandó encender seis para acabar antes el friso.»

«El escriba montó la cuenta como la de la tina de tinte: cuatro es a doce como seis es a equis. Le salieron dieciocho noches. Escribió que con más lámparas el aceite duraba más.»

Iuty señala la tinaja vacía.

«En la octava noche se apagó la última. Y el pan de oro no se puede pegar a oscuras.»

**Pregunta:** ¿Toda pareja de cantidades relacionadas se calcula igual que el tinte y el lino?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Sí: si están relacionadas, la regla de tres siempre vale | — |
| 　 | `b` | No: cuando una sube y la otra baja hay que montarla al revés | — |
| 　 | `c` | No: cuando una baja no se puede calcular nada | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos parejas de cantidades, dos cosas que no cambian**

En las dos hay una relación firme. Lo que se conserva no es lo mismo.

- **Directa · se conserva el cociente** — Las dos suben juntas y su razón vale siempre lo mismo.
- **Inversa · se conserva el producto** — Una sube y la otra baja. El aceite total gastado es el mismo: 48 noches de lámpara.

**Resolución:** Detrás de la proporcionalidad inversa hay una cantidad fija que se reparte: aquí, las 48 noches de lámpara que da la tinaja. Si enciendes más lámparas te toca a menos noches cada una. Por eso lo que no cambia es el producto — y por eso montar la regla de tres como si fuera directa da siempre el resultado en la dirección equivocada.

**Definición — Variación directa e inversa**

$$\text{directa: }\dfrac{y}{x}=k\qquad\text{inversa: }x\,y=k$$

Dos magnitudes varían de forma DIRECTA si al multiplicar una por un número la otra queda multiplicada por el mismo: su cociente es constante. Varían de forma INVERSA si al multiplicar una por un número la otra queda dividida entre ese número: su producto es constante. Hay parejas relacionadas que no son ni lo uno ni lo otro, y ahí ninguna de las dos reglas de tres sirve.

| Símbolo | Se lee | Significa |
|---|---|---|
| `\dfrac{y}{x}=k` | directa | el cociente no cambia |
| `x\,y=k` | inversa | el producto no cambia |
| `4\cdot 12=48` | la constante | las noches de lámpara que da la tinaja |
| `x=\dfrac{48}{6}` | despejar | con la constante, la cuarta cantidad sale sola |
| `\dfrac{a}{b}=\dfrac{d}{c}` | regla de tres inversa | la misma cuenta, con una razón dada la vuelta |

### A5. Ejemplos resueltos

#### Usar el producto constante · *resuelto*

Con 4 lámparas la reserva dura 12 noches. Si se encienden 6 lámparas, ¿cuántas noches dura?

- Primero decido el tipo: más lámparas gastan más deprisa, así que es inversa.
- Lo que se conserva es el producto: 4 · 12 = 48 noches de lámpara.
- Con 6 lámparas, 6 · x = 48.
- x = 48 ÷ 6 = 8 noches.
- Comprobación de dirección: 8 es menos que 12, como tenía que ser ✓.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Qué representa el 48, si no son ni lámparas ni noches?'}

#### Decidir el tipo antes de calcular · *resuelto*

Seis pintores acaban el friso en 10 días. ¿Cuántos días tardarían 15 pintores?

- ¿Más pintores hacen falta más días? No: hacen falta menos. Es inversa.
- El producto constante es el trabajo total: 6 · 10 = 60 jornadas de pintor.
- Con 15 pintores: 15 · x = 60.
- x = 60 ÷ 15 = 4 días.
- Montada como directa habría dado 25 días, más que con seis pintores: un disparate visible.

#### El escriba que usó la cuenta de la tina · *TRAMPA*

Vuelve el caso de la apertura: 4 lámparas dan 12 noches, y se encienden 6. El escriba escribió 4/12 = 6/x y anotó 18 noches.

- Antes de escribir nada: ¿si una sube, la otra sube o baja?
- Aquí baja, así que el resultado tiene que ser menor que 12. Dieciocho queda descartado de un vistazo.
- Regla para no volver a caer: primero el tipo de relación, después la cuenta. Nunca al revés.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '\\dfrac{4}{12}=\\dfrac{6}{x}\\Rightarrow x=18', 'right_latex': '4\\cdot 12=6\\cdot x\\Rightarrow x=8', 'rows': [{'wrong': 'Más lámparas, más noches', 'right': 'Más lámparas, menos noches: el aceite se reparte entre más'}, {'wrong': 'Se conserva el cociente 4/12', 'right': 'Se conserva el producto 4 · 12 = 48'}]}
**¿Por qué falla?:** Explica qué pregunta habría que hacerse ANTES de montar la cuenta, y por qué 18 noches se puede descartar sin calcular nada.


### A6. Puente — parcialmente resueltos

La cuenta de la reserva va empezada; completa los huecos.

**P1** (*falta: last*) — Con 3 lámparas la reserva dura 20 noches. ¿Cuánto dura con 5 lámparas?

- dado: $3\cdot 20=60$
- dado: $5\cdot x=60$
- hueco `P1-b1`: $60\div 5=$ → `12`

**P2** (*falta: middle*) — Ocho pintores acaban un muro en 9 días. ¿Cuántos días tardan 12?

- dado: $\text{inversa: el producto se conserva}$
- hueco `P2-b1`: $8\cdot 9=$ → `72`
- hueco `P2-b2`: $72\div 12=$ → `6`

**P3** (*falta: statement_only*) — Solo el planteamiento: con 10 lámparas la reserva dura 6 noches. ¿Cuántas lámparas se pueden encender para que dure 15 noches?

- hueco `P3-b1`: $x=$ → `4`


### A7. Comparación de métodos

**Dos maneras de resolver una inversa**

Con 5 lámparas la reserva dura 24 noches. ¿Cuánto dura con 8?

- **Método 1 · Hallar la constante** — 
- **Método 2 · Regla de tres inversa** — 

**Pregunta:** ¿Cuál de los dos te avisa si te has equivocado de tipo de relación?

**Insight:** El primero, porque obliga a nombrar la constante. Si el producto de lámparas por noches no significa nada en el problema, es que la relación no era inversa y hay que parar. El segundo funciona igual de bien y es más rápido, pero depende de acordarse de dar la vuelta a una razón — el mismo tipo de olvido que dejaba al silo de simiente sin sacos.

### A8. Práctica independiente (7 ítems)

**E1**

Con 6 lámparas la reserva dura 10 noches. ¿Cuántas noches dura con 4 lámparas?

Respuesta: `15`

Escalera de pistas:
1. Menos lámparas: el resultado tiene que subir.
2. La constante es 6 · 10 = 60.
3. 60 ÷ 4 = …

**E2**

Diez pintores acaban un muro en 12 días. ¿Cómo se calcula lo que tardan 8?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $x=\dfrac{10\cdot 12}{8}$ | — |
| 　 | `direct` | $x=\dfrac{8\cdot 12}{10}$ | `toda_relacion_es_directa` |
| 　 | `sub` | $x=12-2$ | `escalado_aditivo` |
| 　 | `same` | $x=12$ | `ignora_la_proporcionalidad` |

Escalera de pistas:
1. Menos pintores tardan más días: es inversa.
2. Lo que se conserva es el producto 10 · 12.
3. Ese producto dividido entre 8.

**E3**

La reserva da para 72 noches de lámpara. ¿Cuántas lámparas se pueden encender si el friso necesita 9 noches de trabajo?

Respuesta: `8`

Escalera de pistas:
1. La constante ya la tienes: 72.
2. Lámparas por noches = 72.
3. 72 ÷ 9 = …

**E4**

Un escriba calcula: «5 pintores tardan 8 días, luego 10 pintores tardan 16». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `inverse` | Es inversa: el doble de pintores tarda la mitad, $4$ días | — |
| 　 | `calc` | Multiplicó mal: son 15 días | `ignora_la_proporcionalidad` |
| 　 | `direct` | Es directa pero se equivocó en el factor | `toda_relacion_es_directa` |
| 　 | `none` | No hay error | `toda_relacion_es_directa` |

Escalera de pistas:
1. ¿Más manos tardan más o menos?
2. Menos. Así que el resultado debe bajar de 8.
3. El trabajo total es 5 · 8 = 40 jornadas.

**E5**

¿Verdadera o falsa? «Si dos cantidades están relacionadas, se pueden calcular siempre con una regla de tres directa.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: si una sube cuando la otra baja, lo que se conserva es el producto | — |
| 　 | `true` | Verdadera: para eso sirve la regla de tres | `toda_relacion_es_directa` |
| 　 | `true_num` | Verdadera siempre que los tres datos sean números | `toda_relacion_es_directa` |
| 　 | `false_never` | Falsa: la regla de tres directa no sirve para nada | `sobregeneraliza_variacion_directa_e_inversa` |

Escalera de pistas:
1. Piensa en lámparas y noches de reserva.
2. Más lámparas dan menos noches.
3. La regla directa daría más noches: imposible.

**E6**

Selecciona TODAS las parejas que varían de forma INVERSA.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | Lámparas encendidas y noches que dura la reserva | — |
| 　 | `b` | Medidas de tinte y brazadas de lino teñidas | — |
| ✅ | `c` | Pintores y días para acabar el mismo muro | — |
| 　 | `d` | Lado de un cuadrado y su perímetro | — |

Escalera de pistas:
1. Inversa es «una sube y la otra baja».
2. Comprueba si el producto se mantiene constante.
3. El perímetro sube cuando sube el lado: esa es directa.

**E7**

La tinaja da 90 noches de lámpara. El taller enciende 5 lámparas durante 6 noches y después apaga una. ¿Cuántas noches más aguanta la reserva con las 4 restantes?

Respuesta: `15`

Escalera de pistas:
1. Primero calcula lo gastado: 5 lámparas por 6 noches.
2. Quedan 90 − 30 = 60 noches de lámpara.
3. 60 ÷ 4 = …


### A9. Cierre

*¿Se conserva el cociente?* — **Qué tipo de relación tiene cada pareja**

La pregunta no es si están relacionadas: casi todo lo está. La pregunta es qué cantidad no cambia cuando las otras dos se mueven.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Suben juntas y el cociente se conserva. Es lo de la tina. |
|  | ✅ | Al doble de lado, el doble de perímetro. El cociente vale 4 siempre. |
|  | ✗ | Una sube y la otra baja: lo constante es el producto. Es el caso focal. |
|  | ✗ | El producto es el trabajo total, y no cambia por repartirlo entre más manos. |
|  | ~ (ámbar) | Crecen juntas, pero al doble de lado el área se hace CUATRO veces mayor. Ni el cociente ni el producto se conservan. |
|  | ~ (ámbar) | No hay nada que conservar. Aquí ninguna de las dos reglas devuelve un número con sentido. |

La quinta fila es la más importante de todo el nodo: dos cantidades pueden crecer juntas sin ser proporcionales. Que suban a la vez no basta — hay que comprobar si al doblar una se dobla la otra. Y la sexta cierra el aviso: las dos reglas de tres devuelven un número siempre, tenga sentido o no. Decidir el tipo de relación es tu trabajo, no el de la cuenta.

#### Pregunta de abstracción

¿Qué comparten los tres casos de la sala trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `product` | En los tres hay una cantidad total fija que se reparte, y es el producto | — |
| 　 | `direction` | En los tres se puede saber antes de calcular si el resultado sube o baja | — |
| 　 | `quotient` | En los tres lo que se conserva es el cociente de las dos magnitudes | — |
| 　 | `always` | En los tres sirve la misma regla de tres que en la tina de tinte | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántas lámparas se pueden encender?
¿Cuántas lámparas se pueden encender?

Respuesta: `12`

Escalera de pistas:
1. Menos noches: harán falta más lámparas.
2. La constante es 3 · 20 = 60.
3. 60 ÷ 5 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otra reserva. Sin nota.

- **Mejoró:** Avance: ya decides el tipo de relación antes de montar la cuenta.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la pregunta previa: si una sube, ¿la otra sube o baja?

**PD1**

Si 3 pintores tardan 12 días en un muro, ¿cuántos días tardan 6 pintores?

Respuesta: `6`

**PD2**

Si se encienden MENOS lámparas, ¿cuánto dura la misma reserva?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `more` | Más noches | — |
| 　 | `less` | Menos noches | `toda_relacion_es_directa` |
| 　 | `same` | Las mismas noches | `ignora_la_proporcionalidad` |

**PD3**

Cinco lámparas encendidas durante 9 noches. ¿Cuántas noches de lámpara son en total?

Respuesta: `45`

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-R04-VARIACION-D2` | `more` | `toda_relacion_es_directa` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-D2` | `same` | `ignora_la_proporcionalidad` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E2` | `direct` | `toda_relacion_es_directa` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E2` | `sub` | `escalado_aditivo` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E2` | `same` | `ignora_la_proporcionalidad` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E4` | `calc` | `ignora_la_proporcionalidad` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E4` | `direct` | `toda_relacion_es_directa` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E4` | `none` | `toda_relacion_es_directa` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E5` | `true` | `toda_relacion_es_directa` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E5` | `true_num` | `toda_relacion_es_directa` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-E5` | `false_never` | `sobregeneraliza_variacion_directa_e_inversa` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-PD2` | `less` | `toda_relacion_es_directa` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |
| `ALG-N1-R04-VARIACION-PD2` | `same` | `ignora_la_proporcionalidad` | Antes de montar la cuenta: si una sube, ¿la otra sube o baja? Eso decide qué se conserva. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
