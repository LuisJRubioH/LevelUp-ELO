# Plan V2 — LevelUp-ELO: React + FastAPI

Fecha: 2026-04-13
Estado: **En ejecución — Sprint 1**

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
- [ ] 1.5 Fechas reales en gráfico ELO de Stats
- [ ] 1.6 Perfil visible en sidebar (nivel/grado)

**Completadas:** 1.1, 1.2, 1.3, 1.4 (commit 1046421)

## Checklist Sprint 2

- [ ] 2.1 Radar chart por tópico
- [ ] 2.2 Heatmap de actividad
- [ ] 2.3 Racha por curso
- [ ] 2.4 Ranking semanal del grupo
- [ ] 2.5 Logros animados
- [ ] 2.6 Envío de procedimientos

## Checklist Sprint 3

- [ ] 3.1 ELO temporal por estudiante
- [ ] 3.2 Análisis pedagógico IA
- [ ] 3.3 Historial KatIA
- [ ] 3.4 Visor de imagen de procedimiento
- [ ] 3.5 Filtros en cascada
- [ ] 3.6 Ranking del grupo

## Checklist Sprint 4

- [ ] 4.1 Reportes técnicos
- [ ] 4.2 Log de auditoría
- [ ] 4.3 Activar/desactivar usuarios
- [ ] 4.4 Eliminar grupos
- [ ] 4.5 Códigos de invitación

## Checklist Sprint 5

- [ ] 5.1 Navegación móvil
- [ ] 5.2 PWA install prompt
- [ ] 5.3 Caché offline
- [ ] 5.4 Selector de modelo IA
- [ ] 5.5 Transiciones Framer Motion
- [ ] 5.6 Tema claro/oscuro
