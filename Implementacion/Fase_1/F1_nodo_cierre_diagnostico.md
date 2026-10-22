# Nodo: Cierre diagnóstico del nivel
**ID:** PREALG-N1-B13-CIERRE-DIAGNOSTICO

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N1-B13-CIERRE-DIAGNOSTICO |
| **Título visible** | Diagnóstico del nivel |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 1 — Conjuntos numéricos |
| **Tipo de nodo** | Nodo circular final de cierre, diagnóstico y recomendación |
| **Ubicación en la ruta** | Último nodo; se desbloquea al completar B12 (Detective de Falsedades). `next_node_id = null` |
| **Función pedagógica** | Cerrar el recorrido con una síntesis formativa del desempeño: fortalezas, dificultades recurrentes y rutas de refuerzo recomendadas |
| **Objetivo de aprendizaje** | El estudiante recibe una lectura clara de su progreso: qué domina, qué reforzar y qué pantallas revisar |
| **Microhabilidades (evaluadas por agregación)** | • Reconocer ℕ, ℤ, ℚ, irracionales, ℝ, ℂ<br>• Aplicar la convención 0 ∈ ℕ<br>• Representar deudas con enteros negativos<br>• Interpretar fracciones como reparto y división<br>• Diferenciar decimales exactos, periódicos e infinitos no periódicos<br>• Distinguir racionales e irracionales<br>• Reconocer reales como números de la recta<br>• Reconocer complejos como números del plano<br>• Diferenciar conjunto más específico y pertenencia múltiple<br>• Evaluar afirmaciones de inclusión |
| **Misconception tags (consolidados)** | excluye_cero_de_naturales_pese_a_convencion<br>confunde_deuda_con_cantidad_positiva<br>no_interpreta_fraccion_como_division<br>clasifica_decimal_periodico_como_irracional<br>confunde_aproximacion_con_valor_exacto<br>no_reconoce_irracionales_como_reales<br>ubica_complejos_no_reales_en_recta_real<br>marca_solo_conjunto_mas_especifico<br>no_reconoce_pertenencia_multiple<br>confunde_implicacion_con_reciproca |
| **Referencias de refuerzo** | B04, B05, B06, B07, B08, B09, B10, B11, B12 (todo el nivel) |

> **Nota de migración (KaTeX):** En el .docx fuente, las expresiones quedaron como corchetes/paréntesis vacíos. Se restauraron: la convención 0 ∈ ℕ, la equivalencia de fracción 3/4 = 3 ÷ 4, los ejemplos 2i y 3 + 2i, y 5 como ejemplo de pertenencia múltiple, a partir del contexto y la sección JSON técnico del propio documento.

> **Nota de gating:** Las tarjetas de refuerzo y la ruta de repaso que apuntan a complejos (B09) solo se generan si el estudiante exploró la rama compleja (`explored_complex_branch = true`). Para banda Básico, el diagnóstico se construye sobre ℕ→ℝ y la omisión de complejos **no** cuenta como dificultad ni penaliza el cierre (callejón opcional, sin penalización).

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Encabezado

**Texto visible:**
```
Diagnóstico del nivel
```

**Subtítulo:**
```
Terminaste el recorrido por conjuntos numéricos.
```

---

#### 2.2 Mensaje inicial de Katia

**Contexto visual:** Katia aparece junto al mapa completo del nivel.

**Diálogo de Katia:**
```
Llegaste al final del Nivel 1: Conjuntos numéricos.

Durante el recorrido trabajaste con naturales, enteros, racionales, 
irracionales, reales y complejos.

Ahora vamos a revisar cómo te fue y qué conviene reforzar antes de seguir 
avanzando.
```

---

#### 2.3 Resumen de progreso

**Título visible:**
```
Tu progreso
```

**Elementos visibles sugeridos:**
- Nodos completados.
- Actividades realizadas.
- Tiempo total aproximado.
- Intentos usados.
- Pistas consultadas.
- Correcciones realizadas después de retroalimentación.

**Ejemplo de visualización:**

| Indicador | Resultado |
|-----------|-----------|
| Pantallas completadas | 13 de 13 |
| Actividades formativas | 9 |
| Tiempo aproximado | 28 min |
| Correcciones realizadas | 6 |
| Pistas consultadas | 2 |

