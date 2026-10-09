# Nodo: El orden no se puede dar vuelta — PREALG-N2-E02-RESTA-QUITAR

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N2-E02-RESTA-QUITAR` |
| `concept_slug` | `resta` |
| Error focal | `resta_es_conmutativa` |
| Sala / edificio | La Casa de Cuentas |
| Guía | KatIA |
| Entra después de | `PREALG-N2-E00-CIUDAD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** La Casa de Cuentas · Resta

**Título:** El orden no se puede dar vuelta

En el Granero podías cambiar los sumandos de sitio y no pasaba nada. Aquí no. Vas a ver qué significa exactamente 5 − 8, por qué durante siglos se dijo que «no se podía», y qué se rompe si le das vuelta a la resta para que quepa.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir la tablilla. Sin nota.

**D1**

El arca de la Casa tenía 23 óbolos y se prestaron 15. ¿Cuántos le quedan?

Respuesta: `8`

**D2**

¿Cuánto vale $6-11$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `minus_five` | -5 | — |
| 　 | `five` | 5 | `resta_es_conmutativa` |
| 　 | `cannot` | No se puede: 6 es menor que 11 | `resta_menor_menos_mayor_no_existe` |

**D3**

¿Dan lo mismo $9-4$ y $4-9$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: dan resultados distintos | — |
| 　 | `yes` | Sí: la resta es como la suma, el orden da igual | `resta_es_conmutativa` |
| 　 | `same_magnitude` | Sí, porque las dos dan 5 | `resta_es_conmutativa` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Dentro de la Casa de Cuentas* — **El muro donde el cero es una línea**

El segundo edificio es la Casa de Cuentas: un salón con arcas al fondo y, en la pared, un muro de tablillas atravesado por una línea grabada. Lo que se tiene se anota por encima de la línea; lo que se debe, por debajo. La línea es el cero.

El contador viejo, sin embargo, nunca escribía debajo de la línea: decía que restarle a lo poco lo mucho «no se puede anotar». Hoy entró un cliente con 7 óbolos y una deuda de 12. El contador le dio vuelta a la resta para que cupiera arriba y anotó 5. El cliente salió creyendo que le sobraban 5 óbolos.

**Pregunta:** ¿Puede una resta dar vuelta a sus dos números sin cambiar de significado?

**Intento genuino** (`acotado`): Escoge la que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Sí: 7 − 12 y 12 − 7 son la misma cuenta | — |
| 　 | `b` | No: son cuentas distintas y solo una describe al cliente | — |
| 　 | `c` | 7 − 12 simplemente no existe | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **La misma pareja, dos restas distintas**

Abajo están los mismos dos números en las dos restas posibles. Fíjate en qué pregunta responde cada una.

- **Caso que funciona** — Pregunta: ¿cuánto le queda? Le quedan 5.
- **Caso que rompe la expectativa** — Pregunta: ¿cómo queda? Queda debiendo 5. No es lo mismo.

**Resolución:** Los dos resultados tienen el mismo 5, y ahí está la trampa: parece que da igual el orden. Pero uno dice «me sobran 5» y el otro dice «debo 5». El signo no es un detalle de escritura: es la diferencia entre cobrar y pagar.

**Definición — La resta**

$$a-b=a+(-b)$$

