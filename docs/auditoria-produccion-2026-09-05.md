# Preparación para producción — Oulad

Fecha: 2026-09-05. Checkout: `main`, commit `07be80e` (2026-09-02), remoto `Ori-G-A/Oulad_redesing`.

**Decisión: NO APROBADO para migración a producción.** Hay fallos reproducibles de autorización, integridad académica y operación básica. Las 461 pruebas existentes pasan, pero no cubren esos casos. Este informe complementa [la auditoría de arquitectura](auditoria-arquitectura-2026-09-05.md); no sustituye los hallazgos pendientes de esa revisión.

**Reanudación y validación local (2026-09-14):** la decisión anterior corresponde al
diagnóstico inicial; los cierres posteriores no equivalen a certificar el despliegue.
La actualización Python sustituye `python-jose` por `PyJWT`, comparte mínimos de
seguridad en `requirements-security.txt` y mantiene el formato HS256 de access,
refresh y revisión de procedimientos. Las evidencias del 8 de septiembre para API
y V1 no registran vulnerabilidades; no se presentan como una consulta actualizada
de avisos de seguridad ni como cierre de Dependabot remoto.

La ejecución actual con Python 3.11.16 aprueba **666 pruebas de API y unidad**,
incluyendo 10 casos de compatibilidad JWT, con seis avisos de deprecación
([JUnit](validacion-cierre-2026-09-14.xml)). El build TypeScript/Vite y la generación
del service worker pasan. Flake8 crítico pasa sobre `src/`, `api/`, `tests/` y
`scripts/`. Black detecta deuda previa de formato en archivos fuera de esta ronda;
por tanto, no se declara verde el job global de formato. Los dos archivos Python
de esta actualización se formatearon con la versión de Black usada por CI.
Los primeros intentos de pytest y Vite fallaron por permisos del entorno aislado;
las ejecuciones con permisos adecuados pasaron sin cambiar lógica de aplicación.
Siguen pendientes la certificación del entorno real y la publicación de cambios.

**Dependencias frontend (2026-09-08):** pnpm reparado y alineado en 11.19.0.
La actualización anterior había dejado 14 alertas altas; tras actualizar el plugin PWA
a 1.3.0 y aplicar overrides acotados para `brace-expansion`, `browserslist` y `fast-uri`,
`pnpm audit --json` devuelve cero vulnerabilidades en todas las severidades
([evidencia](auditoria-dependencias-2026-09-08.json)). Los overrides se leen desde
`frontend/pnpm-workspace.yaml`. Instalación limpia desde el lockfile y caché aprobada
(526 paquetes); `pnpm run build` aprobado, incluido el service worker. La generación
PWA conserva una observación de rendimiento (~43 s en esta máquina). CI usa Node 24
y la versión de pnpm de `packageManager`; Vercel instala con `--frozen-lockfile`.
Esto no certifica las dependencias Python, las alertas remotas de Dependabot, ni el
despliegue real. Se conserva la decisión de producción hasta cerrar sus demás puertas.

E2E de esta actualización: **28 aprobados, 0 fallidos, 0 omitidos, sin reintentos**
en la ejecución final (64 s), con Playwright 1.63.0 y Chrome instalado 152.0.7977.83,
`PLAYWRIGHT_CHANNEL=chrome` y APIs simuladas
([evidencia](auditoria-dependencias-e2e-2026-09-08.json)). La primera ejecución con
Chrome tuvo una espera de redirección agotada; ese caso pasó aislado y luego pasó
la suite completa, sin modificar sus aserciones ni tiempos. El Chromium versionado
no estaba instalado y su descarga lenta se canceló; no se certifica ese navegador.

