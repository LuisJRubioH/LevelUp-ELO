# Plan V2 — LevelUp-ELO: React + FastAPI

Fecha: 2026-04-14 (última revisión 2026-05-19)
Estado: **Sprints 1-8 + Sprint C completos + QA mayo 2026 + sesión de pulido 2026-05-19 (i18n completo, banners unificados, fix consistencia ELO) — V2 lista para etiquetar `v2.0.1`**

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
- [x] Fix deduplicación: `get_teacher_dashboard_stats` devuelve 1 fila por estudiante (GROUP BY u.id, no group_id)
- [x] Fix deduplicación: `export_teacher_student_data` reemplaza UNION ALL por CTE — cada intento aparece 1 sola vez
- [x] Fix deduplicación: `student_count` usa `COUNT(DISTINCT e.user_id)` en vez de `COUNT(*)`
- [x] Columna `cursos_matriculados` en export (GROUP_CONCAT SQLite / STRING_AGG PostgreSQL)
- [x] Campo `users.email`: TEXT con UNIQUE parcial (NULL OK), login por username O email
- [x] Métodos: `get_user_by_login()`, `email_exists()`, `update_user_email()`, `_valid_email_format()`
- [x] `register_user()` acepta `email` opcional, validación de formato y unicidad
- [x] `PATCH /student/profile` para actualizar email (409 si ya existe, 422 si formato inválido)
- [x] V2 Frontend: campo email obligatorio en registro, login por email, banner + form en sidebar para usuarios sin email
- [x] V1 Streamlit: campo email opcional en registro, label "Usuario o correo electrónico" en login

## Checklist Sprint 7 — Calidad y producción

- [x] 7.1 Tests E2E con Playwright (auth, práctica, stats, rutas protegidas) — `frontend/e2e/`
- [x] 7.2 Code splitting por ruta (`React.lazy`) — commit d8d5291
- [x] 7.3 Error boundaries + pantalla de error amigable — commit d8d5291
- [x] 7.4 Skeleton loaders en listas y charts — commit 28ad50f
- [x] 7.5 Tests de integración de rutas protegidas — `tests/api/test_protected_routes.py` (48 tests, 100%)

## Checklist Sprint 8 — Pulido y accesibilidad

- [x] 8.1 Modo examen end-to-end
- [x] 8.2 Accesibilidad (aria-labels, focus, keyboard nav)
- [x] 8.3 Tema claro / oscuro (CSS variable palette inversion, FOUC-safe)
- [x] 8.4 Internacionalización es/en con react-i18next — Login, Layout, Practice, ThemeToggle; LanguageToggle 🌐 en sidebar
- [x] 8.5 Métricas de uso en dashboard docente

## Checklist Sprint C — Exámenes manuales del docente

**Objetivo:** que el docente arme exámenes personalizados (seleccionando ítems del curso) en vez de depender solo del muestreo automático estándar 30/40/30 de Sprint B.

**Backend (commit cd397af):**

- [x] C.1 Tabla `exam_templates` aditiva en SQLite + PostgreSQL (R1): `id, teacher_id, course_id, title, time_limit_min, item_ids (JSON), archived, created_at` + índice `(course_id, archived)`. Columna `exam_template_id INTEGER NULL` agregada a `exam_sessions`.
- [x] C.1 Métodos CRUD en ambos repos con firma idéntica: `create_exam_template`, `get_exam_template`, `list_exam_templates`, `update_exam_template`, `archive_exam_template`. `db_sync_check` verde.
- [x] C.2 Endpoints docente (`api/routers/teacher.py`):
  - `GET /api/teacher/exam-templates?course_id=&include_archived=`
  - `POST /api/teacher/exam-templates` (crea)
  - `PATCH /api/teacher/exam-templates/{id}` (edita título/tiempo/items)
  - `DELETE /api/teacher/exam-templates/{id}` (archiva — soft delete)
  - `GET /api/teacher/items?course_id=` (catálogo para armar examen)
- [x] C.2 Schemas: `ExamTemplateCreateRequest`, `ExamTemplatePatchRequest`, `ExamTemplateResponse`, `ItemCatalogEntry`. Validación: todos los `item_ids` deben pertenecer al curso. Autorización: solo el dueño (o admin) puede editar/archivar.
- [x] C.3 Endpoints estudiante (`api/routers/student.py`):
  - `GET /api/student/exam/templates?course_id=` (plantillas disponibles, no archivadas)
  - `POST /api/student/exam/start` ahora acepta `template_id` opcional: con template usa los items del template en orden definido y `time_limit_min` del template; sin template mantiene el flujo estándar de Sprint B.

**Frontend (commit 23df646):**

