import streamlit as st  # ✅ Solo una vez
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time
import json

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(
    page_title="IA World Cup Predictor",
    page_icon="⚽",
    layout="wide"
)

# ---------- AUDIO (SILBATO Y MÚSICA) ----------
st.markdown("""
    <div id="top"></div>
    <audio autoplay>
        <source src="https://www.soundjay.com/misc/sounds/whistle-camp-1.mp3" type="audio/mpeg">
    </audio>
    <audio autoplay loop>
        <source src="https://cdn.pixabay.com/audio/2022/10/14/audio_9939ef2a23.mp3" type="audio/mpeg">
    </audio>
""", unsafe_allow_html=True)

# ---------- ESTILOS CSS ----------
st.markdown("""
    <style>
    /* Background with subtle gradient */
    .stApp { 
        background: radial-gradient(circle at top, #1a1a2e, #0e1117); 
        background-attachment: fixed;
    }
    
    /* Glassmorphism Bracket Cards */
    .bracket-card {
        background: rgba(30, 35, 48, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .bracket-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    .bracket-card img {
        width: 80px;
        height: 80px;
        object-fit: contain;
    }
    .bracket-card p {
        color: white;
        font-weight: 700;
        margin-top: 15px;
        font-size: 1.1em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Copa Center Card */
    .copa-card {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Bracket Grid Layout (2x2 for LLMs with FIFA logo in center/top) */
    .bracket-grid {
        display: grid;
        grid-template-columns: 1fr 1.8fr 1fr;
        grid-template-rows: auto auto;
        gap: 20px;
        align-items: center;
        max-width: 900px;
        margin: 20px auto;
    }
    .bracket-grid > .llm-card-1 { grid-column: 1; grid-row: 1; }
    .bracket-grid > .llm-card-2 { grid-column: 3; grid-row: 1; }
    .bracket-grid > .fifa-container { 
        grid-column: 2; 
        grid-row: 1 / span 2; 
        text-align: center; 
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .bracket-grid > .llm-card-3 { grid-column: 1; grid-row: 2; }
    .bracket-grid > .llm-card-4 { grid-column: 3; grid-row: 2; }
    
    .fifa-container img {
        width: 250px !important;
        height: 250px !important;
        object-fit: contain;
        filter: drop-shadow(0 0 35px rgba(255, 255, 255, 0.25));
        transition: transform 0.3s ease;
    }
    .fifa-container img:hover {
        transform: scale(1.08);
    }
    
    /* Responsive Queries */
    @media (max-width: 768px) {
        .bracket-grid {
            grid-template-columns: 1fr 1fr;
            grid-template-rows: auto auto auto;
            gap: 15px;
        }
        .bracket-grid > .llm-card-1 { grid-column: 1; grid-row: 1; }
        .bracket-grid > .llm-card-2 { grid-column: 2; grid-row: 1; }
        .bracket-grid > .fifa-container { grid-column: 1 / span 2; grid-row: 2; }
        .bracket-grid > .llm-card-3 { grid-column: 1; grid-row: 3; }
        .bracket-grid > .llm-card-4 { grid-column: 2; grid-row: 3; }
        
        .fifa-container img {
            width: 200px !important;
            height: 200px !important;
        }
        .ai-badge { width: 45% !important; margin-bottom: 10px; }
        .hero-title { font-size: 2em !important; }
        .bracket-card img { width: 60px !important; height: 60px !important; }
    }
    
    /* Match Result Cards */
    .match-card {
        background: rgba(30, 35, 48, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    .match-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 12px 30px rgba(0,0,0,0.4);
    }
    
    /* Individual AI Prediction Badge inside Match Card */
    .ai-badge {
        text-align: center; 
        background: rgba(0, 0, 0, 0.3); 
        padding: 15px; 
        border-radius: 12px; 
        width: 23%;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: transform 0.2s, background 0.2s;
    }
    .ai-badge:hover {
        transform: scale(1.05);
        background: rgba(0, 0, 0, 0.5);
        border-color: rgba(255,255,255,0.2);
    }
    
    /* Hero Title Gradient */
    .hero-title {
        text-align: center;
        background: linear-gradient(90deg, #FFD700, #FDB931, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.5em;
        margin-bottom: 0px;
        text-shadow: 0px 4px 15px rgba(255, 215, 0, 0.2);
    }
    .hero-subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1.3em;
        margin-top: 10px;
        margin-bottom: 40px;
        font-weight: 300;
    }

    /* Back to Top Button */
    .btn-top {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: linear-gradient(135deg, #4D4B96, #8E75B2);
        color: white !important;
        padding: 12px 25px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        z-index: 1000;
        transition: all 0.3s;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .btn-top:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.7);
        text-decoration: none;
        border-color: rgba(255,255,255,0.5);
    }
    
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 50px;
        height: 50px;
        cursor: pointer;
        z-index: 999;
        opacity: 0.1;
        background: transparent;
    }
    .footer:hover { opacity: 0.3; }
    </style>
""", unsafe_allow_html=True)

