# Documento Técnico — LevelUp-ELO V2

**Estado:** Sprints 1-8 + Sprint C completos ✅ — V2 etiquetada como `v2.0.0` (commit `c791054`, 2026-05-18).
**Última actualización:** 2026-05-18
**Autor:** Luis Rubio

> Documento técnico de referencia del backend FastAPI + frontend React + flujos de datos. Complementa el `README.md` (visión general) y `docs/v2-plan.md` (checklist por sprint).

---

## 1. Visión general de V2

V2 es la reescritura completa de la interfaz de usuario de LevelUp-ELO, manteniendo intacto el núcleo de lógica de negocio (dominio ELO, servicios, banco de preguntas).

| Aspecto | V1 (Streamlit) | V2 (React + FastAPI) |
|---|---|---|
| Frontend | Streamlit (Python) | React 19 + TypeScript + Vite |
| Backend | Streamlit Cloud | FastAPI + Uvicorn |
| Deploy frontend | streamlit.io | Vercel |
| Deploy backend | — | Render (free tier) |
| Estado | Producción estable | En desarrollo |
| Autenticación | Session state | JWT (access) + HttpOnly cookie (refresh) |
| Tiempo real | JS iframe setInterval | WebSocket nativo |
| Mobile | No | Sí (responsive + PWA) |

---

## 2. URLs de producción (V2)

| Servicio | URL |
|---|---|
| Frontend (Vercel) | `https://luislevelupelo.vercel.app` |
| Backend API (Render) | `https://levelup-elo.onrender.com` |
| API Docs (Swagger) | `https://levelup-elo.onrender.com/docs` |

---

## 3. Stack tecnológico

### Frontend
| Tecnología | Versión | Uso |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 5.x | Tipado estático |
| Vite | 8.x | Build tool |
| Tailwind CSS | 4.x | Estilos (utility-first) |
| React Router | 6.x | Ruteo SPA |
| React Query | 5.x | Data fetching + caché |
| Zustand | 4.x | Estado global (auth, practice, settings) |
| Recharts | 3.x | Gráficos ELO, radar, líneas |
| Framer Motion | 12.x | Animaciones |
| vite-plugin-pwa | 1.x | Service Worker + PWA manifest |

### Backend
| Tecnología | Versión | Uso |
|---|---|---|
| FastAPI | 0.115.x | Framework REST + WebSocket |
| Pydantic | 2.x | Validación de schemas |
| python-jose | — | JWT encoding/decoding |
| passlib[argon2] | — | Hash de contraseñas (reutilizado de V1) |
| uvicorn | — | ASGI server |
| psycopg2 | 2.x | Driver PostgreSQL (reutilizado de V1) |

### Infra compartida con V1
- **Dominio ELO**: `src/domain/` — sin cambios
- **Servicios**: `src/application/services/` — sin cambios
- **Repositorios**: `src/infrastructure/persistence/` — sin cambios, con nuevos métodos añadidos para V2
- **Banco de preguntas**: `items/bank/` — sin cambios
- **Base de datos**: SQLite (dev) / PostgreSQL Supabase (prod) — sin cambios

---

## 4. Estructura del proyecto V2