**Nota visible:**
```
Este resultado es formativo. No modifica tu ELO.
```

---

#### 2.4 Resultado general

**Título visible:**
```
Resultado general
```

**Texto visible según desempeño:**

##### Caso 1 — Desempeño alto
```
Terminaste el nivel con buen dominio general.

Reconoces los principales conjuntos numéricos y puedes distinguir entre 
clasificación básica, pertenencia múltiple e inclusión entre conjuntos.
```

##### Caso 2 — Desempeño medio
```
Terminaste el nivel y corregiste varios errores durante el recorrido.

Conviene reforzar algunos conceptos antes de pasar a actividades externas 
al mapa.
```

##### Caso 3 — Desempeño con errores persistentes
```
Terminaste el recorrido, pero aparecen dificultades recurrentes en varios 
conceptos.

Antes de avanzar, es recomendable revisar las pantallas sugeridas y practicar 
de nuevo.
```

> **[NOTA — lenguaje de crecimiento]** El Caso 3 evita el rótulo "desempeño bajo" del borrador original; se reformula como "errores persistentes" + invitación a practicar. El cierre nunca debe sentirse punitivo (coherente con la zona segura).

---

#### 2.5 Conceptos dominados

**Título visible:**
```
Conceptos que dominas
```

**Texto visible:**
```
Estos son los conceptos en los que mostraste buen desempeño durante el nivel.
```

**Ejemplos de tarjetas posibles:**
- Naturales y conteo.
- Enteros y deudas.
- Fracciones como reparto.
- Decimales exactos y periódicos.
- Irracionales como decimales infinitos no periódicos.
- Reales como números de la recta.
- Complejos como números del plano. *(solo si exploró la rama compleja)*
- Clasificación por conjunto más específico.
- Pertenencia múltiple.

**Regla de aparición:**
```
Una tarjeta aparece en "conceptos dominados" si el estudiante resolvió 
correctamente las interacciones asociadas o corrigió el error después de una 
retroalimentación sin volver a fallar en el mismo patrón.
```

---

#### 2.6 Conceptos para reforzar

**Título visible:**
```
Conceptos para reforzar
```

**Texto visible:**
```
Estos son los puntos que conviene revisar porque aparecieron errores o dudas 
durante el recorrido.
```

**Tarjetas de refuerzo (se generan según los errores detectados):**

##### Refuerzo: naturales
- **Concepto:** Convención 0 ∈ ℕ
- **Mensaje visible:**
  ```
  Revisa la convención del nivel: aquí consideramos que 0 pertenece a los 
  números naturales.
  ```
- **Pantalla recomendada:** Volver a "Naturales: contar cantidades completas".

##### Refuerzo: enteros
- **Concepto:** Deudas como números negativos
- **Mensaje visible:**
  ```
  Cuando una cantidad representa deuda, la ubicamos por debajo de cero.
  ```
- **Pantalla recomendada:** Volver a "Enteros: deudas y saldos".

##### Refuerzo: racionales
- **Concepto:** Fracción como división
- **Mensaje visible:**
  ```
  Una fracción como 3/4 también significa 3 ÷ 4.
  ```
- **Pantalla recomendada:** Volver a "Racionales: repartir, fraccionar y dividir".

##### Refuerzo: irracionales
- **Concepto:** Decimal periódico vs. decimal no periódico
- **Mensaje visible:**
  ```
  Un decimal infinito no siempre es irracional. Si repite un patrón, es racional.
  ```
- **Pantalla recomendada:** Volver a "Irracionales: decimales que no se repiten".

##### Refuerzo: reales
- **Concepto:** Irracionales dentro de los reales
- **Mensaje visible:**
  ```
  Los irracionales no son racionales, pero sí pertenecen a los reales.
  ```
- **Pantalla recomendada:** Volver a "Reales: todos los números de la recta".

##### Refuerzo: complejos *(solo con rama compleja)*
- **Concepto:** Recta real y plano complejo
- **Mensaje visible:**
  ```
  Números como 2i o 3 + 2i pertenecen al plano complejo, no a la recta real.
  ```