# ---------- FUNCIÓN PARA CONECTAR A GOOGLE SHEETS ----------
def conectar_sheets():
    # Usar los secretos de Streamlit Cloud
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # ✅ CORRECCIÓN 1: Obtén el ID desde la ruta correcta
    sheet_id = st.secrets["sheets"]["sheet_id"]  # <--- CAMBIO AQUÍ
    
    # ✅ CORRECCIÓN 2: Usa la variable sheet_id (no SHEET_ID)
    sheet = client.open_by_key(sheet_id).worksheet("Pronosticos")  # <--- CAMBIO AQUÍ
    return sheet

# ---------- FUNCIÓN PARA PROCESAR PUNTUACIONES (DATAFRAME) ----------
def procesar_puntuaciones(df):
    df = df.copy()
    ias = ["Claude", "DeepSeek", "Gemini", "ChatGPT"]
    for ia in ias:
        pts_col = f"Pts_{ia}"
        total_col = f"Total_{ia}"
        
        pts_list = []
        for idx, row in df.iterrows():
            pts = calcular_puntaje(
                row.get("GolesLocal"),
                row.get("GolesVisitante"),
                row.get(f"{ia}_L"),
                row.get(f"{ia}_V")
            )
            pts_list.append(pts)
            
        df[pts_col] = pts_list
        df[total_col] = df[pts_col].cumsum()
        
    return df

# ---------- CARGAR DATOS DESDE SHEETS ----------
def cargar_datos():
    try:
        sheet = conectar_sheets()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Renombrar columnas (ajusta según tu hoja)
        # Asumo columnas: Fecha, Local, Visitante, GolesLocal, GolesVisitante,
        # Claude_L, Claude_V, DeepSeek_L, DeepSeek_V, Gemini_L, Gemini_V, ChatGPT_L, ChatGPT_V
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        # Datos de ejemplo si falla
        return pd.DataFrame()

# ---------- CALCULAR PUNTUACIONES ----------
def calcular_puntaje(local_real, visit_real, local_pred, visit_pred):
    try:
        local_real = float(local_real)
        visit_real = float(visit_real)
        local_pred = float(local_pred)
        visit_pred = float(visit_pred)
    except (TypeError, ValueError):
        return 0  # Si no se puede convertir, puntaje 0

    if local_real == local_pred and visit_real == visit_pred:
        return 5
    
    dif_real = local_real - visit_real
    dif_pred = local_pred - visit_pred

    if dif_real == dif_pred:
        return 3
    elif (dif_real > 0 and dif_pred > 0) or (dif_real < 0 and dif_pred < 0):
        return 2
    else:
        return 0