```
api/                              # Backend FastAPI
├── main.py                       # App FastAPI, CORS, routers, WebSocket
├── dependencies.py               # CurrentUser, RepoDep, require_role, build_vector_rating
├── schemas/
│   ├── student.py                # Request/Response schemas del estudiante
│   ├── teacher.py                # Schemas del docente
│   └── auth.py                   # Schemas de autenticación
├── routers/
│   ├── auth.py                   # POST /auth/login, /auth/register, /auth/refresh, /auth/logout
│   ├── student.py                # /student/* — práctica, stats, cursos, procedimientos
│   ├── teacher.py                # /teacher/* — dashboard, grupos, revisión
│   └── admin.py                  # /admin/* — usuarios, grupos, reportes
└── websocket/
    └── notifications.py          # WebSocket rooms por usuario/rol

frontend/                         # Frontend React
├── public/
│   ├── katia/                    # GIFs y avatar de KatIA (correcto_compressed.gif, errores_compressed.gif, katIA.png)
│   ├── favicon.svg
│   └── icons.svg
├── src/
│   ├── api/
│   │   ├── client.ts             # HTTP client base (Bearer token, ApiError, postForm)
│   │   ├── auth.ts               # login(), register(), logout(), refresh()
│   │   ├── student.ts            # studentApi: nextQuestion, answer, stats, courses, history, activity...
│   │   └── teacher.ts            # teacherApi + adminApi
│   ├── stores/
│   │   ├── authStore.ts          # Zustand: user, token, sessionStartTime (persist localStorage)
│   │   ├── practiceStore.ts      # Zustand: courseId, currentItem, lastAnswer, phase, sesión ELO
│   │   ├── settingsStore.ts      # Zustand: apiKey, provider, model (persist localStorage)
│   │   └── themeStore.ts         # Zustand: theme "dark"|"light", aplica .light en <html> (FOUC-safe)
│   ├── hooks/
│   │   ├── useTimer.ts           # Timer nativo React (setInterval), limitSeconds, autoStart
│   │   ├── useStudentSession.ts  # Orquesta loadNextQuestion + submitAnswer
│   │   └── useNotifications.ts   # WebSocket hook: unreadCount, clearUnread, onEvent
│   ├── i18n/
│   │   ├── index.ts              # i18next init: LanguageDetector → localStorage "levelup-lang", fallback "es"
│   │   └── locales/
│   │       ├── es.ts             # Traducciones ES (fuente de verdad, DeepString<T> type export)
│   │       └── en.ts             # Traducciones EN (misma estructura, valores string distintos)
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── ThemeToggle.tsx    # Botón ☀️/🌙 que alterna tema (usa themeStore + i18n)
│   │   │   ├── LanguageToggle.tsx # Botón 🌐 ES/EN en sidebar (usa i18next.changeLanguage)
│   │   │   ├── StreakToast.tsx    # Toast animado para rachas 5/10/20 correctas
│   │   │   ├── ActivityHeatmap.tsx # Heatmap 10 semanas (estilo GitHub)
│   │   │   ├── ErrorBoundary.tsx  # Captura errores de render — pantalla de error amigable
│   │   │   └── PageTransition.tsx # Transición Framer Motion entre rutas
│   │   ├── ELO/
│   │   │   ├── ELOChart.tsx       # Gráfico de línea ELO temporal (recharts)
│   │   │   ├── TopicRadarChart.tsx # Radar chart top-8 tópicos (recharts)
│   │   │   └── RankBadge.tsx      # Badge de rango (16 niveles)
│   │   ├── KatIA/
│   │   │   ├── KatIAAvatar.tsx    # Avatar con GIFs (correct/error/idle states)
│   │   │   └── SocraticChat.tsx   # Chat socrático SSE — usa `${VITE_API_URL}/api/ai/socratic` (no relativo)
│   │   └── Question/
│   │       ├── QuestionCard.tsx   # Enunciado + LaTeX + timer por pregunta + tags
│   │       ├── QuestionImage.tsx  # <img> con fallback amigable + botón reintentar (post-QA mayo)
│   │       └── AnswerOptions.tsx  # Opciones con estado (selected/correct/wrong)
│   ├── lib/
│   │   └── staleChunk.ts          # Recuperación 3-tier para chunks viejos tras deploy Vercel
│   ├── pages/
│   │   ├── Login.tsx             # Login + registro multi-paso (estudiante/docente)
│   │   ├── Layout.tsx            # Sidebar nav por rol + timer sesión + perfil + ThemeToggle
│   │   ├── Student/
│   │   │   ├── Practice.tsx       # Sala de práctica (selector curso → pregunta → feedback + KatIA)
│   │   │   ├── Stats.tsx          # ELO chart + radar + heatmap + ranking grupo + logros
│   │   │   ├── Courses.tsx        # Catálogo + matrícula + código de invitación
│   │   │   ├── Exam.tsx           # Modo examen cronometrado + borrador localStorage + retry submit
│   │   │   ├── Feedback.tsx       # Historial de procedimientos enviados + score KatIA
│   │   │   └── ProcedureUpload.tsx # Procedimiento abierto (drag&drop, multipart, SHA-256)
│   │   ├── Teacher/
│   │   │   ├── Dashboard.tsx      # 3 tabs: Estudiantes · Ranking · Métricas de uso
│   │   │   ├── Exams.tsx          # Builder de plantillas de examen (Sprint C) — ~450 líneas
│   │   │   ├── Groups.tsx         # Crear/gestionar grupos + códigos de invitación
│   │   │   ├── Procedures.tsx     # Cola de revisión de procedimientos
│   │   │   └── Export.tsx         # Descarga CSV/XLSX
│   │   └── Admin/
│   │       ├── Users.tsx          # Aprobar docentes + gestión usuarios
│   │       ├── Groups.tsx         # Vista admin de todos los grupos
│   │       ├── Reports.tsx        # Reportes técnicos de estudiantes
│   │       └── Audit.tsx          # Log de auditoría de reasignaciones
│   ├── App.tsx                   # Router principal React Router v6
│   └── main.tsx                  # Entry point
├── vite.config.ts                # Vite + TailwindCSS + PWA (workbox)
├── vercel.json                   # Deploy config: vite + rewrites SPA
└── package.json
```

---

## 5. API Endpoints — Inventario completo

