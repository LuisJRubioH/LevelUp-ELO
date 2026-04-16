# Plan V2 — LevelUp-ELO: React + FastAPI

Fecha: 2026-04-14 (última revisión 2026-04-16)
Estado: **Sprints 1-6 cerrados + fixes post-Sprint 6 — Sprint 7 (calidad) y Sprint 8 (pulido) pendientes**

## Contexto

V1 es la app Streamlit monolítica (producción actual, funcional, completa).
V2 es la reescritura React + FastAPI con Clean Architecture, desplegada en Vercel (frontend) + Render (backend).

Deploy actual:
- Frontend: `https://luislevelupelo.vercel.app`
- Backend: `https://levelup-elo.onrender.com`
- CI: 7 jobs verdes en GitHub Actions

**Estado V2 al iniciar ejecución del plan: ~50% de la funcionalidad de V1.**

---

## Lo que V2 ya tiene

- Login / logout / registro multi-paso (Estudiante / Docente)
- Sala de práctica: selector de curso, pregunta adaptativa, opciones, feedback ELO, timer por pregunta, KatIA avatar, chat socrático
- Estadísticas: ELO global, ranking, ELO por tópico, logros
- Catálogo de cursos: explorar, matricular, acceso especial por código de invitación
- Panel docente: tabla de estudiantes, detalle por estudiante, calificar procedimientos
- Exportación de datos (endpoint API parcial)
- WebSocket para notificaciones en tiempo real (badge de procedimientos)
- PWA básica configurada (vite-plugin-pwa)
- Panel admin: aprobación de docentes, gestión de usuarios

---

## Lo que falta por sprint

### Sprint 1 — Experiencia del estudiante (UX esencial)
**Objetivo:** cerrar la brecha de experiencia en la sala de práctica y estadísticas.

| # | Tarea | Archivo(s) |
|---|---|---|
| 1.1 | Copiar GIFs de KatIA a `frontend/public/katia/` | bash cp |
| 1.2 | Timer de sesión global en Layout sidebar | `Layout.tsx` + `useTimer` |
| 1.3 | Preview ELO antes de enviar ("Si aciertas: +X / Si fallas: -Y") | `Practice.tsx` + endpoint API |
| 1.4 | Toast de racha (5, 10, 20 preguntas correctas consecutivas) | nuevo `StreakToast.tsx` |
| 1.5 | Corrección de fechas en gráfico ELO (Stats.tsx usa "#1 #2" en lugar de fechas reales) | `Stats.tsx` |
| 1.6 | Perfil de estudiante (nombre, nivel, grado) visible en sidebar | `Layout.tsx` |

### Sprint 2 — Estadísticas avanzadas del estudiante
**Objetivo:** paridad con el panel de estadísticas de V1.

| # | Tarea | Archivo(s) |
|---|---|---|
| 2.1 | Gráfico radar de rendimiento por tópico | `Stats.tsx` + recharts RadarChart |
| 2.2 | Heatmap de actividad semanal (7×24h) | nuevo `ActivityHeatmap.tsx` |
| 2.3 | Racha de estudio por curso (no solo global) | endpoint `GET /student/streak/{course_id}` |
| 2.4 | Ranking semanal del grupo | endpoint `GET /student/group-ranking` |
| 2.5 | Logros animados (fade-in al desbloquear) | `Achievements.tsx` con Framer Motion |
| 2.6 | Envío de procedimientos manuscritos desde V2 | `ProcedureUpload.tsx` |

### Sprint 3 — Panel docente completo
**Objetivo:** paridad con el dashboard docente de V1.

| # | Tarea | Archivo(s) |
|---|---|---|
| 3.1 | Gráfico ELO temporal por estudiante (últimas N sesiones) | `Dashboard.tsx` + recharts |
| 3.2 | Análisis pedagógico con IA por estudiante | endpoint `POST /teacher/ai-analysis` + UI |
| 3.3 | Historial de interacciones KatIA por estudiante | `Dashboard.tsx` panel lateral |
| 3.4 | Visor de imagen de procedimiento (desde Supabase Storage) | `Procedures.tsx` |
| 3.5 | Filtros en cascada: Grupo → Nivel → Materia | `Dashboard.tsx` |
| 3.6 | Ranking del grupo en el dashboard | `Dashboard.tsx` |

### Sprint 4 — Panel admin y funciones administrativas
**Objetivo:** completar el panel admin con paridad V1.

| # | Tarea | Archivo(s) |
|---|---|---|
| 4.1 | Sección de reportes de problemas técnicos (con botón "Resuelto") | `admin/Reports.tsx` |
| 4.2 | Log de auditoría de reasignaciones de grupo | `admin/AuditLog.tsx` |
| 4.3 | Activar / desactivar usuarios desde el panel admin | `admin/Users.tsx` |
| 4.4 | Eliminar grupos (con confirmación) | `admin/Groups.tsx` |
| 4.5 | Generación de códigos de invitación en el panel docente | `teacher/Groups.tsx` |

