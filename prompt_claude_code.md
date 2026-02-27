# Prompt para Claude Code — LevelUp-ELO: Diagnóstico y corrección integral

## Contexto del proyecto

Este es un proyecto llamado **LevelUp-ELO**, una plataforma de aprendizaje adaptativo gamificada construida con Python + Streamlit. Usa el sistema de rating ELO para medir el nivel académico de estudiantes. La arquitectura es Clean Architecture con estas capas:

- `src/interface/streamlit/app.py` → UI principal (Streamlit)
- `src/application/services/` → Servicios de estudiante y profesor
- `src/domain/elo/` → Motor ELO
- `src/domain/selector/` → Selector adaptativo de preguntas
- `src/infrastructure/persistence/` → SQLite (base de datos)
- `src/infrastructure/external_api/` → Cliente IA (LM Studio)
- `src/infrastructure/security/` → Hashing con Argon2
- `items/bank.json` → Banco de preguntas

La app se despliega en **Streamlit Cloud**. Los roles son: **Estudiante**, **Profesor** y **Admin**.

---

## Instrucciones generales

Antes de hacer CUALQUIER cambio:
1. Lee TODOS los archivos del proyecto completo para entender la estructura y las dependencias.
2. Identifica cada problema descrito abajo en el código fuente.
3. Presenta un plan de acción antes de ejecutar cambios.
4. Haz los cambios uno por uno, verificando que no rompas funcionalidad existente.
5. Al final, muestra un resumen de todos los archivos modificados y qué cambió en cada uno.

---

## BUGS CRÍTICOS A CORREGIR

### 1. Sesión se pierde al recargar la página
**Síntoma:** Al recargar la página (F5 o cambio de pestaña), el usuario (estudiante, profesor o admin) es expulsado y debe hacer login de nuevo.
**Causa probable:** `st.session_state` no se está persistiendo correctamente o se reinicializa en cada ejecución del script.
**Solución esperada:** Verificar que el manejo de sesión use `st.session_state` correctamente, que no se sobreescriban las variables de sesión al inicio del script, y que el flujo de login solo se ejecute cuando NO hay sesión activa.

### 2. Base de datos temporal (se borran usuarios registrados)
**Síntoma:** Los usuarios registrados (estudiantes y profesores) desaparecen al reiniciar la app en Streamlit Cloud.
**Causa:** El filesystem de Streamlit Cloud es efímero; la base de datos SQLite se genera en tiempo de ejecución y se pierde al reiniciar.
**Solución esperada:**
- Crear un sistema de inicialización que precargue datos de prueba si la base de datos no existe.
- Precarga: 1 admin (usuario: "admin", contraseña: "admin1234"), 1 profesor (usuario: "profesor1", contraseña: "demo1234"), 2 estudiantes (usuario: "estudiante1" y "estudiante2", contraseña: "demo1234").
- Las contraseñas DEBEN usar el mismo sistema de hashing que ya tiene el proyecto (Argon2).
- Agregar un comentario en el código indicando que para producción se debe usar una base de datos externa.

### 3. Preguntas repetidas sin justificación
**Síntoma:** El selector adaptativo repite preguntas que el estudiante ya contestó correctamente, sin motivo pedagógico.
**Causa probable:** El `AdaptiveItemSelector` no filtra correctamente las preguntas ya respondidas o no registra bien el historial.
**Solución esperada:** Modificar el selector para que:
- No repita una pregunta contestada correctamente en la misma sesión de práctica.
- Solo repita preguntas falladas, y con un intervalo mínimo (no inmediatamente).
- Priorice preguntas no vistas sobre preguntas ya respondidas.

---

## PROBLEMAS DE UX/INTERFAZ

### 4. Selector de temas mal ubicado
**Síntoma:** El selector de temas de estudio no es visible para el estudiante porque está oculto o tapado por el selector de modelo de IA.
**Solución esperada:**
- Mover el selector de temas para que aparezca **debajo del botón de Práctica**, visible y accesible para estudiantes y profesores.
- El selector de modelo de IA **solo debe ser visible para el rol Admin**, NO para estudiantes ni profesores. Ocultarlo completamente para los demás roles.

