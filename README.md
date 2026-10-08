# Oulad

> Plataforma educativa adaptativa de matemáticas. Un motor **ELO** —el del
> ajedrez— mide el nivel de cada estudiante por tema y le sirve siempre el reto
> del tamaño correcto. Encima, una ruta de 60 lecciones narradas que enseñan el
> concepto en vez de solo medirlo.

[![Python](https://img.shields.io/badge/python-3.11+-green)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19-61DAFB)](https://react.dev/)
[![Licencia](https://img.shields.io/badge/licencia-MIT-orange)](LICENSE)

> **Este repo es el playground del rediseño**, no producción. Aquí se
> reestructura el frontend y se construye contenido nuevo antes de portarlo al
> repo de producción (`LuisJRubioH/LevelUp-ELO`, donde la plataforma todavía se
> llama LevelUp-ELO). El port a producción está **bloqueado hasta el visto bueno
> del equipo**.
>
> **This repository is a development copy and is not deployed.** Pushing or
> merging here deploys nothing and migrates no remote database. The owner
> transfers finished work to the final deployment repository by hand — see
> [Deployment](#deployment) and [docs/transfer.md](docs/transfer.md).

---

## Tabla de contenidos

- [Qué es](#qué-es)
- [Lo que hay construido](#lo-que-hay-construido)
- [Arquitectura](#arquitectura)
- [Motor ELO](#motor-elo)
- [La ruta de aprendizaje](#la-ruta-de-aprendizaje)
- [Banco de preguntas](#banco-de-preguntas)
- [Roles](#roles)
- [Instalación local](#instalación-local)
- [Variables de entorno](#variables-de-entorno)
- [Deployment](#deployment)
- [Tests y CI](#tests-y-ci)
- [Usuarios de prueba](#usuarios-de-prueba)
- [Documentación](#documentación)
- [Qué queda pendiente](#qué-queda-pendiente)

---

## Qué es

Cada respuesta actualiza dos ratings a la vez: el del estudiante y el de la
pregunta. Con eso, la plataforma sabe en todo momento qué pregunta cae en la
**Zona de Desarrollo Próximo** de cada persona — ni tan fácil que aburra, ni tan
difícil que frustre — y la sirve.

Audiencia: semillero matemático (grados 6°–11°), colegio, universidad y adultos
preparando concursos públicos (DIAN, SENA) en Colombia. Estudiantes desde el
celular, docentes desde el escritorio.

---

## Lo que hay construido

### Motor adaptativo
- **ELO vectorial por tópico** — un rating independiente por tema, no uno global.
- **Factor K por incertidumbre** — el peso de cada respuesta se escala con la
  RD del estudiante: `K = 32 × (RD / 350)`, así que las primeras respuestas
  mueven mucho y luego el rating se asienta. (`calculate_dynamic_k`, con la
  escala 40/32/16/24, pertenece al modelo escalar y no al vectorial que usa
  la práctica.)
- **Rating Deviation tipo Glicko** — incertidumbre por tópico (RD inicial 350,
  mínimo 30). K efectivo = `K_base × (RD / 350)`.
- **Selector con Fisher Information** — sortea entre preguntas con al menos el
  95 % de la mejor información ponderada `P×(1−P)×peso` dentro del rango ZDP
  [0,40 – 0,75], expandiéndolo ±0,05 por paso si no hay candidatos. Conserva la
  prioridad de preguntas no vistas y las exclusiones de la sesión; los empates
  de dificultad no fuerzan a elegir siempre la primera pregunta.

### Flujo del estudiante
- **Diagnóstico de entrada** — 10 preguntas por materia que fijan el ELO inicial
  **por tópico**. Obligatorio la primera vez, rehacible. «No lo sé» es una opción
  y no penaliza.
- **Mapa de contenido** — camino en zigzag con los temas de la materia; estado
  derivado de `student_topic_elo` (completado ≥ 1250 / actual / disponible). Al
  entrar por un nodo, la práctica queda **filtrada a ese tema**.
- **Ruta de lecciones guiadas** — 60 nodos narrados. Ver
  [§ La ruta de aprendizaje](#la-ruta-de-aprendizaje).
- **Liga PvP en tiempo real** — duelo 1v1 por WebSocket: 10 preguntas, 180 s,
  carrera libre. El ELO se mueve **por el resultado de la partida** (K=24), como
  en ajedrez, no por respuesta individual.
- **Modo examen** — estándar automático o plantilla del docente, con borrador en
  `localStorage` y reintento con backoff para no perder el envío.
- **Procedimientos manuscritos** — foto o PDF; la IA propone nota 0–100, el
  docente pone la oficial. Anti-plagio por SHA-256 del archivo.
- **Bloque Concursos** — UI deliberadamente sobria (sin rachas de colores, sin
  logros, sin KatIA animada) y navegación por bloques temáticos en lista, porque
  DIAN tiene ~209 tópicos y el mapa visual no escala. Los ítems se calibran a
  P\*=0,25. El examen es **evaluativo, no formativo**: `/exam/submit` califica
  y no toca el ELO, ni en Concursos ni en ningún otro bloque.

### IA pedagógica
- **KatIA** — tutora socrática con avatar y GIFs. Chat con streaming SSE, tope de
  120 tokens, y **post-validación que descarta la respuesta si revela la
  solución**.
- **Revisión de procedimientos** — Groq + Llama 4 Scout para revisión rigurosa;
  otros proveedores con visión para la genérica. `ai_proposed_score` **nunca**
  toca el ELO: solo `teacher_score`, vía `(score − 50) × 0,2`.
- **Multi-proveedor** — Anthropic, Groq, OpenAI, Gemini, HuggingFace, Ollama,
  LM Studio. Detección por prefijo de la API key. Todo degrada con gracia si no
  hay proveedor.

### Plataforma
- **Dual DB** — SQLite local y PostgreSQL (Supabase) con API pública idéntica;
  selección automática por `DATABASE_URL`.
- **16 rangos** de Aspirante (0) a Leyenda Suprema (2500+).
- **Consola docente** — ELO temporal, radar por tópico, historial de KatIA,
  análisis con IA, métricas de uso, exportación CSV/XLSX.
- **Seguridad** — Argon2id con migración transparente desde SHA-256; JWT con
  access token corto + refresh en cookie HttpOnly; bucket de procedimientos
  privado, servido por bytes.
- **i18n es/en**, tema claro/oscuro sin FOUC, ARIA, code splitting por ruta.

---

## Arquitectura

Clean Architecture. Dos interfaces sobre un núcleo compartido:

```
src/                              ← núcleo compartido (V1 y V2)
├── domain/                       # lógica pura, sin dependencias externas
│   ├── elo/                      # ELO, VectorRating, Glicko, ZDP
│   ├── selector/                 # AdaptiveItemSelector (Fisher Information)
│   ├── learning/                 # los 60 nodos de la ruta guiada
│   └── katia/                    # mensajes predefinidos de KatIA
├── application/services/         # StudentService, TeacherService
├── infrastructure/               # SQLite + Postgres, Storage, clientes de IA
└── interface/streamlit/          # V1 (Streamlit)

api/                              ← V2: FastAPI, REST + WebSocket
frontend/                         ← V2: React 19 + TypeScript + Vite
```

**Regla de dependencia:** `domain/ ← application/ ← infrastructure/ ← interface/`.
Nunca al revés. Los servicios reciben los repositorios por constructor.

**Regla dual DB:** cualquier cambio en `sqlite_repository.py` se replica en
`postgres_repository.py` y viceversa. `python scripts/db_sync_check.py` lo
verifica y corre en CI.

### V2 — endpoints

| Router | Qué cubre |
|---|---|
| `api/routers/auth.py` | login, registro, refresh, logout, perfil |
| `api/routers/student.py` | práctica, stats, cursos, diagnóstico, mapa, lecciones, examen, procedimientos, PvP |
| `api/routers/teacher.py` | dashboard, grupos, procedimientos, plantillas de examen, métricas, exportación |
| `api/routers/admin.py` | usuarios, aprobación de docentes, grupos, reportes, auditoría |
| `api/routers/ai.py` | chat socrático (SSE), revisión de procedimientos |
| `api/websocket/pvp.py` | `/api/ws/pvp/{course_id}` — matchmaking y partida |
| `api/websocket/notifications.py` | `/api/ws/notifications/{room}` — avisos por sala |

### V2 — rutas del frontend

```
/                              landing
/login
/student                       práctica adaptativa
/student/courses               catálogo y matrícula
/student/course/:id            diagnóstico → bifurcación practicar/mapa
/student/course/:id/map        mapa de contenido
/student/course/:id/lesson/:nodeId   lección guiada
/student/league                liga PvP
/student/exam                  exámenes
/student/procedure             subir procedimiento
/student/feedback              historial + KatIA
/teacher{,/groups,/procedures,/exams,/export}
/admin{,/groups,/reports,/audit}
```

---

## Motor ELO

### Al responder una pregunta

```
StudentService.process_answer()
  ├→ VectorRating.update()           ← delta ELO al tópico
  ├→ Repository.update de items       ← nueva dificultad del ítem (ELO simétrico)
  └→ Repository.save_answer_transaction()
       ├→ INSERT attempts
       ├→ UPSERT student_topic_elo
       └→ UPDATE users.current_elo
```

Todo en una **transacción atómica**: si falla el update del ítem, el intento
tampoco se guarda.

### Fórmulas

```
P(éxito) = 1 / (1 + 10^((dificultad_ítem − rating_estudiante) / 400))
delta    = K_eff × (resultado − P(éxito))
K_eff    = K_base × (RD / 350)
```

| Condición | K base |
|---|---|
| < 30 intentos | 40 |
| ELO < 1400 | 32 |
| Estable (error < 15 % en los últimos 20) | 16 |
| Default | 24 |

### Calibración de dificultad

```
D*(R, P*) = R + 400 × log10((1 − P*) / P*)
```

Para concursos, P\*=0,25 → `D = R + 191`. Para olimpiadas, P\*=0,10 → `D = R + 382`.
Protocolo completo en `.claude/skills/item-calibration/SKILL.md`.

**El ELO del ítem se actualiza simétricamente con cada respuesta** — el banco se
autocalibra con el uso.

---

## La ruta de aprendizaje

60 nodos de lección guiada bajo el curso `algebra_basica`. **No mueven el ELO**:
son para construir el concepto, no para medirlo.

| Mundo | Nodos | Escenario |
|---|---|---|
| PREALG-N1 · Conjuntos numéricos | 13 | La escalera de la necesidad |
| PREALG-N2 · Operaciones | 7 | La ciudad de las seis operaciones |
| PREALG-N3 · Propiedades | 6 | La fábrica de propiedades |
| PREALG-N4 · Divisibilidad | 7 | El Puerto de la Polis |
| ALG-N1 · Fundamentos | 17 | El Papiro de las Cuatro Casas (Kemet) |
| ALG-N2 · Productos notables | 5 | La sala de los troqueles (Bagdad) |
| ALG-N3 · Factorización | 5 | El almacén de la caravana (Bagdad) |

**52 de los 60** usan la arquitectura de 11 bloques y se pintan con un renderer
genérico que no conoce ningún `node_id`. Añadir un nodo = escribir un módulo en
`src/domain/learning/nodes/`, listarlo en `NODE_MODULES` y encadenarlo por
`unlock_after`. No se toca el frontend.

Todo el detalle —los once bloques, los invariantes con test, la taxonomía de
errores y el catálogo completo— en
**[docs/ruta-de-aprendizaje.md](docs/ruta-de-aprendizaje.md)**.

---

## Banco de preguntas

**2.031 ítems** en 49 archivos, en `items/bank/` y `items/bank/semillero/`. El
`course_id` es el nombre del archivo sin extensión.

| Bloque | Cursos |
|---|---|
| **Universidad** | Álgebra Lineal, Cálculo Diferencial / Integral / Varias Variables, Ecuaciones Diferenciales, Probabilidad |
| **Colegio** | Álgebra Básica, Aritmética Básica, Trigonometría, Geometría, Evaluar para Avanzar 8 |
| **Concursos** | DIAN, SENA |
| **Semillero** | Álgebra, Aritmética, Geometría, Lógica, Conteo y Combinatoria, Probabilidad — grados 6°–11° |

### Campos requeridos por ítem

`id` (único global) · `content` (LaTeX con `$...$`) · `difficulty` (600–1800) ·
`topic` · `options` · `correct_option` (idéntico a uno de `options`).

> **LaTeX en JSON: backslashes dobles.** `\\frac`, `\\sin`, `\\alpha`. Un `\f`
> sin escapar rompe el parser.

### Agregar un curso

1. Crear `items/bank/mi_curso.json`.
2. Añadir `'mi_curso': 'Bloque'` a `_COURSE_BLOCK_MAP` en **ambos** repositorios.
3. `python scripts/validate_bank.py`
4. Reiniciar — `sync_items_from_bank_folder()` lo carga solo.

### Extracción de libros

`items/source/` tiene **4.656 enunciados** extraídos de tres libros (Hipertexto,
Caminos, EPA8) con enunciado, respuesta y dificultad ya en escala ELO. **Todavía
no alimentan el banco**: les faltan los distractores, que es justo lo que ningún
libro trae. Ver [CABOS_SUELTOS](Implementacion/CABOS_SUELTOS.md) §D4.

---

## Roles

| Rol | Acceso |
|---|---|
| **Estudiante** | Práctica adaptativa, diagnóstico, mapa, lecciones guiadas, liga PvP, exámenes, procedimientos, KatIA, racha, ranking del grupo |
| **Docente** | Requiere aprobación. Dashboard ELO temporal, radar, historial KatIA, análisis IA, revisión de procedimientos, plantillas de examen, métricas, exportación CSV/XLSX, códigos de invitación inter-nivel |
| **Admin** | Aprueba docentes, reasigna estudiantes (auditado), activa/desactiva usuarios, atiende reportes técnicos |

---

## Instalación local

### V2 — React + FastAPI

```bash
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000
```

```bash
cd frontend && pnpm install --frozen-lockfile && pnpm run dev
```

→ http://localhost:5173 (proxy `/api` → `localhost:8000`)

> `--legacy-peer-deps` es obligatorio: `vite-plugin-pwa` no declara compatibilidad
> con Vite 8.

> Al tocar repositorios o WebSocket, **reinicia el backend limpio** (matando
> todos los procesos de uvicorn, padre y worker). `--reload` no recarga de forma
> fiable y deja procesos huérfanos ocupando el puerto 8000; el síntoma típico es
> código viejo corriendo sin error visible.

### V1 — Streamlit

```bash
pip install -r requirements.txt
streamlit run src/interface/streamlit/app.py
```

Siempre desde la raíz del repo: `app.py` inyecta el root en `sys.path` antes de
importar `src.*`. Sin `DATABASE_URL` usa SQLite y crea la base con datos demo.

---

## Variables de entorno

| Variable | Para qué | Requerida |
|---|---|---|
| `DATABASE_URL` | PostgreSQL Supabase; ausente → SQLite local | En producción |
| `ADMIN_PASSWORD` / `ADMIN_USER` | Credenciales del admin | Sí / No |
| `SUPABASE_URL` / `SUPABASE_KEY` | Storage de procedimientos | Para Storage |
| `JWT_SECRET_KEY` | Firma de los JWT | V2 |
| `CORS_ORIGINS` | Orígenes permitidos | V2 |
| `SYSTEM_AI_API_KEY` | Key de IA del sistema | V2 |
| `SYSTEM_AI_PROVIDER` | Proveedor explícito; autodetectado si falta | No |
| `AI_KEY_KATIA` / `_PROCEDURE` / `_STUDENT_ANALYSIS` / `_TEACHER_ANALYSIS` | Key por función; caen a `SYSTEM_AI_API_KEY` | No |
| `VITE_API_URL` | URL del backend, en el frontend | V2 |

Prioridad por request: key del usuario > key de función > key general
(`settings.get_ai_key("procedure", user_key)`).

> **API keys nunca se persisten en la base ni se loggean.**

> **Supabase:** usar el connection pooler (puerto 6543). El pool interno es
> `ThreadedConnectionPool(1, 5)`; no subir `maxconn` en el free tier. Y nunca
> `conn.close()` — siempre `put_connection(conn)`, o el pool se agota.

---

## Deployment

This repository is not deployed. `render.yaml` and `frontend/vercel.json` are templates for the
final environment and are inert here. Transferring the work to the final deployment repository —
code, dependencies, environment variables, backups, migrations and verification — is a manual step
done by the owner: [docs/transfer.md](docs/transfer.md).

---

## Tests y CI

```bash
ADMIN_PASSWORD=testadmin123 python -m pytest tests/ --ignore=tests/e2e -q
python scripts/validate_bank.py                            # integridad del banco
python scripts/db_sync_check.py                            # paridad SQLite ↔ Postgres
cd frontend && pnpm run build                              # tsc + vite
cd frontend && pnpm exec playwright test                   # E2E (frontend/e2e/)
```

Storage tests run on SQLite always and also on PostgreSQL when `POSTGRES_TEST_DATABASE_URL` points
at a throwaway **local** database (`tests/conftest.py` refuses any other host).

CI in GitHub Actions, 8 jobs: item bank, lint (Black + Flake8), unit tests with coverage ≥ 70 %,
integration, DB parity, PostgreSQL (the integration suite on an ephemeral PostgreSQL service), API
and frontend build. CI only tests; it deploys nothing.

---

## Usuarios de prueba

| Usuario | Contraseña | Rol / Nivel |
|---|---|---|
| `admin` | (variable de entorno) | Admin |
| `profesor1` | `demo1234` | Docente (pre-aprobado) |
| `estudiante1` | `demo1234` | Universidad |
| `estudiante2` | `demo1234` | Colegio |
| `concursante1` | `demo1234` | Concursos — DIAN |
| `estudiante_colegio_1..3` | `test1234` | Colegio (protegidos) |
| `estudiante_universidad_1..2` | `test1234` | Universidad (protegidos) |
| `estudiante_semillero_1..2` | `test1234` | Semillero, grados 9 y 11 (protegidos) |

Los marcados como protegidos llevan `is_test_user=1`: se excluyen de las
exportaciones docentes y **nunca deben eliminarse**.

> Para probar la liga PvP hacen falta **dos cuentas distintas matriculadas en la
> misma materia** — dos pestañas del mismo usuario no emparejan, el backend lo
> bloquea. El seed no las trae: `estudiante1` y `estudiante2` están en materias
> distintas, así que hay que crear un segundo estudiante en el curso del primero.

---

## Documentación

| Documento | Qué cubre |
|---|---|
| [docs/README.md](docs/README.md) | Índice de toda la documentación |
| [docs/ruta-de-aprendizaje.md](docs/ruta-de-aprendizaje.md) | Los 60 nodos, la arquitectura de 11 bloques, cómo añadir uno |
| [docs/guia-estudiante.md](docs/guia-estudiante.md) | Guía de uso para estudiantes |
| [docs/guia-docente.md](docs/guia-docente.md) | Guía de uso para docentes |
| [CLAUDE.md](CLAUDE.md) | Reglas de trabajo en el repo (R1–R14, V2-R1–R18) |
| [PRODUCT.md](PRODUCT.md) · [DESIGN.md](DESIGN.md) | Marca, principios de diseño, anti-referencias |
| [Implementacion/CABOS_SUELTOS.md](Implementacion/CABOS_SUELTOS.md) | Qué queda pendiente, verificado contra el repo |

---

## Qué queda pendiente

Lo grande, con el detalle en
[CABOS_SUELTOS](Implementacion/CABOS_SUELTOS.md):

- **El contenido de la ruta es solo español.** 47 de los 60 nodos llevan el texto
  en dicts de Python. Falta decidir si el inglés sigue en alcance.
- **Faltan los cierres diagnósticos** de N2, N3, N4 y ALG-N1 — sin ellos la ruta
  de repaso no llega al estudiante fuera del primer nivel.
- **El arte de N2 y de Kemet está aplazado a propósito.** Los prompts están
  escritos; los PNG de N2 todavía dibujan la versión descartada y los de Kemet no
  existen. Efecto conocido: el hub de Kemet pide un PNG que no está → 404 en cada
  carga.
- **Los 4.656 ítems extraídos no alimentan el banco** — les faltan distractores.
- **Accesibilidad:** el código está corregido; falta la revisión con lector de
  pantalla real y la medición de contraste.
- **Calibración del piloto:** los 7 ítems de práctica por nodo son una convención,
  no una medida. Se resuelve con datos de uso real.

---

## Licencia

MIT — ver [LICENSE](LICENSE).
