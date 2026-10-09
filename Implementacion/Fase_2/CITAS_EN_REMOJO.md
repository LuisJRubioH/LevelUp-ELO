# Citas en remojo — pendientes de anclar a la biblioteca aprobada

Estado 2026-08-13. No se elimina ninguna: quedan aquí, sin usarse en texto publicable,
hasta decidir si entran a la biblioteca del proyecto.

**Regla mientras estén en remojo:** se pueden usar para diseñar contenido, no para
respaldarlo por escrito. Ninguna debe aparecer como cita en un documento que salga del
equipo.

## Las siete de `VALIDACION_pedagogica_N2.md:135` — emparejadas

El checklist de N2 solo lista apellidos, pero **el par afirmación↔cita sí estaba escrito**:
en la sección de referencias de cada ficha de nodo. Recuperado el 2026-08-13:

| Cita | Qué afirmación sostiene | Dónde |
|---|---|---|
| **Bruner** | Progresión concreto → representacional → abstracto | `F2_nodo_suma.md:907` |
| **Carpenter & Moser (1984)** | Problemas aditivos y composición de cantidades | `F2_nodo_suma.md:908` |
| **Carpenter & Moser (1984)** | Los dos sentidos de la resta: quitar y comparar | `F2_nodo_resta.md:256` |
| **Vergnaud (1983)** | Multiplicación como suma repetida y razonamiento multiplicativo | `F2_nodo_multiplicacion.md:254` |
| **Sweller & Cooper (1985)** | Conmutatividad por descubrimiento; carga cognitiva | `F2_nodo_multiplicacion.md:255` |
| **Greer (1992)** | División: partición y cuotición; residuo | `F2_nodo_division.md:228` |
| **Vergnaud (1983)** | División como operación inversa | `F2_nodo_division.md:229` |
| **Confrey & Smith (1994)** | Crecimiento exponencial; confusión exponencial/lineal | `F2_nodo_potenciacion.md:269` |
| **Hattie & Timperley (2007)** | Retroalimentación formativa por error | Los seis nodos de N2 |

Las siete son atribuciones **correctas**: cada autor sostiene lo que se le atribuye, y las
obras existen y dicen eso.

### Una corrección de año

Los tres modos de representación (enactivo → icónico → simbólico) son de **Bruner (1966)**,
*Toward a Theory of Instruction*. Varias fichas citan **Bruner (1960)**, que es
*The Process of Education* — otro libro, sobre currículo en espiral. Donde se cite la
progresión concreto→abstracto, el año correcto es 1966.

`Bruner (1961)` sí está bien donde aparece: es «The act of discovery», y se cita para el
descubrimiento guiado (`F3_nodo_conmutativa.md`, `F3_nodo_laboratorio_hub.md`).

### Un matiz de alcance

**Carpenter & Moser (1984)** estudia grados 1 a 3. Para 8.º grado sirve como fundamento de
la tipología de problemas aditivos, no como evidencia sobre esta población. Si la cita sale
en un documento externo, conviene decirlo.

### Dos que probablemente ya están dentro

**Sweller** y **Hattie & Timperley** se citan en la spec de B06 y en las siete fichas de
Fase 1, junto a Black & Wiliam, Mayer, Atkinson/Renkl/Merrill y Arnold & Pistilli. Si esa
lista es la biblioteca aprobada, los dos salen de aquí sin más trámite.

## La afirmación causal de `invierte_cociente`

Marcada `[SIN RESPALDO]` en `specs/PREALG-N1-B06-…md:544`. Distinguir dos cosas:

- **El error existe** y está atestiguado en el propio banco. El tag se conserva.
- **La explicación causal** —que el sesgo de número natural lleva a invertir el cociente
  cuando el dividendo es menor que el divisor— es la que no tenía fuente aprobada.

Búsqueda del 2026-08-12: la afirmación **tiene respaldo en la literatura**, y la fuente
canónica es **Fischbein, Deri, Nello & Marino (1985)**, «The role of implicit models in
solving verbal problems in multiplication and division» (*JRME* 16(1)). Documenta el modelo
implícito de la división partitiva con sus restricciones tácitas —entre ellas que el divisor
debe ser menor que el dividendo—, con 623 estudiantes de grados 5, 7 y 9. Hay una
replicación reciente (Maffia et al., 2022, *Implementation and Replication Studies in
Mathematics Education* 2(2)) que la sostiene.

Complementarias, por si la biblioteca prefiere algo más cercano al sesgo de número natural
como tal: **Graeber & Tirosh (1990)** sobre lo que traen estudiantes de 4.º y 5.º a la
multiplicación y división con decimales, y la línea de **Van Dooren / Van Hoof** sobre
*natural number bias* en operaciones.

**Qué falta:** confirmar que Fischbein et al. (1985) está en la biblioteca aprobada. Si
está, el marcador `[SIN RESPALDO]` se sustituye por la cita y el asunto se cierra.

## La dosis del intento genuino

El segundo marcador de esa spec (línea 548) **no necesita fuente**: el propio documento ya
la declara como predicción comprobable para el piloto, no como hallazgo. Se queda como
hipótesis registrada y se resuelve con datos, no con bibliografía.

---

## Qué queda por decidir

1. ¿Cuál es la **biblioteca aprobada**? Sin esa lista, «anclar» no tiene destino.
2. Confirmar Fischbein et al. (1985) y las siete de N2 contra ella.
3. Corregir el año de Bruner donde se cite la progresión de representaciones.

---

Fuentes consultadas:
[Fischbein et al. — implicit models](https://www.semanticscholar.org/paper/THE-ROLE-OF-IMPLICIT-MODELS-IN-SOLVING-VERBAL-IN-Fischbein-Deri/a358d95e385ea09593860a48ab1453ceb8cbd01d) ·
[Maffia et al. 2022 — replicación](https://brill.com/view/journals/irme/2/2/article-p149_2.xml?language=en) ·
[Natural number bias en operaciones](https://link.springer.com/article/10.1007/s11858-015-0675-6) ·
[Bruner — modos de representación (1966)](https://www.simplypsychology.org/bruner.html)
