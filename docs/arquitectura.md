# Arquitectura — referencia vigente

Estado del sandbox de rediseño (repo `Oulad_redesing`), al **2026-09-07**.

Este documento sustituye a `v2-tecnico.md` y `v2-plan.md`, que describen mayo de 2026 y se
conservan solo por trazabilidad. Aquí hay tres cosas: **qué se decidió y por qué**, **qué límites
tiene el sistema hoy**, y **cómo se despliega**. Las reglas operativas cortas viven en
[AGENTS.md](../AGENTS.md); esto es el porqué detrás de ellas.

Origen: la [auditoría de arquitectura del 2026-09-05](auditoria-arquitectura-2026-09-05.md).

---

## Forma del sistema

Monolito modular. Un proceso FastAPI sirve la API y los WebSockets; el frontend React se despliega
aparte en Vercel. La auditoría concluyó que **conservar el monolito es lo razonable** y que no hay
nada que justifique separar servicios: los problemas eran de integridad y de coordinación, no de
tamaño.

```
src/domain/          aritmética y reglas. Sin I/O, sin librerías externas, sin capas superiores.
src/application/     casos de uso. Importa domain/. NUNCA infrastructure/.
src/infrastructure/  repositorios, storage, clientes de IA, el calibrador isotónico.
src/interface/       Streamlit (V1).
api/                 FastAPI (V2). Junto con interface/, es la CAPA DE COMPOSICIÓN.
```

Las dos primeras líneas están **comprobadas**, no solo escritas:
`tests/unit/test_architecture_layers.py` recorre cada módulo de `domain/` y `application/` y falla
si aparece un import prohibido. Se añadió porque no lo estaban: los servicios importaban el cliente
de IA de infraestructura y el calibrador —que carga un pickle de disco— vivía en `domain/`.

**La composición es explícita.** `api/routers/student.py::_make_service` y
`src/interface/streamlit/app.py` son los únicos sitios que resuelven infraestructura y se la
inyectan a los servicios. Un servicio recibe lo que necesita; no lo va a buscar.

---

## El motor ELO

### `student_topic_elo` es el estado, y es el único

El rating de un estudiante en un tópico vive en una fila de `student_topic_elo`. Nada más es
estado:

- `users.current_elo` es **derivado** — el promedio de las filas del alumno. Se recalcula, no se
  escribe a mano.
- `attempts` es **bitácora** — sirve para analítica e historial, no para reconstruir el rating.

Cuatro caminos escriben, y cada uno aplica su efecto **exactamente una vez**:

| Camino | Cómo | Efecto |
|---|---|---|
| Diagnóstico | `set_topic_elo_baseline` → `_set_topic_elo` | fija el valor |
| Respuesta con `elo_valid=1` | `save_answer_transaction` → `_set_topic_elo` | fija el valor |
| Procedimiento validado por el docente | `validate_procedure_submission` → `_bump_topic_elo` | suma `elo_delta`, marca `elo_applied=1` |
| Partida de PvP terminada | `finish_pvp_match` → `_bump_topic_elo` | suma el delta al tópico del curso |

**Por qué importa.** Antes, `get_latest_elo_by_topic` reconstruía el rating leyendo el último
intento de `attempts` y sumándole la suma histórica de los deltas de procedimiento. Eso producía
tres fallos a la vez: el delta del procedimiento se reaplicaba en **cada lectura posterior**; la
lectura no filtraba `elo_valid`, así que un intento fuera del rango [3s, 600s] —que el sistema
declara inválido— sí movía el rating; y el baseline del diagnóstico se perdía en cuanto había un
intento. Hoy esa función es un `SELECT` de una tabla y nada más.

`finish_pvp_match` escribía `users.current_elo` directamente. Como ese campo es un promedio
derivado, el resultado de cada partida **se borraba solo** en el siguiente ejercicio que hiciera el
alumno.

Regresión: `tests/integration/test_elo_single_source.py`, que corre en los dos motores.

### Responder es una unidad de trabajo