Restar es quitar, o medir la distancia dirigida desde b hasta a. Restar b es lo mismo que sumar el opuesto de b: por eso la resta no necesita reglas nuevas, solo los negativos.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a` | minuendo | de lo que se quita; va primero y no se puede mover |
| `b` | sustraendo | lo que se quita |
| `a-b` | diferencia | el resultado |
| `-b` | el opuesto de b | el número que apunta al lado contrario (B05) |
| `a-b\neq b-a` | la resta no es conmutativa | cambiar el orden cambia el resultado; se formaliza en N3-M01 |

### A5. Ejemplos resueltos

#### La cuenta del cliente · *resuelto*

El cliente llega con 7 óbolos y debe 12 al prestamista. ¿Cómo queda su cuenta después de pagar todo lo que puede?

- Tiene 7 y hay que quitarle 12: la resta se escribe 7 − 12, en ese orden.
- Convierto a suma: 7 − 12 = 7 + (−12). Restar es sumar el opuesto.
- 7 y −12 apuntan a lados contrarios: se cancelan 7 con 7.
- Del −12 sobran 5 sin cancelar, y apuntan hacia abajo: −5.
- 7 − 12 = −5. Queda debiendo 5 óbolos, no sobrándole 5.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': 'En el paso 2 la resta se convierte en suma. ¿Qué gano al reescribirla así?'}

#### Borrar una tablilla de debajo de la línea · *resuelto*

En el muro, una cuenta está justo en la línea del cero y tiene colgada debajo una tablilla de deuda de 4 óbolos. Se descubre que esa deuda ya estaba pagada y se retira la tablilla. ¿En cuánto queda la cuenta?

- La cuenta parte en 0 y lo que se quita es una tablilla de −4.
- Escribo la resta: 0 − (−4).
- Restar es sumar el opuesto, y el opuesto de −4 es +4: 0 + 4.
- 0 + 4 = 4. Quitar algo que colgaba POR DEBAJO de la línea sube la cuenta.
- Por eso menos por menos da más: no es una regla arbitraria, es qué pasa al retirar un déficit.

#### El contador que dio vuelta la resta · *TRAMPA*

La tablilla del contador viejo dice: «El cliente trae 7 y debe 12. Como 7 − 12 no se puede anotar encima de la línea, escribo 12 − 7 = 5. Le sobran 5 óbolos».

- Comprueba al revés: si al cliente le sobraran 5, tendría 12 óbolos, no 7.
- 12 − 7 responde otra pregunta: cuánto le queda al ARCA de la Casa, no al cliente.
- La resta correcta es 7 − 12 = −5, y el signo dice quién le debe a quién.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '7-12=5', 'right_latex': '7-12=-5', 'rows': [{'wrong': 'Si el minuendo es menor, se da vuelta la resta', 'right': 'El orden se respeta y el resultado sale negativo'}, {'wrong': 'El cliente tiene 5 óbolos de sobra', 'right': 'El cliente queda debiendo 5 óbolos'}]}
**¿Por qué falla?:** ¿Por qué 12 − 7 no responde la pregunta del cliente? Escribe la resta correcta.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Un tejedor tenía 18 óbolos y pagó una multa de 25.

- dado: $18-25=18+(-25)$
- dado: $\text{se cancelan 18 con 18}$
- hueco `P1-b1`: $18-25=$ → `-7`

**P2** (*falta: middle*) — Una cuenta del muro estaba 3 óbolos por debajo de la línea y se le añaden 5 de deuda.

- dado: $-3-5$
- hueco `P2-b1`: $-3-5=-3+(\square),\ \square=$ → `-5`
- hueco `P2-b2`: $-3-5=$ → `-8`

**P3** (*falta: statement_only*) — Solo el planteamiento: en el muro, la cuenta de un naviero está 6 óbolos por encima de la línea y la de un alfarero, 9 por debajo. ¿Cuántos óbolos separan una cuenta de la otra?

- hueco `P3-b1`: $6-(-9)=$ → `15`


### A7. Comparación de métodos

**Dos caminos para la misma diferencia**

¿Cuánto vale $-4-(-11)$? Las dos soluciones de abajo son correctas.

- **Método 1 · Convertir a suma del opuesto** — 
- **Método 2 · Contar la distancia en la recta** — 

**Pregunta:** ¿Cuál usarías con números grandes? ¿Y qué te dice el método 2 sobre el signo del resultado?

**Insight:** El método 2 explica el signo sin memorizar reglas: si vas hacia la derecha el resultado es positivo, si vas hacia la izquierda es negativo. Y deja ver por qué a − b y b − a solo se diferencian en el sentido del recorrido: mismo tramo, dirección contraria.

### A8. Práctica independiente (7 ítems)

**E1**

Un naviero llega con 92 óbolos y salda una deuda de 47. ¿Cuántos le quedan?

Respuesta: `45`

Escalera de pistas:
1. El minuendo es lo que tenía.
2. 92 − 40 = 52.
3. 52 − 7 = …

**E2**

Un aprendiz tenía 14 óbolos y debía pagar 31. ¿Cómo queda su cuenta?

Respuesta: `-17`

Escalera de pistas:
1. Respeta el orden: primero lo que tiene.
2. 14 − 31 = 14 + (−31): se cancelan 14.
3. Del −31 sobran 17, y apuntan hacia abajo.

**E3**

Una cuenta está 6 óbolos por debajo de la línea y se le retira una deuda de 2. ¿En cuánto queda?

Respuesta: `-4`

Escalera de pistas:
1. Restar un negativo es sumar su opuesto.
2. −6 − (−2) = −6 + 2.
3. Se cancelan 2 del −6.

**E4**

Un escriba anota «5 - 9 = 4». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `swapped` | Restó al revés: hizo 9 - 5. Lo correcto es -4 | — |
| 　 | `arith` | Se equivocó en la aritmética: da 14 | `confunde_resta_con_suma` |
| 　 | `sign_only` | El resultado debía ser 4 pero con otro signo por casualidad | `signo_es_decorativo` |
| 　 | `none` | Ningún error, está bien | `habito_valida_sin_verificar` |

Escalera de pistas:
1. ¿Qué número escribió primero y cuál está primero en el enunciado?
2. 9 − 5 = 4, pero la cuenta pedida era 5 − 9.
3. 5 − 9 = 5 + (−9) = −4.

**E5**

¿Es verdadera o falsa? «Para cualesquiera $a$ y $b$: $a-b=b-a$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_opposite` | Falsa: dan opuestos, salvo cuando a = b | — |
| 　 | `true` | Verdadera: el orden no importa, como en la suma | `resta_es_conmutativa` |
| 　 | `false_never` | Falsa: nunca pueden coincidir | `olvida_el_caso_de_igualdad` |
| 　 | `true_positive` | Verdadera solo si los dos son positivos | `resta_es_conmutativa` |

