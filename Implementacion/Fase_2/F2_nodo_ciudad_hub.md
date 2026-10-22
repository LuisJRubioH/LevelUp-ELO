# Nodo: La Ciudad de las Operaciones Básicas (Hub)
**ID:** PREALG-N2-E00-CIUDAD

> **Nivel 2 — Operaciones básicas** (módulo Preálgebra). Pantalla de entrada / hub de la ciudad 3D.

> **Origen del contenido:** Desarrolla la **Página 1** del borrador fuente (verbatim: Texto 1 y los 6 carteles). Lo marcado **[NUEVO]** es autoría para el calibre (gating de carteles, storyboard, accesibilidad, JSON).

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N2-E00-CIUDAD |
| **Título visible** | La Ciudad de las Operaciones Básicas |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 2 — Operaciones básicas |
| **Tipo de nodo** | Hub / mapa del nivel (ciudad 3D con 6 edificios) |
| **Ubicación en la ruta** | Entrada del Nivel 2; precede a los 6 edificios |
| **Función pedagógica** | Presentar las 6 operaciones como espacios explorables y activar la curiosidad con un problema real por operación |
| **Objetivo de aprendizaje** | El estudiante reconoce las 6 operaciones básicas y asocia cada una con una situación cotidiana antes de profundizar |
| **Mecánica de avance** | El estudiante debe **desplegar los 6 carteles** (uno por edificio) para habilitar la entrada a los edificios |
| **Personajes** | Katia (mascota guía) |
| **Referencias de refuerzo** | E01-SUMA, E02-RESTA, E03-MULTIPLICACION, E04-DIVISION, E05-POTENCIACION, E06-RADICACION |

> **Nota de corrección:** El título interno del borrador dice "Nivel 1: Operaciones básicas"; se corrige a **Nivel 2** (Nivel 1 es Conjuntos numéricos). El cartel de Potenciación se alineó a **"empiezas con 1 bacteria"** (en vez de 2) para que coincida con el modelo del edificio E05: población(hora n) = baseⁿ; tras 3 horas hay 2³ = 8. Notación es-CO.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Descripción de la escena (verbatim del borrador)
```
El estudiante ingresa a una ciudad virtual en 3D donde hay 6 edificios, cada 
uno representando una operación. Al hacer clic en cualquier edificio se 
despliega un cartel con un problema de la vida real relacionado con la 
operación matemática. El estudiante tendrá que desplegar todos los carteles 
para poder avanzar.
```

#### 2.2 Texto de bienvenida (Texto 1 — verbatim)
**Diálogo de Katia:**
```
Hola, bienvenido a la ciudad de las operaciones básicas. Aquí podrás conocer 
cada una de las operaciones primordiales de las matemáticas, que en ámbitos 
de la vida cobran mucha importancia. Espero que te diviertas y te deseo el 
mayor de los éxitos.
```

#### 2.3 Carteles de los edificios (verbatim)

| Edificio | Operación | Cartel (problema real) |
|---|---|---|
| 1 | Suma | "Tienes 3 manzanas y tu amigo te da 2 más. ¿Cuántas tienes ahora?" |
| 2 | Resta | "Tienes 5 galletas y te comes 2. ¿Cuántas te quedan?" |
| 3 | Multiplicación | "Tienes 4 bolsas con 3 caramelos cada una. ¿Cuántos caramelos tienes en total?" |
| 4 | División | "Tienes 12 chocolates y quieres repartirlos entre 4 amigos. ¿Cuántos le tocan a cada uno?" |
| 5 | Potenciación | "Un cultivo de bacterias se duplica cada hora. Si empiezas con 1 bacteria, ¿cuántas tendrás después de 3 horas?" |
| 6 | Radicación | "Tienes un jardín cuadrado de 16 m². ¿Cuánto mide cada lado?" |

> **[NOTA — coherencia con el edificio de Radicación]** El cartel de Suma usa la misma situación de la portada (3 + 2). El de Potenciación (empieza con 2, se duplica, 3 horas) se resuelve como 2 × 2³ = 16; se modela con cuidado en E05. El de Radicación (16 m² → lado) tiene respuesta **4 m** (ver corrección en E06).

