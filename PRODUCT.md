# Product

## Register

product

## Users

Estudiantes de matemáticas en Colombia (semillero matemático de grado 9-11, colegio y
universidad) que practican de forma adaptativa, normalmente desde el celular, en sesiones
cortas dentro o fuera del aula. Docentes que revisan el progreso del grupo desde un
dashboard de escritorio. El estudiante llega buscando el reto justo para su nivel — ni tan
fácil que aburra, ni tan difícil que frustre — y una tutora (KatIA) que lo guía sin darle la
respuesta directa.

## Product Purpose

Plataforma educativa adaptativa: un motor ELO vectorial por tópico calibra la dificultad de
cada pregunta al nivel real del estudiante, con selección por Zona de Desarrollo Próximo.
KatIA (tutora socrática) acompaña sin revelar soluciones. Éxito = el estudiante vuelve a
practicar (racha), sube de rango con consistencia, y los docentes detectan a tiempo dónde
un estudiante se está quedando atrás.

## Brand Personality

Adaptativo, lúdico-culto, riguroso. El "lúdico-culto" se expresa en el storytelling de los
niveles de Preálgebra: cada nivel grande vive en su propio escenario mitológico/histórico
(el ágora griega para operaciones y propiedades, El Puerto de la Polis para divisibilidad)
narrado por KatIA, una gata cyborg — gamificado pero con contenido curricularmente serio,
nunca infantil ni genérico.

## Anti-references

Gradientes morados decorativos. Tarjetas anidadas ("Cardocalypse"). Inter sin jerarquía
tipográfica. Bajo contraste sobre fondos oscuros (el tema por defecto es oscuro, #0A0A0F).
Look de SaaS corporativo genérico — esto es una plataforma gamificada con identidad propia,
no un dashboard B2B anónimo. Ejemplos/contextos de una sola nota temática repetidos sin
variedad dentro de un mismo nivel (corregido explícitamente en N3→N4: "como que no
existiera más cosas en la antigua Grecia").

## Design Principles

- Cada componente nuevo necesita al menos una decisión de diseño no genérica (tipografía,
  espaciado, acento o animación de entrada) — nunca el default de una librería sin ajustar.
- La animación tiene función pedagógica, no decorativa: logros (scale+opacity), delta de
  ELO (número animado visible), timer bajo cierto umbral (pulso visual). Nunca movimiento
  porque sí.
- El storytelling y el rigor matemático conviven sin pisarse: el lore (mundo narrativo)
  nunca debe oscurecer ni contradecir el guión pedagógico de la pantalla (qué se está
  enseñando, en qué orden, con qué ejemplos) — es telón de fondo, no el foco.
- Estudiante → mobile-first (375px). Docente → desktop-first (1280px), datos antes que
  decoración (gráficos ELO/radar antes que acciones, sin cards grandes con iconos
  decorativos).
- LaTeX siempre renderizado (react-katex), nunca texto plano con expresiones matemáticas.

## Accessibility & Inclusion

ARIA ya integrado en varias vistas (`aria-label`, `aria-pressed`, `aria-live`,
`role="dialog"`, `role="timer"`). Bilingüe es/en vía i18next con detección de localStorage.
Tema claro/oscuro con inversión de paleta vía CSS vars (sin FOUC). Sin requisitos WCAG
formales documentados aún — tratar AA como piso razonable (contraste ≥4.5:1 en texto de
cuerpo) dado el fondo oscuro por defecto.