**Actualización posterior a la auditoría (2026-09-07):** se introdujo variedad controlada en el selector y se corrigieron diagnóstico, datos canónicos de `/answer`, calificación, permisos docentes, sesión/revocación, idempotencia de respuestas e integridad de examen. También se endurecieron cachés por cuenta, WebSockets, configuración, readiness, rate limiting, uploads, antiplagio, procedencia de notas IA y CI. Las 20 comprobaciones automatizadas de readiness están aprobadas. Esto cierra la puerta operativa en código, pero no aprueba todavía la migración: falta la certificación final sobre instalación limpia, E2E, restauración, carga y configuración efectiva. La matriz siguiente conserva el diagnóstico original para trazabilidad. No hay despliegue de estos cambios.

Validación del último ajuste: 40 pruebas de API de estudiante pasan, incluyendo manipulación de id/dificultad/tópico/RD/opciones, rechazo sin escrituras y petición mínima; TypeScript compila. El backend acepta e ignora `item_data` de clientes antiguos; el frontend nuevo ya no lo envía. Al desplegar este contrato, publicar primero el backend compatible y después el frontend. Sigue pendiente vincular la respuesta a una sesión/pregunta emitida por el servidor y deduplicar reintentos.

Validación de calificación docente: 48 pruebas de API docente, servicio y dominio pasan en SQLite temporal. Se comprueban notas 0/80/100, delta persistido y retornado, conservación de la propuesta IA, rechazo de entrega ajena/inexistente y rechazo de una segunda calificación secuencial. La fórmula del delta se centralizó en dominio y se utiliza en ambos repositorios; `db_sync_check.py` pasa. La comprobación de propiedad y la escritura todavía no son atómicas: queda pendiente proteger peticiones simultáneas y reasignaciones concurrentes. No se ejecutó esta validación sobre PostgreSQL real.

Validación de permisos docentes (2026-09-06): 72 pruebas de rutas docentes, procedimientos y roles pasan en SQLite temporal. Reporte, historial ELO, historial KatIA, ranking y análisis IA exigen que el alumno pertenezca actualmente a un grupo del usuario; también rechazan alumnos sin grupo e IDs inexistentes o de docentes. El rechazo ocurre antes de generar análisis IA. La renovación del código exige grupo propio y la eliminación de asignaciones comprueba pertenencia a la plantilla autorizada. Se verifican accesos legítimos, ausencia de cambios ante rechazos y reevaluación después de quitar al alumno del grupo. Estas rutas de alumno/grupo mantienen el alcance del dashboard incluso para el rol admin; las plantillas conservan su excepción administrativa existente. No se agregaron consultas ni cambios a repositorios. Las comprobaciones y las operaciones siguen siendo pasos separados: esto no certifica seguridad ante reasignaciones concurrentes ni completa la revisión de WebSocket.

Reauditoría de comprobaciones aprobadas (2026-09-06): se endurecieron las seis sondas que habían cambiado de FALLIDO a APROBADO para evitar falsos positivos. La autorización de alumnos comprueba cuatro rutas, sus rechazos y el acceso legítimo; el código de invitación comprueba que el rechazo no lo rote; el diagnóstico verifica recuperación por tópico y curso en un alumno aislado; la respuesta canónica exige HTTP 200, exactamente un intento y los campos persistidos del ítem real; la calificación usa una entrega propia real, rechaza docente ajeno y recalificación, y valida nota, propuesta IA, delta y estado persistidos; la asignación verifica conservación exacta de la ajena y eliminación legítima de la propia. Las seis pasan en SQLite temporal. Su alcance sigue siendo limitado: no prueban carreras concurrentes, PostgreSQL, vínculo de `/answer` con una pregunta emitida, ni la política para repetir un diagnóstico después de iniciar práctica. Por ello son evidencia local aprobada, no cierre global de esos riesgos.

Endurecimiento de atomicidad docente (2026-09-06): la propiedad y el estado pendiente del procedimiento forman ahora parte del mismo `UPDATE`; una reasignación entre la lectura de la cola y la escritura produce 404 sin calificar. La pertenencia de una asignación a su plantilla forma parte del mismo `DELETE`. Las firmas y condiciones se replicaron en SQLite y PostgreSQL. Son 40 pruebas verdes, incluida una reasignación simulada entre autorización y escritura.