- **Pantalla recomendada:** Volver a "Complejos: números en el plano".

##### Refuerzo: pertenencia múltiple
- **Concepto:** Un número puede pertenecer a varios conjuntos
- **Mensaje visible:**
  ```
  Por ejemplo, 5 es natural, entero, racional, real y complejo.
  ```
- **Pantalla recomendada:** Volver a "El Clasificador II: pertenencia múltiple".

---

#### 2.7 Ruta de repaso recomendada

**Título visible:**
```
Ruta de repaso recomendada
```

**Texto visible:**
```
Según tus respuestas, esta es la ruta sugerida para reforzar el nivel.
```

**Ejemplo de ruta generada:**
- Volver a "Racionales: repartir, fraccionar y dividir".
- Volver a "Irracionales: decimales que no se repiten".
- Repetir "El Clasificador II: pertenencia múltiple".
- Repetir "El Detective de Falsedades".

**Regla:**
```
La ruta debe mostrar máximo 4 recomendaciones para no saturar al estudiante.
```

---

#### 2.8 Resumen para el docente

**Título visible para estudiante:**
```
Señales registradas para acompañamiento
```

**Texto visible:**
```
Algunas dificultades pueden quedar marcadas para que tu docente sepa en qué 
ayudarte.
```

**Versión visible al estudiante:**
```
No es una sanción. Es una forma de saber qué tema necesita más apoyo.
```

**Versión para panel docente:** El sistema expone los patrones relevantes en el panel docente, indicando: estudiante, nivel, concepto afectado, microhabilidad, patrón de error, bloque donde ocurrió, frecuencia, nivel de alerta y recomendación de intervención.

---

#### 2.9 Insignia o cierre visual

**Título visible:**
```
Nivel completado
```

**Texto visible:**
```
Completaste el Nivel 1: Conjuntos numéricos.
```

**Insignia sugerida:**
```
Explorador de conjuntos numéricos
```

**Diálogo de Katia:**
```
Buen trabajo. Ahora tienes una base para reconocer qué tipo de número 
necesitas según el problema.

Puedes repasar las pantallas recomendadas o continuar cuando tu docente 
habilite el siguiente nivel.
```

---

#### 2.10 Botones finales

**Botones visibles:**
- Volver al mapa.
- Repasar recomendaciones.
- Repetir clasificador.
- Continuar al siguiente nivel.

**Regla sobre "Continuar al siguiente nivel":**
```
El botón solo debe aparecer activo si el siguiente nivel está habilitado para 
el estudiante.
```

---

### A3. Storyboard — Flujo visual y de interacción

#### 3.1 Estado inicial

**Contexto del mapa:**
- El mapa enfoca el nodo PREALG-N1-B13-CIERRE-DIAGNOSTICO.
- El nodo aparece en estado `actual` tras completar el Detective de Falsedades (B12).
- Un hexágono de transición aparece **antes** del nodo:
  ```
  De evaluación formativa a diagnóstico
  ```

---

#### 3.2 Entrada de elementos (Secuencia visual)

1. Aparece el título "Diagnóstico del nivel".
2. Katia felicita al estudiante por completar el recorrido.
3. Se muestra el mapa del nivel con todos los nodos completados.
4. Aparece el resumen de progreso.
5. Se muestran los conceptos dominados.
6. Se muestran los conceptos para reforzar.
7. Se genera la ruta de repaso recomendada.
8. Se muestra la insignia del nivel.
9. Aparecen los botones finales.

---

#### 3.3 Interacción del estudiante (Fase de actividad)

El estudiante puede:

1. **Ver su resumen de progreso.**
2. **Revisar conceptos dominados.**
3. **Revisar conceptos para reforzar.**
4. **Abrir una recomendación de repaso.**
5. **Volver a una pantalla sugerida.**
6. **Repetir el clasificador.**
7. **Volver al mapa.**
8. **Continuar al siguiente nivel** si está habilitado.

---

#### 3.4 Estados de pantalla (Evolución visual)

