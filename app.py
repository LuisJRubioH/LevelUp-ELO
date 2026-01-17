import streamlit as st
import json
import matplotlib.pyplot as plt
from elo.vector_elo import VectorELO, aggregate_global_elo
from selector.item_selector import AdaptiveItemSelector
from elo.model import Item

# ==================================================
# 1. CONFIGURACIÓN
# ==================================================
st.set_page_config(page_title="LevelUp-ELO", layout="wide")

# HEADER
logo_col, title_col = st.columns([1, 4])
with logo_col:
    st.image("logo.png", width=160)
with title_col:
    st.markdown(
        """
        <h1 style="margin-bottom: 0;">
            <span style="color: white;">LevelUp -</span>
            <span style="color: #5DA25F;">ELO</span>
        </h1>
        """,
        unsafe_allow_html=True
    )


# ==================================================
# 2. INICIALIZACIÓN DE SESIÓN
# ==================================================
if 'vector' not in st.session_state:
    st.session_state.vector = VectorELO()
    st.session_state.history = [1000.0]
    st.session_state.correct_count = 0
    st.session_state.incorrect_count = 0
    st.session_state.last_elo_diff = 0.0
    st.session_state.answered = False
    st.session_state.last_result = None
    st.session_state.current_item = None
    st.session_state.last_item_id = None

    # NUEVO: preguntas respondidas correctamente
    st.session_state.answered_correctly_ids = set()

    with open('items/bank.json', 'r', encoding='utf-8') as f:
        st.session_state.bank = json.load(f)

# ==================================================
# 3. FUNCIÓN DE PROCESAMIENTO
# ==================================================
def procesar_envio(eleccion, correcta, dificultad):
    es_correcta = (eleccion == correcta)

    old_elo = aggregate_global_elo(st.session_state.vector)
    st.session_state.vector.update('global', dificultad, es_correcta, k_factor=32)
    new_elo = aggregate_global_elo(st.session_state.vector)

    st.session_state.last_elo_diff = new_elo - old_elo
    st.session_state.history.append(new_elo)

    if es_correcta:
        st.session_state.correct_count += 1
        # Registrar pregunta como definitivamente resuelta
        st.session_state.answered_correctly_ids.add(
            st.session_state.current_item['id']
        )
    else:
        st.session_state.incorrect_count += 1

    st.session_state.last_item_id = st.session_state.current_item['id']
    st.session_state.answered = True
    st.session_state.last_result = es_correcta

# ==================================================
# 4. MÉTRICAS
# ==================================================
current_elo = aggregate_global_elo(st.session_state.vector)
total_retos = st.session_state.correct_count + st.session_state.incorrect_count
precision_real = (st.session_state.correct_count / total_retos * 100) if total_retos > 0 else 0.0
diff_inicial = current_elo - 1000

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        "ELO Actual",
        f"{current_elo:.2f}",
        f"Desde inicio: {diff_inicial:+.2f} | Último: {st.session_state.last_elo_diff:+.2f}"
    )

with m2:
    st.metric("Precisión Real", f"{precision_real:.1f}%")

with m3:
    st.metric(
        "Retos Totales",
        total_retos,
        f"✅ {st.session_state.correct_count} | ❌ {st.session_state.incorrect_count}"
    )

st.markdown("---")

# ==================================================
# 5. LAYOUT
# ==================================================
col1, col2 = st.columns([1, 2])

# ------------------ GRÁFICO -----------------------
with col1:
    st.subheader("Evolución de Nivel")

    color = "#5DA25F" if st.session_state.last_elo_diff >= 0 else "red"
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(st.session_state.history, marker='o', color=color, linewidth=2)

    ax.set_facecolor('#0e1117')
    fig.patch.set_facecolor('#0e1117')
    ax.tick_params(colors='white')
    ax.grid(alpha=0.2)

    st.pyplot(fig)

    if st.button("Resetear Progreso"):
        st.session_state.clear()
        st.rerun()

# ------------------ RETO --------------------------
with col2:
    selector = AdaptiveItemSelector()
    items_objs = [Item(difficulty=i['difficulty']) for i in st.session_state.bank]
    target_item = selector.select(current_elo, items_objs)

    # CANDIDATOS: excluir preguntas ya respondidas correctamente
    candidatos = [
        i for i in st.session_state.bank
        if i['id'] not in st.session_state.answered_correctly_ids
    ]

    if not candidatos:
        st.success("🎉 Has resuelto correctamente todas las preguntas disponibles.")
        st.stop()

    if st.session_state.current_item is None:
        st.session_state.current_item = min(
            candidatos,
            key=lambda x: abs(x['difficulty'] - target_item.difficulty)
        )

    item = st.session_state.current_item

    if not st.session_state.answered:
        st.subheader("Próximo Reto")
        st.info(f"**Tópico:** {item['topic']} | **Dificultad:** {item['difficulty']}")
        st.write(f"### {item['content']}")

        opcion = st.radio(
            "Selecciona la respuesta correcta:",
            item['options'],
            index=None,
            key="respuesta_actual"
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Enviar Respuesta", type="primary", disabled=opcion is None):
                procesar_envio(opcion, item['correct_answer'], item['difficulty'])
                st.rerun()

        with c2:
            if st.button("No lo sé / Salir"):
                procesar_envio(None, "SKIP", item['difficulty'])
                st.session_state.last_result = "skip"
                st.rerun()

    else:
        st.subheader("Resultado")

        if st.session_state.last_result is True:
            st.success(f"Correcto. +{st.session_state.last_elo_diff:.2f} puntos.")
            st.balloons()
        elif st.session_state.last_result is False:
            st.error(f"Incorrecto. {st.session_state.last_elo_diff:.2f} puntos.")
        else:
            st.warning("Reto saltado.")

        if st.button("Siguiente Reto"):
            st.session_state.answered = False
            st.session_state.last_result = None
            st.session_state.current_item = None
            st.session_state.pop("respuesta_actual", None)
            st.rerun()