Validación PostgreSQL (2026-09-06): las seis guardas reauditoradas se ejecutaron contra PostgreSQL 16 en un contenedor local desechable y las dos pruebas integrales pasan. El primer arranque de una base vacía reveló dos errores de orden: `init_db()` creaba índices antes de `enrollments` y `procedure_submissions`, y la migración alteraba `exam_sessions` antes de crearla. Se corrigió el orden, se agregó `DATABASE_SSLMODE` con valor seguro predeterminado `require` y valor `disable` solo para PostgreSQL local, y se añadió una puerta PostgreSQL a CI. Los índices equivalentes quedaron en ambas bases; `db_sync_check.py` vuelve a pasar. Regresión final: 68 pruebas SQLite y 2 PostgreSQL aprobadas. El contenedor se detuvo y eliminó automáticamente. La política de repetir diagnóstico después de comenzar práctica sigue pendiente dentro de este bloque.

Política de repetición diagnóstica (2026-09-06): repetir el diagnóstico actualiza el informe diagnóstico, pero no sobrescribe ninguna línea ELO que ya tenga intentos de práctica por tópico o por curso. El envío rechaza antes de escribir ítems duplicados, ítems de otro curso y opciones inexistentes. La consulta que detecta práctica está replicada en ambos repositorios. Pasan 43 pruebas de API de estudiante en SQLite y las 2 pruebas integrales PostgreSQL, incluida la comparación del ELO persistido antes y después de repetir el diagnóstico. Con esta evidencia, la puerta de integridad y permisos básicos queda cerrada; el siguiente bloque autorizado es sesión y revocación.

Sesión y revocación (2026-09-06): la cookie HttpOnly/Secure usa `Path=/api/auth`; `/refresh` consume la cookie sin exponerla a JavaScript, mantiene compatibilidad temporal con el body anterior y rota el `jti`. El cliente React comparte una sola renovación entre solicitudes simultáneas, reintenta una vez la operación original y limpia la sesión si no puede renovar. Cada access token se contrasta con la cuenta actual en DB, por lo que un usuario desactivado pierde acceso y refresh inmediatamente; el rol y nombre vigentes proceden de DB. La duración predeterminada vuelve a los 15 minutos documentados. Las tres sondas del bloque pasan, junto con 65 pruebas API SQLite, compilación TypeScript y 3 guardas PostgreSQL. La política aceptada para logout es eliminar la cookie de renovación; un access token ya emitido conserva como máximo sus 15 minutos salvo que la cuenta sea desactivada. Con esta evidencia, la puerta de sesión y revocación queda cerrada; el siguiente bloque autorizado es idempotencia de práctica.

Idempotencia de práctica (2026-09-06): `Idempotency-Key` queda asociado al usuario y a una huella de ítem, opción y línea ELO mediante un índice único en ambos motores. La inserción del intento y las actualizaciones ELO/ítem comparten transacción; solo la inserción ganadora aplica efectos. Un reintento devuelve el resultado persistido y reutilizar la clave con otra respuesta produce 409. El frontend conserva una clave por pregunta durante reintentos y dobles envíos. La sonda `answer_retry_idempotent` pasa; también pasan 61 pruebas de estudiante/servicio y una carrera real de dos solicitudes simultáneas dentro de 4 guardas PostgreSQL. Con esta evidencia, la puerta de idempotencia queda cerrada; el siguiente bloque autorizado es integridad de examen.

Integridad de examen (2026-09-06): `/exam/start` solo acepta plantillas visibles para el grupo dentro de su ventana activa y rechaza plantillas con ítems duplicados o faltantes. El servidor crea una sesión persistida con identificador, composición exacta y vencimiento; `/exam/submit` usa esa sesión como fuente de verdad, exige una respuesta por cada ítem en el orden emitido, valida opciones y rechaza duplicados o sustituciones. El resultado y el historial se guardan en una sola transacción y un reintento devuelve el resultado ya persistido sin duplicarlo. El borrador React conserva el identificador de sesión. Las dos sondas pendientes pasan, junto con 43 pruebas de estudiante, compilación de producción y 5 guardas en PostgreSQL 16, incluida persistencia e idempotencia real. `db_sync_check.py` pasa. Con esta evidencia, la puerta de integridad de examen queda cerrada; el siguiente bloque autorizado es aislamiento de cuenta y operación.