# ---------- LOGO Y CABECERA ----------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", use_container_width=True)
    st.markdown("""
        <h1 class='hero-title' style='font-size: 2.5em; line-height: 1.2; margin-bottom: 30px;'>Las IA compiten para ver quien es mejor prediciendo los partidos del mundial 2026</h1>
        <div style="text-align: center; color: #a0aec0; font-size: 1.1em; max-width: 800px; margin: 0 auto 40px auto; line-height: 1.6; background: rgba(30, 35, 48, 0.6); padding: 15px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <strong style="color: white; font-size: 1.2em;">Reglas de puntuación:</strong><br>
            🎯 Por acierto de marcador suman <strong style="color: #FFD700;">5 puntos</strong><br>
            ✅ Por acierto de ganador y diferencia de goles suman <strong style="color: #FFD700;">3 puntos</strong><br>
            ✔️ Por acierto de ganador <strong style="color: #FFD700;">2 puntos</strong><br>
            ❌ Todo lo demas es <strong style="color: #FFD700;">0 puntos</strong><br>
            <em style="display: block; margin-top: 10px; color: white;">¡Que ruede el balón y veamos quién será la mejor analizadora!</em>
        </div>
    """, unsafe_allow_html=True)

# ---------- BRACKET DE IAS ----------
st.markdown("## 🤖 ¿Quién será el mejor pronosticador?")

ias = {
    "Claude": "https://cdn.simpleicons.org/claude/D97757",
    "DeepSeek": "https://cdn.simpleicons.org/deepseek/4D4B96",
    "Gemini": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg",
    "ChatGPT": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg"
}