### Auth (`/api/auth`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/login` | Login → access token (Bearer) + refresh cookie HttpOnly |
| POST | `/auth/register` | Registro de estudiante o docente (pendiente de aprobación) |
| POST | `/auth/refresh` | Renueva access token con refresh cookie |
| POST | `/auth/logout` | Invalida la sesión |

### Estudiante (`/api/student`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/student/next-question` | Siguiente pregunta adaptativa ZDP |
| POST | `/student/answer` | Procesar respuesta + actualizar ELO |
| GET | `/student/stats` | ELO global, por tópico, racha, rank_label |
| GET | `/student/history` | Últimos 20 intentos (elo_after + timestamp) |
| GET | `/student/activity` | Heatmap: {date: count} últimos 70 días |
| GET | `/student/streak/{course_id}` | Racha por curso específico |
| GET | `/student/group-ranking` | Ranking ELO del grupo del estudiante |
| GET | `/student/achievements` | Logros desbloqueados + catálogo completo |
| GET | `/student/courses` | Catálogo de cursos disponibles por nivel |
| POST | `/student/enroll` | Matricularse en un curso |
| POST | `/student/enroll-by-code` | Acceso inter-nivel por código de invitación |
| DELETE | `/student/enroll/{course_id}` | Darse de baja de un curso |
| POST | `/student/procedure` | Subir procedimiento manuscrito (multipart) |
| POST | `/student/exam/start` | Inicia examen cronometrado. Acepta `template_id` opcional (Sprint C) |
| POST | `/student/exam/submit` | Envía respuestas del examen |
| GET | `/student/exam/templates` | Plantillas de examen del docente disponibles para el curso (Sprint C) |
| GET | `/student/exam/history` | Historial de exámenes presentados |
| POST | `/student/procedure/analyze` | Revisión IA del procedimiento (KatIA + score) |
| PATCH | `/student/profile` | Actualizar email del perfil |
| POST | `/student/problems` | Reportar problema técnico |

### IA (`/api/ai`)
| Método | Ruta | Descripción |
|---|---|---|
| GET/SSE | `/ai/socratic` | Chat socrático KatIA con streaming (SSE) |

### Docente (`/api/teacher`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/teacher/dashboard` | Resumen de grupos y estudiantes |
| GET | `/teacher/groups` | Lista de grupos del docente |
| POST | `/teacher/groups` | Crear grupo |
| POST | `/teacher/groups/{id}/invite-code` | Generar código de invitación |
| GET | `/teacher/procedures` | Cola de procedimientos pendientes |
| POST | `/teacher/procedures/grade` | Calificar procedimiento + aplicar ELO |
| GET | `/teacher/student/{id}` | Reporte detallado del estudiante |
| GET | `/teacher/student/{id}/elo-history` | Historial ELO temporal del estudiante |
| GET | `/teacher/student/{id}/katia-history` | Interacciones KatIA del estudiante |
| POST | `/teacher/student/{id}/ai-analysis` | Análisis pedagógico con IA |
| GET | `/teacher/student/{id}/ranking` | Ranking del grupo del estudiante |
| GET | `/teacher/metrics` | Métricas de uso: tiempos, abandono, distribución horaria |
| GET | `/teacher/items` | Catálogo de ítems del curso (para builder de exámenes, Sprint C) |
| GET | `/teacher/exam-templates` | Plantillas de examen del docente (Sprint C) |
| POST | `/teacher/exam-templates` | Crear plantilla de examen (Sprint C) |
| PATCH | `/teacher/exam-templates/{id}` | Editar plantilla (título, tiempo, items) (Sprint C) |
| DELETE | `/teacher/exam-templates/{id}` | Archivar plantilla (soft delete) (Sprint C) |
| GET | `/teacher/export/csv` | Exportar intentos como CSV |
| GET | `/teacher/export/xlsx` | Exportar datos completos (4 hojas) |

### Admin (`/api/admin`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/admin/users` | Todos los usuarios activos |
| GET | `/admin/teachers/pending` | Docentes pendientes de aprobación |
| POST | `/admin/teachers/approve` | Aprobar o rechazar docente |
| PATCH | `/admin/users/{id}/deactivate` | Desactivar usuario |
| PATCH | `/admin/users/{id}/reactivate` | Reactivar usuario |
| PATCH | `/admin/students/group` | Reasignar estudiante de grupo |
| GET | `/admin/groups` | Todos los grupos |
| DELETE | `/admin/groups/{id}` | Eliminar grupo |
| GET | `/admin/reports` | Reportes técnicos de usuarios |
| PATCH | `/admin/reports/{id}/resolve` | Marcar reporte como resuelto |

### WebSocket
| Ruta | Descripción |
|---|---|
| `ws://.../ws/{room}` | Notificaciones en tiempo real por room (teacher_{id}, student_{id}) |

---

## 6. Autenticación V2