Aislamiento y operación, cerrado en código el 2026-09-07: logout elimina QueryClient, los cachés `api-*` del service worker, el borrador de examen, la sesión de práctica y la API key local. Los WebSockets validan access token contra la cuenta actual; las salas de notificaciones comprueban propietario/grupo y PvP exige rol estudiante e inscripción al curso. `/api/health` ejecuta `SELECT 1`, devuelve 503 sin exponer el error y el proceso deja de arrancar si falla la configuración o la DB. Producción exige DB, JWT de al menos 32 caracteres, CORS sin localhost y almacenamiento Redis/Valkey compartido para límites; los seeds demo/test quedan desactivados con `ENVIRONMENT=production`. Login, registro, KatIA y revisión de procedimientos tienen límites efectivos. Los uploads se leen con tope, validan MIME real, integridad, píxeles o páginas; V2 aplica antiplagio. La propuesta IA se acepta únicamente mediante un token firmado ligado a usuario, ítem, hash y expiración; los campos manipulables del cliente se ignoran. Las claves se envían en body/form. CI usa el lockfile pnpm congelado y fija el gestor. Pasan 167 pruebas API, el build frontend, 6 guardas PostgreSQL y las 20 sondas. La configuración efectiva de servicios se comprobará en la certificación.

## Alcance y excepción acordada

Se revisaron código, contratos API/frontend, sesiones, permisos por recurso, exámenes, procedimientos, persistencia, despliegue, CI y pruebas. Las comprobaciones API se ejecutaron en SQLite nueva y temporal; no se conectó a datos de producción ni se llamó a proveedores de IA. La auditoría inicial no modificó código de aplicación; los ajustes locales posteriores se detallan arriba y no se han desplegado.

**Excepción solicitada por el usuario:** las imágenes aún no generadas con placeholder intencional no son defectos ni bloqueos. `KatiaStorySlot.tsx:31` contempla un placeholder cuando no hay imagen. La excepción no implica certificar todos los estados visuales; la aceptación funcional de un flujo sigue siendo necesaria. Ningún fallo listado abajo se debe a imágenes pendientes.

Los estados significan: **APROBADO** para una comprobación concreta; **FALLIDO** cuando existe evidencia adversa; **PENDIENTE** cuando falta evidencia. Un aprobado parcial no equivale a aprobar el sistema.

## Matriz de salida