`save_answer_transaction(user_id, item_id, topic, compute, ...)` no recibe un resultado
precalculado: recibe el **cálculo**. El repositorio abre la transacción, bloquea, lee, llama a
`compute(state)` y persiste, todo dentro de la misma transacción.

- PostgreSQL: `SELECT ... FOR UPDATE` sobre `users` y después sobre `items`, **siempre en ese
  orden** — un orden fijo es lo que evita que dos transacciones se crucen en un deadlock.
- SQLite: `BEGIN IMMEDIATE`, que toma el lock de escritura *antes* de leer.

`compute` lo aporta `StudentService` y contiene la aritmética de dominio. **No debe hacer I/O**:
corre con una conexión del pool tomada y filas bloqueadas.

**Por qué.** El vector de rating y la dificultad del ítem se leían fuera de la transacción y se
escribían después. Dos respuestas concurrentes del mismo alumno partían del mismo rating y una
borraba el efecto de la otra. La atomicidad de las escrituras no arregla una lectura obsoleta.

### Reintentos que no duplican

El cliente reintenta los POST ante errores de red y 502/503/504. Si el servidor confirmó y se
perdió la respuesta, el reintento llegaría como una respuesta nueva. Por eso `/answer` acepta una
cabecera `Idempotency-Key`: la clave se persiste con el intento bajo una restricción única, y un
reintento con la misma clave devuelve el resultado guardado en vez de mover el rating otra vez.
No se deduplica por estudiante+ítem, porque volver a practicar el mismo ítem es legítimo.

### Qué NO mueve el ELO

- El **modo examen**. `/exam/submit` es evaluativo: califica y no toca el rating, en ningún bloque.
- El `ai_proposed_score` de un procedimiento. Solo la nota del docente (`teacher_score`) lo mueve.
- Un intento con `time_taken` fuera de [3s, 600s]. Se guarda para analítica, marcado
  `elo_valid=0`, y no altera el rating.

### El factor K

La práctica usa el modelo vectorial: `K = 32 × (RD / 350)`, con RD entre 350 y 30. Las primeras
respuestas mueven mucho y el rating se asienta con la experiencia. `calculate_dynamic_k`
(40/32/16/24) existe en `src/domain/elo/model.py` pero pertenece al modelo escalar y **no está en
el camino de la práctica**. El PvP usa K=24 fijo sobre el resultado de la partida.

---

## Concurrencia y procesos

### Un solo proceso, y comprobado

`_lobby` y `_matches` (`api/websocket/pvp.py`) y `_rooms` (`notifications.py`) viven en memoria del
proceso. Con dos procesos cada uno tiene su propio lobby: dos jugadores del mismo curso conectados
a procesos distintos **no se emparejan nunca**, y un evento llega solo a los sockets locales. Sin
excepción, sin log, sin nada visible.

Por eso `settings.validate_runtime()` **rechaza el arranque** en producción si
`WEB_CONCURRENCY > 1`, y `render.yaml` lo fija en `"1"`. Es una restricción declarada, no un
accidente.

Lo que sí trasciende al proceso ya está resuelto: las partidas se persisten en `pvp_matches`, y las
que un reinicio deja huérfanas —el cronómetro vive en el proceso que creó la partida— las cierra
`expire_stale_pvp_matches()` como `abandoned`, sin tocar ELO, al preparar el esquema.

### Nada bloqueante en el event loop

Los repositorios son síncronos. Toda llamada desde un `async def` va por `asyncio.to_thread(...)`,
y **nunca** con `_lock` tomado: el lock del lobby cubre el traspaso en memoria y nada más. Una
consulta a la base con el lock tomado congela el emparejamiento de todos los cursos a la vez, y el
backoff del pool agotado (que duerme) lo haría con el event loop entero.

`notify_sync` usa el loop registrado al arrancar (`bind_event_loop`). Buscarlo desde el hilo del
threadpool —donde FastAPI corre los endpoints `def`— fallaba siempre, y la notificación se
descartaba en silencio.

---

## Persistencia

### Dual DB

SQLite y PostgreSQL mantienen **API pública idéntica**. Cualquier cambio en uno se replica en el
otro; `python scripts/db_sync_check.py` es obligatorio antes de un commit que toque repositorios.