### Flujo
```
POST /auth/login
  → Verifica credenciales en DB (Argon2id)
  → Genera access token (JWT, exp: 30 min)
  → Genera refresh token (JWT, exp: 7 días)
  → Access token en response body → guardado en Zustand authStore (memoria + localStorage)
  → Refresh token en HttpOnly cookie (credentials: "include")

Cada request autenticado:
  → Header "Authorization: Bearer <access_token>"
  → Si 401 → frontend llama POST /auth/refresh → nuevo access token
```

### JWT payload
```json
{
  "sub": "42",
  "username": "estudiante1",
  "role": "student",
  "education_level": "universidad",
  "exp": 1234567890
}
```

### CurrentUser (dependency FastAPI)
```python
# Extrae user_id, username, role, education_level del JWT
user: CurrentUser  # dict con estas claves
```

---

## 7. Estado global — Zustand stores

### authStore
```typescript
{
  accessToken: string | null
  user: { user_id, username, role, education_level, grade } | null
  isAuthenticated: boolean
  sessionStartTime: number | null  // ms, para timer de sesión

  setAuth(token, user) → sessionStartTime = Date.now()
  clearAuth()
  updateUser(partial)
}
// Persistido en localStorage "levelup-auth"
```

### practiceStore
```typescript
{
  courseId: string | null
  currentItem: Item | null
  lastAnswer: { isCorrect, correctOption, eloBefore, eloAfter, deltaElo } | null
  phase: "loading" | "question" | "empty"
  isLoading: boolean
  sessionCorrectIds: string[]
  sessionWrongTimestamps: Record<string, number>
  sessionQuestionsCount: number
  questionStartTime: number | null

  startSession(courseId)
  resetSession()
  setCurrentItem(item)
  setPhase(phase)
  setLoading(bool)
  recordAnswer(...)
}
// No persistido (solo memoria de sesión)
```

### settingsStore
```typescript
{
  apiKey: string
  provider: string  // "groq" | "anthropic" | "openai" | "google"
  model: string     // ID del modelo seleccionado (vacío = auto)

  setApiKey(key)
  setProvider(provider)
  setModel(model)
}
// Persistido en localStorage "levelup-settings"
```

### themeStore
```typescript
{
  theme: "dark" | "light"

  setTheme(theme)
  toggleTheme()
}
// Persistido en localStorage "levelup-theme"
// FOUC prevention: lee localStorage directamente al cargar el módulo
// y aplica .light en <html> antes de que React monte el árbol
```

---

## 8. Características implementadas (estado actual)

### ✅ Completamente implementadas

**Estudiante:**
- Login / logout / registro multi-paso (estudiante/docente) — por username o email
- Sala de práctica: selector de curso, pregunta adaptativa ZDP, opciones, feedback ELO
- Timer por pregunta (hook useTimer) + timer de sesión global en sidebar
- Preview ELO antes de enviar ("Si aciertas +X / Si fallas -Y")
- Toast de racha en hitos 5/10/20 respuestas correctas consecutivas
- KatIA: avatar con GIFs animados + chat socrático con streaming SSE
- Procedimiento manuscrito integrado en práctica (vinculado a pregunta actual)
- Procedimiento abierto (ProcedureUpload) — drag&drop, multipart, anti-plagio SHA-256
- Centro de feedback: historial de procedimientos con score y GIFs KatIA
- Estadísticas: ELO chart temporal, radar chart top-8 tópicos, heatmap de actividad
- Ranking del grupo + logros/badges animados con Framer Motion
- Catálogo de cursos + matrícula + acceso por código de invitación inter-nivel
- Modo examen cronometrado con mapa de respuestas y resultados — soporta plantillas del docente (Sprint C) o muestreo automático estándar 30/40/30 (Sprint B)
- **Borrador de examen en `localStorage`** + retry de submit con backoff (resistente a caídas de red)
- Reporte de problemas técnicos desde sidebar
- Actualizar email de perfil desde sidebar

**Docente:**
- Dashboard: tabla de estudiantes deduplicada + panel detalle (ELO chart, tópicos, KatIA, análisis IA)
- Tab Métricas: tiempo promedio por pregunta, tasa de abandono, top tópicos, distribución horaria
- Revisión y calificación de procedimientos (aplica ELO al aprobar)
- Generación de códigos de invitación de grupo
- Exportación CSV/XLSX (filtrada: excluye is_test_user=1)
- **Exámenes manuales (Sprint C):** builder de plantillas, selector de ítems del catálogo, edición/archivado — `Teacher/Exams.tsx`

**Admin:**
- Aprobación de docentes + activar/desactivar usuarios
- Reasignación de estudiantes entre grupos (auditada en Audit.tsx)
- Reportes técnicos con resolución

