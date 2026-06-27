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
    .stApp { background-color: #0e1117; }
    .bracket-card {
        background: #1e2330;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px;
        border: 1px solid #3a4050;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    .bracket-card img {
        width: 80px;
        height: 80px;
        object-fit: contain;
    }
    .bracket-card p {
        color: white;
        font-weight: bold;
        margin-top: 10px;
    }
    .copa-card {
        background: #1e2330;
        border-radius: 50%;
        padding: 20px;
        text-align: center;
        border: 2px solid #f1c40f;
        box-shadow: 0 0 20px #f1c40f55;
    }
    .copa-card img {
        width: 100px;
        height: 100px;
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
    .puntaje-highlight {
        font-weight: bold;
        color: #FFD700;
    }
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
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏆 IA WORLD CUP PREDICTOR CHALLENGE</h1>", unsafe_allow_html=True)

# ---------- BRACKET DE IAS ----------
st.markdown("## 🤖 ¿Quién será el mejor pronosticador?")

ias = {
    "Claude": "https://cdn.simpleicons.org/claude/D97757",
    "DeepSeek": "https://cdn.simpleicons.org/deepseek/4D4B96",
    "Gemini": "https://cdn.simpleicons.org/googlegemini/8E75B2",
    "ChatGPT": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg"
}

cols = st.columns(5)
with cols[0]:
    st.markdown(f"""
        <div class="bracket-card">
            <img src="{ias['Claude']}" alt="Claude">
            <p>Claude</p>
        </div>
    """, unsafe_allow_html=True)
with cols[1]:
    st.markdown(f"""
        <div class="bracket-card">
            <img src="{ias['DeepSeek']}" alt="DeepSeek">
            <p>DeepSeek</p>
        </div>
    """, unsafe_allow_html=True)
with cols[2]:
    # Logo oficial del Mundial 2026 (con fondo colorido)
    logo_url = "https://digitalhub.fifa.com/transform/4e622b7f-3db3-441f-8012-c2e36696dbf1/FIFA-World-Cup-2026-Brand-Launch-Generic-News-Article-Header"
    st.markdown(f"""
        <div class="bracket-card copa-card" style="border-color: #ffffff; box-shadow: 0 0 20px #ffffff55;">
            <img src="{logo_url}" alt="Copa" style="width: 120px; height: 120px; object-fit: contain;">
            <p style="color: #ffffff;">🏆 CAMPEÓN</p>
        </div>
    """, unsafe_allow_html=True)
with cols[3]:
    st.markdown(f"""
        <div class="bracket-card">
            <img src="{ias['Gemini']}" alt="Gemini">
            <p>Gemini</p>
        </div>
    """, unsafe_allow_html=True)
with cols[4]:
    st.markdown(f"""
        <div class="bracket-card">
            <img src="{ias['ChatGPT']}" alt="ChatGPT">
            <p>ChatGPT</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------- CARGAR Y MOSTRAR DATOS ----------
df = cargar_datos()
if not df.empty:
    df_procesado = procesar_puntuaciones(df)
    
    # Mostrar tabla principal
    st.subheader("📊 Tabla de Posiciones")
    
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
    
    # Mostrar tabla de posiciones ocultando el índice
    st.dataframe(resumen, use_container_width=True, hide_index=True)
    
    # Mostrar detalle de partidos agrupado
    st.subheader("📋 Resultados y Predicciones por Partido")
    
    for idx, row in df_procesado.iterrows():
        # Tarjeta del partido
        with st.container():
            st.markdown(f"""
<div style="background-color: #1e2330; border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 1px solid #3a4050;">
<h3 style="text-align: center; color: #ffffff; margin-bottom: 5px;">
{row.get('Local', 'Local')} {row.get('GolesLocal', '-')} : {row.get('GolesVisitante', '-')} {row.get('Visitante', 'Visitante')}
</h3>
<p style="text-align: center; color: #8892b0; font-size: 14px; margin-bottom: 15px;">Fecha: {row.get('Fecha', '')}</p>
<div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
<div style="text-align: center; background: #2a3040; padding: 10px; border-radius: 8px; width: 22%;">
<strong style="color: #D97757;">Claude</strong><br>
<span style="font-size: 18px;">{row.get('Claude_L', '-')} - {row.get('Claude_V', '-')}</span><br>
<span style="color: #FFD700; font-weight: bold;">+{row.get('Pts_Claude', 0)} pts</span>
</div>
<div style="text-align: center; background: #2a3040; padding: 10px; border-radius: 8px; width: 22%;">
<strong style="color: #4D4B96;">DeepSeek</strong><br>
<span style="font-size: 18px;">{row.get('DeepSeek_L', '-')} - {row.get('DeepSeek_V', '-')}</span><br>
<span style="color: #FFD700; font-weight: bold;">+{row.get('Pts_DeepSeek', 0)} pts</span>
</div>
<div style="text-align: center; background: #2a3040; padding: 10px; border-radius: 8px; width: 22%;">
<strong style="color: #8E75B2;">Gemini</strong><br>
<span style="font-size: 18px;">{row.get('Gemini_L', '-')} - {row.get('Gemini_V', '-')}</span><br>
<span style="color: #FFD700; font-weight: bold;">+{row.get('Pts_Gemini', 0)} pts</span>
</div>
<div style="text-align: center; background: #2a3040; padding: 10px; border-radius: 8px; width: 22%;">
<strong style="color: #74aa9c;">ChatGPT</strong><br>
<span style="font-size: 18px;">{row.get('ChatGPT_L', '-')} - {row.get('ChatGPT_V', '-')}</span><br>
<span style="color: #FFD700; font-weight: bold;">+{row.get('Pts_ChatGPT', 0)} pts</span>
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
st.caption("⚽ Datos actualizados en tiempo real | Desarrollado con Streamlit")