### 5. Formato LaTeX roto en algunas preguntas
**Síntoma:** Fórmulas y expresiones matemáticas no se renderizan correctamente.
**Causa probable:** Uso incorrecto de delimitadores LaTeX o falta de uso de `st.latex()` o `st.markdown()` con soporte KaTeX.
**Solución esperada:**
- Revisar cómo se renderizan las preguntas del `bank.json`.
- Asegurar que se use `st.markdown()` con delimitadores `$...$` para inline y `$$...$$` para bloques.
- Si hay preguntas con LaTeX mal escapado en `bank.json`, corregir el formato.

### 6. Gráficos estadísticos poco atractivos
**Síntoma:** Los gráficos del dashboard son visualmente pobres y poco profesionales.
**Solución esperada:**
- Aplicar un tema oscuro coherente con la UI de la app.
- Usar `plotly` en vez de `matplotlib` si es posible (más interactivo y elegante en Streamlit).
- Mejorar: colores consistentes, títulos claros, leyendas legibles, bordes redondeados.
- Si se usa matplotlib, aplicar un estilo como `'seaborn-v0_8-darkgrid'` o similar.

---

## PROBLEMAS DE FUNCIONALIDAD IA

### 7. Tutor socrático y recomendaciones muy lentas en local
**Síntoma:** Las respuestas del tutor socrático y las recomendaciones tardan demasiado cuando se usa LM Studio local.
**Solución esperada:**
- Implementar streaming de respuestas (mostrar texto mientras se genera, no esperar a que termine).
- Agregar un spinner o indicador de progreso ("El tutor está pensando...").
- Si la conexión a LM Studio falla o no está disponible (como en Streamlit Cloud), mostrar un mensaje amigable: "Tutor IA no disponible en esta versión" en lugar de un error. NO debe crashear la app.

### 8. Recomendaciones de IA desbalanceadas
**Síntoma:** Las recomendaciones solo señalan los errores del estudiante sin analizar su avance real. No son equilibradas.
**Solución esperada:**
- Modificar el prompt del sistema de IA para que las recomendaciones incluyan:
  - Fortalezas del estudiante (temas donde ha mejorado, rachas de acierto).
  - Áreas de mejora (temas con bajo ELO o alta tasa de error).
  - Sugerencias concretas de estudio.
- Lo mismo aplica para las recomendaciones que ve el profesor sobre cada estudiante: deben ser un análisis equilibrado, no solo una lista de errores.

---

## PROBLEMAS DE ROLES Y PERMISOS

### 9. Admin no puede ver estadísticas ni puntajes
**Síntoma:** El rol admin no tiene acceso al dashboard de estadísticas ni a los puntajes de los estudiantes.
**Solución esperada:** El admin debe tener acceso a TODO:
- Dashboard de estadísticas globales.
- Puntajes ELO de todos los estudiantes.
- Todas las funcionalidades del profesor.
- Configuraciones del sistema (como el selector de modelo de IA).

---

## SEGURIDAD

### 10. Revisión general de seguridad
Revisa y corrige si encuentras:
- Contraseñas expuestas en texto plano (logs, variables, session_state visible).
- API keys o secrets hardcodeados.
- SQL injection en queries a SQLite.
- Falta de validación de inputs del usuario.
- Sesiones sin expiración o sin cierre de sesión funcional.

---

## Reglas de trabajo

- **NO cambies la arquitectura general** (Clean Architecture con las capas existentes).
- **NO elimines funcionalidad existente** que funcione correctamente.
- **Haz commits atómicos**: un commit por cada problema resuelto.
- **Prioridad de ejecución**: Bugs críticos (1-3) → UX (4-6) → IA (7-8) → Roles (9) → Seguridad (10).
- Si necesitas instalar nuevas dependencias, agrégalas a `requirements.txt`.
- Comenta el código donde hagas cambios significativos.
- Al terminar cada corrección, ejecuta la app con `streamlit run src/interface/streamlit/app.py` para verificar que funciona.