| Requisito | Estado | Evidencia / condición de cierre |
|---|---|---|
| Pruebas Python existentes | APROBADO | 461 passed, 4 warnings; Python 3.13.5, SQLite temporal. No certifica Python 3.11 ni PostgreSQL. |
| Banco y catálogo | APROBADO | Revisión previa: 49 archivos, 2.031 ítems únicos; 60 lecciones, 52 con once bloques. |
| Paridad estática DB | APROBADO | Verificador previo pasa; no demuestra equivalencia semántica. |
| TypeScript | APROBADO | `tsc -b`, exit 0. |
| Bundle frontend | APROBADO con observaciones | Vite build exit 0, genera SW; avisos de plugin PWA/Rolldown y chunk principal de 540,69 kB (171,89 kB gzip). |
| Aislamiento entre docentes | FALLIDO | Otro docente lee historial de alumno ajeno y renueva código de grupo ajeno: HTTP 200. |
| Asignaciones de examen | FALLIDO | Una plantilla propia permite borrar la asignación de otra plantilla: HTTP 204. |
| Sesión y renovación | FALLIDO | Cookie `Path=/auth`; refresh exige JSON y devuelve 422 con cookie solamente; frontend sin renovación implementada. |
| Usuario desactivado | FALLIDO | Access token previo sigue obteniendo HTTP 200 en cursos. |
| Datos canónicos del ELO | FALLIDO | Dificultad canónica 600; cliente envía 1777 y se guarda 1777. |
| Diagnóstico → práctica | FALLIDO | Baseline 1234 recuperado como 1000. |
| Reintentos idempotentes | FALLIDO | Misma clave lógica de envío produce dos intentos. |
| Calificación docente | FALLIDO | Endpoint devuelve 500 por contrato incompatible con servicio. |
| Ventanas e integridad de examen | FALLIDO | Examen asignado para 2099 inicia hoy; ítem repetido se cuenta tres veces. |
| Autorización WebSocket | FALLIDO | Revisión de código previa: falta permiso de sala y exigencia de access token. |
| Límites de abuso/IA | FALLIDO en aplicación | Hay configuración de límites, pero no conexión de limitador ni uso en rutas. Controles del perímetro no verificados. |
| Reproducibilidad de CI/deploy | FALLIDO | CI busca `frontend/package-lock.json`, ausente; solo se versiona `pnpm-lock.yaml`, pero instala con npm. |
| Navegación E2E vigente | FALLIDO como puerta de calidad | 11 passed / 17 failed; suite desactualizada respecto a textos/rutas y mocks incompletos. No equivale a declarar todos los flujos rotos. |
| PostgreSQL, migración y concurrencia | PENDIENTE | Docker está instalado pero su motor no está disponible. No se ejecutó PostgreSQL efímero ni migración sobre copia representativa. |
| Dos instancias / recuperación PvP | FALLIDO por diseño actual | Estado y coordinación en memoria local; ver auditoría de arquitectura. |
| Readiness y fallo de persistencia | FALLIDO | Health degradado sigue con HTTP 200; examen puede ocultar fallo al guardar. |
| Backup/restauración/rollback | PENDIENTE | Hay mención histórica de backup, no evidencia actual de restauración ensayada ni runbook de corte/reversión. |
| Configuración real de producción | PENDIENTE | Sin evidencia de secretos efectivos, permisos del bucket, CORS, backups y versión desplegada. |
| Carga, latencia y uso de conexiones | PENDIENTE | No se ejecutó carga representativa ni se fijó volumen objetivo. |
| Imágenes intencionalmente pendientes | EXENTO | Aceptado por el usuario; no bloquean por faltar la imagen generada. |

## Fallos nuevos confirmados mediante ejecución

El script [audit_production_readiness.py](../scripts/audit_production_readiness.py) crea su propia SQLite y produce [evidencia JSON](auditoria-produccion-evidencia.json) sin imprimir tokens o secretos. Ejecutar desde raíz:

```text
python scripts/audit_production_readiness.py
```

Su salida 1 significa que algún criterio de preparación falló. Los doce checks son casos seleccionados para verificar sospechas: no representan doce fallos independientes ni una tasa global de fallos.

### P1 — Autorización incompleta sobre recursos

- `api/routers/teacher.py:247`: recibe `student_id` y consulta historial sin verificar relación con el docente. Un segundo docente sin grupos recibe 200. Las rutas de reporte, historial ELO, análisis y ranking requieren la misma revisión.
- `teacher.py:111`: regenera códigos por `group_id` sin comprobar propiedad. El repositorio solo recibe el identificador del grupo; no puede aplicar autorización por docente.
- `teacher.py:536`: verifica propiedad de `template_id`, pero elimina usando `assignment_id` sin comprobar que pertenezca a esa plantilla. La prueba crea una plantilla propia y otra ajena y confirma la eliminación de la asignación ajena.

Cerrar con políticas por recurso y tests de dos docentes, grupos y alumnos diferentes; cubrir lectura y escritura. La protección general por rol no resuelve estos casos.

### P1 — Renovación y revocación de sesión

`api/routers/auth.py:55` emite cookie HttpOnly con ruta `/auth`, pero los endpoints reales están bajo `/api/auth`. `:92` exige `RefreshRequest` con token en JSON, no lee cookie. `frontend/src/api/auth.ts` no ofrece refresh y el cliente común no renueva ante expiración. La prueba de refresh vía cookie devuelve 422.