- [x] C.4 Nueva pantalla `Teacher/Exams.tsx` (~450 líneas): listado de plantillas, builder con selector de ítems del catálogo, editor de título y duración, archivar/restaurar. Entry en sidebar docente con i18n `nav.exams`.
- [x] C.4 `studentApi.examTemplates(course_id)` + tipo `ExamTemplateSummary`. `teacherApi` con métodos CRUD completos.
- [x] C.5 `Student/Exam.tsx` ampliado: en la pantalla de setup el estudiante elige entre **"Estándar (auto)"** o **"Del docente"** (selector de plantilla); si elige template, los sliders de N preguntas y tiempo se ocultan (los define el template). El payload pasa `template_id` opcional al backend.

**Sin tocar:** lógica ELO (`domain/elo/*`), `exam_submit` (sigue desacoplado del ELO según Sprint B), endpoints de práctica. 112 tests API verdes, `db_sync_check` verde.

## Fixes post-Sprint C — QA mayo 2026

Capturas reportadas por estudiantes durante uso real (13 imágenes en `bugs/`). Triadas y cerradas en sesión 2026-05-18 (commits `7cbea93` → `71398cb`):

- [x] Examen no enviaba si el POST fallaba (estudiante perdía intento completo) → borrador en `localStorage` + retry con backoff 0/3/8s + banner "Reintentar enviar" inline (commit 7cbea93)
- [x] `Failed to fetch dynamically imported module` tras deploy de Vercel → recuperación escalonada en 3 tiers: reload simple → SW+caches cleanup → giveup, con `frontend/src/lib/staleChunk.ts` compartido entre `main.tsx` y `ErrorBoundary` (commit f3234a2)
- [x] `TypeError: Failed to fetch` crudo en UI → nueva `NetworkError extends ApiError(status=0)` con mensaje en español apto para mostrar (commit caa2ed6)
- [x] Stats sin retry automático de cold start → queryClient global con `retry: 3, retryDelay: exponencial 2s→15s` + banner "El servidor está iniciando (intento N de 4)…" en `Stats.tsx` (commit 59afcea)
- [x] Banco: 7 ítems con opciones literalmente duplicadas (correct_option × 2) → distractores matemáticamente distintos (commit 95df6ad)
- [x] Banco: 8 ítems en `algebra_semillero_7.json` con precios `$\$NUMBER$` que rompían el regex de RenderMath → reescritos a `USD NUMBER` (commit 95df6ad)
- [x] Imagen del problema mostraba `alt="Figura"` cuando fallaba la carga (confundía al estudiante) → nuevo `<QuestionImage>` con banner "No se pudo cargar la imagen del problema" + botón Reintentar (commit 8db971e)
- [x] LaTeX en chat KatIA → ya estaba resuelto en commit edf6602 (Sprint A.1 B4); regex de `RenderMath` valida `$x$`, `$x^2$`, `$(24)(35)(46)(57)$`
- [x] CVEs npm transitivas (4: babel/systemjs, brace-expansion, fast-uri, postcss) → `npm audit fix --legacy-peer-deps` (commit 71398cb)
- [x] `bugs/` carpeta de capturas QA agregada al `.gitignore` (commit f82b020)

## Sesión de pulido — 2026-05-19

