# Guía del docente

Qué ve, qué puede hacer y qué decisiones toma un docente en Oulad.

---

## 1 · Entrar por primera vez

Te registras eligiendo rol **docente**. Tu cuenta queda pendiente hasta que un
**administrador la aprueba** — es a propósito: un docente ve datos de menores de
edad, así que el alta no es automática. Mientras tanto puedes entrar pero no ves
grupos.

La consola está pensada para **escritorio** (1280 px). La vista de estudiante es
la que está pensada para celular.

---

## 2 · Grupos

Un estudiante sin grupo no aparece en tu dashboard. Dos formas de que entre:

**Código de invitación** (lo normal). Creas el grupo, generas su código y lo
repartes. El estudiante lo pega al registrarse o desde Materias. **El código
funciona entre niveles**: puedes meter a un estudiante de Universidad en un grupo
de Colegio si tiene sentido para tu curso.

**Reasignación por el administrador.** Si alguien entró al grupo equivocado, el
admin lo mueve. Queda **auditado** — quién, cuándo y de dónde a dónde.

Los nombres de grupo se normalizan: no puedes tener dos que solo se diferencien
en mayúsculas o tildes.

---

## 3 · Dashboard — leer el grupo

Está ordenado por datos, no por decoración: primero los gráficos, después las
acciones.

**Por estudiante:**

- **ELO en el tiempo** — la curva. Lo que buscas no es que suba siempre, sino que
  **se estabilice**: al principio se mueve mucho porque el sistema todavía no lo
  conoce.
- **Radar por tema** — dónde está fuerte y dónde no. Es lo más accionable de la
  pantalla: dice qué repasar con esa persona.
- **Historial de KatIA** — todo lo que le preguntó a la tutora. Sirve para ver
  dónde se atascó de verdad, no dónde falló la respuesta.
- **Ranking dentro del grupo**.
- **Análisis con IA** — un resumen pedagógico bajo demanda. Es un apoyo, no un
  diagnóstico; contrástalo con el radar.

**Métricas de uso del grupo:** tiempo promedio por pregunta, tasa de abandono,
temas más trabajados y distribución horaria de la actividad.

> **Los estudiantes de prueba están marcados** (`is_test_user`) y se excluyen de
> las exportaciones. No los borres: sostienen los tests de la plataforma.

### Cómo leer el ELO sin malinterpretarlo

- **Es por tema, no global.** Un promedio de 1.200 puede esconder 1.600 en
  fracciones y 800 en potencias. Mira siempre el radar antes de concluir.
- **Bajar no siempre es empeorar.** Si un estudiante subió de nivel, empieza a
  recibir preguntas más difíciles y el puntaje se ajusta. Lo preocupante es una
  caída sostenida en un tema concreto.
- **Comparar dos estudiantes por ELO global es la lectura más floja disponible.**
  Compara trayectorias, no cifras de un día.

---

## 4 · Procedimientos manuscritos

El circuito completo:

1. El estudiante sube foto o PDF de su procedimiento.
2. La IA lo revisa y propone una nota de 0 a 100 con observaciones paso a paso.
3. **Tú pones la nota oficial.** La de la IA nunca toca el ELO — es una lectura
   previa para que no partas de cero.
4. Al calificar, el ELO del estudiante se ajusta con `(nota − 50) × 0,2`: un 100
   suma 10 puntos, un 0 resta 10, un 50 no mueve nada.
5. Al estudiante le llega el aviso en el momento.

El sistema calcula una **huella SHA-256** de cada archivo y detecta si el mismo
estudiante sube dos veces lo mismo.

Las imágenes viven en almacenamiento **privado** — se sirven por bytes
autenticados, nunca por un enlace público que se pueda reenviar.

---

## 5 · Exámenes

Puedes armar exámenes propios y asignarlos a un grupo: eliges las preguntas del
banco, defines el tiempo y lo publicas. El estudiante los ve en su pantalla de
Exámenes junto a la opción «Estándar (auto)», que arma la plataforma sola.

Los resultados quedan por plantilla.

**La respuesta correcta nunca viaja al navegador del estudiante**, ni durante el
examen ni al enviarlo. Al responder solo se colorea la opción que eligió.

---

## 6 · Exportar

Dos formatos, ambos filtrados para excluir a los usuarios de prueba:

- **CSV** — intentos en plano, una fila por respuesta.
- **XLSX** — cuatro hojas, incluida la columna `cursos_matriculados`.

Sirven para llevarlos a Excel, a SPSS o a lo que uses para calificar.

---

## 7 · Las lecciones guiadas de Álgebra básica

Además de la práctica adaptativa, **Álgebra básica** tiene una ruta de 60
lecciones narradas que va de conjuntos numéricos a factorización.

Lo que conviene saber para no interpretarlas mal:

- **No mueven el ELO.** Son para construir el concepto; el rating se mueve
  practicando. Un estudiante puede llevar media ruta y tener el ELO donde estaba.
- **Se desbloquean en orden.** Cada lección abre la siguiente.
- **Cada lección abre y cierra con las mismas dos preguntas.** Las del principio
  **no se corrigen** a propósito — son la línea base. La comparación entre las dos
  tomas es lo que dice si la pantalla sirvió.
- **Cada lección trae un ejemplo mal resuelto a propósito**, con el error más
  común del tema. Si un estudiante te dice que «la plataforma tiene un ejercicio
  malo», probablemente sea ese: está señalado con color de advertencia y el
  ejercicio siguiente lo corrige.
- **Cada error tiene nombre y ruta de repaso.** Cuando un estudiante se equivoca
  se guarda qué error concreto cometió, y el sistema sabe qué lección se lo
  enseña.

El detalle completo (los 60 nodos, el error que caza cada uno) está en
[ruta-de-aprendizaje.md](ruta-de-aprendizaje.md).

**Pendiente conocido:** solo el primer nivel tiene pantalla de cierre
diagnóstico. Los otros terminan en su último concepto sin recoger qué quedó
flojo.

---

## 8 · El diagnóstico de entrada

La primera vez que un estudiante abre una materia, la plataforma le pide 10
preguntas para fijar su punto de partida por tema.

Dos cosas que vale la pena decirle al grupo antes:

- **«No lo sé» es una respuesta válida y no penaliza.** Adivinar sí distorsiona
  el punto de partida hacia arriba y le deja ejercicios más duros de la cuenta.
- **No es una nota.** No genera intentos ni entra en tu dashboard como
  evaluación.

Se puede rehacer.

---

## 9 · Qué NO hace la plataforma

Para no prometerlo en clase:

- **No califica procedimientos sola.** La IA propone; tú decides.
- **No sustituye la clase.** Elige el ejercicio del tamaño correcto; no explica
  el tema desde cero salvo en las lecciones guiadas de Álgebra básica.
- **KatIA no da respuestas.** Está construida para no hacerlo, y hay una
  verificación que descarta su respuesta si se le escapa la solución.
- **El ELO no es una nota.** Es una estimación de nivel que se mueve sola. Usarlo
  como calificación directa premia la constancia por encima del aprendizaje.

---

## 10 · Si algo falla

- Un estudiante que reporta que **perdió un examen**: revisa antes de repetírselo
  — hay borrador local y reintento automático, casi siempre está guardado.
- **Reportes técnicos** de estudiantes llegan al administrador, no a ti.
- Un **ítem sospechoso** (opciones repetidas, enunciado ambiguo, 0 % de acierto
  con muchos intentos) se recalibra o se retira. Pásalo a quien mantenga el
  banco: hay un validador que corre en cada cambio.
