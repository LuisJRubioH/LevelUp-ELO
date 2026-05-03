# Documento Técnico — LevelUp-ELO V2

**Estado:** Sprints 1-8 completos ✅ — paridad funcional 100% con V1. Listo para `v2.0.0`.
**Última actualización:** 2026-05-02
**Autor:** Luis Rubio

> Este documento es de trabajo interno. No se sube a GitHub hasta que V2 esté completamente implementada.

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
│   │       └── AnswerOptions.tsx  # Opciones con estado (selected/correct/wrong)
│   ├── pages/
│   │   ├── Login.tsx             # Login + registro multi-paso (estudiante/docente)
│   │   ├── Layout.tsx            # Sidebar nav por rol + timer sesión + perfil + ThemeToggle
│   │   ├── Student/
│   │   │   ├── Practice.tsx       # Sala de práctica (selector curso → pregunta → feedback + KatIA)
│   │   │   ├── Stats.tsx          # ELO chart + radar + heatmap + ranking grupo + logros
│   │   │   ├── Courses.tsx        # Catálogo + matrícula + código de invitación
│   │   │   ├── Exam.tsx           # Modo examen cronometrado con mapa de respuestas
│   │   │   ├── Feedback.tsx       # Historial de procedimientos enviados + score KatIA
│   │   │   └── ProcedureUpload.tsx # Procedimiento abierto (drag&drop, multipart, SHA-256)
│   │   ├── Teacher/
│   │   │   ├── Dashboard.tsx      # 3 tabs: Estudiantes · Ranking · Métricas de uso
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
| POST | `/student/exam/start` | Inicia examen cronometrado (N preguntas) |
| POST | `/student/exam/submit` | Envía respuestas del examen |
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
- Modo examen cronometrado con mapa de respuestas y resultados
- Reporte de problemas técnicos desde sidebar
- Actualizar email de perfil desde sidebar

**Docente:**
- Dashboard: tabla de estudiantes deduplicada + panel detalle (ELO chart, tópicos, KatIA, análisis IA)
- Tab Métricas: tiempo promedio por pregunta, tasa de abandono, top tópicos, distribución horaria
- Revisión y calificación de procedimientos (aplica ELO al aprobar)
- Generación de códigos de invitación de grupo
- Exportación CSV/XLSX (filtrada: excluye is_test_user=1)

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

---

## 14. Próximos pasos

V2 está lista para tagging. Tareas de cierre opcionales:

1. Etiquetar `v2.0.0` en git (`git tag v2.0.0 && git push origin v2.0.0`)
2. Hacer público `docs/v2-tecnico.md` en el repositorio (actualmente gitignoreado)
3. Migrar el backend Render a un plan de pago si hay uso real de estudiantes (sleep tras 15 min en free tier)