| Estado | Contenido visible | Controles activos | Nota |
|---|---|---|---|
| **1 — Cierre** | Mensaje de finalización del nivel | Lectura | Apertura emocional positiva |
| **2 — Resumen** | Progreso, tiempo, actividades, correcciones | Lectura | Síntesis cuantitativa formativa |
| **3 — Diagnóstico** | Conceptos dominados + conceptos para reforzar | Abrir tarjetas | Síntesis cualitativa |
| **4 — Recomendaciones** | Ruta de repaso (máx. 4) | Abrir recomendación / navegar | Acción sugerida |
| **5 — Insignia** | Insignia "Explorador de conjuntos numéricos" | Lectura | Refuerzo motivacional |
| **6 — Acciones finales** | Botones: repasar / volver al mapa / repetir / continuar | Navegación | Cierre del nivel |

---

#### 3.5 Eventos visuales y animaciones (Framer Motion)

- **Entrada del nodo:** Fade-in del título y hexágono de transición.
- **Mapa completo:** Animación que recorre los 13 nodos marcándolos como completados (stagger).
- **Resumen de progreso:** Contadores que animan de 0 al valor final.
- **Tarjetas dominadas:** Entran con fade-in verde suave.
- **Tarjetas de refuerzo:** Entran con acento ámbar (no rojo, para no penalizar).
- **Ruta de repaso:** Las recomendaciones se conectan al mapa con líneas sutiles.
- **Insignia:** Aparece con una animación de "logro" (escala + brillo), sin sonido intrusivo.
- **Estado final del mapa:** Los nodos con refuerzo quedan con marca visual secundaria.

---

#### 3.6 Relación con el mapa visual

**Nodo circular final:** Representa el cierre diagnóstico.

**Punticos internos (eventos registrados):**
- Visualizó resumen de progreso
- Visualizó conceptos dominados
- Visualizó refuerzos sugeridos
- Abrió ruta de repaso
- Abrió recomendación específica
- Recibió insignia
- Completó nivel

**Estado final del mapa:** Todos los nodos del Nivel 1 quedan marcados como completados. Los nodos con refuerzo sugerido pueden quedar con un estado visual secundario:
- `completed_with_review_suggested`
- `completed_with_teacher_attention`
- `completed_strong`

**Hexágono posterior:** No aplica — es el nodo final del nivel (`next_node_id = null`). La salida es hacia el mapa o el siguiente nivel (si está habilitado).

---

### A4. Diferenciación por nivel (Básico / Intermedio / Avanzado)

| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| **Alcance del diagnóstico** | ℕ→ℝ (sin complejos) | ℕ→ℂ completo | ℕ→ℂ completo |
| **Tarjetas/ruta de complejos** | No se generan | Se generan si hubo errores | Se generan si hubo errores |
| **Resultado general** | Lenguaje más concreto y alentador | Estándar | Estándar + sugerencia de reto opcional |
| **Ruta de repaso** | Prioriza microhabilidades base | Equilibrada | Puede incluir variantes de reto (vía Pitágoras, filas difíciles) |
| **Insignia** | Misma para todos | Misma | Misma + posible mención de exploración compleja |

> El alcance del diagnóstico depende de la banda y del flag `explored_complex_branch`, no del rendimiento. Omitir complejos (Básico) nunca cuenta como dificultad.

---

### A5. Notas pedagógicas inline

**[NOTA PEDAGÓGICA — Diagnóstico formativo, no sumativo]**
El cierre consolida eventos formativos sin tocar el ELO (zona segura). Su función es **evaluación para el aprendizaje**: decirle al estudiante qué domina y qué revisar, con rutas accionables (Black & Wiliam, 1998; Hattie & Timperley, 2007). No es una calificación.

**[NOTA PEDAGÓGICA — Lenguaje de crecimiento]**
El resultado general reformula el "desempeño bajo" como "errores persistentes + invitación a practicar". Esto sostiene la motivación intrínseca y evita el marco de fracaso, coherente con la autonomía/competencia de la zona segura.

**[NOTA PEDAGÓGICA — Alertas en tres niveles, sin sobre-escalar]**
Las reglas de dominio distinguen cuatro estados (dominado → revisión sugerida → refuerzo necesario → intervención docente). La intervención docente requiere errores en **varios** patrones y persistencia tras feedback, no un fallo aislado. Las alertas son hipótesis de diseño para el piloto, no datos calibrados (Arnold & Pistilli, 2012).

