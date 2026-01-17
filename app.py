import streamlit as st
import json
import random
import pandas as pd
import matplotlib.pyplot as plt
from elo.vector_elo import VectorELO, aggregate_global_elo
from selector.item_selector import AdaptiveItemSelector
from elo.model import Item

# Configuración de página para Responsive Design
st.set_page_config(page_title="MVP ELO Dashboard", layout="wide")

# Estilos CSS básicos para mejorar el look profesional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .elo-card { padding: 20px; border-radius: 10px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE SESIÓN ---
if 'vector' not in st.session_state:
    st.session_state.vector = VectorELO()
    st.session_state.history = [1000]
    st.session_state.current_step = 0
    with open('items/bank.json', 'r') as f:
        st.session_state.bank = json.load(f)

# --- LÓGICA ---
def handle_answer(is_correct, item_difficulty):
    # Actualizar ELO
    st.session_state.vector.update('global', item_difficulty, is_correct, k_factor=32)
    new_elo = aggregate_global_elo(st.session_state.vector)
    st.session_state.history.append(new_elo)
    st.session_state.current_step += 1

# --- INTERFAZ ---
st.title("🚀 Sistema de Aprendizaje Adaptativo (MVP)")

col1, col2 = st.columns([1, 2])

with col1:
    current_elo = aggregate_global_elo(st.session_state.vector)
    st.markdown(f"""
        <div class="elo-card">
            <h3>Tu Nivel Actual (ELO)</h3>
            <h1 style="color: #007bff;">{current_elo:.2f}</h1>
            <p>Retos completados: {st.session_state.current_step}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Gráfico de progreso
    st.subheader("Evolución")
    fig, ax = plt.subplots()
    ax.plot(st.session_state.history, marker='o', color='#007bff')
    ax.set_ylabel("ELO Score")
    ax.set_xlabel("Pasos")
    st.pyplot(fig)

with col2:
    st.subheader("Próximo Reto")
    
    # Seleccionar ítem basado en ELO
    selector = AdaptiveItemSelector()
    # Convertimos el JSON a objetos Item para el selector
    items_objs = [Item(difficulty=i['difficulty']) for i in st.session_state.bank]
    target_item_obj = selector.select(current_elo, items_objs)
    
    # Buscar el contenido real del item seleccionado
    item_data = next(i for i in st.session_state.bank if i['difficulty'] == target_item_obj.difficulty)
    
    st.info(f"**Tópico:** {item_data['topic']}")
    st.write(f"### {item_data['content']}")
    
    c_btn1, c_btn2 = st.columns(2)
    if c_btn1.button("✅ Lo sé / Correcto"):
        handle_answer(True, item_data['difficulty'])
        st.rerun()
    
    if c_btn2.button("❌ No lo sé / Incorrecto"):
        handle_answer(False, item_data['difficulty'])
        st.rerun()

if st.button("Resetear Simulación"):
    st.session_state.clear()
    st.rerun()