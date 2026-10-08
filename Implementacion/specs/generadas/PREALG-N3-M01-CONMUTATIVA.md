# Nodo: Cambiar de boca no siempre da lo mismo — PREALG-N3-M01-CONMUTATIVA

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N3-M01-CONMUTATIVA` |
| `concept_slug` | `conmutativa` |
| Error focal | `todas_las_operaciones_son_conmutativas` |
| Sala / edificio | La Prensa de Intercambio |
| Guía | KatIA |
| Entra después de | `PREALG-N3-M00-LABORATORIO` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La Prensa de Intercambio · Conmutativa

**Título:** Cambiar de boca no siempre da lo mismo

Ya conoces las seis operaciones. Ahora vas a preguntarles algo que ninguna te había pedido: ¿qué pasa si intercambias los dos números de sitio? En cuatro de ellas el resultado se derrumba, y saber en cuáles es lo que te deja calcular rápido sin equivocarte.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de encender la prensa. Sin nota.

**D1**

¿Dan lo mismo $7+5$ y $5+7$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí | — |
| 　 | `no` | No | `orden_altera_toda_operacion` |

**D2**

¿Dan lo mismo $12\div 4$ y $4\div 12$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No | — |
| 　 | `yes` | Sí | `todas_las_operaciones_son_conmutativas` |

**D3**

¿En cuáles de estas operaciones puedes cambiar los dos números de sitio sin que cambie el resultado?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum_mult` | Solo en la suma y la multiplicación | — |
| 　 | `all` | En todas | `todas_las_operaciones_son_conmutativas` |
| 　 | `sum_only` | Solo en la suma | `multiplicacion_no_conmutativa` |
| 　 | `none` | En ninguna | `orden_altera_toda_operacion` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En la Prensa de Intercambio* — **Las dos bocas de la prensa**

La primera estación de la fábrica es una prensa con dos bocas de carga, una a cada lado. Entran placas de bronce por las dos y sale una pieza única. Sobre el bastidor hay una palanca que intercambia las bocas: lo que iba por la izquierda pasa a la derecha y al revés.

El operario lleva años tirando de esa palanca cuando se equivoca al cargar. «Da igual el lado», dice. Hoy la prensa está configurada para dividir, tiró de la palanca por costumbre, y salió una pieza que no encaja en ningún molde.

**Pregunta:** ¿En qué operaciones se puede tirar de la palanca sin que cambie la pieza que sale?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | En todas: el orden nunca importa | — |
| 　 | `b` | Solo en algunas | — |
| 　 | `c` | En ninguna: siempre importa | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **La misma palanca, dos resultados distintos**

Abajo están las mismas dos placas cargadas en los dos órdenes, primero con la prensa sumando y después dividiendo.

- **Caso que confirma lo que esperas** — La palanca no cambió nada: la pieza es la misma.
- **Caso que rompe la expectativa** — La palanca cambió la pieza por completo. Ni siquiera se parecen.

**Resolución:** La palanca no es buena ni mala: depende de para qué esté configurada la prensa. Sumar y multiplicar juntan cosas sin preguntar quién llegó primero. Restar y dividir tienen un papel de PROTAGONISTA — el minuendo, el dividendo — y otro de instrumento. Intercambiarlos cambia la pregunta.

**Definición — La propiedad conmutativa**

$$a+b=b+a\qquad a\times b=b\times a$$