### Sprint 5 — Exclusivas V2 (mejoras vs V1)
**Objetivo:** aprovechar las ventajas de React para superar a V1.

| # | Tarea | Archivo(s) |
|---|---|---|
| 5.1 | Navegación móvil (bottom nav bar) | `Layout.tsx` + `BottomNav.tsx` |
| 5.2 | Prompt de instalación PWA | `PWAPrompt.tsx` |
| 5.3 | Caché offline para preguntas (Service Worker + IndexedDB) | `vite.config.ts` + `sw.ts` |
| 5.4 | Selector de modelo IA en sidebar (Groq/Anthropic/OpenAI) | `Layout.tsx` |
| 5.5 | Transiciones de página (Framer Motion) | `App.tsx` + rutas |
| 5.6 | Tema claro / oscuro | `ThemeToggle.tsx` + Tailwind |

### Sprint 6 — Paridad V1 faltante (crítico)
**Objetivo:** cerrar los huecos visuales y de flujo que V1 tiene y V2 aún no.

| # | Tarea | Archivo(s) |
|---|---|---|
| 6.1 | Banners pixel art en tarjetas de curso (geometria, aritmetica, logica, conteo_combinatoria, probabilidad, algebra) | `Courses.tsx` + copiar `Banners/` a `frontend/public/banners/` |
| 6.2 | Centro de feedback del estudiante con badge de no leídos (mensajes bidireccionales docente↔estudiante) | nuevo `FeedbackCenter.tsx` + endpoint `GET/PATCH /student/feedback` + tabla `feedback_messages` (o reutilizar notifications) |
| 6.3 | Formulario de reporte de problemas técnicos en sidebar del estudiante (expander con textarea, mín 10 chars) | `Layout.tsx` + endpoint `POST /student/report` (tabla `problem_reports` ya existe) |
| 6.4 | Revisión de procedimiento con IA en tiempo real + GIFs animados de KatIA (revisando → resultado por rango) | `ProcedureUpload.tsx` — wire endpoint `POST /student/procedure/analyze` con streaming/spinner + GIFs |

### Sprint 7 — Calidad y producción
**Objetivo:** poner V2 al nivel de confiabilidad de V1 para uso real por estudiantes.

| # | Tarea | Archivo(s) |
|---|---|---|
| 7.1 | Tests E2E con Playwright (login, práctica, stats, procedimiento) | `tests/e2e/` + `playwright.config.ts` + job CI |
| 7.2 | Code splitting por ruta (`React.lazy` + `Suspense`) — bundle inicial ~200 kB | `App.tsx` — lazy-load cada página |
| 7.3 | Error boundaries + pantalla de error amigable con botón "recargar" | nuevo `ErrorBoundary.tsx` wrap en `App.tsx` |
| 7.4 | Skeleton loaders reemplazan "Cargando..." plano en listas y charts | `components/ui/Skeleton.tsx` + aplicar en Stats, Dashboard, Courses |
| 7.5 | Tests de integración de rutas protegidas (RequireAuth, RequireRole) | `tests/api/test_auth_flow.py` + frontend tests Vitest |

### Sprint 8 — Pulido y accesibilidad (deseable)
**Objetivo:** cerrar detalles finos que hacen la diferencia entre "funciona" y "producto profesional".

| # | Tarea | Archivo(s) |
|---|---|---|
| 8.1 | Modo examen end-to-end: selector de cursos, N preguntas, timer global, resumen final sin revelar correctas | `Exam.tsx` + endpoints ya existentes + tests |
| 8.2 | Accesibilidad: aria-labels en botones icono-only, focus states visibles, navegación por teclado | auditoría en `Layout.tsx`, `AnswerOptions.tsx`, modales |
| 8.3 | Tema claro / oscuro (ex-5.6) con CSS variables y `dark:` strategy | `ThemeToggle.tsx` + refactor ~40 componentes |
| 8.4 | Internacionalización (es/en) con `react-i18next` (opcional, si hay demanda) | `i18n/` + claves |
| 8.5 | Métricas de uso (tiempo promedio por pregunta, tasa de abandono) en dashboard docente | endpoint + `Dashboard.tsx` tab "Métricas" |

---

## Reglas de desarrollo V2

1. **No tocar V1** — V1 (Streamlit) es producción. Los cambios en `src/`, `scripts/`, `items/` deben respetar todas las reglas del CLAUDE.md.
2. **Dual DB en API** — cualquier endpoint nuevo debe funcionar con SQLite (dev) y PostgreSQL (prod) vía `get_repo()`.
3. **No romper el CI** — todos los commits pasan los 7 jobs de GitHub Actions.
4. **Commits atómicos** — un commit por tarea completada; mensaje en inglés estilo `feat(v2): ...`.