**[NOTA PEDAGÓGICA — Límite de 4 recomendaciones]**
La ruta de repaso se topa en 4 ítems para no sobrecargar la memoria de trabajo ni desmotivar (Sweller, 1988). Prioriza microhabilidades base que condicionan bloques posteriores.

---

### A6. Accesibilidad

- **Resumen y tarjetas:** Estructura semántica; tarjetas dominadas/refuerzo distinguibles por ícono y etiqueta, no solo por color (verde/ámbar).
- **Mapa completo:** Alternativa textual que liste el estado de cada nodo.
- **Matemática:** Expresiones (0 ∈ ℕ, 3/4 = 3 ÷ 4, 2i, 3 + 2i, 5) con KaTeX y MathML/`aria-label`.
- **Insignia:** Texto alternativo descriptivo; el logro se anuncia por lector de pantalla.
- **Botones finales:** Foco navegable por teclado; "Continuar" deshabilitado se anuncia como tal.
- **Contraste:** Mínimo 4.5:1, también en modo oscuro.

---

### A7. Notas de citas pedagógicas

- **Evaluación para el aprendizaje; diagnóstico formativo:** Black, P., & Wiliam, D. (1998). Inside the black box; Hattie, J., & Timperley, H. (2007). The power of feedback.
- **Analítica de aprendizaje; alertas tempranas con retroalimentación individualizada:** Arnold, K. E., & Pistilli, M. D. (2012). Course Signals at Purdue.
- **Carga cognitiva; límite de recomendaciones:** Sweller, J. (1988). Cognitive load during problem solving.
- **Zona segura sin ELO; autonomía/competencia/relación:** Deci, E. L., & Ryan, R. M. Self-Determination Theory.
- **Gamificación con propósito (insignia significativa, no vacía):** Huang, R., et al. (2024); Kurnaz, F. (2025).

---

### A8. Handoff a Claude Design

**Componentes clave:**
- [componente-katia-dialogo] — apertura y cierre
- [componente-mapa-nivel-completo] — mapa con los 13 nodos y sus estados
- [componente-resumen-progreso] — tabla/tarjetas de indicadores con contadores animados
- [componente-resultado-general] — bloque de texto por caso de desempeño
- [componente-tarjeta-concepto-dominado]
- [componente-tarjeta-refuerzo] — concepto + mensaje + pantalla recomendada
- [componente-ruta-repaso] — lista de máx. 4 recomendaciones enlazadas al mapa
- [componente-resumen-docente] — versión estudiante + payload para panel docente
- [componente-insignia] — "Explorador de conjuntos numéricos"
- [componente-nav-inferior] — botones finales

**Gating:**
- [flag-explored_complex_branch] — Controla generación de tarjetas/ruta de complejos

**Tokens del sistema de diseño:**
- [asset-mascota:Katia], [asset-insignia:explorador-conjuntos], [color-acento-morado], [color-acento-teal], [color-dominado-verde], [color-refuerzo-ambar], [tipografia-titulo], [tipografia-body]