Una operación es conmutativa si intercambiar sus dos números no cambia el resultado. La suma y la multiplicación lo son; la resta, la división y la potenciación no.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a,b` | los dos operandos | las dos placas cargadas en la prensa |
| `=` | igual | los dos órdenes producen exactamente la misma pieza |
| `a-b\neq b-a` | la resta no conmuta | salvo cuando a = b; lo viste en la Casa de Cuentas (E02) |
| `a\div b\neq b\div a` | la división no conmuta | salvo cuando a = b y ninguno es 0 |
| `a^{b}\neq b^{a}` | la potencia no conmuta | 2³ = 8 pero 3² = 9 |

### A5. Ejemplos resueltos

#### La palanca que sí se puede tirar · *resuelto*

La prensa debe procesar placas de 25 y 4, primero sumando y después multiplicando. ¿Conviene cargar en un orden concreto?

- Sumando: 25 + 4 = 29 y 4 + 25 = 29. Los dos órdenes coinciden.
- Multiplicando: 25 × 4 = 100 y 4 × 25 = 100. También coinciden.
- Coincidir no significa que dé igual para TRABAJAR: 4 × 25 se calcula de cabeza mucho más rápido.
- La conmutativa no cambia el resultado; cambia lo cómodo que es llegar a él.
- Por eso el operario puede tirar de la palanca cuando la prensa suma o multiplica: solo gana comodidad.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 los dos órdenes dan lo mismo pero uno es «mejor». ¿Mejor en qué sentido, si el resultado es idéntico?'}

#### La palanca que rompe la pieza · *resuelto*

Las mismas placas de 25 y 4, ahora con la prensa configurada para restar y para dividir. ¿Qué pasa al intercambiarlas?

- Restando: 25 − 4 = 21, pero 4 − 25 = −21. No son iguales: son opuestos.
- Dividiendo: 25 ÷ 4 = 6,25, pero 4 ÷ 25 = 0,16. Ni siquiera son opuestos.
- En los dos casos el primer número tiene un papel distinto al segundo.
- En la resta, el primero es de lo que se quita; en la división, lo que se reparte.
- Intercambiarlos no reordena la misma cuenta: plantea otra cuenta.

#### El operario que generalizó la palanca · *TRAMPA*

El operario deja escrito en el turno de noche: «La palanca de intercambio es segura. Lo comprobé con 6 + 2 y 2 + 6, y con 6 × 2 y 2 × 6. Sale lo mismo. Vale para cualquier configuración de la prensa».

- El operario probó donde la propiedad SÍ vale y no probó donde falla.
- Basta configurar la prensa para restar: 6 − 2 = 4 y 2 − 6 = −4.
- Un contraejemplo derriba una afirmación general; mil ejemplos a favor no la sostienen (lo viste en B12).

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '6-2=2-6', 'right_latex': '6-2=4\\quad\\text{pero}\\quad 2-6=-4', 'rows': [{'wrong': 'Dos casos que funcionan prueban la regla general', 'right': 'Un solo caso que falla tumba la regla general'}, {'wrong': 'La palanca es segura en cualquier configuración', 'right': 'Es segura solo sumando y multiplicando'}]}
**¿Por qué falla?:** Da un caso que tumbe la nota del operario y escribe las dos cuentas.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Reordena para calcular de cabeza: placas de 2, 47 y 5, prensa multiplicando.

- dado: $2\times 47\times 5=2\times 5\times 47$
- dado: $2\times 5=10$
- hueco `P1-b1`: $10\times 47=$ → `470`

**P2** (*falta: middle*) — La prensa resta placas de 9 y 14, y el operario tira de la palanca.

- dado: $\text{cuenta pedida: }9-14$
- hueco `P2-b1`: $9-14=$ → `-5`
- hueco `P2-b2`: $14-9=$ → `5`

**P3** (*falta: statement_only*) — Solo el planteamiento: la prensa está configurada para elevar. Cargan placas de 2 y 4. Calcula el resultado en el orden 2 elevado a 4.

- hueco `P3-b1`: $2^{4}=$ → `16`


### A7. Comparación de métodos

**Dos caminos para el mismo producto**

¿Cuánto vale $4\times 17\times 25$? Las dos soluciones de abajo son correctas.

- **Método 1 · En el orden escrito** — 
- **Método 2 · Reordenar primero** — 

**Pregunta:** ¿Cuál harías sin papel? ¿Y podrías hacer el mismo movimiento si en vez de productos hubiera restas?

**Insight:** El método 2 vale por la conmutativa: 4 × 17 × 25 = 4 × 25 × 17. Con restas el movimiento es ilegal tal cual: 20 − 8 − 3 = 9, pero 8 − 20 − 3 = −15. Lo único que sí puedes mover en una resta es cada número CON su signo, tratándolo como una suma: 20 + (−8) + (−3). Ese truco lo vas a formalizar en la estación siguiente.

### A8. Práctica independiente (7 ítems)

**E1**

Reordena para calcular rápido: 5 × 37 × 2. ¿Cuánto da?

Respuesta: `370`

Escalera de pistas:
1. ¿Qué dos factores juntos dan un número redondo?
2. 5 × 2 = 10.
3. 10 × 37 = …

**E2**

La prensa resta placas de 6 y 19, en ese orden. ¿Qué sale?

Respuesta: `-13`

Escalera de pistas:
1. Respeta el orden: no tires de la palanca.
2. 6 − 19 = 6 + (−19).
3. Se cancelan 6, y del −19 sobran 13.

**E3**

¿Cuál de estas igualdades es FALSA?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `power` | 2 elevado a 3 igual a 3 elevado a 2 | — |
| 　 | `sum` | 9 + 4 = 4 + 9 | `orden_altera_toda_operacion` |
| 　 | `mult` | 9 × 4 = 4 × 9 | `multiplicacion_no_conmutativa` |
| 　 | `same` | 7 − 7 = 7 − 7 | `no_evalua_antes_de_juzgar` |

Escalera de pistas:
1. Calcula las dos partes de cada igualdad antes de decidir.
2. 2³ = 8.
3. 3² = 9, y 8 no es 9.

**E4**

Un operario anota «La prensa dividió 3 entre 15 y dio 5». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `swapped` | Calculó 15 ÷ 3; el orden pedido daba 0,2 | — |
| 　 | `arith` | Se equivocó al dividir: 3 ÷ 15 son 3 | `error_de_calculo_no_de_orden` |
| 　 | `rounded` | Redondeó mal el decimal | `error_de_notacion_no_de_valor` |
| 　 | `none` | Ningún error, está bien | `todas_las_operaciones_son_conmutativas` |

Escalera de pistas:
1. ¿Qué número escribió primero el enunciado?
2. Dividir 3 entre 15 reparte 3 en 15 partes: el resultado es menor que 1.
3. 3 ÷ 15 = 0,2, y 15 ÷ 3 = 5.

**E5**

¿Es verdadera o falsa? «Para cualesquiera $a$ y $b$: $a\div b=b\div a$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_unless` | Falsa: solo coinciden si a = b y ninguno es 0 | — |
| 　 | `true` | Verdadera: el orden nunca importa | `todas_las_operaciones_son_conmutativas` |
| 　 | `false_never` | Falsa: nunca pueden coincidir | `olvida_el_caso_de_igualdad` |
| 　 | `true_positive` | Verdadera si los dos son positivos | `todas_las_operaciones_son_conmutativas` |