Ese verificador compara texto, firmas y DDL: **no demuestra equivalencia de resultados**. Para eso
está `tests/integration/test_elo_single_source.py`, parametrizado sobre los dos motores; el job
`test-postgres` de CI levanta un PostgreSQL efímero y ejecuta la rama PostgreSQL.

### Migraciones

Solo aditivas: `ALTER TABLE ADD COLUMN IF NOT EXISTS`. Nunca `DROP` ni cambios de tipo.

El bootstrap (`_bootstrap_schema`: esquema + seeds + backfills) corre **solo si `RUN_MIGRATIONS` ≠ 0**.
En despliegue lo aplica `scripts/migrate.py` como proceso aparte y el proceso web lleva
`RUN_MIGRATIONS=0`.

**Por qué separado.** `_migrate_db()` toma `pg_try_advisory_lock`, que es un lock de **sesión**.
Sobre el pooler de transacciones de Supabase (puerto 6543) la sesión física no sobrevive al commit,
así que el lock puede acabar liberándose desde otra sesión y dejar de proteger nada. El script usa
`MIGRATION_DATABASE_URL` — conexión directa (5432) o pooler de sesión.

### Pool de conexiones

`ThreadedConnectionPool(1, 5)`. Nunca `conn.close()`: siempre `put_connection(conn)`, porque cerrar
destruye la conexión y agota el pool. No subir `maxconn` en el free tier de Supabase.

---

## Contratos

`src/application/interfaces/repositories.py` declara lo que cada servicio llama **de verdad**.
Antes declaraba métodos inexistentes (`get_item`, `get_available_items`, `get_teacher_groups`,
`get_group_students`, `get_student_attempts`, `save_procedure_score`) y omitía los que sí se usan:
era decoración con sintaxis de contrato.

`tests/unit/application/test_repository_contracts.py` lo comprueba en las dos direcciones: todo lo
declarado existe en ambos motores con los mismos nombres de parámetro, y todo
`self.repository.<algo>` que un servicio invoca está declarado. La segunda es la que atrapa el
olvido normal.

`RepoDep` está tipado con `IRepository` (la unión de los tres roles), no con `object`. No cubre
todos los métodos que usan los routers; cubre el núcleo y ancla el test.

---

## Seguridad

- **Datos canónicos.** `/answer` identifica el ítem por id y toma **todo** lo académico de la base:
  dificultad, tópico, RD y opciones. El cliente solo aporta identificación, respuesta y telemetría.
  Antes podía enviar una dificultad alterada, o comparar la solución de un ítem mientras se
  persistía otro identificador.
- **La respuesta correcta nunca viaja al frontend.** Ni en `/answer` ni en `/exam/submit`. Al
  responder se colorea solo la opción elegida.
- **WebSockets.** `authenticate_access_token` es la política común de REST y WS: exige
  `type=access`, cuenta activa y docente aprobado. Además, la sala se autoriza contra el usuario
  (`student_{id}` propio, `teacher_{id}` propio, `group_{id}` del alumno o del docente dueño); PvP
  exige rol estudiante y matrícula en el curso.
- Contraseñas con Argon2id, migración transparente desde SHA-256 legacy.
- Bucket `procedimientos` privado; las imágenes se sirven por bytes, nunca por URL pública.
- Claves de IA solo en variables de entorno del backend. Nunca en la base ni en logs.

---

## Observabilidad

`/api/health` es **readiness**, no liveness: ejecuta una consulta mínima y devuelve **503** si la
base no responde. El health check del despliegue apunta ahí, así que una instancia con la
persistencia caída no recibe tráfico. El arranque no traga el error de inicialización.

---

## Despliegue

Frontend en Vercel, backend en Render, base en Supabase. Los tres son del **sandbox**, aparte de
producción.

### Variables de entorno del backend