# Logo oficial del Mundial 2026 (imagen local convertida a base64)
import base64
try:
    with open("fifa.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    logo_url = f"data:image/jpeg;base64,{encoded_string}"
except Exception:
    logo_url = ""

st.markdown(f"""
<div class="bracket-grid">
    <div class="bracket-card llm-card-1">
        <img src="{ias['Claude']}" alt="Claude">
        <p>Claude</p>
    </div>
    <div class="bracket-card llm-card-2">
        <img src="{ias['Gemini']}" alt="Gemini">
        <p>Gemini</p>
    </div>
    <div class="fifa-container">
        <img src="{logo_url}" alt="FIFA 2026">
    </div>
    <div class="bracket-card llm-card-3">
        <img src="{ias['DeepSeek']}" alt="DeepSeek">
        <p>DeepSeek</p>
    </div>
    <div class="bracket-card llm-card-4">
        <img src="{ias['ChatGPT']}" alt="ChatGPT">
        <p>ChatGPT</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------- CARGAR Y MOSTRAR DATOS ----------
df = cargar_datos()
if not df.empty:
    df_procesado = procesar_puntuaciones(df)
    
    # Mostrar tabla principal
    st.markdown("<h2 style='color: white; font-weight: 800; font-size: 2.2em; margin-bottom: 20px; text-shadow: 0 2px 5px rgba(0,0,0,0.5);'>Tabla de posiciones al momento</h2>", unsafe_allow_html=True)
    
    # Crear tabla de resumen (totales por IA)
    resumen = pd.DataFrame({
        "IA": ["Claude", "DeepSeek", "Gemini", "ChatGPT"],
        "Puntaje": [
            df_procesado["Total_Claude"].iloc[-1] if not df_procesado.empty else 0,
            df_procesado["Total_DeepSeek"].iloc[-1] if not df_procesado.empty else 0,
            df_procesado["Total_Gemini"].iloc[-1] if not df_procesado.empty else 0,
            df_procesado["Total_ChatGPT"].iloc[-1] if not df_procesado.empty else 0
        ]
    }).sort_values("Puntaje", ascending=False).reset_index(drop=True)
    
    # Mostrar tabla de posiciones ocultando el índice (HTML personalizado con iconos y números grandes)
    leaderboard_html = f"""
<div style="background: rgba(30, 35, 48, 0.4); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 16px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.08); max-width: 600px; margin: 20px auto 40px auto; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
<table style="width: 100%; border-collapse: collapse; color: white;">
<thead>
<tr style="border-bottom: 2px solid rgba(255, 255, 255, 0.1); text-align: left;">
<th style="padding: 12px; color: #a0aec0; font-weight: 600; font-size: 1.1em;">Posición</th>
<th style="padding: 12px; color: #a0aec0; font-weight: 600; font-size: 1.1em;">IA</th>
<th style="padding: 12px; color: #a0aec0; font-weight: 600; font-size: 1.1em; text-align: right;">Puntaje</th>
</tr>
</thead>
<tbody>
"""
    for index, row in resumen.iterrows():
        name = row['IA']
        score = row['Puntaje']
        icon_url = ias.get(name, "")
        medal = "🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "🏅"
        
        leaderboard_html += f"""
<tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background 0.2s;">
<td style="padding: 15px 12px; font-weight: bold; font-size: 1.3em;">{medal} {index + 1}</td>
<td style="padding: 15px 12px; display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 1.2em;">
<img src="{icon_url}" style="width: 28px; height: 28px; object-fit: contain; background: white; border-radius: 50%; padding: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);" alt="{name}">
<span>{name}</span>
</td>
<td style="padding: 15px 12px; text-align: right; font-weight: 900; font-size: 2.2em; color: #FFD700; text-shadow: 0 2px 5px rgba(0,0,0,0.5);">{score}</td>
</tr>
"""
    leaderboard_html += """
</tbody>
</table>
</div>
"""
    st.markdown(leaderboard_html, unsafe_allow_html=True)
    
    # Mostrar detalle de partidos agrupado
    st.markdown("<h2 style='color: white; font-weight: 800; font-size: 2.2em; margin-top: 40px; margin-bottom: 20px; text-shadow: 0 2px 5px rgba(0,0,0,0.5);'>Resultados y Predicciones por Partido</h2>", unsafe_allow_html=True)
    
    for idx, row in df_procesado.iterrows():
        # Tarjeta del partido
        with st.container():
            st.markdown(f"""
<div class="match-card">
<h3 style="text-align: center; color: #ffffff; margin-bottom: 5px; font-size: 1.8em; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">
{row.get('Local', 'Local')} {row.get('GolesLocal', '-')} : {row.get('GolesVisitante', '-')} {row.get('Visitante', 'Visitante')}
</h3>
<p style="text-align: center; color: #a0aec0; font-size: 15px; margin-bottom: 25px;">📅 Fecha: {row.get('Fecha', '')}</p>
<div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
<div class="ai-badge">
<strong style="color: #D97757; font-size: 1.2em;">Claude</strong><br>
<span style="font-size: 22px; color: #ffffff; font-weight: bold; text-shadow: 1px 1px 2px #000;">{row.get('Claude_L', '-')} - {row.get('Claude_V', '-')}</span><br>
<span style="color: #FFD700; font-weight: bold; background: rgba(255,215,0,0.1); padding: 4px 10px; border-radius: 12px; display: inline-block; margin-top: 8px;">+{row.get('Pts_Claude', 0)} pts</span>
</div>
<div class="ai-badge">
<strong style="color: #4D4B96; font-size: 1.2em;">DeepSeek</strong><br>
<span style="font-size: 22px; color: #ffffff; font-weight: bold; text-shadow: 1px 1px 2px #000;">{row.get('DeepSeek_L', '-')} - {row.get('DeepSeek_V', '-')}</span><br>
<span style="color: #FFD700; font-weight: bold; background: rgba(255,215,0,0.1); padding: 4px 10px; border-radius: 12px; display: inline-block; margin-top: 8px;">+{row.get('Pts_DeepSeek', 0)} pts</span>
</div>
<div class="ai-badge">
<strong style="color: #8E75B2; font-size: 1.2em;">Gemini</strong><br>
<span style="font-size: 22px; color: #ffffff; font-weight: bold; text-shadow: 1px 1px 2px #000;">{row.get('Gemini_L', '-')} - {row.get('Gemini_V', '-')}</span><br>
<span style="color: #FFD700; font-weight: bold; background: rgba(255,215,0,0.1); padding: 4px 10px; border-radius: 12px; display: inline-block; margin-top: 8px;">+{row.get('Pts_Gemini', 0)} pts</span>
</div>
<div class="ai-badge">
<strong style="color: #74aa9c; font-size: 1.2em;">ChatGPT</strong><br>
<span style="font-size: 22px; color: #ffffff; font-weight: bold; text-shadow: 1px 1px 2px #000;">{row.get('ChatGPT_L', '-')} - {row.get('ChatGPT_V', '-')}</span><br>
<span style="color: #FFD700; font-weight: bold; background: rgba(255,215,0,0.1); padding: 4px 10px; border-radius: 12px; display: inline-block; margin-top: 8px;">+{row.get('Pts_ChatGPT', 0)} pts</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)

else:
    st.warning("No hay datos cargados. Agrega pronósticos desde el panel de administración.")

# ---------- PANEL DE ADMIN (OCULTO) ----------
if "clicks" not in st.session_state:
    st.session_state.clicks = 0
if "last_click_time" not in st.session_state:
    st.session_state.last_click_time = time.time()
if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

footer_click = st.button(
    label="", 
    key="admin_hidden_btn",
    help="Haz clic 5 veces en 5 segundos para acceder al panel de admin",
    use_container_width=False
)

if footer_click:
    now = time.time()
    if now - st.session_state.last_click_time <= 5.0:
        st.session_state.clicks += 1
    else:
        st.session_state.clicks = 1
    st.session_state.last_click_time = now
    
    if st.session_state.clicks >= 5:
        st.session_state.show_admin = True
        st.session_state.clicks = 0
        st.success("🔓 Panel de administrador desbloqueado")

if st.session_state.show_admin:
    with st.sidebar:
        st.header("👑 Panel de Administración")
        st.info("Agrega o actualiza pronósticos")
        
        # Formulario para agregar partido
        with st.form("admin_form"):
            fecha = st.text_input("Fecha y hora (ej: 2026-06-20 15:00)")
            local = st.text_input("Equipo Local")
            visitante = st.text_input("Equipo Visitante")
            goles_local = st.number_input("Goles Local Real", min_value=0, step=1)
            goles_visitante = st.number_input("Goles Visitante Real", min_value=0, step=1)
            
            st.subheader("Pronósticos de las IAs")
            claude_l = st.number_input("Claude - Local", min_value=0, step=1)
            claude_v = st.number_input("Claude - Visitante", min_value=0, step=1)
            deepseek_l = st.number_input("DeepSeek - Local", min_value=0, step=1)
            deepseek_v = st.number_input("DeepSeek - Visitante", min_value=0, step=1)
            gemini_l = st.number_input("Gemini - Local", min_value=0, step=1)
            gemini_v = st.number_input("Gemini - Visitante", min_value=0, step=1)
            chatgpt_l = st.number_input("ChatGPT - Local", min_value=0, step=1)
            chatgpt_v = st.number_input("ChatGPT - Visitante", min_value=0, step=1)
            
            submitted = st.form_submit_button("Guardar Partido")
            if submitted:
                try:
                    sheet = conectar_sheets()
                    # Añadir nueva fila
                    nueva_fila = [fecha, local, visitante, goles_local, goles_visitante,
                                  claude_l, claude_v,
                                  deepseek_l, deepseek_v,
                                  gemini_l, gemini_v,
                                  chatgpt_l, chatgpt_v]
                    sheet.append_row(nueva_fila)
                    st.success("✅ Partido guardado correctamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
        
        if st.button("Cerrar panel de admin"):
            st.session_state.show_admin = False
            st.rerun()

# ---------- PIE DE PÁGINA ----------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding-bottom: 50px;">
    <p style="color: #8892b0; font-size: 14px;">⚽ Datos actualizados en tiempo real | Desarrollado con Streamlit</p>
    <a href="#top" target="_self" class="btn-top">⬆️ Regresar Arriba</a>
</div>
""", unsafe_allow_html=True)