**Plataforma:**
- Notificaciones WebSocket en tiempo real (badge de procedimientos)
- PWA: manifest, service worker, caché offline de assets estáticos
- Code splitting por ruta con `React.lazy` — bundle inicial <220 kB
- Error boundaries — pantalla de recuperación amigable
- Skeleton loaders en Stats, Courses y Dashboard
- Tema claro/oscuro — inversión de paleta CSS (Tailwind v4 CSS vars)
- Accesibilidad ARIA: `aria-label`, `aria-pressed`, `aria-live`, `role="dialog"`, `role="timer"`
- Transiciones de página Framer Motion
- Selector de modelo IA en sidebar (proveedor + modelo + API key)

### ✅ Sprints 7–8 completados (mayo 2026)

**Sprint 7 — Calidad:**
- 7.1 Tests E2E Playwright — `frontend/e2e/` (auth.spec, practice.spec, stats.spec, protected-routes.spec); helpers con mocking de API y localStorage injection
- 7.2 Code splitting por ruta con `React.lazy` + `Suspense` — bundle inicial <220 kB
- 7.3 Error boundaries — `ErrorBoundary.tsx` wrapping en `App.tsx`
- 7.4 Skeleton loaders en Stats, Courses y Dashboard
- 7.5 Tests de integración FastAPI — `tests/api/test_protected_routes.py` (48 tests, 100% pass)

**Sprint 8 — Pulido:**
- 8.1 Modo examen E2E — selector de cursos + N preguntas + timer global + mapa de respuestas + resumen final (sin revelar correctas)
- 8.2 Accesibilidad ARIA — `aria-label`, `aria-pressed`, `aria-live`, `role="dialog"`, `role="timer"`, focus management en modales
- 8.3 Tema claro/oscuro — inversión de paleta Tailwind v4 via CSS vars, FOUC-safe mediante lectura síncrona de localStorage en `themeStore.ts`
- 8.4 Internacionalización es/en — `react-i18next` + `i18next-browser-languagedetector`, localStorage key `levelup-lang`, `LanguageToggle` 🌐 en sidebar
- 8.5 Métricas de uso docente — tiempo promedio por pregunta, tasa de abandono, top tópicos, distribución horaria (tab "Métricas" en Dashboard)

**Fixes de producción (mayo 2026):**
- KatIA SSE: `SocraticChat.tsx` usaba URL relativa sin `VITE_API_URL` → Vercel redirigía al rewrite SPA en vez de Render. Fix: `const API_BASE = import.meta.env.VITE_API_URL ?? ""`
- CORS: corregida origin `luislevelupelo.vercel.app` en `api/config.py`
- i18n TypeScript: tipo `DeepString<T>` en `es.ts` permite que `en.ts` use valores de string distintos sin errores de tipo literal

### Sin pendientes de desarrollo
V2 lista para etiquetar `v2.0.0`.

---

## 9. Variables de entorno

### Backend (Render)
```env
DATABASE_URL=postgresql://...@...pooler.supabase.com:6543/postgres
ADMIN_PASSWORD=...
ADMIN_USER=admin
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=sb_publishable_...
SECRET_KEY=...          # Para JWT signing
CORS_ORIGINS=["https://luislevelupelo.vercel.app"]
```

### Frontend (Vercel)
```env
VITE_API_URL=https://levelup-elo.onrender.com
```

---

## 10. Ejecución local V2

```bash
# Backend FastAPI
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000

# Frontend React (en otra terminal)
cd frontend
npm install --legacy-peer-deps
npm run dev
# → http://localhost:5173 (proxy /api → localhost:8000)
```

El proxy Vite redirige todas las peticiones `/api/*` al backend en `localhost:8000`.

---

## 11. CI/CD

GitHub Actions — 7 jobs (todos verdes):

| Job | Descripción |
|---|---|
| `validate-bank` | Integridad del banco de preguntas |
| `lint` | Black + Flake8 |
| `test-unit` | pytest tests/unit/ (cobertura ≥70%) |
| `test-integration` | pytest tests/integration/ (SQLite) |
| `db-sync` | Paridad SQLite ↔ PostgreSQL |
| `test-api` | pytest tests/api/ (FastAPI con httpx) |
| `build-frontend` | tsc + vite build |

Render y Vercel tienen deploy automático en cada push a `main`.

---

## 12. Decisiones de diseño clave

### Por qué React Query sobre Zustand para datos del servidor
Los datos del servidor (stats, historial, procedimientos) son queries con caché, invalidación y refetch. Zustand es solo para estado de UI (sesión de práctica, auth, settings). Esta separación evita duplicar lógica de loading/error.

### Por qué Render free tier en lugar de Railway
Render free tier incluye HTTPS automático y deploys desde GitHub. La limitación (sleep tras 15 min de inactividad) es aceptable para un entorno de demostración. En producción real se migraría a un plan de pago.

