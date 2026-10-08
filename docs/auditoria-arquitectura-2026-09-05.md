# Auditoría de arquitectura y documentación — Oulad

Fecha: 2026-09-05. Alcance: checkout local; revisión de código, documentación operativa, contratos, persistencia, configuración de despliegue y CI. No se inspeccionaron servicios desplegados ni bases de datos remotas. No se modificó código de aplicación.

**Dictamen:** hay una base útil de monolito modular, pero la separación de capas es parcial, la documentación mezcla estados históricos y actuales, y existen problemas de integridad y concurrencia que deben resolverse antes de escalar el backend a varios procesos o instancias. No hay mediciones de carga en esta auditoría que permitan asignar una capacidad de usuarios concurrentes.

## Hallazgos prioritarios

P1 = corregir antes de ampliar uso o despliegue; P2 = deuda que compromete mantenimiento, operación o crecimiento. Las consecuencias de concurrencia se deducen del flujo de código; no se ejecutó una prueba de carga distribuida.

### 1. P1 — El cliente controla datos que determinan el ELO

Evidencia: `api/routers/student.py:135`, `:145`; `api/schemas/student.py:46`; `src/application/services/student_service.py:130`.

`/answer` busca el ítem canónico, pero solo toma de él `correct_option`. El resto procede de `body.item_data`, incluido el identificador que se persiste, dificultad, tópico y RD; además admite `body.elo_topic`. Es posible calcular el rating con una dificultad alterada o comparar la solución de un ítem mientras se persiste otro identificador. Esto compromete la integridad del motor incluso sin mucha carga.

Corrección: construir el ítem íntegramente desde la base de datos, derivar el tópico en el servidor y validar pertenencia a curso/sesión. El cliente debería enviar identificación de intento, respuesta y telemetría acotada. Verificación: modificar dificultad, tópico e identificador en la petición no debe alterar los datos canónicos usados.

### 2. P1 — Varias fuentes de ELO producen estados incompatibles

Evidencia: `api/dependencies.py:154` en adelante; PostgreSQL `get_latest_elo_by_topic` (`:2453`), `_update_current_elo` (`:2502`) y `set_topic_elo_baseline` (`:5111`); equivalentes SQLite (`:2074`, `:2126`).

El diagnóstico escribe en `student_topic_elo`, pero la reconstrucción del vector consulta `attempts` y procedimientos. Un alumno recién diagnosticado sin intentos no recupera ese baseline al practicar. Además:

- La lectura del último intento no filtra `elo_valid=1`, aunque la escritura dice excluir tiempos inválidos de la actualización del rating.
- Se suma el total histórico de deltas de procedimientos a un `elo_after` que puede haber incorporado ya esos ajustes en una respuesta posterior, permitiendo su aplicación repetida.
- La reconstrucción del agregado desde intentos y la lectura con procedimientos no siguen la misma regla.
- El orden por timestamp no tiene desempate por identificador en esas consultas.

Corrección: establecer un único estado canónico de rating por estudiante/tópico, actualizarlo transaccionalmente y registrar eventos para auditoría. Diagnóstico, práctica y revisión docente deben aplicar sus cambios una sola vez. Verificar baseline → primera práctica, intento inválido → siguiente práctica y procedimiento → dos prácticas sucesivas en ambos motores.

### 3. P1 — La transacción de respuesta no protege el ciclo de lectura y cálculo

Evidencia: `api/routers/student.py:135`; `src/application/services/student_service.py:130`; PostgreSQL `:1583` y SQLite `:1232`.

El vector y la dificultad se leen/calculan antes de `save_answer_transaction`. La transacción inserta el resultado ya calculado y asigna una dificultad absoluta. Dos respuestas concurrentes pueden partir del mismo rating y sobrescribir parte del efecto esperado; distintos estudiantes también compiten por el rating compartido del ítem. La atomicidad de las escrituras no resuelve estas lecturas obsoletas.

