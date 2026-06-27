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

# ---------- BLOQUE DE DEPURACIÓN DE SECRETS ----------
st.write("### 🔍 Depuración de Secrets")
st.write("Contenido completo de st.secrets:", st.secrets)

if "sheets" in st.secrets:
    st.write("✅ La clave 'sheets' EXISTE")
    st.write("Contenido de sheets:", st.secrets["sheets"])
    if "sheet_id" in st.secrets["sheets"]:
        st.write("✅ 'sheet_id' EXISTE dentro de sheets")
        st.write("Valor de sheet_id:", st.secrets["sheets"]["sheet_id"])
    else:
        st.write("❌ 'sheet_id' NO EXISTE dentro de sheets")
else:
    st.write("❌ La clave 'sheets' NO EXISTE en st.secrets")
    st.write("Las claves disponibles son:", list(st.secrets.keys()))
# ---------- FIN DEL BLOQUE DE DEPURACIÓN ----------

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

# ---------- FUNCIÓN PARA CALCULAR PUNTAJE ----------
def calcular_puntaje(local_real, visit_real, local_pro, visit_pro):
    if local_pro == local_real and visit_pro == visit_real:
        return 5
    dif_real = local_real - visit_real
    dif_pro = local_pro - visit_pro
    if dif_real * dif_pro > 0 and abs(dif_real) == abs(dif_pro):
        return 3
    if dif_real * dif_pro > 0:
        return 2
    return 0

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
def procesar_puntuaciones(df):
    ias = ["Claude", "DeepSeek", "Gemini", "ChatGPT"]
    for ia in ias:
        col_l = f"{ia}_L"
        col_v = f"{ia}_V"
        df[f"Pts_{ia}"] = df.apply(
            lambda row: calcular_puntaje(
                row["GolesLocal"], row["GolesVisitante"],
                row[col_l], row[col_v]
            ) if pd.notna(row["GolesLocal"]) and pd.notna(row["GolesVisitante"]) else 0,
            axis=1
        )
    return df
# ---------- LOGO Y CABECERA ----------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏆 IA WORLD CUP PREDICTOR CHALLENGE</h1>", unsafe_allow_html=True)

# ---------- BRACKET DE IAS ----------
st.markdown("## 🤖 ¿Quién será el mejor pronosticador?")

ias = {
    "Claude": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/claude.svg",
    "DeepSeek": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/deepseek.svg",
    "Gemini": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/google.svg",
    "ChatGPT": "https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/openai.svg"
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
    st.markdown(f"""
        <div class="bracket-card copa-card">
            <img src="logo.png" alt="Copa">
            <p style="color: #FFD700;">🏆 CAMPEÓN</p>
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
        "Puntaje Total": [
            df_procesado["Total_Claude"].iloc[-1] if not df_procesado.empty else 0,
            df_procesado["Total_DeepSeek"].iloc[-1] if not df_procesado.empty else 0,
            df_procesado["Total_Gemini"].iloc[-1] if not df_procesado.empty else 0,
            df_procesado["Total_ChatGPT"].iloc[-1] if not df_procesado.empty else 0
        ]
    }).sort_values("Puntaje Total", ascending=False)
    
    st.dataframe(resumen, use_container_width=True)
    
    # Mostrar detalle de partidos
    st.subheader("📋 Detalle de Partidos")
    # Seleccionar columnas a mostrar (ajusta según tus columnas)
    columnas_mostrar = ["Fecha", "Local", "Visitante", "GolesLocal", "GolesVisitante",
                        "Claude_L", "Claude_V", "Pts_Claude",
                        "DeepSeek_L", "DeepSeek_V", "Pts_DeepSeek",
                        "Gemini_L", "Gemini_V", "Pts_Gemini",
                        "ChatGPT_L", "ChatGPT_V", "Pts_ChatGPT"]
    # Filtrar solo las que existen
    columnas_existentes = [col for col in columnas_mostrar if col in df_procesado.columns]
    st.dataframe(df_procesado[columnas_existentes], use_container_width=True)

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