### Por qué vite-plugin-pwa con legacy-peer-deps
`vite-plugin-pwa@1.2.0` require vite ^3-7 pero el proyecto usa vite@8. El flag `--legacy-peer-deps` evita el error de peer deps sin forzar un downgrade de Vite. Los GIFs de KatIA (6.5MB) se excluyen del precaché de Workbox (`globIgnores: ["katia/**"]`).

### ELO preview client-side
El preview "Si aciertas +X / Si fallas -Y" se calcula en el frontend con K=24 como estimación. No es exacto (el K real depende del historial del estudiante y del RD) pero es suficientemente preciso para que el estudiante calibre la apuesta.

### sessionStartTime en authStore persistido
Para que el timer de sesión sobreviva los reloads de página (React Query refetch, navegación), `sessionStartTime` se persiste en localStorage junto con el token. Se resetea en clearAuth() (logout).

### Tema claro/oscuro mediante inversión de paleta CSS (Tailwind v4)
Tailwind v4 compila `bg-slate-900` como `background-color: var(--color-slate-900)`. Al agregar `html.light { --color-slate-900: <valor claro>; ... }` se invierte toda la paleta sin tocar ningún componente. Esto fue más eficiente que agregar variantes `dark:` en 40+ archivos. Se complementa con:
- Variables `--surface` / `--canvas` para los colores hex arbitrarios (`#12121A`, `#0A0A0F`)
- Reemplazo global `text-white` → `text-slate-100` (white no pertenece a la paleta y no se invertía)
- Prevención de FOUC: el módulo `themeStore.ts` lee `localStorage` al cargarse (antes de que React monte) y aplica `.light` en `<html>` de forma síncrona

---

## 13. Estado de sprints completados

Ver `docs/v2-plan.md` para el checklist completo por sprint.

**Sprints 1-8 completados** (paridad funcional ~100% con V1):

| Sprint | Enfoque | Estado |
|---|---|---|
| 1 | UX esencial: KatIA GIFs, timer sesión, preview ELO, toasts racha, fechas gráficos, perfil sidebar | ✅ |
| 2 | Estadísticas avanzadas: radar chart, heatmap, ranking grupo, logros animados, procedimientos | ✅ |
| 3 | Panel docente completo: gráfico ELO temporal, historial KatIA, análisis IA, filtros cascada | ✅ |
| 4 | Admin: reportes, auditoría reasignaciones, activación usuarios, códigos invitación inter-nivel | ✅ |
| 5 | V2 exclusives: mobile nav, PWA prompt, offline, Framer Motion, selector modelo IA | ✅ |
| 6 | Banners pixel art, centro feedback bidireccional, reportes problemas, revisión IA en vivo | ✅ |
| Post-6 | KatIA socrático con avatar, procedimiento integrado en práctica, `student_topic_elo`, email login | ✅ |
| 7 | E2E Playwright, code splitting, error boundaries, skeleton loaders, tests rutas protegidas | ✅ |
| 8 | Modo examen E2E, accesibilidad ARIA, tema claro/oscuro, i18n es/en, métricas docente | ✅ |
| C | Exámenes manuales del docente (templates) — tabla `exam_templates` aditiva (R1), CRUD docente, selector estudiante | ✅ |

---

## 14. Sprint C — Exámenes manuales del docente

**Objetivo:** que el docente arme exámenes con ítems seleccionados a mano (no solo el muestreo automático 30/40/30 de Sprint B).

### Esquema de datos

Nueva tabla `exam_templates` en SQLite y PostgreSQL (R1 — Dual DB):

```sql
CREATE TABLE IF NOT EXISTS exam_templates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id      INTEGER NOT NULL REFERENCES users(id),
    course_id       TEXT NOT NULL,
    title           TEXT NOT NULL,
    time_limit_min  INTEGER NOT NULL,
    item_ids        TEXT NOT NULL,    -- JSON array de strings
    archived        INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_exam_templates_course ON exam_templates(course_id, archived);
```

Columna nueva en `exam_sessions`:
```sql
ALTER TABLE exam_sessions ADD COLUMN exam_template_id INTEGER NULL;
```

### Métodos CRUD (firma idéntica en ambos repos)

```python
create_exam_template(teacher_id, course_id, title, time_limit_min, item_ids) -> int
get_exam_template(template_id) -> dict | None
list_exam_templates(course_id, include_archived=False) -> list[dict]
update_exam_template(template_id, title=None, time_limit_min=None, item_ids=None) -> bool
archive_exam_template(template_id) -> bool   # soft delete: archived = 1
```

### Endpoints

