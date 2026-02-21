# 🎓 LevelUp-ELO

Plataforma de **aprendizaje adaptativo gamificada**, construida con **Python + Streamlit**, que usa el **sistema de rating ELO** (el mismo usado en ajedrez) para medir y mejorar el nivel académico de los estudiantes.

---

## 🧩 Componentes principales

| Módulo | Archivo | Qué hace |
|---|---|---|
| **App principal** | `app.py` | Interfaz Streamlit con login, práctica y dashboard |
| **Base de datos** | `database.py` | SQLite — usuarios, intentos y progreso |
| **Motor ELO** | `elo/model.py` + `elo/vector_elo.py` | Calcula y actualiza ratings ELO por materia |
| **Selector adaptativo** | `selector/item_selector.py` | Elige preguntas óptimas según tu nivel |
| **IA** | `ai_analysis.py` | Genera recomendaciones de estudio via LM Studio |
| **Banco de preguntas** | `items/bank.json` | Preguntas clasificadas por tema y dificultad |

---

## ⚙️ ¿Cómo funciona?

1. **Login/Registro** — El usuario crea una cuenta o inicia sesión (contraseñas hasheadas con SHA-256).

2. **Modo Práctica** — El sistema selecciona preguntas de forma inteligente:
   - Calcula tu **ELO actual** por materia (empieza en 1000).
   - Usa el `AdaptiveItemSelector` para elegir preguntas dentro de un rango de dificultad óptimo (zona de desarrollo próximo).
   - Si respondes bien → **tu ELO sube**; si fallas → **baja**.
   - Las preguntas ya respondidas no se repiten.

3. **Sistema de rangos** — Tu ELO determina tu "rango":

   `🌱 Novato` → `🔨 Aprendiz` → `⚔️ Competente` → `🛡️ Avanzado` → `🔥 Experto` → `👑 Maestro` → `🦄 Gran Maestro`

4. **Dashboard** — Visualiza:
   - Ejercicios resueltos y precisión promedio
   - Gráfico de **dominio por materia** (barras)
   - Gráfico de **progreso en el tiempo** (líneas por tema)

5. **Asistente IA** — Se conecta a un modelo local vía **LM Studio** (API compatible con OpenAI) para generar 3 recomendaciones personalizadas de estudio basadas en tus errores recientes. Si no hay conexión, usa un fallback offline.

---

## 🧠 El algoritmo ELO adaptativo

En lugar de un solo rating global, se mantiene un **vector de ratings independiente por materia** (ej: `{"Álgebra": 1150, "Cálculo": 980}`). El ELO global es el promedio de todos.

La fórmula de actualización es la estándar de ELO:

```
nuevo_elo = elo_actual + K × (resultado - probabilidad_esperada)
```

---

## 🚀 Cómo ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```