| Variable | Para qué |
|---|---|
| `DATABASE_URL` | Tráfico normal — pooler de transacciones (6543) |
| `MIGRATION_DATABASE_URL` | Solo `scripts/migrate.py` — conexión directa (5432) o pooler de sesión |
| `RUN_MIGRATIONS` | `0` en el proceso web: el esquema lo aplica el paso previo |
| `WEB_CONCURRENCY` | `1`, obligatorio — ver § Un solo proceso |
| `JWT_SECRET_KEY` | ≥32 caracteres; Render lo genera |
| `CORS_ORIGINS` | JSON con el dominio exacto de Vercel. Sin `localhost` en producción |
| `RATE_LIMIT_STORAGE_URI` | Redis/Valkey. `memory://` está prohibido en producción |
| `SUPABASE_URL` / `SUPABASE_KEY` | Bucket `procedimientos` |
| `SYSTEM_AI_API_KEY` | IA. Sin ella la IA degrada con gracia y el resto funciona |
| `ADMIN_USER` / `ADMIN_PASSWORD` | Seed del administrador |

`validate_runtime()` falla el arranque si alguna de las críticas está mal. Es deliberado: mejor no
arrancar que arrancar en un estado que nadie va a notar.

### Orden de arranque

El `startCommand` es `python scripts/migrate.py && uvicorn api.main:app ...`. Primero migra en un
proceso corto que termina, después sirve. Si la migración falla, uvicorn no arranca y el health
check no pasa — fallo visible en lugar de esquema viejo sirviendo tráfico.

`preDeployCommand` sería el sitio natural para la primera mitad, pero **Render no lo ofrece en
instancias free**. Al pasar a un plan de pago, moverlo allí.

### Verificación antes de un commit

```bash
python scripts/db_sync_check.py                                  # obligatorio si tocas repos
python scripts/validate_bank.py                                  # si tocas items/
ADMIN_PASSWORD=testadmin123 python -m pytest tests/ --ignore=tests/e2e -q
cd frontend && pnpm install --frozen-lockfile && pnpm run build
```

---

## Capacidad

**Objetivo: 20–30 estudiantes concurrentes.** Medido el 2026-09-07 con
`python scripts/measure_capacity.py`, que corre el ciclo real
(`/next-question` → `/answer`) con N estudiantes en hilos.

### Lo que cuesta atender a un estudiante

**26 CPU-ms por petición**, estable entre 24 y 32 en todos los escenarios (8 y 30 estudiantes,
con y sin pausa). Es el número que se traslada a otra máquina: el reloj de un portátil no dice
nada sobre una vCPU compartida, pero el trabajo de Python hay que hacerlo en los dos sitios.

Un estudiante genera **2 peticiones por pregunta** (pedirla y responderla). A 20 s por pregunta
—ritmo normal en práctica de matemáticas— son 0,1 peticiones/s por estudiante.

| CPU | peticiones/s | estudiantes a 20 s/pregunta | a 5 s/pregunta |
|---|---|---|---|
| 0.1 vCPU (free) | 3,8 | ~38 | ~11 |
| 0.5 vCPU | 19 | ~190 | ~53 |
| 1 vCPU | 38 | ~380 | ~105 |

La sensibilidad al ritmo es enorme: el mismo hardware pasa de 38 estudiantes a 11 solo con que
respondan cuatro veces más rápido. Un examen cronometrado o un repaso a contrarreloj caen en la
columna de la derecha.

Es un **suelo optimista**: SQLite local, sin red, sin el pool de PostgreSQL y con una CPU más
rápida que 0.1 vCPU compartida. La realidad solo puede ser peor.

### Qué limita de verdad

En orden, y ninguno es el código:

1. **El spin-down del free tier.** Render apaga un servicio free tras 15 minutos sin tráfico y
   tarda ~1 minuto en volver. En una clase eso es el primer estudiante de cada sesión esperando
   un minuto delante de una pantalla de carga. Es la razón más fuerte para salir del free.
2. **0.1 vCPU compartida.** La tabla dice que da para el objetivo a ritmo normal, pero sin
   margen: una ráfaga (todos entran a la vez al empezar la clase) no tiene dónde absorberse.
3. **Un solo proceso.** No es un límite de capacidad sino de arquitectura — ver R18. Mientras
   siga, no se puede compensar con más workers.