**Docente** (`api/routers/teacher.py`):
- `GET /teacher/exam-templates?course_id=&include_archived=` — listar
- `POST /teacher/exam-templates` — crear (valida que todos los `item_ids` pertenezcan al `course_id`)
- `PATCH /teacher/exam-templates/{id}` — editar título, tiempo o items
- `DELETE /teacher/exam-templates/{id}` — archivar (solo el dueño o admin)
- `GET /teacher/items?course_id=` — catálogo de ítems del curso para el builder

**Estudiante** (`api/routers/student.py`):
- `GET /student/exam/templates?course_id=` — plantillas disponibles (no archivadas)
- `POST /student/exam/start` ahora acepta `template_id` opcional:
  - Con `template_id`: usa los items del template en el orden definido y `time_limit_min` del template (ignora N y tiempo del request).
  - Sin `template_id`: examen estándar 30/40/30 (Sprint B sin cambios).

### Frontend

- `frontend/src/pages/Teacher/Exams.tsx` (~450 líneas) — listado de plantillas con builder, editor de título/tiempo, selector de ítems del catálogo, archivar/restaurar.
- `frontend/src/pages/Student/Exam.tsx` ampliado — pantalla de setup ahora ofrece tipos de examen **"Estándar (auto)"** y **"Del docente"** (selector de plantilla). Si elige template, los sliders de N preguntas y tiempo se ocultan (los define el template).
- `frontend/src/api/student.ts` — `studentApi.examTemplates(course_id)` + tipo `ExamTemplateSummary`.
- `frontend/src/api/teacher.ts` — `teacherApi` con `examTemplates()`, `createExamTemplate()`, `updateExamTemplate()`, `archiveExamTemplate()`, `courseItems()`.
- i18n: `nav.exams` agregada en `es.ts` y `en.ts`.

**Sin tocar:** lógica ELO (`domain/elo/*`), `exam_submit` (sigue desacoplado del ELO según Sprint B), endpoints de práctica.

**Validación:** 112 tests API verdes, `db_sync_check` verde.

---

## 15. Fixes post-Sprint C — QA mayo 2026

Capturas reportadas por estudiantes durante uso real (13 imágenes en `bugs/`, ahora gitignoreado). Triadas y cerradas en sesión 2026-05-18 con 10 commits (`7cbea93` → `71398cb`).

### Resiliencia del flujo de examen (commit 7cbea93)

`frontend/src/pages/Student/Exam.tsx` — el estudiante perdía un examen completo si fallaba el POST `/exam/submit`. Cambios:

- **Borrador en `localStorage`** (`levelup-exam-draft`, TTL 6h): se guarda en cada respuesta y cambio de navegación. Sobrevive recargas y caídas de red.
- **Retry con backoff** dentro de `handleSubmit`: 3 intentos a 0s / 3s / 8s. Sumado al retry interno de `api.post` (cold start), son hasta 6 llamadas reales antes de rendirse.
- **Banner inline** de error con botón **"Reintentar enviar"** (antes el botón salía sin label). Se mantiene en phase `answering` con el estado intacto en vez de pasar a `error`.
- **Banner de progreso** "Reintentando envío (intento N de 3)…" durante los reintentos.
- **Banner en setup** "Tienes un examen pendiente" con botones Continuar / Descartar al volver a `/student/exam` si existe un draft válido.
- `handleResume()` restaura items + answers + itemTimes y recalcula `timeLeft = max(0, startedAt + timeLimitSeconds - now)`.
- `itemStartTime` se resetea tras computar el tiempo del ítem actual al enviar, para que reintentos no dupliquen el tiempo en pantalla.
- `clearDraft()` en submit exitoso o al descartar manualmente.

### Auto-recuperación de chunks stale (commit f3234a2)

Tras un deploy en Vercel los clientes con la SPA vieja intentaban cargar chunks con hash que ya no existe ("Failed to fetch dynamically imported module"). La protección anterior solo recargaba una vez por sesión; el flag quedaba pegado.

Nuevo módulo `frontend/src/lib/staleChunk.ts` con recuperación escalonada en **3 tiers**:

1. **1ª vez en la sesión** → `window.location.reload()` simple.
2. **2ª vez en la sesión** → `navigator.serviceWorker.getRegistrations() + r.unregister()` + `caches.keys() + caches.delete(k)`, luego reload.
3. **3ª vez en adelante** → se rinde, deja que la UI muestre el error.

`main.tsx` ahora escucha tanto `unhandledrejection` como `error` (en algunos navegadores los chunks fallidos se reportan vía el segundo). `startStaleChunkFlagCleanup()` borra los flags 5s después del `load` para que un segundo incidente en la misma sesión vuelva a tener todos los tiers disponibles. `ErrorBoundary` delega en el mismo módulo (DRY).

Patrones detectados:
```ts
msg.includes("Failed to fetch dynamically imported module")
msg.includes("Importing a module script failed")
msg.includes("error loading dynamically imported module")
msg.includes("Loading chunk")
msg.includes("Loading CSS chunk")
```