Escalera de pistas:
1. Para tumbar un «cualesquiera» basta UN caso.
2. Prueba con a = 8 y b = 2.
3. 8 ÷ 2 = 4 y 2 ÷ 8 = 0,25. ¿Y si a y b fueran iguales?

**E6**

Reordena para calcular de cabeza: 25 × 13 × 4. ¿Cuánto da?

Respuesta: `1300`

Escalera de pistas:
1. Junta primero los factores que dan un número redondo.
2. 25 × 4 = 100.
3. 100 × 13 = …

**E7**

El operario quiere reordenar «40 − 8 × 5» poniendo el 5 delante del 8. ¿Puede hacerlo?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes_mult` | Sí: el 8 y el 5 se multiplican, y el producto sí conmuta | — |
| 　 | `no` | No: hay una resta en la expresión | `aplica_la_restriccion_a_toda_la_expresion` |
| 　 | `yes_all` | Sí: cualquier número se puede mover a cualquier sitio | `todas_las_operaciones_son_conmutativas` |
| 　 | `only_paren` | Solo si añade paréntesis alrededor de todo | `parentesis_como_amuleto` |

Escalera de pistas:
1. La conmutativa se aplica a UNA operación, no a la expresión entera.
2. ¿Qué operación conecta al 8 con el 5?
3. 8 × 5 = 40 y 5 × 8 = 40: la resta de fuera no se ve afectada.


### A9. Cierre

*Validez a lo largo de las operaciones* — **¿En qué operaciones se puede tirar de la palanca?**

La escalera de este nivel no recorre conjuntos: recorre las seis operaciones que ya visitaste.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Los dos sumandos hacen el mismo papel: juntar no distingue quién llegó primero. |
|  | ✗ | Dan opuestos. El minuendo no es intercambiable con el sustraendo. |
|  | ✅ | Un rectángulo de 8 por 3 tiene las mismas teselas que uno de 3 por 8 (E03). |
|  | ✗ | El dividendo se reparte y el divisor reparte: papeles distintos. |
|  | ✗ | La base se repite y el exponente cuenta: intercambiarlos cambia quién hace qué (E05). |
|  | ✗ | Índice y radicando tampoco son intercambiables (E06). |

Dos sí y cuatro no. La regla no se memoriza: se deduce preguntando si los dos números hacen el mismo papel. En la estación siguiente vas a hacerle la misma pregunta a los paréntesis.

#### Pregunta de abstracción

¿Qué comparten las operaciones donde la palanca SÍ se puede tirar?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `same_role` | Sus dos números hacen el mismo papel en la operación | — |
| 　 | `grow` | Su resultado siempre crece | — |
| 　 | `join` | Las dos juntan cantidades en lugar de separarlas | — |
| 　 | `naturals` | Solo funcionan con números naturales | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuánto sale?
¿Cuánto sale?

Respuesta: `1700`

Escalera de pistas:
1. Busca dos factores que juntos den 100.
2. 50 × 2 = 100.
3. 100 × 17 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya distingues en qué operaciones el orden se puede mover.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué la resta y la división no aguantan el intercambio.

**PD1**

¿Dan lo mismo $6\times 9$ y $9\times 6$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes` | Sí | — |
| 　 | `no` | No | `multiplicacion_no_conmutativa` |