4. **El pool de 5 conexiones.** A 3,8 peticiones/s con ~100 ms de base por petición, la
   ocupación media es de 0,4 conexiones. **No es el cuello a esta escala**, y no hay que tocarlo.

### La cola de escritura

`/answer` da p50 ≈ 50–110 ms pero p95 ≈ 1,1 s cuando varios responden en el mismo instante. Es la
unidad de trabajo serializándose (R16), y en la medición está exagerado por dos motivos: SQLite
usa un lock de escritura **global** —PostgreSQL solo bloquea la fila del estudiante y la del
ítem—, y el arranque sincronizado de los hilos crea un rebaño que ningún grupo real reproduce.

Si en producción esa cola resulta molesta, el siguiente ajuste es **quitar el `FOR UPDATE` sobre
`items` y volver la dificultad un delta relativo**: eso elimina la contención entre estudiantes
distintos (que hoy compiten por el mismo ítem cuando el selector los manda al mismo sitio) sin
tocar la serialización por estudiante, que es la que protege el rating. Se paga con que la
dificultad del ítem deja de ser serialmente equivalente — aceptable en una calibración que
converge despacio. **No está hecho: hace falta medirlo contra PostgreSQL antes**, porque la cola
que se ve aquí es en buena parte de SQLite.

### Recomendación

Para 20–30 estudiantes en clase, subir a una instancia de pago. No por CPU —la tabla dice que
0.1 vCPU llega a ritmo normal— sino por **el spin-down y la falta de margen para ráfagas**. El
código no es lo que hay que optimizar todavía.

---

## Límites conocidos

Lo que **no** está resuelto, a propósito y con el criterio para cerrarlo.

| Límite | Estado | Qué haría falta |
|---|---|---|
| **Una sola instancia** | Declarado y forzado (`WEB_CONCURRENCY=1`) | Matchmaking atómico sobre almacén compartido (el Redis del rate limiting ya está), pub/sub para eventos, y el despertar entre procesos que hoy es un `asyncio.Event` local. Criterio: dos instancias con usuarios en cada una deben emparejarse y recibir sus eventos. |
| **Equivalencia PostgreSQL** | Cubierta en CI, no en local | El job `test-postgres` corre la rama PostgreSQL de las pruebas de ELO. Localmente hace falta Docker. |
| **Router de estudiante de ~1.500 líneas** | Sin tocar | La auditoría dice que el tamaño no es un defecto por sí solo. Extraer diagnóstico y examen a casos de uso cuando haya que cambiarlos, no antes. |
| **Capacidad** | Medida — ver § Capacidad | Objetivo acordado: 20–30 estudiantes concurrentes. El cuello es la instancia, no el código. |
| **`CLAUDE.md` no está versionado** | `.gitignore:27` | Un clon limpio no lo obtiene. `AGENTS.md` es la fuente versionada; no apoyar reglas obligatorias en `CLAUDE.md`. |
| **Skills de autoría de nodos** | Solo locales (`.claude/skills/`, gitignoreado) | Igual: un clon no los tiene. |
| **PDF de las guías** | Obsoletos (mayo 2026) | La fuente de verdad son `guia-estudiante.md` y `guia-docente.md`. |

---

## Cambios que esta ronda introdujo

Por si algo se comporta distinto a como recordabas:

1. `save_answer_transaction` cambió de firma: `(user_id, item_id, topic, compute, ...)`.
   `process_answer` **no** cambió, así que los llamadores siguen igual.
2. `get_latest_elo_by_topic` lee `student_topic_elo` y ya no reconstruye desde `attempts`.
3. El delta de un procedimiento y el de una partida de PvP se aplican una sola vez, al validar y al
   cerrar respectivamente.
4. El proceso web ya no migra.
5. `StudentService.get_socratic_help()` se borró: no lo llamaba nadie (V2 usa `api/routers/ai.py`).
6. `IsotonicCalibrator` se movió a `src/infrastructure/ml/calibration.py` y se inyecta.
7. `src/interface/streamlit/app.py` pasaba `enable_cognitive_modifier` a un constructor que ya no
   lo aceptaba: **V1 no arrancaba**. Corregido.