### NetworkError amigable (commit caa2ed6)

`frontend/src/api/client.ts` — antes `TypeError: Failed to fetch` se propagaba crudo. Ahora:

```ts
export class NetworkError extends ApiError {
  constructor(detail = "No pudimos conectar con el servidor. Puede estar iniciando — inténtalo de nuevo en unos segundos.") {
    super(0, detail);  // status=0 lo diferencia de HTTP
    this.name = "NetworkError";
  }
}
```

`safeFetchWithRetry()` envuelve `fetchWithRetry` y, si lanza `TypeError`, re-lanza `NetworkError`. Aplica a `request<T>` y `requestForm<T>`.

### Retry global + cold start (commit 59afcea)

`App.tsx` — `queryClient` con backoff progresivo:

```ts
retry: (failureCount, error) => {
  const status = (error as { status?: number } | null)?.status ?? 0;
  if (status >= 400 && status < 500) return false;  // 4xx no se reintenta
  return failureCount < 3;
},
retryDelay: (attemptIndex) => Math.min(2000 * 2 ** attemptIndex, 15_000),
```

`Stats.tsx` lee `failureCount` y muestra banner ámbar "El servidor está iniciando (intento N de 4)…" mientras reintenta, en vez del skeleton estático.

### Banco de preguntas (commit 95df6ad)

- 7 ítems con opciones literalmente duplicadas (la opción correcta repetida): reemplazadas por distractores matemáticamente distintos.
  - `calculo_diferencial.json q25`, `ecuaciones_diferenciales.json ed55/ed85/ed86`
  - `semillero/algebra_semillero_7.json as_7_08/as_7_10`
  - `semillero/conteo_combinatoria_semillero_10.json ccs_10_02`
- 8 ítems en `algebra_semillero_7.json` (`as_7_18, 19, 20, 21, 23, 24, 25, 32`) usaban `$\\$NUMBER$` (math mode con `\$` escapado). El regex de `RenderMath` no maneja `\$` dentro de math mode → rompía el split y dejaba prosa española dentro de math (variables itálicas pegadas sin espacios). Reescritos a `USD NUMBER` (texto plano, sin `$` delimitador).
- Nueva utilidad `scripts/scan_dollar_prices.py` para detectar futuras regresiones (regex + heurística de prosa española).
- `scripts/validate_bank.py`: 1971 IDs únicos, validación verde.

### QuestionImage con fallback (commit 8db971e)

`frontend/src/components/Question/QuestionImage.tsx` — antes el `<img alt="Figura">` mostraba el alt text como contenido cuando fallaba a cargar (los estudiantes pensaban que era parte del enunciado). Ahora:

- Si la imagen carga → `<img>` normal.
- Si dispara `onError` → banner ámbar "No se pudo cargar la imagen del problema" + botón **"Reintentar"** que fuerza nuevo fetch vía cambio de `key`.
- Si `imageUrl` es null/vacío → no renderiza nada.

Reemplaza el `<img>` directo en `Exam.tsx` y `QuestionCard.tsx`.

### CVEs npm (commit 71398cb)

`npm audit fix --legacy-peer-deps` — 4 devDependencies transitivas:

| Paquete | Fix | Severidad | GHSA |
|---|---|---|---|
| `@babel/plugin-transform-modules-systemjs` | 7.29.0 → 7.29.4 | high | GHSA-fv7c-fp4j-7gwp |
| `brace-expansion` | 5.0.5 → 5.0.6 | moderate | GHSA-jxxr-4gwj-5jf2 |
| `fast-uri` | 3.1.0 → 3.1.2 | high | GHSA-q3j6-qgpj-74h6 + GHSA-v39h-62p7-jpjc |
| `postcss` | 8.5.9 → 8.5.14 | moderate | GHSA-qx2v-qp2m-jg93 |

Solo `package-lock.json` cambió; sin impacto en runtime.

---

## 16. Próximos pasos

V2 fue etiquetada como `v2.0.0` (commit `c791054`, tag pusheado a `origin`). Tareas opcionales:

1. **Convertir el tag en GitHub Release** con notas formateadas: visitar la URL del tag y clickear "Create release from tag". El mensaje del tag ya está en markdown con resumen completo.
2. **QA manual en producción** — smoke test end-to-end en `luislevelupelo.vercel.app` para confirmar que los 13 fixes resuelven los reportes del QA de mayo (registro, examen, KatIA, procedimiento).
3. **Migrar el backend a plan de pago en Render** — el sleep tras 15 min en free tier impacta la primera carga (~30s de cold start). Los fixes #2/#7/#9 mitigan pero no eliminan.
4. **Considerar branch protection** en `main` ahora que está en producción — exigir CI verde y al menos 1 review antes de merge.
