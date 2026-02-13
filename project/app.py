import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
from elo.vector_elo import VectorELO, aggregate_global_elo
from selector.item_selector import AdaptiveItemSelector
from elo.model import Item
from database import DatabaseManager
from ai_analysis import analyze_performance_local

# Configuración de página
st.set_page_config(page_title="MVP ELO Dashboard", layout="wide", page_icon="🎓")

# Inicializar Base de Datos
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# --- GAMIFICACIÓN: RANGOS ---
def get_rank(elo):
    if elo < 800: return "🌱 Novato", "#28a745" # Green
    if elo < 1000: return "🔨 Aprendiz", "#17a2b8" # Teal
    if elo < 1200: return "⚔️ Competente", "#007bff" # Blue
    if elo < 1400: return "🛡️ Avanzado", "#6610f2" # Purple
    if elo < 1600: return "🔥 Experto", "#fd7e14" # Orange
    if elo < 1800: return "👑 Maestro", "#dc3545" # Red
    return "🦄 Gran Maestro", "#e83e8c" # Pink

# --- ESTILOS CSS MODERNOS (DARK GAMING THEME) ---
st.markdown("""
    <style>
    /* Importar fuente Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Títulos con gradiente Neón */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(0, 201, 255, 0.3);
    }

    /* Cards Dark Glassmorphism */
    .elo-card {
        padding: 25px;
        border-radius: 20px;
        background: rgba(38, 39, 48, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s;
        margin-bottom: 20px;
        color: #ffffff; /* Asegurar texto blanco */
    }
    
    .elo-card h3, .elo-card p, .elo-card li {
        color: #e0e0e0 !important; /* Forzar color de texto interno */
    }
    
    .elo-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 201, 255, 0.15);
        border-color: rgba(0, 201, 255, 0.5);
    }

    ul {
        text-align: left;
        color: #e0e0e0;
    }
    
    /* Botones principales - Cyberpunk Style */
    .stButton>button { 
        border-radius: 12px; 
        height: 3.5em; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
        font-weight: 700;
        border: none;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(118, 75, 162, 0.5);
    }

    /* Inputs Dark */
    .stTextInput>div>div>input {
        border-radius: 10px;
        background-color: #1E1E1E;
        color: white;
        border: 1px solid #333;
        padding: 10px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #764ba2;
        box-shadow: 0 0 10px rgba(118, 75, 162, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 25px;
        background-color: #262730;
        color: #aaa;
        border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-weight: bold;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #00C9FF;
    }
    
    /* Sidebar info */
    .sidebar-text {
        color: #aaa;
        font-size: 0.9rem;
    }

    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE SESIÓN ---
def login():
    st.session_state.logged_in = True

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- PÁGINA DE LOGIN / REGISTRO Y BIENVENIDA ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-bottom: 10px;'>🎓 ELO Learning</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaa; font-size: 1.3rem; margin-bottom: 60px;'>Domina tus materias con inteligencia artificial adaptativa.</p>", unsafe_allow_html=True)
    
    col_info, col_login = st.columns([1.3, 1])
    
    with col_info:
        st.markdown("""
        <div class="elo-card" style="text-align: left; padding: 30px;">
            <h3>🚀 Sube de Nivel</h3>
            <p>Olvídate del estudio aburrido. Aquí cada pregunta cuenta para tu ranking global. Compite contra ti mismo.</p>
        </div>
        
        <div class="elo-card" style="text-align: left; padding: 30px;">
            <h3>⚔️ Mecánica de Juego</h3>
            <ul style="margin-top: 10px;">
                <li><b>Gana Puntos (ELO):</b> Responde bien y sube de liga.</li>
                <li><b>Rachas:</b> Mantén la consistencia para bonificaciones.</li>
                <li><b>Adaptación Real:</b> Si es muy fácil, te retamos. Si es difícil, te entrenamos.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_login:
        with st.container(border=True):
            st.markdown("### 🎮 Press Start")
            tab1, tab2 = st.tabs(["EXISTENTE", "NUEVO JUGADOR"])
            
            with tab1:
                username = st.text_input("Usuario / Gamertag", key="login_user")
                password = st.text_input("Contraseña", type="password", key="login_pass")
                st.write("")
                if st.button("🔴 CONTINUAR PARTIDA", type="primary"):
                    user = st.session_state.db.login_user(username, password)
                    if user:
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        login()
                        st.rerun()
                    else:
                        st.error("Game Over: Credenciales inválidas.")
        
            with tab2:
                new_user = st.text_input("Elige tu Gamertag", key="reg_user")
                new_pass = st.text_input("Contraseña Secreta", type="password", key="reg_pass")
                st.write("")
                if st.button("✨ NEW GAME"):
                    if st.session_state.db.register_user(new_user, new_pass):
                        st.success("Player Ready! Inicia sesión.")
                    else:
                        st.error("Ese Gamertag ya está en uso.")

else:
    # --- APLICACIÓN PRINCIPAL ---
    
    # 1. Recuperar Estado Inicial de DB para VectorELO
    if 'vector_initialized' not in st.session_state:
        latest_elos = st.session_state.db.get_latest_elo_by_topic(st.session_state.user_id)
        st.session_state.vector = VectorELO()
        for topic, elo in latest_elos.items():
            st.session_state.vector.ratings[topic] = elo
        st.session_state.vector_initialized = True
    
    # Sidebar Estilizado
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.write(f"### Hola, **{st.session_state.username}**")
        
        mode = st.radio("Modo", ["🚀 Practicar", "📊 Dashboard"], label_visibility="collapsed")
        st.caption("Navegación Principal")
        
        st.markdown("---")
        st.caption("Sesión")
        if st.button("Cerrar Sesión"):
            logout()

    # --- LÓGICA DE ACTUALIZACIÓN ---
    def handle_answer_topic(is_correct, item_data):
        # Actualizar ELO del Tópico Específico
        # Nota: K-factor podría ser dinámico, por ahora fijo en 32
        st.session_state.vector.update(item_data['topic'], item_data['difficulty'], 1.0 if is_correct else 0.0, 32)
        
        # Obtenemos el nuevo valor recién calculado
        new_elo_val = st.session_state.vector.get(item_data['topic'])
        
        # Guardar en BD
        st.session_state.db.save_attempt(
            st.session_state.user_id,
            item_data['id'],
            is_correct,
            item_data['difficulty'],
            item_data['topic'],
            new_elo_val
        )
        st.rerun()


            
    # --- VISTAS ---
    
    if mode == "🚀 Practicar":
        # --- VISTA DE PRÁCTICA ---
        
        # Cargar tópicos
        with open('items/bank.json', 'r', encoding='utf-8') as f:
            bank_data = json.load(f)
            topics = list(set([i['topic'] for i in bank_data]))
        
        st.sidebar.markdown("### Configuración de Estudio")
        selected_topic = st.sidebar.selectbox("¿Qué quieres estudiar hoy?", ["Todos"] + topics)
        
        # Determinar ELO a mostrar
        if selected_topic == "Todos":
            current_elo_display = aggregate_global_elo(st.session_state.vector)
            topic_display_name = "Global"
        else:
            current_elo_display = st.session_state.vector.get(selected_topic)
            topic_display_name = selected_topic
            
        rank_name, rank_color = get_rank(current_elo_display)

        st.title("🚀 Sala de Estudio")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
                <div class="elo-card">
                    <p style="color: #aaa; margin-bottom: 5px; font-weight: 600;">NIVEL ACTUAL</p>
                    <h2 style="color: {rank_color}; margin: 0; text-shadow: 0 0 10px {rank_color};">{rank_name}</h2>
                    <h1 style="font-size: 3.5rem; margin: 10px 0; color: white;">{current_elo_display:.0f}</h1>
                    <p style="color: #aaa; font-size: 0.9rem;">Puntos ELO en {topic_display_name}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 **Consejo:** La constancia es clave. Practica diariamente para consolidar tu aprendizaje.")

        with col2:
            st.subheader(f"📚 Sesión Activa: {selected_topic}")
            
            if selected_topic != "Todos":
                filtered_items = [i for i in bank_data if i['topic'] == selected_topic]
            else:
                filtered_items = bank_data
                
            answered_ids = st.session_state.db.get_answered_item_ids(st.session_state.user_id)
            filtered_items = [i for i in filtered_items if i['id'] not in answered_ids]
            
            if not filtered_items:
                 st.success("🎉 ¡Excelente trabajo! Has completado todos los ejercicios disponibles de este nivel.")
                 st.balloons()
            else:
                selector = AdaptiveItemSelector()
                items_objs = [Item(difficulty=i['difficulty']) for i in filtered_items]
                
                target_item_obj = selector.select(current_elo_display, items_objs)
                item_data = next(i for i in filtered_items if i['difficulty'] == target_item_obj.difficulty)
                
                with st.container(border=True):
                    # Badge de dificultad
                    diff_color = "#28a745" if item_data['difficulty'] < 1000 else "#ffc107" if item_data['difficulty'] < 1400 else "#dc3545"
                    st.markdown(f"**Tema:** {item_data['topic']} <span style='background-color: {diff_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; margin-left: 10px;'>⚡ Dificultad {item_data['difficulty']}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"### {item_data['content']}")
                    st.write("")
                    
                    if 'options' in item_data:
                        with st.form(key=f"form_{item_data['id']}"):
                            selected_option = st.radio("Selecciona tu respuesta:", item_data['options'], key=f"radio_{item_data['id']}")
                            st.write("")
                            submit_button = st.form_submit_button(label="📝 Enviar Respuesta")
                        
                        if submit_button:
                            is_correct = (selected_option == item_data['correct_option'])
                            if is_correct:
                                st.success("¡Correcto! Excelente análisis. 🎉")
                            else:
                                st.error(f"Incorrecto. La respuesta correcta era: **{item_data['correct_option']}**")
                            import time
                            time.sleep(1.5)
                            handle_answer_topic(is_correct, item_data)
                    else:
                        st.warning("Pregunta sin opciones configuradas.")

    elif mode == "📊 Dashboard":
        # --- VISTA DE DASHBOARD ---
        st.title("📊 Estadísticas de Aprendizaje")
        
        history_full = st.session_state.db.get_user_history_full(st.session_state.user_id)
        attempts_data = st.session_state.db.get_attempts_for_ai(st.session_state.user_id, limit=1000)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Ejercicios Resueltos", len(history_full), delta=f"+{len(attempts_data)} recientes")
        
        with m2:
            if attempts_data:
                accuracy = sum(1 for a in attempts_data if a['is_correct']) / len(attempts_data)
                st.metric("Precisión Promedio", f"{accuracy:.1%}")
            else:
                st.metric("Precisión Promedio", "0%")
            
        with m3:
            global_elo = aggregate_global_elo(st.session_state.vector)
            rank_n, rank_c = get_rank(global_elo)
            st.metric("Nivel Global", f"{global_elo:.0f}", delta=rank_n)
        
        st.markdown("---")
        
        # 2. Gráfico de Barras
        st.subheader("🏆 Dominio por Materia")
        current_elos = st.session_state.db.get_latest_elo_by_topic(st.session_state.user_id)
        
        if current_elos:
            try:
                # Datos
                topics = list(current_elos.keys())
                elos = list(current_elos.values())
                
                # Crear DataFrame para ordenar (opcional pero recomendado)
                df_elo = pd.DataFrame({'Tema': topics, 'ELO': elos}).sort_values('ELO', ascending=False)
                
                # Crear figura Matplotlib
                fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
                fig_bar.patch.set_alpha(0) # Fondo transparente
                ax_bar.set_facecolor('#1E1E1E')
                
                # Barras con degradado (simulado con color único por ahora)
                bars = ax_bar.bar(df_elo['Tema'], df_elo['ELO'], color='#00C9FF')
                
                # Etiquetas y Estilo
                ax_bar.set_ylabel("ELO", color="white")
                ax_bar.set_xlabel("Materia", color="white")
                ax_bar.tick_params(axis='x', colors='white', rotation=45)
                ax_bar.tick_params(axis='y', colors='white')
                ax_bar.set_ylim(bottom=max(0, min(elos) - 50)) # Ajustar escala para ver diferencias
                
                # Grid
                ax_bar.grid(True, axis='y', linestyle=':', alpha=0.3, color='gray')
                for spine in ax_bar.spines.values():
                    spine.set_color('#444')
                
                st.pyplot(fig_bar)
                
            except Exception as e:
                st.error(f"Error visualizando gráfica: {str(e)}")
                st.write(current_elos) # Fallback texto simple dict
        else:
            st.info("Completa ejercicios para visualizar tu perfil de fortalezas.")
            
        # 3. Línea de Tiempo
        st.subheader("📈 Progreso Académico")
        if history_full:
            df_hist = pd.DataFrame(history_full)
            df_hist['intento'] =  range(1, len(df_hist) + 1)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            # Fondo transparente para Dark Mode
            fig.patch.set_alpha(0)
            ax.set_facecolor('#1E1E1E') # Darker inner bg
            
            for topic in df_hist['topic'].unique():
                topic_data = df_hist[df_hist['topic'] == topic]
                ax.plot(topic_data['intento'], topic_data['elo'], marker='o', label=topic, linewidth=2)
            
            ax.set_ylabel("Nivel ELO", color="white")
            ax.set_xlabel("Secuencia de Ejercicios", color="white")
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            
            # Leyenda fuera del gráfico para no tapar datos
            legend = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
            legend.get_frame().set_facecolor('#262730')
            legend.get_frame().set_edgecolor('gray')
            for text in legend.get_texts():
                text.set_color("white")
                
            ax.grid(True, linestyle=':', alpha=0.3, color='gray')
            for spine in ax.spines.values():
                spine.set_color('#444')
            
            # Ajustar layout para dar espacio a la leyenda
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.write("Sin datos históricos.")

        # 4. Sección AI
        st.markdown("---")
        
        st.subheader("🧠 Asistente Virtual Inteligente")
        st.write("Generando recomendaciones personalizadas basadas en tu desempeño reciente.")
        
        lm_studio_url_dash = st.text_input("Servidor de IA (URL)", value="http://localhost:1234/v1", key="lm_dash")
        
        if st.button("✨ Generar Recomendaciones de Estudio"):
             try:
                 with st.spinner("Analizando patrones de aprendizaje..."):
                    recent_attempts = st.session_state.db.get_attempts_for_ai(st.session_state.user_id)
                    current_elo_val = aggregate_global_elo(st.session_state.vector)
                    
                    # Llamada a la IA (o fallback)
                    recommendations = analyze_performance_local(recent_attempts, current_elo_val, base_url=lm_studio_url_dash)
                    
                    if isinstance(recommendations, list) and len(recommendations) > 0:
                        # VISTA VERTICAL (Más estable)
                        for idx, rec in enumerate(recommendations):
                            with st.container(border=True):
                                st.markdown(f"#### 💡 Consejo #{idx+1}")
                                st.info(rec)
                                    
                    elif isinstance(recommendations, list) and len(recommendations) == 0:
                        st.warning("No hay suficientes datos para generar recomendaciones aún.")
                    else:
                        st.error(f"Respuesta inesperada de IA: {recommendations}")
                        
             except Exception as e:
                 st.error(f"Error crítico en interfaz: {str(e)}")