Escalera de pistas:
1. Prueba con a = 9 y b = 4.
2. 9 − 4 = 5 y 4 − 9 = −5. No son iguales.
3. ¿Hay algún par donde sí coincidan? Prueba a = b.

**E6**

En el muro, una cuenta está 8 óbolos por encima de la línea y otra 11 por debajo. ¿Cuántos óbolos separan la de abajo de la de arriba?

Respuesta: `19`

Escalera de pistas:
1. La distancia es la resta de los dos niveles.
2. 8 − (−11) = 8 + 11.
3. Cuenta desde −11 hasta 0 y de 0 hasta 8.

**E7**

¿Cuál es el conjunto más pequeño de la escalera donde TODA resta tiene resultado?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `integers` | Los enteros | — |
| 　 | `naturals` | Los naturales | `resta_menor_menos_mayor_no_existe` |
| 　 | `rationals` | Los racionales | `no_busca_el_minimo` |
| 　 | `reals` | Los reales | `no_busca_el_minimo` |

Escalera de pistas:
1. Busca el primer peldaño donde 5 − 8 ya tiene respuesta.
2. En ℕ la resta 5 − 8 se sale del conjunto.
3. Piden el MÁS PEQUEÑO que sirva, no cualquiera que sirva.


### A9. Cierre

*La escalera de la resta* — **¿La resta de dos elementos del conjunto vive en el conjunto?**

Aquí es donde la escalera dio su primer salto obligado.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✗ | El primer conjunto que se rompe: no hay natural que responda 7 − 12. |
|  | ✅ | ℤ nació exactamente de esto (B05): darle respuesta a toda resta. |
|  | ✅ | Fracción menos fracción sigue siendo fracción. |
|  | ✗ | Dos irracionales pueden restar un racional: el resultado SE SALE. Ninguna operación aritmética los cierra. |
|  | ✅ | ℝ = ℚ ∪ 𝕀 (B08) sí cierra: la resta vive cómoda ahí. |
|  | ✅ | También cierra. Desvío opcional (B09). |

La suma no rompió ningún peldaño; la resta rompió el primero. Ese es el motor de toda la escalera: una operación que no cabe obliga a inventar números nuevos.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `order` | En los tres el orden de los números cambia el resultado | — |
| 　 | `negative` | En los tres el resultado es negativo | — |
| 　 | `as_sum` | Los tres se pueden reescribir como una suma del opuesto | — |
| 　 | `naturals` | En los tres los dos números son naturales | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuál es el saldo final del cliente?
¿Cuál es el saldo final del cliente?

Respuesta: `-5`

Escalera de pistas:
1. Empieza en −34 y aplica un movimiento a la vez.
2. −34 + 20 = −14.
3. Retirar una deuda de 9 es −14 − (−9) = −14 + 9.

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya respetas el orden de la resta aunque el minuendo sea menor.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo por qué a − b y b − a no responden la misma pregunta.

**PD1**

El arca tenía 41 óbolos y se prestaron 16. ¿Cuántos le quedan?

Respuesta: `25`

**PD2**

¿Cuánto vale $4-13$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `minus_nine` | -9 | — |
| 　 | `nine` | 9 | `resta_es_conmutativa` |
| 　 | `cannot` | No se puede | `resta_menor_menos_mayor_no_existe` |

**PD3**

¿Existe algún par de números donde $a-b=b-a$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `yes_equal` | Sí: cuando a y b son iguales | — |
| 　 | `no_never` | No, nunca | `olvida_el_caso_de_igualdad` |
| 　 | `yes_always` | Sí, siempre | `resta_es_conmutativa` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N2-E02-RESTA-QUITAR-D2` | `five` | `resta_es_conmutativa` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-D2` | `cannot` | `resta_menor_menos_mayor_no_existe` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-D3` | `yes` | `resta_es_conmutativa` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-D3` | `same_magnitude` | `resta_es_conmutativa` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E4` | `arith` | `confunde_resta_con_suma` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E4` | `sign_only` | `signo_es_decorativo` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E4` | `none` | `habito_valida_sin_verificar` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E5` | `true` | `resta_es_conmutativa` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E5` | `false_never` | `olvida_el_caso_de_igualdad` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E5` | `true_positive` | `resta_es_conmutativa` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E7` | `naturals` | `resta_menor_menos_mayor_no_existe` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E7` | `rationals` | `no_busca_el_minimo` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-E7` | `reals` | `no_busca_el_minimo` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-PD2` | `nine` | `resta_es_conmutativa` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-PD2` | `cannot` | `resta_menor_menos_mayor_no_existe` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-PD3` | `no_never` | `olvida_el_caso_de_igualdad` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |
| `PREALG-N2-E02-RESTA-QUITAR-PD3` | `yes_always` | `resta_es_conmutativa` | Revisa cuál número va primero antes de operar y vuelve a intentarlo. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/02-prealg-n2-mercado/e02-resta-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
