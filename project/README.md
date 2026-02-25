# 🎓 LevelUp-ELO

Plataforma de **aprendizaje adaptativo gamificada**, construida con **Python + Streamlit**, que usa el **sistema de rating ELO** (el mismo usado en ajedrez) para medir y mejorar el nivel académico de los estudiantes.

---

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una arquitectura limpia (Clean Architecture) organizada por capas dentro del directorio `src/`:

- **Domain**: Contiene la lógica central de negocio (modelos ELO, algoritmos de selección).
- **Application**: Servicios que orquestan el flujo de datos entre la infraestructura y el dominio.
- **Infrastructure**: Implementaciones de persistencia (SQLite), seguridad (hashing) y clientes externos (IA).
- **Interface**: El punto de entrada de la aplicación mediante Streamlit.

---

## 🧩 Componentes principales

| Módulo | Directorio/Archivo | Qué hace |
|---|---|---|
| **App Streamlit** | `src/interface/streamlit/app.py` | Interfaz de usuario, login y paneles. |
| **Servicios Estudiante/Profesor** | `src/application/services/` | Orquestación de lógica para cada rol. |
| **Motor ELO** | `src/domain/elo/` | Cálculo y actualización de ratings ELO competitivos. |
| **Selector Adaptativo** | `src/domain/selector/` | Elige la siguiente pregunta óptima para el estudiante. |
| **Repositorio SQLite** | `src/infrastructure/persistence/` | Gestión de base de datos local y sincronización. |
| **Cliente IA** | `src/infrastructure/external_api/` | Conexión con modelos locales (LM Studio) para feedback. |
| **Seguridad** | `src/infrastructure/security/` | Hashing de contraseñas y validación de sesiones. |
| **Banco de preguntas** | `items/bank.json` | Preguntas clasificadas por tema y dificultad base. |

---

## ⚙️ ¿Cómo funciona?

1. **Login/Registro** — El usuario crea una cuenta. Las contraseñas se almacenan de forma segura con Argon2.
2. **Modo Práctica** — El sistema selecciona preguntas inteligentes usando el `AdaptiveItemSelector`.
    - Si respondes bien → **tu ELO sube**; si fallas → **baja**.
    - El sistema detecta "zona de desarrollo próximo" para no aburrir ni frustrar.
3. **Análisis con IA** — Si tienes configurado **LM Studio**, un tutor socrático y un analista pedagógico te brindarán retroalimentación personalizada.
4. **Dashboard Docente** — Los profesores pueden monitorear el progreso de sus grupos, ver probabilidades de fallo y generar reportes con IA.

---

## 🚀 Cómo ejecutar

Asegúrate de tener Python 3.10+ instalado.

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar la aplicación**:
   ```bash
   streamlit run src/interface/streamlit/app.py
   ```

---

## 📊 Algoritmo ELO Adaptativo

Utilizamos un sistema de **Vector ELO**, donde cada materia tiene su propio rating independiente. La probabilidad de acierto se calcula basándose en la diferencia entre el ELO del estudiante y la dificultad del ítem, ajustando el rating mediante una constante *K* dinámica que considera la incertidumbre (RD).