**PD2**

¿Dan lo mismo $15-6$ y $6-15$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No | — |
| 　 | `yes` | Sí | `todas_las_operaciones_son_conmutativas` |

**PD3**

¿Existe algún par de números donde $a-b=b-a$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes_equal` | Sí: cuando a y b son iguales | — |
| 　 | `no_never` | No, nunca | `olvida_el_caso_de_igualdad` |
| 　 | `yes_always` | Sí, siempre | `todas_las_operaciones_son_conmutativas` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N3-M01-CONMUTATIVA-D1` | `no` | `orden_altera_toda_operacion` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-D2` | `yes` | `todas_las_operaciones_son_conmutativas` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-D3` | `all` | `todas_las_operaciones_son_conmutativas` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-D3` | `sum_only` | `multiplicacion_no_conmutativa` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-D3` | `none` | `orden_altera_toda_operacion` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E3` | `sum` | `orden_altera_toda_operacion` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E3` | `mult` | `multiplicacion_no_conmutativa` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E3` | `same` | `no_evalua_antes_de_juzgar` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E4` | `arith` | `error_de_calculo_no_de_orden` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E4` | `rounded` | `error_de_notacion_no_de_valor` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E4` | `none` | `todas_las_operaciones_son_conmutativas` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E5` | `true` | `todas_las_operaciones_son_conmutativas` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E5` | `false_never` | `olvida_el_caso_de_igualdad` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E5` | `true_positive` | `todas_las_operaciones_son_conmutativas` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E7` | `no` | `aplica_la_restriccion_a_toda_la_expresion` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E7` | `yes_all` | `todas_las_operaciones_son_conmutativas` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-E7` | `only_paren` | `parentesis_como_amuleto` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-PD1` | `no` | `multiplicacion_no_conmutativa` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-PD2` | `yes` | `todas_las_operaciones_son_conmutativas` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-PD3` | `no_never` | `olvida_el_caso_de_igualdad` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |
| `PREALG-N3-M01-CONMUTATIVA-PD3` | `yes_always` | `todas_las_operaciones_son_conmutativas` | Pregúntate si los dos números hacen el mismo papel antes de moverlos. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/03-prealg-n3-fabrica/m01-conmutativa-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