Corrección: unidad de trabajo que coordine lectura, cálculo de dominio y persistencia, con bloqueo de filas o control optimista por versión. Mantener las fórmulas en dominio y la coordinación transaccional fuera del router. Probar solicitudes concurrentes sobre el mismo estudiante y el mismo ítem; verificar equivalencia con un orden serial válido.

### 4. P1 — Reintentos de escrituras sin idempotencia

Evidencia: `frontend/src/api/client.ts:47`, `:103`; `api/schemas/student.py:46`; inserción incondicional de intentos en ambos `save_answer_transaction`.

El cliente reintenta también POST ante errores de red y 502/503/504. Si el servidor confirmó la operación y se perdió la respuesta, el reintento registra otro intento y puede volver a mover ratings. El modo examen tampoco presenta aquí una identidad de envío que permita deduplicar la sesión.

Corrección: clave de idempotencia por envío lógico con restricción única y respuesta persistida; reutilizar la clave en reintentos. No deduplicar únicamente por estudiante/ítem, porque volver a practicar un ítem es legítimo.

### 5. P1 — Autenticación WebSocket sin autorización de sala

Evidencia: `api/websocket/notifications.py:66` y `:80`; `api/websocket/pvp.py:163`.

Notificaciones valida la firma del JWT y después añade el socket a la sala solicitada sin comprobar que pertenezca al usuario, rol o grupo. Tampoco exige `type=access`. Un usuario autenticado puede suscribirse a otra sala. PvP también decodifica el token sin exigir explícitamente tipo de acceso; la política debe ser común.

Corrección: verificar tipo, usuario habilitado y permiso sobre el recurso antes de suscribir; reutilizar una política compartida para REST y WebSocket. Probar tokens refresh y salas de terceros. Este hallazgo no afirma acceso a todo el contenido de la base: afecta a los eventos enviados a esas salas.

### 6. P1 — PvP y notificaciones dependen de un solo proceso

Evidencia: `api/websocket/pvp.py:62` (`_lobby`, `_matches`) y `api/websocket/notifications.py:37` (`_rooms`).

Dos instancias mantienen colas y partidas independientes. Los jugadores conectados a procesos distintos no se emparejan mediante esos diccionarios; las notificaciones solo alcanzan sockets locales. Un reinicio pierde el estado activo aunque haya registros persistidos de la partida.

Corrección: mientras se resuelve, documentar explícitamente la restricción de un proceso. Para varias instancias, disponer de coordinación compartida de matchmaking, distribución de eventos y recuperación/expiración de partidas. Mantener sockets locales es correcto; la coordinación y el estado recuperable deben trascender al proceso.

### 7. P1 — Migraciones con locks de sesión sobre pooler de transacciones

Evidencia: `render.yaml:20` recomienda puerto 6543; PostgreSQL `:558` adquiere `pg_try_advisory_lock`, hace commit y libera después (`:1096`–`:1108`). El constructor ejecuta migraciones, seeds y backfills (`:206` en adelante).

El puerto 6543 del pooler compartido corresponde al modo transacción: no garantiza mantener la sesión física entre transacciones. El lock de sesión adquirido antes del commit puede no corresponder a la sesión usada para liberarlo después. Este es un riesgo de la configuración documentada; no se comprobó el modo de conexión real del servicio.