#### 2.4 Nota de ambientación (verbatim)
```
Se puede decorar el fondo detrás de los edificios con una imagen de una ciudad 
con más edificios al fondo.
```

#### 2.5 Avance [NUEVO]
**Diálogo de Katia (al desplegar los 6 carteles):**
```
¡Ya conociste las seis operaciones de la ciudad! Ahora entra a cada edificio 
cuando quieras y descúbrelas a fondo. Te recomiendo empezar por la suma.
```

---

### A3. Storyboard [NUEVO]

#### 3.1 Estado inicial
- Cámara sobre la ciudad 3D; 6 edificios con su símbolo (+, −, ×, ÷, potencia, radical). Fondo de ciudad.
- Katia da la bienvenida (Texto 1).

#### 3.2 Interacción del estudiante
1. Lee la bienvenida.
2. Hace clic en cada edificio → se despliega su cartel con el problema real.
3. Cierra el cartel; el edificio queda marcado como "explorado".
4. Al desplegar los 6, se habilita la entrada a los edificios y aparece el mensaje de avance.
5. Entra al edificio que elija (recomendado: Suma).

#### 3.3 Estados de pantalla

| Estado | Contenido | Controles | Nota |
|---|---|---|---|
| 1 — Bienvenida | Ciudad 3D + Katia + Texto 1 | Explorar | — |
| 2 — Exploración | Carteles desplegables por edificio | Clic en edificios | Contador 0/6 → 6/6 |
| 3 — Habilitado | Edificios entrables + mensaje de Katia | Entrar a un edificio | Gating cumplido |

#### 3.4 Animaciones (Framer Motion)
- Cartel: despliegue tipo "pop" desde el edificio.
- Edificio explorado: marca/brillo sutil.
- Habilitación: los 6 edificios "se encienden" al llegar a 6/6.

#### 3.5 Relación con el mapa
- Es el contenedor de los 6 nodos-edificio. Estado de cada edificio: `bloqueado` → `actual` → `completado`.
- El hub registra cuáles carteles se desplegaron (gating) y el progreso global del nivel.

---

### A4. Diferenciación por nivel [NUEVO]
| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| Orden sugerido | Forzado: Suma→Radicación | Sugerido, navegación libre | Libre |
| Carteles | Texto + ícono grande | Texto | Texto |
| Pista de avance | "Te faltan N carteles" | Contador 0/6 | Solo contador |

---

### A5. Notas pedagógicas inline [NUEVO]
**[NOTA — Activación de conocimientos previos]** Los carteles funcionan como organizadores previos situados: cada operación se ancla a una experiencia cotidiana antes de formalizarse, reduciendo la abstracción inicial.

**[NOTA — Exploración como gating motivacional]** Exigir desplegar los 6 carteles garantiza una panorámica del nivel completo antes de profundizar, sin penalización; es un gating de exploración, no de evaluación.

---

### A6. Accesibilidad [NUEVO]
- Edificios navegables por teclado; cada cartel con rol de diálogo y foco gestionado.
- Símbolos de operación con etiqueta textual ("suma", "resta"…), no solo el glifo.
- Escena 3D con alternativa 2D / descripción textual de la ciudad.
- Contraste ≥ 4.5:1.

---

### A7. Citas pedagógicas [NUEVO]
- **Organizadores previos:** Ausubel, D. (1968).
- **Aprendizaje situado:** Brown, Collins & Duguid (1989).

---

