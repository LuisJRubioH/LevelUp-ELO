# LevelUp-ELO — Roadmap V1.0 → V2.0

> Documento de planificación estratégica. Fecha: 2026-04-10.
> Autor: Luis Rubio. Modelo: Claude Sonnet 4.6.

---

## Estado actual — V0.9 Beta (pre-V1.0)

El proyecto tiene arquitectura sólida (Clean Architecture, dual DB, ELO vectorial, multi-IA) pero presenta bloqueantes operacionales que impiden etiquetarlo como V1.0 estable.

### Bloqueantes para V1.0 (resolver antes de taggear)

| # | Problema | Impacto | Esfuerzo |
|---|---|---|---|
| B1 | Encoding UTF-8 BOM en ~20 JSONs del banco (DIAN, SENA, Algebra Lineal, varios Semillero) → items no cargan | Crítico — usuarios ven "sin preguntas" | Bajo (script de fix) |
| B2 | `cognitive.py` genera confidence con `random.uniform()` — feature falsa | Medio — engaña métricas de IA | Bajo (eliminar o documentar) |
| B3 | `symbolic_math_verifier.py` (430 líneas SymPy) nunca se invoca — dead code | Bajo — confusión de arquitectura | Bajo (eliminar) |
| B4 | 13 bloques `except Exception: pass` sin logging — fallos silenciosos | Alto — imposible diagnosticar producción | Medio |
| B5 | `importlib.reload()` de 6 módulos en cada rerun de Streamlit | Alto — race conditions en multiusuario | Medio |
| B6 | Flujo de validación docente de procedimientos sin UI clara | Alto — docentes no saben cómo confirmar | Medio |
| B7 | Sin índices en `attempts(user_id, timestamp)` — queries O(n) | Medio — se degrada con escala | Bajo |

### Criterios de V1.0

- [ ] Los 7 bloqueantes anteriores resueltos
- [ ] Banco de preguntas 100% cargable (encoding limpio)
- [ ] Flujo de procedimientos completo y testeado manualmente
- [ ] `db_sync_check.py` configurado como pre-commit hook
- [ ] Tag git `v1.0.0` + changelog

---

## Por qué salir de Streamlit

Streamlit fue la elección correcta para prototipar rápido. Con él se construyó un MVP funcional con ELO vectorial, multirol, dual DB y multi-IA en tiempo récord. Pero sus limitaciones estructurales son insuperables para una plataforma educativa con crecimiento real:

| Limitación Streamlit | Consecuencia real |
|---|---|
| Rerun completo de Python en cada interacción | UX lenta; timers deben ser JavaScript externo |
| Un solo hilo por sesión (GIL) | No escala a usuarios concurrentes reales |
| Sin routing nativo | URLs no compartibles; no hay `/estudiante/stats` |
| Sin WebSockets nativos | No hay notificaciones en tiempo real (nuevo procedimiento revisado, etc.) |
| Sin separación frontend/backend | Lógica de negocio y UI en el mismo archivo (3,669 líneas en `app.py`) |
| No indexable por buscadores | Impide SEO, crecimiento orgánico |
| Sin Progressive Web App | No instalable en móvil; experiencia degradada en pantallas pequeñas |
| Componentes UI limitados | No hay drag & drop, canvas, editores ricos, notificaciones push |
| No hay control de estado granular | Toda la sesión se recarga con cada widget |

---

## Visión V2.0

**LevelUp-ELO V2.0** es una plataforma educativa adaptativa de primera clase, con una interfaz web moderna, API robusta y experiencia de usuario comparable a productos como Khan Academy o Duolingo — pero con el motor ELO y la tutoría socrática de IA que ya existen.

### Principios de V2.0