Corrección: separar migraciones del arranque HTTP y ejecutarlas una sola vez mediante conexión directa o pooler de sesión. Mantener migraciones aditivas y no sustituir los locks por variantes prohibidas por AGENTS.md. Fuente: [modos de conexión de Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres) y [semántica de locks de sesión](https://supabase.com/docs/guides/database/connection-management).

### 8. P2 — Trabajo síncrono dentro del bucle asíncrono

Evidencia: `api/websocket/pvp.py:174`, `:196`, `:212`, `:308`; `postgres_repository.py:231`; `api/websocket/notifications.py:129`; llamada desde `api/routers/teacher.py:208`.

PvP invoca directamente consultas síncronas desde `async def`, algunas dentro del lock global del lobby. Una espera de base de datos —incluido el backoff con `time.sleep` al agotar el pool— bloquea el bucle y retrasa otros sockets. Por separado, `notify_sync` busca un event loop en el hilo del endpoint síncrono y descarta `RuntimeError`, por lo que puede perder silenciosamente avisos.

Corrección: trasladar operaciones bloqueantes a un ejecutor acotado o usar acceso asíncrono; no mantener el lock global durante I/O. Programar notificaciones mediante un puente explícito al loop o un publicador de eventos. FastAPI no mueve automáticamente al threadpool las utilidades síncronas invocadas desde una función asíncrona: [documentación oficial](https://fastapi.tiangolo.com/async/).

### 9. P2 — Clean Architecture y contratos solo parcialmente implementados

Evidencia: `student_service.py:5`, `teacher_service.py:1`; `src/domain/elo/calibration.py:11`; `src/application/interfaces/repositories.py:23`.

Los servicios importan el cliente de IA de infraestructura. El dominio contiene carga de archivos pickle, entrenamiento y dependencias numpy/sklearn. El protocolo de estudiante declara métodos como `get_item` y `get_available_items` que no están implementados con esos nombres, y omite métodos consumidos como `get_items_from_db` y `get_answered_item_ids`. `RepoDep` está tipado como `object`.

El router de estudiante tiene 1.408 líneas; SQLite 4.829 y PostgreSQL 5.571. Estos tamaños no son por sí solos defectos, pero acompañan mezcla de diagnóstico, exámenes, lecciones y persistencia generalista, elevando el coste de cambios coordinados.

Corrección: puertos de IA/calibración y repositorios ajustados a consumidores reales; composición en la entrada; casos de uso de diagnóstico/examen fuera del router; comprobación estática de contratos en CI. Conservar un monolito modular es razonable: la auditoría no justifica separar servicios independientes ahora.

### 10. P2 — Salud y fallos de persistencia poco observables

Evidencia: `api/main.py:48`, `:123`; `api/routers/student.py:815`.

El startup captura el error de inicialización y permite arrancar. Health obtiene/devuelve conexión, sin consulta de verificación, y devuelve HTTP 200 incluso en estado degradado. El deploy utiliza esa ruta como health check. Guardar un examen también puede fallar y aun así devolverse una calificación exitosa porque la excepción se descarta.

Corrección: separar liveness de readiness, comprobar una consulta mínima y disponibilidad del esquema, responder 503 si no está listo; registrar fallos con contexto sin secretos y no confirmar persistencia fallida. Medir espera de pool, latencia p95/p99, errores, duración de IA y partidas abandonadas antes de ajustar capacidad.

## Coherencia de documentación

| Afirmación o documento | Estado comprobado |
|---|---|
| README: playground Oulad, despliegue sandbox | Coherente con `render.yaml`; AGENTS.md sigue describiendo el repo de producción y su estado de mayo. |
| README: 49 archivos y 2.031 ítems | Confirmado por `validate_bank.py`. |
| README/ruta: 60 lecciones, 52 con once bloques | Confirmado importando el catálogo y contando sus entradas. |
| README: K dinámico 40/32/16/24 | No describe el flujo vectorial de práctica: `VectorRating.update` crea `RatingModel`, cuyo `K_BASE=32` se escala por RD (`uncertainty.py:19`). `calculate_dynamic_k` existe en otro modelo. |
| README: examen de Concursos sí mueve ELO (`:86`) | Contradice `/exam/submit`, que evalúa sin modificar ELO y no tiene excepción de Concursos. |
| README/AGENTS: `SimpleConnectionPool` | El código usa `ThreadedConnectionPool(1,5)` (`postgres_repository.py:190`). |
| README/AGENTS: flujo con `update_item_rating` separado | `process_answer` calcula dificultad y la entrega a `save_answer_transaction`. Actualizar el diagrama. |
| AGENTS: repositorio SQLite de ~1.200 líneas | Tiene 4.829; PostgreSQL tiene 5.571. |
| AGENTS: sin pendientes y listo para etiquetar; contexto Sprints 1–6 y próximo Sprint 7 | Inconsistencia interna y con el contexto actual de sandbox. |
| `docs/v2-tecnico.md` / `v2-plan.md` | `docs/README.md` ya los declara históricos. Falta una referencia técnica actual que los sustituya; React Router 6/Zustand 4/TypeScript 5 de la tabla histórica difieren de package.json (7/5/6). No es una comprobación de últimas versiones disponibles. |
| AGENTS: técnico gitignoreado | `docs/v2-tecnico.md` y `docs/v2-plan.md` están versionados. |
| Índice: CLAUDE.md como reglas compartidas | Está presente localmente pero no versionado; un clon limpio no obtiene esa fuente. |
| Skills `.Codex/skills/...` citadas por AGENTS | No se encontró la guía de arquitectura solicitada en esa ruta ni en la búsqueda de skills locales. Evitar reglas operativas apoyadas en archivos ausentes. |
| CI como prueba de paridad | Hay siete jobs. Integración/API usan SQLite; el verificador de paridad analiza texto/firmas/DDL, no equivalencia de resultados ni concurrencia PostgreSQL. Solo existe `ci.yml`; no ejecuta Playwright. |

Los PDF y notas históricas no necesitan reescribirse como si fueran actuales: el índice ya reconoce los PDF obsoletos. Conviene añadir el aviso histórico dentro de los propios documentos técnicos, para quien llegue por enlace directo.

## Verificaciones ejecutadas y límites

- `python scripts/db_sync_check.py`: correcto; paridad estática.
- `python scripts/validate_bank.py`: correcto; 49 archivos, 2.031 identificadores únicos.
- Conteo del catálogo: 60 lecciones, 52 `eleven_block_node`.
- `python -m pytest tests/unit/domain/ tests/unit/application/ tests/unit/infrastructure/test_pvp_logic.py -q -p no:cacheprovider`: **309 passed**.
- Intento de suite completa de 461 tests: no certificable por errores de permisos de temporales y fallo final `PermissionError [WinError 5]` en `.tmp/architecture-audit-tests`. No se consideran fallos funcionales confirmados del producto.
- Runtime disponible: Python 3.13.5; CI declara 3.11. No se ejecutó build frontend ni E2E; `npm` no está disponible como comando en esta sesión.
- No se certifica estado verde actual de CI remoto, configuración efectiva de Render/Supabase, comportamiento PostgreSQL bajo carga ni vigencia de dependencias frente a sus últimas releases.

## Orden de corrección propuesto

Este orden queda sujeto a la puerta de calidad definida en la auditoría de producción: no se comienza un punto mientras las comprobaciones fallidas del punto anterior no estén resueltas y respaldadas por evidencia actualizada. Los pendientes que requieran PostgreSQL, staging o infraestructura real deben validarse allí antes de declarar cerrado el punto.

1. Integridad: datos canónicos en `/answer`, fuente única de ELO, idempotencia y autorización WebSocket. Cerrar con pruebas de regresión que reproduzcan cada caso.
2. Concurrencia y operación: unidad de trabajo, migraciones separadas, readiness veraz y eliminación de I/O bloqueante en WebSocket. Probar contra PostgreSQL efímero, además de SQLite.
3. Escalado horizontal: coordinación compartida de partidas/eventos y recuperación tras reinicios. Validar dos instancias con usuarios conectados a cada una antes de habilitar más workers.
4. Mantenimiento: extraer casos de uso y puertos, corregir contratos, unificar AGENTS/README y crear un documento técnico vigente con decisiones, límites y procedimiento de despliegue.
5. Capacidad: definir objetivos de latencia y volumen con el equipo, medir consultas/historiales y consumo de conexiones; después optimizar selección de ítems, paginación y cachés según resultados. El selector actual carga el pool del curso y los ítems respondidos del alumno por petición; su coste crecerá con el catálogo y el historial.

Criterio de aceptación global: misma secuencia lógica de eventos produce el mismo rating en ambos motores; reintentos no duplican efectos; concurrencia no pierde actualizaciones; diagnóstico se conserva; usuarios solo reciben eventos autorizados; dos instancias pueden coordinar partidas; documentación y configuración explican el sistema realmente desplegable.