`api/dependencies.py` confía en el usuario/rol del JWT sin consultar desactivación; tras desactivar el alumno en la DB temporal, su token obtiene 200. Logout borra cookie, pero no invalida tokens emitidos. El plazo efectivo por defecto es 30 minutos, no los 15 documentados.

Cerrar con renovación mediante cookie correctamente delimitada, validación de estado de cuenta, política explícita de revocación y prueba de expiración durante práctica/examen. Si se habilita autenticación por cookie para más acciones, definir también protección CSRF. El comportamiento de `Path` está documentado por [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie).

### P1 — Calificar procedimientos falla siempre antes de validar la entrega

`api/routers/teacher.py:192` llama `validate_procedure(teacher_id=..., teacher_feedback=...)` y espera una terna. `src/application/services/teacher_service.py:50` acepta `(submission_id, teacher_score, feedback)` y devuelve `None`. El resultado observado es 500 incluso antes de buscar la entrega.

Cerrar alineando el contrato, comprobando que la entrega pertenece al docente y devolviendo resultado consistente. No basta con renombrar argumentos: también falta resolver la autorización y el formato de retorno. Probar entrega real propia, ajena, inexistente y recalificación.

### P1 — El examen confía en estado y composición proporcionados por el cliente

**Resuelto el 2026-09-06.** La descripción siguiente conserva el defecto original como trazabilidad; la corrección y su evidencia están registradas en la actualización de integridad de examen.

`student.py:712` valida existencia/curso de plantilla, pero no su asignación activa al alumno. La prueba inicia una plantilla con ventana futura y obtiene 200. `:771` acepta una lista de respuestas sin sesión emitida por servidor, sin validar composición única, plazo ni correspondencia de preguntas con la sesión. Repetir tres veces un ítem produce `correct_count=3`.

Cerrar con sesión de examen persistida, preguntas emitidas y ventana verificadas en start y submit; deduplicación por sesión; envío final idempotente. La disponibilidad filtrada en el listado no protege el acceso directo al endpoint.

## Riesgos adicionales encontrados por inspección

### P1 — Cachés de datos de alumnos sin separación por cuenta

**Resuelto en código el 2026-09-07.** Falta repetir el escenario A → logout → B en la certificación E2E servida; la descripción conserva el defecto original.

`frontend/vite.config.ts:49` cachea cursos y estadísticas autenticados con `StaleWhileRevalidate` en un caché común. Las claves de React Query en `Stats.tsx:40` y siguientes tampoco incluyen usuario. Logout en `StudentLayout.tsx:66` limpia auth, pero no QueryClient ni CacheStorage. Hay riesgo de mostrar información previa al cambiar de cuenta en un equipo compartido; no se reprodujo una filtración completa en navegador en esta auditoría.

