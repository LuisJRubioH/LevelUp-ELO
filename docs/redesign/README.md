# Rediseño — referencia de diseño (export de claude.ai/design)

Bundle exportado del proyecto de diseño, reorganizado. Los HTML son **standalone**
(cargan React 18 + Babel desde unpkg y referencian a sus hermanos por ruta plana),
así que `source/` se mantiene como una sola carpeta para que los previews funcionen:
ábrelos directo en el navegador.

## Estructura

```
docs/redesign/
  source/        ← bundle de diseño (HTML/JSX/CSS/assets) — previews funcionan aquí
  screenshots/   ← capturas de cada pantalla (referencia visual, no código)
  uploads/       ← imágenes subidas al diseño (referencia)
```

## Mapa pantalla → archivos (en `source/`)

| Pantalla | Preview HTML | Fuente (JSX/CSS) |
|---|---|---|
| **Home / Landing** | `LevelUp-ELO.html` | `landing.css`, `landing.js` |
| **Auth** (login/signup) | `Oulad Auth.html` | `auth-parts.jsx`, `auth-variations.jsx`, `auth.css` |
| **Diagnóstico** | `Oulad Diagnostico.html` | `diag-app.jsx`, `diag-parts.jsx`, `diag-data.jsx`, `diag.css` |
| **Mapa de contenido** | `Oulad Mapa.html` | `map-app.jsx`, `map-parts.jsx`, `map-data.jsx`, `map.css` |
| **Teacher Console** | `Oulad Teacher Console.html` | `teacher-shell.jsx`, `teacher-dashboard.jsx`, `teacher-groups.jsx`, `teacher-procedures.jsx`, `teacher-exams.jsx`, `teacher-export.jsx`, `teacher-data.jsx`, `teacher.css` |
| **Direcciones** (exploración de heros, el enlace `Ka3RkFi1…`) | `Direcciones.html`, `LevelUp-ELO Direcciones (standalone).html` | `directions/hero-a-arena.html`, `hero-b-editorial.html`, `hero-c-pixelquest.html`, `design-canvas.jsx` |

## Compartidos / no portables

- `landing.css` — base de estilos compartida por varias pantallas.
- `tweaks-panel.jsx`, `tweaks-config.jsx` — panel de "edit mode" de la design app
  (lo cargan Home/Diagnóstico/Mapa). **No se porta**, pero se conserva para los previews.
- `design-canvas.jsx`, `ios-frame.jsx` — andamiaje de la design app (canvas tipo Figma,
  marco iOS). **No se porta.** `ios-frame.jsx` no lo referencia ningún HTML.
- `assets/` — favicon, gifs de KatIA, logos usados por los previews.

## Assets reales de producción (sí sirven para el port)

`source/frontend/` trae assets reales pulidos por el diseño:
- `public/banners/*.png` — banners de cursos (álgebra, aritmética, cálculo, geometría, probabilidad, trigonometría)
- `public/katia/*.gif` — KatIA correcto/errores
- `public/favicon.svg`, `src/assets/hero.png`

## Borrado

Eliminados por basura: `.thumbnail`, `scraps/` (sketches `.napkin`).