Continuación del QA: 2 hallazgos UX (#5 inconsistencia ELO, #9 i18n parcial) + 1 mejora visual (estilo banners). Verificado en producción con Playwright.

**Fix de consistencia ELO entre header y feedback (commit `13e1ab3`):**

- [x] `Practice.tsx` pisaba el ELO global del header (`RankBadge`) con `lastAnswer.eloAfter` tras cada respuesta. El problema: `eloAfter` es el ELO del TÓPICO (devuelto por `/answer`), no el global (que se obtiene de `/stats`). Resultado: sidebar mostraba 1022, feedback mostraba 1009 — el estudiante percibía inconsistencia.
- [x] Solución: tras cada respuesta, refresca `/stats` para obtener el ELO global actualizado en lugar de pisarlo con el del tópico. El feedback ahora etiqueta claramente: `ELO en este tema (Cálculo Diferencial): 1010 → 1015 (+5.1)` con nota italic explicando que el global del header promedia todos los temas.

**Internacionalización completa del flujo estudiante + docente (commits `407a3dc` → `74b18c2`, `ff1b950`):**

Cobertura previa: solo Login + Sidebar + Practice. Cerrado en esta sesión:

- [x] **Estudiante**: Courses (tabs, intros, CTAs), Stats (radar/ranking/historial/logros), Exam (setup completo + modal de confirmación con número resaltado en verde vía `confirmAnsweredPrefix`/`Suffix`), ProcedureUpload (dropzone + estados KatIA por score + secciones de revisión), Feedback (histórico de procedimientos con 3 estados KatIA por puntaje), ReportProblem modal, AnswerOptions (aria-labels de Opción A/B/C/D + sufijos Correcto/Incorrecto), ProcedureSection inline.
- [x] **Docente**: Teacher Dashboard completo — KPIs (Total intentos, Tiempo promedio, Tasa de abandono, Hora pico), tabs (Estudiantes/Ranking/Métricas), tabla con filtros (Todos los grupos, Todos los niveles, Buscar), detalle de estudiante (tabs ELO/Tópicos/KatIA/Análisis IA con sus textos de vacío y errores), gráficos de actividad diaria + distribución horaria.
- [x] Toggle 🌐 ES↔EN funciona en ambos sentidos sin recargar la página.
- [x] Pantallas docente Groups/Procedures/Exams/Export y admin Users/Reports/Audit quedan en español — uso interno, fuera del alcance original del Sprint 8.4.

**Unificación visual de banners — pixel-art + LaTeX mathtext (commits `90e124c`, `256d7e7`):**

- [x] Problema: las fórmulas con caracteres Unicode (∫, ∂, →, ²) renderizaban roto en fuente Consolas Bold del generador. Además, los banners user-supplied (1689×843, 1514×757, etc.) tenían aspect ratios distintos al 16:7 del componente `CourseBanner.tsx`, causando recortes que cortaban la fórmula. Por encima, un gradiente del 33% inferior al 85% de opacidad oscurecía la zona de la ecuación.
- [x] `scripts/generate_banners.py` refactorizado:
  - **Modo generativo**: canvas pequeño (256×112) con montañas/estrellas/título pixel-art → NEAREST upscale a 1536×672. La fórmula se renderiza por separado con `matplotlib.mathtext` en resolución final (anti-aliased crisp) y se compone con backdrop rounded box semi-transparente.
  - **Modo overlay** (parámetro `base_image`): carga banner user-supplied, hace **crop centrado al ratio 16:7 + LANCZOS resize a 1536×672**, luego añade overlay LaTeX. Originales en `frontend/public/banners/_originals/` (gitignored) como fuente idempotente.
- [x] Fórmulas elegidas por curso:
  - Aritmética: `a^m · a^n = a^{m+n}` (regla de exponentes)
  - Álgebra: `x = (-b ± √(b²-4ac)) / 2a` (cuadrática)
  - Geometría: `a² + b² = c²` (Pitágoras)
  - Lógica: `\overline{A ∪ B} = \overline{A} ∩ \overline{B}` (De Morgan)
  - Conteo: `C(n,k) = n! / (k!(n-k)!)` (binomial)
  - Probabilidad: teorema de Bayes
  - Cálculo Diferencial: definición de derivada por límite
  - Cálculo Integral: teorema fundamental del cálculo
  - Varias Variables: regla de la cadena multivariable
  - Ecuaciones Diferenciales: transformada de Laplace
  - Álgebra Lineal: `Av = λv` (autovalores — más limpio que un determinante 2×2)
  - Trigonometría: identidad pitagórica
- [x] `CourseBanner.tsx`: gradiente inferior reducido de `h-1/3 / 0.85` a `h-[18%] / 0.45` — fade decorativo sutil que ya no oscurece la fórmula (que tiene su propio backdrop).
- [x] **Resultado:** los 14 banners (8 generados + 6 con overlay sobre arte original) ahora son **1536×672 idénticos**, sin recortes en la grilla de cursos. Título y fórmula completamente visibles al entrar a la plataforma.

**Verificación QA en navegador (Playwright):**

- [x] Login + sidebar + toggle 🌐 ES/EN
- [x] Practice: header ELO global ≠ feedback ELO tópico (con nota explicativa). LaTeX renderiza en pregunta + opciones.
- [x] Grilla de cursos universidad (estudiante1): 6 banners visibles con título + fórmula
- [x] Grilla de cursos colegio (estudiante2): 4 banners visibles con título + fórmula
- [x] Stats: KPIs, evolución ELO, heatmap, radar, ranking grupo, logros, historial exámenes (todo en EN al toggle)
- [x] Exam: setup → pregunta con LaTeX → modal de confirmación con highlight verde + pluralización
- [x] ProcedureUpload: textos + dropzone + interpolación de cursos matriculados
- [x] Feedback empty state: emptyTitle/emptyHint/emptySection (bold) renderizado correcto
- [x] ReportProblem modal: title + description + placeholder + contador + botones (todo en ES/EN)
- [x] Teacher Dashboard: grupos, tabs, tabla, filtros, métricas con chart de actividad diaria — todo en ES y EN

**Sin bugs nuevos encontrados.** Cambios desplegados en Vercel + Render.