**Render bloqueante:**
- Verificar render de: 0 ∈ ℕ, 3/4 = 3 ÷ 4, 2i, 3 + 2i, 5, y los estados de nodo del mapa.
- **Crítico:** El mapa completo y los botones finales deben ser responsivos y accesibles en móvil; el botón "Continuar al siguiente nivel" respeta su estado habilitado/deshabilitado.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N1-B13-CIERRE-DIAGNOSTICO",
  "level_id": "PREALG-N1",
  "module": "Preálgebra",
  "name": "Diagnóstico del nivel",
  "display_title": "Diagnóstico del nivel",
  "node_type": "final_formative_diagnostic",
  "map_shape": "circle",
  "position_in_route": "ruta_nucleo_cierre_final",
  "unlock_rule": "completed_node:PREALG-N1-B12-DETECTIVE-FALSEDADES",
  "previous_node_id": "PREALG-N1-B12-DETECTIVE-FALSEDADES",
  "next_node_id": null,
  "order": 13,
  "skip_penalty": false,
  "node_state": "bloqueado",
  "is_safe_zone": true,
  "safe_zone": true,
  "affects_elo": false,
  "concept": "Cierre diagnóstico de conjuntos numéricos",
  "general_tag": "Preálgebra",
  "specific_tag": "Conjuntos numéricos",

  "gating": {
    "flag": "explored_complex_branch",
    "affects": "Tarjetas de refuerzo y ruta de repaso de complejos (B09) solo si flag=true",
    "note": "Banda Básico: diagnóstico sobre ℕ→ℝ; omitir complejos no cuenta como dificultad ni penaliza el cierre"
  },

  "consolidates": [
    "progreso_del_estudiante", "tiempo_estimado", "actividades_completadas",
    "intentos", "uso_de_pistas", "correcciones", "errores_por_microhabilidad",
    "misconceptions_persistentes", "recomendaciones_de_repaso",
    "alertas_individuales_y_grupales"
  ],

  "progress_summary_fields": [
    "completed_nodes", "total_nodes", "formative_activities_completed",
    "estimated_time_seconds", "corrections_made", "hints_used"
  ],

  "overall_result_cases": {
    "high": {
      "status": "completed_strong",
      "text": "Terminaste el nivel con buen dominio general.\nReconoces los principales conjuntos numéricos y puedes distinguir entre clasificación básica, pertenencia múltiple e inclusión entre conjuntos."
    },
    "medium": {
      "status": "completed_with_review_suggested",
      "text": "Terminaste el nivel y corregiste varios errores durante el recorrido.\nConviene reforzar algunos conceptos antes de pasar a actividades externas al mapa."
    },
    "persistent_errors": {
      "status": "completed_with_teacher_attention",
      "text": "Terminaste el recorrido, pero aparecen dificultades recurrentes en varios conceptos.\nAntes de avanzar, es recomendable revisar las pantallas sugeridas y practicar de nuevo."
    }
  },

  "diagnostic_payload_schema": {
    "student_id": "student_uuid",
    "level_id": "PREALG-N1",
    "completed_nodes": 13,
    "total_nodes": 13,
    "estimated_time_seconds": 1680,
    "formative_activities_completed": 9,
    "hints_used": 2,
    "corrections_made": 6,
    "overall_status": "completed_with_review_suggested",
    "mastered_concepts": [
      {
        "concept": "Números naturales",
        "micro_skill": "reconocer_numeros_naturales",
        "evidence": ["PREALG-N1-B04-Q04", "PREALG-N1-B10-Q01"]
      }
    ],
    "review_suggestions": [
      {
        "concept": "Decimales periódicos",
        "micro_skill": "diferenciar_decimal_periodico_no_periodico",
        "reason": "El estudiante clasificó un decimal periódico como irracional.",
        "recommended_node_id": "PREALG-N1-B07-IRRACIONALES-DECIMALES",
        "priority": "medium"
      }
    ],
    "teacher_alerts": [
      {
        "level": "refuerzo_sugerido",
        "concept": "Pertenencia múltiple",
        "micro_skill": "reconocer_pertenencia_multiple",
        "reason": "El estudiante marcó solo el conjunto más específico en la clasificación rigurosa.",
        "source_nodes": ["PREALG-N1-B11-CLASIFICADOR-RIGUROSO", "PREALG-N1-B12-DETECTIVE-FALSEDADES"]
      }
    ]
  },

  "mastery_rules": {
    "mastered": {
      "label": "mastered",
      "criteria": "Responde correctamente las actividades asociadas, O comete un error inicial, recibe feedback y corrige sin repetir el patrón en bloques posteriores."
    },
    "review_suggested": {
      "label": "review_suggested",
      "criteria": "Comete un error puntual pero lo corrige, O usa pista para completar, O muestra duda en una sola microhabilidad."
    },
    "needs_reinforcement": {
      "label": "needs_reinforcement",
      "criteria": "Repite el mismo error en dos o más bloques, O necesita más de dos intentos, O falla tras feedback, O mantiene el mismo misconception_tag en actividades distintas."
    },
    "teacher_intervention": {
      "label": "teacher_intervention_recommended",
      "criteria": "Mantiene errores en varios patrones conceptuales, O no corrige tras feedback, O falla en microhabilidades base que afectan bloques posteriores."
    }
  },

  "review_route": {
    "max_recommendations": 4,
    "rule": "Mostrar máximo 4 recomendaciones, priorizando microhabilidades base; no saturar al estudiante",
    "example": [
      "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION",
      "PREALG-N1-B07-IRRACIONALES-DECIMALES",
      "PREALG-N1-B11-CLASIFICADOR-RIGUROSO",
      "PREALG-N1-B12-DETECTIVE-FALSEDADES"
    ]
  },

  "reinforcement_cards": [
    {"concept": "Convención 0 ∈ ℕ", "message": "Revisa la convención del nivel: aquí consideramos que 0 pertenece a los números naturales.", "recommended_node_id": "PREALG-N1-B04-NATURALES-CONTAR"},
    {"concept": "Deudas como negativos", "message": "Cuando una cantidad representa deuda, la ubicamos por debajo de cero.", "recommended_node_id": "PREALG-N1-B05-ENTEROS-DEUDA"},
    {"concept": "Fracción como división", "message": "Una fracción como 3/4 también significa 3 ÷ 4.", "recommended_node_id": "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION"},
    {"concept": "Decimal periódico vs no periódico", "message": "Un decimal infinito no siempre es irracional. Si repite un patrón, es racional.", "recommended_node_id": "PREALG-N1-B07-IRRACIONALES-DECIMALES"},
    {"concept": "Irracionales dentro de los reales", "message": "Los irracionales no son racionales, pero sí pertenecen a los reales.", "recommended_node_id": "PREALG-N1-B08-REALES-RECTA"},
    {"concept": "Recta real y plano complejo", "message": "Números como 2i o 3 + 2i pertenecen al plano complejo, no a la recta real.", "recommended_node_id": "PREALG-N1-B09-COMPLEJOS-PLANO", "requires_flag": "explored_complex_branch"},
    {"concept": "Pertenencia múltiple", "message": "Por ejemplo, 5 es natural, entero, racional, real y complejo.", "recommended_node_id": "PREALG-N1-B11-CLASIFICADOR-RIGUROSO"}
  ],

  "teacher_panel_fields": [
    "estudiante", "nivel", "concepto_afectado", "microhabilidad",
    "patron_de_error", "bloque_donde_ocurrio", "frecuencia",
    "nivel_de_alerta", "recomendacion_de_intervencion"
  ],

  "badge": {
    "title": "Nivel completado",
    "label": "Explorador de conjuntos numéricos",
    "asset": "[asset-insignia:explorador-conjuntos]"
  },

  "final_buttons": [
    {"id": "back_to_map", "label": "Volver al mapa", "always_enabled": true},
    {"id": "review_recommendations", "label": "Repasar recomendaciones", "always_enabled": true},
    {"id": "repeat_classifier", "label": "Repetir clasificador", "always_enabled": true},
    {"id": "continue_next_level", "label": "Continuar al siguiente nivel", "enabled_if": "next_level_unlocked_for_student"}
  ],

  "final_map_states": [
    "completed_strong",
    "completed_with_review_suggested",
    "completed_with_teacher_attention"
  ],

  "events_to_register": [
    "node_viewed",
    "progress_summary_viewed",
    "mastered_concepts_viewed",
    "reinforcement_concepts_viewed",
    "review_route_opened",
    "specific_recommendation_opened",
    "badge_received",
    "level_completed",
    "navigation_action"
  ],

  "alert_conditions": [
    {
      "condition_id": "ALERT_OBSERVATION_REVIEW_SUGGESTED",
      "level": "observation",
      "trigger": "Diagnostic aggregates isolated, corrected errors",
      "message_educator": "El estudiante completó el nivel corrigiendo errores puntuales. Se sugiere revisión ligera de las pantallas indicadas; no requiere intervención."
    },
    {
      "condition_id": "ALERT_REINFORCEMENT_PERSISTENT_TAG",
      "level": "reinforcement_suggested",
      "trigger": "Same misconception_tag persists across 2+ blocks",
      "message_educator": "El estudiante mantiene un mismo patrón de error en varios bloques. Se recomienda reforzar el concepto asociado antes de habilitar el siguiente nivel."
    },
    {
      "condition_id": "ALERT_INTERVENTION_MULTI_PATTERN",
      "level": "teacher_intervention",
      "trigger": "Errors persist after feedback across 3+ conceptual patterns or in base micro-skills",
      "message_educator": "El estudiante presenta dificultades amplias y persistentes que afectan microhabilidades base. Se recomienda intervención docente antes de avanzar de nivel."
    }
  ],

  "persistence_required": [
    "node_viewed", "progress_summary", "mastered_concepts", "review_suggestions",
    "review_route_opened", "recommendations_opened", "badge_received",
    "overall_status", "teacher_alerts", "time_on_node", "level_completed"
  ],
  "persistence_excluded": ["elo_score"],

  "level_presentation": {
    "basico": {
      "diagnostic_scope": "N_to_R",
      "generate_complex_cards": false,
      "result_language": "concrete_encouraging",
      "review_route_priority": "base_micro_skills"
    },
    "intermedio": {
      "diagnostic_scope": "N_to_C",
      "generate_complex_cards": true,
      "result_language": "standard",
      "review_route_priority": "balanced"
    },
    "avanzado": {
      "diagnostic_scope": "N_to_C",
      "generate_complex_cards": true,
      "result_language": "standard_plus_challenge",
      "review_route_priority": "may_include_challenge_variants"
    }
  },

  "design_handoff": {
    "node_state": "bloqueado|actual|completado",
    "path_position": "ruta_nucleo_cierre_final",
    "gating_flag": "explored_complex_branch",
    "components_required": [
      "[componente-katia-dialogo]",
      "[componente-mapa-nivel-completo]",
      "[componente-resumen-progreso]",
      "[componente-resultado-general]",
      "[componente-tarjeta-concepto-dominado]",
      "[componente-tarjeta-refuerzo]",
      "[componente-ruta-repaso]",
      "[componente-resumen-docente]",
      "[componente-insignia]",
      "[componente-nav-inferior]"
    ],
    "design_tokens": [
      "[asset-mascota:Katia]",
      "[asset-insignia:explorador-conjuntos]",
      "[color-acento-morado]",
      "[color-acento-teal]",
      "[color-dominado-verde]",
      "[color-refuerzo-ambar]",
      "[tipografia-titulo]",
      "[tipografia-body]"
    ],
    "render_blocker": "Verificar render de: 0 ∈ ℕ, 3/4 = 3 ÷ 4, 2i, 3 + 2i, 5, estados de nodo del mapa; mapa completo y botones finales responsivos y accesibles en móvil; botón 'Continuar' respeta estado habilitado/deshabilitado"
  },

  "i18n_prefix": "prealgebra.n1.b13"
}
```

---

## Notas finales

Este documento preserva **todo el guión íntegro** de B13 (Cierre diagnóstico del nivel):
- ✅ Texto completo de Katia (apertura + cierre)
- ✅ Resumen de progreso con tabla de indicadores
- ✅ Resultado general por los 3 casos de desempeño (con lenguaje de crecimiento)
- ✅ Conceptos dominados con regla de aparición
- ✅ Las 7 tarjetas de refuerzo (concepto + mensaje + pantalla recomendada)
- ✅ Ruta de repaso recomendada (máx. 4)
- ✅ Resumen docente (versión estudiante + panel docente)
- ✅ Insignia y botones finales
- ✅ Storyboard detallado con 6 estados de pantalla
- ✅ **Reglas de dominio en 4 niveles** (mastered → review_suggested → needs_reinforcement → teacher_intervention)
- ✅ **Gating de complejos** sin penalización por omisión
- ✅ JSON técnico completo (payload diagnóstico, reglas, alertas en 3 niveles, persistencia, handoff)

**Corrección de migración:** Se restauraron las expresiones (0 ∈ ℕ, 3/4 = 3 ÷ 4, 2i, 3 + 2i, 5) que en el .docx original quedaron como corchetes/paréntesis vacíos.

**Nota de diseño — lenguaje de crecimiento:** El "Caso 3 — Desempeño bajo" del borrador se reformuló como "Desempeño con errores persistentes" con invitación a practicar, evitando el marco de fracaso y manteniendo la zona segura.