1. **El motor ELO, la lógica de dominio y la IA son el valor diferencial** — no se reescriben, se exponen via API
2. **El frontend es una SPA reactiva** — no SSR completo, porque el estado educativo (pregunta activa, ELO, streak) es inherentemente dinámico
3. **La API es el contrato** — permite futuras apps móviles, integraciones, extensiones
4. **No reinventar lo que funciona** — PostgreSQL (Supabase), dominio ELO, integración multi-IA, banco de preguntas

---

## Arquitectura V2.0

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                              │
│                                                             │
│   React + TypeScript (Vite)                                 │
│   ├── Tailwind CSS + shadcn/ui (componentes)                │
│   ├── React Query (cache + sincronización de estado)        │
│   ├── Zustand (estado local: sesión, pregunta activa)       │
│   ├── React Router (rutas por rol: /student, /teacher)      │
│   └── Recharts / Victory (gráficos ELO)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS + WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                      API BACKEND                            │
│                                                             │
│   FastAPI (Python)                                          │
│   ├── /auth — JWT con refresh token                         │
│   ├── /student — práctica, ELO, intentos, streak            │
│   ├── /teacher — dashboard, procedimientos, exportación     │
│   ├── /admin — usuarios, grupos, reportes                   │
│   ├── /ai — socrático, análisis, revisión procedimientos    │
│   └── /ws — WebSocket: notificaciones en tiempo real        │
│                                                             │
│   Capas internas (reutilizadas de V1):                      │
│   ├── domain/        ← sin cambios (ELO, ZDP, KatIA)        │
│   ├── application/   ← sin cambios (StudentService, etc.)   │
│   └── infrastructure/← sin cambios (PostgresRepository)     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    INFRAESTRUCTURA                          │
│                                                             │
│   Supabase (PostgreSQL + Storage + Auth opcional)           │
│   Redis (cache de sesiones, rate limiting de IA)            │
│   Supabase Realtime (o WebSockets nativos en FastAPI)       │
│   CDN (imágenes del banco, GIFs de KatIA)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Stack tecnológico detallado

### Backend — FastAPI

**¿Por qué FastAPI?**
- Python nativo → reutiliza 100% del dominio y servicios existentes
- Async nativo → escala mejor que Flask/Django para IA (que es I/O-bound)
- OpenAPI automático → documentación de API gratis
- WebSockets → notificaciones en tiempo real sin dependencia externa
- Pydantic → validación de datos con tipos (elimina bugs silenciosos)

```
api/
├── main.py                  # App FastAPI + CORS + middleware
├── routers/
│   ├── auth.py              # POST /login, /register, /refresh, /logout
│   ├── student.py           # GET /next-question, POST /answer, GET /stats
│   ├── teacher.py           # GET /dashboard, POST /grade-procedure
│   ├── admin.py             # GET /users, PATCH /approve-teacher
│   └── ai.py                # POST /socratic, POST /review-procedure
├── schemas/                 # Pydantic models (request/response)
│   ├── auth.py
│   ├── student.py
│   └── teacher.py
├── dependencies.py          # get_current_user(), get_repo(), rate_limiter()
├── middleware/
│   ├── auth.py              # JWT verification
│   └── rate_limit.py        # Rate limiting de endpoints de IA
└── websocket/
    └── notifications.py     # Notificaciones push (procedimiento revisado, etc.)
```

**Seguridad V2.0:**
- JWT con `python-jose` — access token (15 min) + refresh token (7 días)
- Rate limiting con Redis: socrático (10 req/min/user), análisis (3 req/min/user)
- RLS en Supabase activado (política por `user_id`)
- CORS estricto (solo el dominio del frontend)
- Sanitización de inputs con Pydantic

### Frontend — React + TypeScript