Cerrar con claves por usuario y purga al cambiar sesión; excluir respuestas sensibles del caché compartido o implementar partición explícita. Validar A → logout → B, también offline. [Workbox](https://developer.chrome.com/docs/workbox/caching-strategies-overview/) explica cómo se reutilizan respuestas almacenadas.

### P1 — Credenciales demo y configuración permisiva

**Resuelto en código el 2026-09-07.** La configuración real del proveedor sigue siendo una comprobación de despliegue; la descripción conserva el defecto original.

Ambos constructores ejecutan seeds demo y test sin una bandera de entorno que los reserve al sandbox. El docente demo se crea preaprobado con contraseña conocida. Unido al fallo de autorización anterior, mantenerlo accesible incrementa el riesgo. No se verificó si estas cuentas existen o están habilitadas en producción.

`api/config.py:15` permite un secreto JWT por defecto conocido si falta configuración. `render.yaml` genera un secreto, lo cual ayuda en ese camino de despliegue, pero la aplicación no falla al arrancar con el valor inseguro.

Cerrar deshabilitando seeds demo en producción y rechazando secretos por defecto. Conservar siempre `is_test_user`; no eliminar esa protección ni borrar usuarios como parte de esta auditoría.

### P1/P2 — Uploads, IA y coste

**Resuelto en código el 2026-09-07.** La verificación con proveedores reales y almacenamiento privado permanece para la certificación de infraestructura; la descripción conserva los defectos originales.

- El rate limiting solo está declarado en `api/config.py:58`; no se encontraron `Limiter`, decoradores o middleware que lo apliquen. Validar controles reales antes de exponer login y consumo de IA.
- Los uploads leen todo el archivo antes de comprobar 10 MB y confían en el MIME declarado. Limitar lectura y validar contenido/formato y dimensiones antes de procesarlo.
- `student.py:495` importa `fitz` para PDF, pero `requirements-api.txt` no incluye PyMuPDF; `requirements.txt` sí. El soporte PDF no es reproducible con la instalación declarada del backend.
- V2 calcula y almacena hash, pero no invoca `check_file_hash_duplicate`; V1 sí lo hace. La afirmación de anti-plagio previo a aceptación no es equivalente en ambas interfaces.
- `frontend/src/api/teacher.ts:169` manda `api_key` en body, pero `teacher.py:258` lo declara como query param; la key del usuario no se usa como promete el contrato. `api/routers/ai.py:149` también acepta key por query. Corregir a body/form y evitar que una key termine en URLs/logs.
- La propuesta IA enviada a `/procedure` viene del cliente y no se vincula a un análisis autenticado del servidor; puede alterarse aunque no modifique ELO directamente. El docente debe poder distinguir una propuesta verificable.

Prioridad P1 para controles de abuso/exposición antes de apertura pública; P2 para funcionalidades que se retiren explícitamente del alcance de lanzamiento. No dar por aprobadas funciones anunciadas que no se pueden ejecutar en un entorno limpio.

## Despliegue, pruebas y migración

CI usa caché npm con `cache-dependency-path: frontend/package-lock.json`; ese archivo no existe. El lock versionado es pnpm, pero CI/Vercel instalan con npm. Hay que alinear gestor, lock y comando reproducible. El build auditado usa dependencias locales existentes: no certifica una instalación limpia. Vite local resuelve 8.0.16 y PWA 0.19.8; el plugin registra operaciones no soportadas por Rolldown, aunque genera bundle y SW. Validar actualización del SW, navegación y cachés sobre el build servido.

La suite Python pasó completa al permitir temporales fuera de la restricción inicial; el impedimento de la auditoría anterior queda resuelto para SQLite. Black y Flake8 no están disponibles en el intérprete usado: lint pendiente. No se certifica el estado remoto de CI.

Las pruebas E2E actuales simulan APIs y no representan integración real con FastAPI. Se ejecutaron con una configuración auxiliar, puerto 5187, dos workers, timeout de prueba 12 s y expectativas 3 s. Los snapshots muestran login actualizado, pero los tests buscan placeholders antiguos; el navegador también selecciona inglés mientras los tests esperan español. Son fallos de cobertura/determinismo y hay que actualizarlos antes de usarlos como puerta de salida. No se atribuyen automáticamente al producto.

Resultado inicial: **11 passed / 17 failed**. Hubo llamadas no simuladas a `/api/student/exam/history` rechazadas por el proxy local sin backend (`ECONNREFUSED`).

**Cierre de la suite E2E local (2026-09-07): 28 passed, 0 failed, 0 skipped, sin reintentos, en 34,2 segundos.** Se fijó el idioma español del navegador, se actualizaron las expectativas de portada pública y el flujo catálogo → diagnóstico completado → práctica, y se corrigieron los contratos de mocks de estadísticas, historial, logros, ranking y mapa. El mock general `**/api/**` interceptaba también módulos de Vite bajo `/src/api/`; se retiró del caso de autorización docente. Se asociaron las etiquetas del formulario de acceso a sus inputs mediante `useId`, y `Stats` tolera colecciones auxiliares ausentes. La prueba de respuesta comprueba el resultado completo del tópico y el bloqueo de la opción enviada. TypeScript (`tsc -b`) y `git diff --check` finalizan con código 0.

[Resultado final de Playwright](auditoria-produccion-e2e.json). La configuración reproducible es `frontend/audit.playwright.config.ts`; ejecutar desde frontend con `node node_modules/@playwright/test/cli.js test --config=audit.playwright.config.ts`. Este cierre corresponde a Chromium local con APIs simuladas: no certifica integración FastAPI en staging, service worker del build servido, cambio de cuenta A → logout → B, restauración ni carga. Las imágenes intencionalmente pendientes siguen exentas. Los avisos PWA/Rolldown del build permanecen como observación pendiente; no se consideran resueltos por este resultado.

No se dispone de comparación contra el commit exacto actualmente desplegado en `LuisJRubioH/LevelUp-ELO`. Está pendiente confirmar ese commit y si V1 seguirá activa. Por tanto, no se certifican compatibilidad de datos, ausencia de regresiones V1 ni una ruta de migración concreta.

Para cerrar producción se requiere evidencia de:

1. Commit origen/destino, diferencias de esquema y contratos, y convivencia o retirada de V1.
2. Backup reciente y restauración ensayada de DB **y objetos de Storage**, con tiempos y responsable.
3. Migración aditiva ensayada sobre copia anonimizada/representativa, usando conexión adecuada para los locks; rollback de aplicación compatible con el esquema expandido.
4. PostgreSQL de prueba: mismos casos de rating/permisos y solicitudes concurrentes/reintentos; ninguna prueba destructiva sobre producción.
5. Configuración efectiva: dominios, HTTPS, cookies, secreto JWT, seeds, bucket privado, límites, readiness, logs y alertas.
6. E2E reales en staging para práctica, diagnóstico, examen, procedimiento y docente; móvil y red inestable; imágenes pendientes exentas.
7. Prueba de capacidad con objetivo acordado y verificación de recuperación tras reinicio. Varias instancias solo cuando se resuelva la coordinación PvP/eventos.

## Orden de remediación y autorización de salida

La remediación se ejecutará como una secuencia de puertas de calidad. **No se inicia el bloque siguiente mientras alguna comprobación del bloque actual continúe fallida.** Cada corrección debe cerrar el caso que reprodujo el defecto, mantener verdes las pruebas relacionadas, actualizar `auditoria-produccion-evidencia.json` y registrar aquí sus límites. Un resultado pendiente por falta de infraestructura tampoco se considera aprobado: debe obtener evidencia o quedar formalmente fuera del alcance de lanzamiento.

1. **Integridad y permisos básicos:** permisos por recurso, ELO canónico, diagnóstico y contrato de calificación. Estado actual: las comprobaciones locales seleccionadas de este bloque están aprobadas; quedan por validar concurrencia y PostgreSQL donde corresponda.
2. **Sesión y revocación:** cookie de renovación, renovación desde navegador y rechazo de tokens de usuarios desactivados. No avanzar hasta que las tres comprobaciones pasen.
3. **Idempotencia de práctica:** un reintento de la misma respuesta debe producir un solo intento y un solo cambio de ELO. No avanzar mientras `answer_retry_idempotent` falle; cerrar también con concurrencia en PostgreSQL.
4. **Integridad de examen:** exigir asignación y ventana vigentes, composición emitida por servidor, preguntas únicas y envío final idempotente. No avanzar mientras fallen `future_exam_window_enforced` o `duplicate_exam_items_rejected`.
5. **Aislamiento de cuenta y operación:** cachés por usuario, límites de abuso, readiness, configuración y despliegue reproducible.
6. **Certificación final:** PostgreSQL, migración y restauración ensayadas, E2E en staging y prueba de carga con evidencias.

La modularización completa puede continuar después. No es necesario convertir el proyecto en microservicios para lanzar. Sí es necesario cerrar los fallos P1 y todos los pendientes que afecten al alcance de lanzamiento. Las correcciones ya realizadas constan en las actualizaciones fechadas al inicio; esta regla gobierna las siguientes intervenciones.