---

## Checklist Sprint 1

- [x] 1.1 GIFs de KatIA en `frontend/public/katia/`
- [x] 1.2 Timer global de sesión en Layout sidebar
- [x] 1.3 Preview ELO ("Si aciertas +X / Si fallas -Y") en Practice
- [x] 1.4 Toast de racha (5/10/20 correctas consecutivas)
- [x] 1.5 Fechas reales en gráfico ELO de Stats
- [x] 1.6 Perfil visible en sidebar (nivel/grado)

**Completadas:** todas — commits 1046421 y 82578e6

## Checklist Sprint 2

- [x] 2.1 Radar chart por tópico
- [x] 2.2 Heatmap de actividad
- [x] 2.3 Racha por curso
- [x] 2.4 Ranking semanal del grupo
- [x] 2.5 Logros animados
- [x] 2.6 Envío de procedimientos

**Completadas:** todas — commit da4c0e7

## Checklist Sprint 3

- [x] 3.1 ELO temporal por estudiante
- [x] 3.2 Análisis pedagógico IA
- [x] 3.3 Historial KatIA
- [x] 3.4 Visor de imagen de procedimiento (Supabase Storage)
- [x] 3.5 Filtros en cascada: Grupo → Nivel → Materia
- [x] 3.6 Ranking del grupo en el dashboard

**Completadas:** todas — commit b9f98f0

## Checklist Sprint 4

- [x] 4.1 Reportes técnicos
- [x] 4.2 Log de auditoría
- [x] 4.3 Activar/desactivar usuarios
- [x] 4.4 Eliminar grupos
- [x] 4.5 Códigos de invitación

**Completadas:** todas — 4.1/4.3/4.4/4.5 ya estaban; 4.2 agregada en este sprint

## Checklist Sprint 5

- [x] 5.1 Navegación móvil (bottom nav + top bar)
- [x] 5.2 PWA install prompt
- [x] 5.3 Caché offline (vite-plugin-pwa runtimeCaching)
- [x] 5.4 Selector de modelo IA (provider ya está — falta elección de modelo específico)
- [x] 5.5 Transiciones Framer Motion
- [→] 5.6 Tema claro/oscuro — **movido a Sprint 8.3** (costo alto; se pospone hasta después de cerrar paridad y calidad)

## Checklist Sprint 6 — Paridad V1 faltante

- [x] 6.1 Banners pixel art en tarjetas de curso
- [x] 6.2 Centro de feedback del estudiante (bidireccional con badge)
- [x] 6.3 Formulario de reporte de problemas técnicos
- [x] 6.4 Revisión de procedimiento con IA + GIFs animados de KatIA en tiempo real

**Completadas:** todas — commit d4bdf1d (banners, feedback, reportes, IA en vivo) + keys del sistema por función

## Fixes post-Sprint 6

- [x] Fix `/ai/socratic`: endpoint pasaba 4 args incorrectos a `get_socratic_guidance()` (10 params). Ahora consulta ítem desde DB, calcula ELO del estudiante, auto-detecta proveedor/modelo
- [x] KatIA SocraticChat: avatar visible (foto estática + GIF animado mientras piensa), mensajes de bienvenida con personalidad, manejo de errores SSE
- [x] Procedimiento manuscrito integrado en `Practice.tsx` como sección colapsable (`ProcedureSection.tsx`), auto-vinculado al `currentItem`
- [x] `ProcedureUpload.tsx` convertida a "Procedimiento abierto" para ejercicios de desarrollo / preguntas abiertas
- [x] Menú: "Procedimientos" renombrado a "Proc. abierto" para evitar confusión
- [x] Nueva tabla `student_topic_elo`: PK `(user_id, topic)`, `current_elo`, `rd`, `updated_at` — ELO por materia consultable directamente
- [x] Campo `users.current_elo`: ELO global (promedio de `student_topic_elo`), actualizado automáticamente en `save_attempt`, `save_answer_transaction`, `validate_procedure_submission`
- [x] Backfill `_backfill_current_elo()`: pobla `student_topic_elo` y `users.current_elo` para usuarios existentes al iniciar la app

## Checklist Sprint 7 — Calidad y producción

- [ ] 7.1 Tests E2E con Playwright
- [ ] 7.2 Code splitting por ruta (`React.lazy`)
- [ ] 7.3 Error boundaries + pantalla de error amigable
- [ ] 7.4 Skeleton loaders en listas y charts
- [ ] 7.5 Tests de integración de rutas protegidas

## Checklist Sprint 8 — Pulido y accesibilidad

- [ ] 8.1 Modo examen end-to-end
- [ ] 8.2 Accesibilidad (aria-labels, focus, keyboard nav)
- [ ] 8.3 Tema claro / oscuro
- [ ] 8.4 Internacionalización es/en (opcional)
- [ ] 8.5 Métricas de uso en dashboard docente