**¿Por qué React?**
- Ecosistema maduro para dashboards educativos
- React Query elimina el problema de estado/cache que Streamlit intentaba resolver
- TypeScript previene bugs de tipos (problema frecuente en Python-JS interop)
- Componentes reutilizables: pregunta, ELO chart, procedimiento, KatIA

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Student/
│   │   │   ├── Practice.tsx        # Pregunta adaptativa + KatIA
│   │   │   ├── Stats.tsx           # ELO por tópico, historial
│   │   │   ├── Courses.tsx         # Matrícula + tarjetas con banner
│   │   │   └── Feedback.tsx        # Centro de procedimientos
│   │   ├── Teacher/
│   │   │   ├── Dashboard.tsx       # Filtros cascada + ELO estudiantes
│   │   │   ├── Procedures.tsx      # Cola de revisión + calificación
│   │   │   ├── Rankings.tsx        # Rankings por nivel/grupo/curso
│   │   │   └── Export.tsx          # CSV/Excel descarga
│   │   └── Admin/
│   │       ├── Users.tsx
│   │       └── Reports.tsx
│   ├── components/
│   │   ├── Question/
│   │   │   ├── QuestionCard.tsx    # Enunciado + LaTeX + imagen
│   │   │   ├── AnswerOptions.tsx   # Opciones con feedback visual
│   │   │   └── Timer.tsx           # Cronómetro nativo (no JS externo)
│   │   ├── KatIA/
│   │   │   ├── KatIAAvatar.tsx     # Avatar + GIF condicional
│   │   │   └── SocraticChat.tsx    # Chat socrático streaming
│   │   ├── ELO/
│   │   │   ├── ELOChart.tsx        # Línea de evolución ELO
│   │   │   ├── RankBadge.tsx       # Nivel (Aspirante → Leyenda)
│   │   │   └── TopicRadar.tsx      # Radar de tópicos
│   │   ├── Procedure/
│   │   │   ├── UploadZone.tsx      # Drag & drop de imagen/PDF
│   │   │   └── ReviewPanel.tsx     # Panel de calificación docente
│   │   └── ui/                     # shadcn/ui componentes base
│   ├── hooks/
│   │   ├── useStudentSession.ts    # Estado de sesión de práctica
│   │   ├── useELO.ts               # ELO vectorial en cliente
│   │   ├── useNotifications.ts     # WebSocket listener
│   │   └── useKatIAStream.ts       # Streaming de respuesta socrática
│   ├── api/                        # Clientes HTTP tipados (React Query)
│   │   ├── student.ts
│   │   ├── teacher.ts
│   │   └── auth.ts
│   └── stores/
│       ├── authStore.ts            # Zustand: user, token
│       └── practiceStore.ts        # Zustand: item actual, historial sesión
```

### Mejoras UX específicas sobre Streamlit

| Feature | V1 (Streamlit) | V2 (React) |
|---|---|---|
| Timers | JavaScript embebido vía `st.components.v1.html` | Componente React nativo con `useInterval` |
| Animaciones KatIA | Imagen base64 en `st.markdown` | Componente animado con `framer-motion` |
| Chat socrático | `st.write_stream()` con rerun | Streaming real via `EventSource` (SSE) |
| Notificaciones | Badge estático recargado | WebSocket: badge se actualiza en tiempo real |
| Upload procedimiento | `st.file_uploader` | Drag & drop con preview inmediato |
| Dashboard docente | Tabs de Streamlit | Layout responsivo con sidebar colapsable |
| LaTeX | `st.markdown` con KaTeX | `react-katex` integrado en componentes |
| Rutas | Sin routing (todo en una URL) | `/student/practice`, `/teacher/procedures` |
| Modo offline | No | Service Worker + cache de banco de preguntas |
| PWA | No | Instalable en móvil (manifest + SW) |

---

## Nuevas funcionalidades V2.0

### F1 — Sistema de notificaciones en tiempo real
**Problema V1**: el docente no sabe cuándo un estudiante sube un procedimiento hasta que recarga. El estudiante no sabe cuándo el docente lo califica.

**Solución**: WebSocket con sala por grupo. Eventos:
- `procedure_submitted` → docente ve badge actualizado en tiempo real
- `procedure_graded` → estudiante recibe notificación push (y PWA notification)
- `new_group_member` → docente ve estudiante unido al grupo
- `streak_milestone` → celebración visual sin rerun

### F2 — Editor de banco de preguntas (admin/docente)
**Problema V1**: agregar preguntas requiere editar JSON manualmente con doble backslash de LaTeX.

**Solución**: panel de administración con:
- Editor WYSIWYG con preview LaTeX en tiempo real (KaTeX)
- Upload de imagen para el ítem
- Validación automática: `correct_option` debe existir en `options`, dificultad en rango
- Preview de cómo verá el estudiante la pregunta

### F3 — Modo examen cronometrado
**Problema V1**: el temporizador existe pero no hay modo "examen" con tiempo límite y sin ayudas.

**Solución**:
- Modo práctica libre (actual)
- Modo examen: N preguntas, T minutos, sin KatIA, sin pedir siguiente — automático
- Al terminar: reporte PDF descargable con análisis por ítem

### F4 — Analytics avanzado para docentes
**Problema V1**: dashboard muestra ELO y tasa de acierto, pero sin tendencias temporales.

**Solución**:
- Gráfico de evolución de ELO por semana (no solo valor actual)
- Mapa de calor de errores por tópico × período
- Detección de "estudiantes en riesgo" (ELO bajando + baja frecuencia de práctica)
- Comparación anonimizada entre grupos del mismo docente

### F5 — Gamificación extendida
**Problema V1**: hay rachas y niveles pero sin recompensas visuales persistentes.

**Solución**:
- Sistema de logros (badges): "Primera racha de 10", "100 preguntas respondidas", "ELO 1500"
- Tabla de logros visible en perfil del estudiante
- Animaciones de desblogueo (Lottie animations)
- XP semanal con ranking dentro del grupo

### F6 — Revisión de procedimientos mejorada
**Problema V1**: el docente ve el procedimiento en el dashboard, pone un número y listo.

**Solución**:
- Anotaciones directas sobre la imagen (canvas overlay): el docente puede marcar errores con flechas/círculos
- Comentarios por paso (basados en el JSON de pasos del LLM)
- Historial de versiones: estudiante puede subir corrección del procedimiento
- Comparación lado a lado: versión original vs. corrección del estudiante

### F7 — API pública con rate limiting (para integraciones)
**Problema V1**: no hay forma de integrar LevelUp-ELO con Moodle, Google Classroom u otros LMS.

**Solución**:
- Endpoints de estudiante protegidos con API key por docente
- Webhook: cuando estudiante termina sesión, notifica al LMS externo con resultados
- Importar banco de preguntas desde Moodle XML o QTI

### F8 — Soporte móvil real (PWA)
**Problema V1**: Streamlit en móvil es funcional pero no óptima.

**Solución**:
- Progressive Web App instalable en Android/iOS desde el navegador
- Cache de las últimas 20 preguntas del curso activo (funciona offline)
- Sincronización en segundo plano al recuperar conexión
- Notificaciones push nativas (nuevo procedimiento calificado, racha en riesgo)

---

## Plan de implementación V2.0

### Fase 0 — Prerequisitos (antes de empezar V2)
Completar V1.0 limpiando los bloqueantes (B1–B7 arriba). No tiene sentido migrar a FastAPI si el banco de preguntas tiene encoding roto.

**Duración estimada**: 1–2 semanas.

---

### Fase 1 — API FastAPI (Backend)
**Objetivo**: exponer toda la lógica existente como API REST+WS. El dominio no cambia.

**Entregas**:
1. Setup FastAPI + Pydantic schemas + JWT auth
2. Router `/auth`: login, register, refresh, logout
3. Router `/student`: next-question, answer, stats, enrollments
4. Router `/teacher`: dashboard, grade-procedure, export
5. Router `/ai`: socratic (SSE streaming), review-procedure
6. WebSocket: notificaciones en tiempo real
7. Rate limiting con Redis (o in-memory para V2.0 inicial)
8. OpenAPI docs auto-generados en `/docs`

**Criterio de completitud**: la app Streamlit de V1 puede coexistir apuntando al mismo PostgreSQL. La API es una capa nueva, no reemplaza — permite migración gradual.

---

### Fase 2 — Frontend React (autenticación + práctica)
**Objetivo**: reemplazar los flujos más usados primero.

**Entregas** (en orden de prioridad de uso):
1. Setup React + TypeScript + Vite + Tailwind + shadcn/ui
2. Páginas: Login, Register (wizard)
3. Layout base: sidebar por rol, header con KatIA avatar
4. Página Student/Practice: pregunta adaptativa + opciones + timer nativo + KatIA
5. Chat socrático con SSE streaming (ver tokens aparecer en tiempo real)
6. Página Student/Stats: ELO chart + radar de tópicos + historial

**Criterio de completitud**: un estudiante puede hacer una sesión completa de práctica desde React sin tocar Streamlit.

---

### Fase 3 — Frontend React (docente + admin)
**Objetivo**: completar todos los roles.

**Entregas**:
1. Teacher/Dashboard: filtros cascada + tabla de ELO por estudiante
2. Teacher/Procedures: cola de revisión + calificación + anotaciones (canvas)
3. Teacher/Rankings: tres modos (nivel/curso/grupo)
4. Teacher/Export: CSV/XLSX descarga
5. Admin/Users: aprobación, activación, reasignación
6. Admin/Reports: reportes técnicos de estudiantes

---

### Fase 4 — Nuevas features V2.0
**Objetivo**: las funcionalidades que Streamlit no podía dar.

**Entregas**:
1. F1 — Notificaciones WebSocket en tiempo real
2. F2 — Editor de banco de preguntas con preview LaTeX
3. F3 — Modo examen cronometrado
4. F5 — Sistema de logros/badges
5. F6 — Anotaciones sobre procedimientos (canvas)
6. F8 — PWA (manifest + service worker)

*(F4 analytics avanzado y F7 API pública son candidatos para V2.1)*

---

### Fase 5 — QA, tests y despliegue
**Objetivo**: calidad de producción.

**Entregas**:
1. Tests de integración del backend (pytest + httpx): cobertura >= 80% de routers
2. Tests de componentes React (Vitest + Testing Library)
3. Tests E2E (Playwright): flujo completo estudiante + docente
4. CI/CD: GitHub Actions con lint + tests + deploy automático
5. Monitoreo: Sentry (errores), métricas de ELO en Grafana/Supabase Dashboard
6. Tag `v2.0.0` + changelog completo

---

## Decisiones de arquitectura pendientes

### ¿Supabase Auth o JWT propio?
- **Supabase Auth**: más rápido, integrado con RLS, pero acoplamiento con Supabase
- **JWT propio** (recomendado para V2.0): control total, sin vendor lock-in, compatible con cualquier DB
- Decisión: JWT propio con python-jose + refresh token en HttpOnly cookie

### ¿Redis obligatorio desde V2.0?
- Para rate limiting de IA: **sí, necesario** (evitar abuso de API keys del usuario)
- Para caché de sesiones: opcional (JWT es stateless)
- Alternativa sin Redis: rate limiting in-memory con `slowapi` (no distribuido)
- Decisión: `slowapi` para V2.0 inicial; Redis para V2.1 cuando haya >100 usuarios concurrentes

### ¿Migración gradual o big bang?
- **Gradual** (recomendado): Streamlit V1 en `/legacy`, React V2 en `/` — mismo PostgreSQL
- No big bang: demasiado riesgo de romper producción
- La API FastAPI puede servir ambos frontends simultáneamente
- Se retira Streamlit cuando el 100% de flujos estén en React y validados

### ¿Qué pasa con el banco de preguntas JSON?
- En V2.0 sigue siendo JSON → DB (idéntico)
- El editor de banco (F2) guarda directamente en DB, sin JSON intermediario
- Los JSONs se mantienen como fuente de verdad + backup
- Decisión: migración de JSONs a DB completa en Fase 2 (con herramienta de admin)

---

## Stack completo V2.0

### Backend
| Paquete | Uso |
|---|---|
| `fastapi` | Framework API async |
| `uvicorn` | ASGI server |
| `python-jose[cryptography]` | JWT generation y verificación |
| `pydantic>=2` | Validación de schemas |
| `slowapi` | Rate limiting (por usuario/IP) |
| `psycopg2-binary` | PostgreSQL driver (igual que V1) |
| `passlib[argon2]` | Hashing de contraseñas (igual que V1) |
| `httpx` | Cliente HTTP async (tests de integración) |
| `pytest` + `pytest-asyncio` | Tests |
| `openai`, `anthropic`, `groq` | Proveedores de IA (igual que V1) |

### Frontend
| Paquete | Uso |
|---|---|
| `react` + `react-dom` | UI library |
| `typescript` | Tipado estático |
| `vite` | Build tool (reemplaza CRA) |
| `tailwindcss` | Utility CSS |
| `shadcn/ui` | Componentes base (accesibles, sin opinión) |
| `react-router-dom` | Routing por rol |
| `@tanstack/react-query` | Cache + sync estado servidor |
| `zustand` | Estado local (sesión, pregunta activa) |
| `recharts` | Gráficos ELO |
| `react-katex` | Render LaTeX en componentes |
| `framer-motion` | Animaciones (KatIA, logros) |
| `react-dropzone` | Upload de procedimientos |
| `fabric.js` o `konva` | Canvas para anotaciones sobre procedimientos |

### Infraestructura
| Servicio | Uso |
|---|---|
| Supabase (PostgreSQL) | DB principal (igual que V1) |
| Supabase Storage | Procedimientos (igual que V1) |
| Vercel o Railway | Deploy del frontend React + API FastAPI |
| GitHub Actions | CI/CD: lint + tests + deploy |
| Sentry | Monitoreo de errores en producción |

---

## Lo que NO cambia en V2.0

Esto es el núcleo del valor diferencial y no se toca:

- `src/domain/` — ELO vectorial, factor K dinámico, Glicko-simplificado, KatIA messages, AdaptiveItemSelector
- `src/application/services/` — StudentService, TeacherService
- `src/infrastructure/persistence/postgres_repository.py` — todas las queries, migraciones, seeds
- `src/infrastructure/external_api/ai_client.py` — multi-proveedor IA
- `src/infrastructure/external_api/math_procedure_review.py` — revisión Groq
- `items/bank/` — banco de preguntas
- `items/images/` + `Banners/` + `KatIA/` — assets

FastAPI envuelve exactamente lo mismo que llama `app.py` hoy. La migración es de presentación, no de lógica.

---

## Criterios de éxito V2.0

| Métrica | V1 actual | Objetivo V2.0 |
|---|---|---|
| Tiempo de respuesta UI | ~800ms (rerun Streamlit) | < 150ms (React + API cache) |
| Usuarios concurrentes soportados | ~10 (Streamlit single-thread) | > 200 (FastAPI async + pool) |
| Cobertura de tests | 0% | >= 80% backend, >= 60% frontend |
| Tiempo de carga inicial | ~3s (Streamlit cold start) | < 1s (SPA + CDN assets) |
| Soporte móvil | Funcional pero no óptimo | PWA instalable, UX nativa |
| Notificaciones | Manual (recarga) | Tiempo real (WebSocket) |
| Routing | Sin URLs propias | URL compartibles por rol y vista |
| Modo offline | No | Cache de últimas 20 preguntas |