### A8. Handoff a Design [NUEVO]
**Componentes:** [componente-ciudad-3d], [componente-edificio-operacion] (×6), [componente-cartel-problema], [componente-katia-dialogo], [componente-contador-exploracion], [componente-gate-edificios].
**Tokens:** [asset-mascota:Katia], [asset-ciudad-fondo], [color-acento-morado], [color-acento-teal].
**Render bloqueante:** símbolos +, −, ×, ÷, potencia (aⁿ), radical (√); "16 m²".

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N2-E00-CIUDAD",
  "level_id": "PREALG-N2",
  "module": "Preálgebra",
  "name": "La Ciudad de las Operaciones Básicas",
  "node_type": "level_hub_3d",
  "position_in_route": "ciudad_operaciones_hub",
  "unlock_rule": "level_unlocked:PREALG-N2",
  "previous_node_id": null,
  "next_node_id": "PREALG-N2-E01-SUMA-JUNTAR",
  "order": 0,
  "safe_zone": true,
  "affects_elo": false,
  "characters": { "guide": "Katia" },

  "welcome_text": "Hola, bienvenido a la ciudad de las operaciones básicas. Aquí podrás conocer cada una de las operaciones primordiales de las matemáticas, que en ámbitos de la vida cobran mucha importancia. Espero que te diviertas y te deseo el mayor de los éxitos.",

  "buildings": [
    { "id": "E01", "operation": "suma", "node_id": "PREALG-N2-E01-SUMA-JUNTAR", "card": "Tienes 3 manzanas y tu amigo te da 2 más. ¿Cuántas tienes ahora?" },
    { "id": "E02", "operation": "resta", "node_id": "PREALG-N2-E02-RESTA-QUITAR", "card": "Tienes 5 galletas y te comes 2. ¿Cuántas te quedan?" },
    { "id": "E03", "operation": "multiplicacion", "node_id": "PREALG-N2-E03-MULTIPLICACION-AGRUPAR", "card": "Tienes 4 bolsas con 3 caramelos cada una. ¿Cuántos caramelos tienes en total?" },
    { "id": "E04", "operation": "division", "node_id": "PREALG-N2-E04-DIVISION-REPARTIR", "card": "Tienes 12 chocolates y quieres repartirlos entre 4 amigos. ¿Cuántos le tocan a cada uno?" },
    { "id": "E05", "operation": "potenciacion", "node_id": "PREALG-N2-E05-POTENCIACION-CRECER", "card": "Un cultivo de bacterias se duplica cada hora. Si empiezas con 1 bacteria, ¿cuántas tendrás después de 3 horas?" },
    { "id": "E06", "operation": "radicacion", "node_id": "PREALG-N2-E06-RADICACION-RAIZ", "card": "Tienes un jardín cuadrado de 16 m². ¿Cuánto mide cada lado?" }
  ],

  "gating": {
    "rule": "all_cards_opened",
    "cards_required": 6,
    "note": "Desplegar los 6 carteles habilita la entrada a los edificios; sin penalización (exploración)"
  },

  "events_to_register": ["hub_viewed","card_opened","all_cards_opened","building_entered","level_progress_updated"],

  "level_presentation": {
    "basico": { "navigation": "forced_order", "hint": "remaining_cards" },
    "intermedio": { "navigation": "suggested_order", "hint": "counter" },
    "avanzado": { "navigation": "free", "hint": "counter" }
  },

  "persistence_required": ["hub_viewed","cards_opened","buildings_completed","level_progress"],
  "persistence_excluded": ["elo_score"],

  "design_handoff": {
    "components_required": ["[componente-ciudad-3d]","[componente-edificio-operacion]","[componente-cartel-problema]","[componente-katia-dialogo]","[componente-contador-exploracion]","[componente-gate-edificios]"],
    "design_tokens": ["[asset-mascota:Katia]","[asset-ciudad-fondo]","[color-acento-morado]","[color-acento-teal]"],
    "render_blocker": "Verificar render de símbolos +, −, ×, ÷, aⁿ, √ y '16 m²'"
  },

  "i18n_prefix": "prealgebra.n2.e00"
}
```

---

## Notas finales
Verbatim del borrador: escena, Texto 1, los 6 carteles, nota de ambientación. **[NUEVO]:** gating explícito, storyboard, diferenciación, accesibilidad, citas, handoff, JSON. **Corrección:** "Nivel 1" → "Nivel 2".
