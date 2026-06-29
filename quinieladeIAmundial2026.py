import streamlit as st  # ✅ Solo una vez
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time
import json
import streamlit.components.v1 as components

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

# ---------- ESTILOS CSS BLOQUE 1: Base, Hero, Tipografía ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Rajdhani:wght@400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-deep: #0E1117;
        --bg-elevated: #161B22;
        --surface: #1C212B;
        --accent-gold: #DFB76C;
        --accent-amber: #C99A49;
        --text-primary: #F0F2F5;
        --text-secondary: #8B949E;
        --claude: #E07A4B;
        --gemini: #4A90D9;
        --chatgpt: #5BB87D;
        --deepseek: #8B6EC7;
    }

    .stApp {
        background: linear-gradient(180deg, #0E1117 0%, #161B22 50%, #0E1117 100%) !important;
        background-attachment: fixed !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: var(--text-primary);
    }

    header[data-testid="stHeader"] { background: transparent !important; }
    .stApp > footer { visibility: hidden; }
    hr { border-color: rgba(255, 255, 255, 0.06) !important; margin: 40px 0 !important; }

    .main h1, .main h2, .main h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stImage"] img {
        filter: drop-shadow(0 0 35px rgba(223, 183, 108, 0.12));
        animation: logo-fade-in 1.2s ease-out forwards;
    }
    @keyframes logo-fade-in {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }

    .hero-title {
        font-family: 'Rajdhani', sans-serif !important;
        text-align: center;
        background: linear-gradient(135deg, #DFB76C 0%, #C99A49 50%, #DFB76C 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3em;
        line-height: 1.1;
        margin-bottom: 0;
        letter-spacing: -0.02em;
        animation: shimmer-gold 4s ease-in-out infinite;
    }
    @keyframes shimmer-gold {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .typewriter-cursor {
        display: inline-block;
        color: var(--accent-gold);
        font-weight: 700;
        margin-left: 2px;
        animation: cursor-blink 0.75s step-end infinite;
    }
    @keyframes cursor-blink {
        from, to { opacity: 0; }
        50% { opacity: 1; }
    }

    .section-header {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 2em !important;
        color: var(--text-primary) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding-left: 16px;
        border-left: 4px solid var(--accent-gold);
        margin-top: 40px;
        margin-bottom: 24px;
        -webkit-text-fill-color: initial;
    }

    .section-subheader {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.3em !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 15px;
    }

    .rules-ticker {
        background: var(--bg-elevated);
        border-left: 4px solid var(--accent-gold);
        border-radius: 0 12px 12px 0;
        padding: 20px 24px;
        max-width: 700px;
        margin: 40px auto;
        font-family: 'IBM Plex Sans', sans-serif;
        color: var(--text-secondary);
        line-height: 1.9;
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-left: 4px solid var(--accent-gold);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .rules-ticker .rules-title {
        color: var(--text-primary);
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.3em;
        font-weight: 700;
        display: block;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    .rules-ticker .pts-value {
        color: var(--accent-gold);
        font-family: 'Oswald', sans-serif;
        font-weight: 600;
        font-size: 1.05em;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- ESTILOS CSS BLOQUE 2: Grid, Cards, Badges ----------
st.markdown("""
    <style>
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

    .bracket-card {
        background: var(--bg-elevated);
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        margin: 10px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-bottom: 3px solid var(--text-secondary);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: transform 0.25s ease-out, box-shadow 0.25s ease-out;
        opacity: 0;
        animation: fade-in-fast 0.6s ease-out forwards;
    }
    .bracket-card.ia-claude { border-bottom-color: var(--claude); }
    .bracket-card.ia-gemini { border-bottom-color: var(--gemini); }
    .bracket-card.ia-chatgpt { border-bottom-color: var(--chatgpt); }
    .bracket-card.ia-deepseek { border-bottom-color: var(--deepseek); }

    .bracket-card.ia-claude:hover { box-shadow: 0 8px 35px rgba(224, 122, 75, 0.25); }
    .bracket-card.ia-gemini:hover { box-shadow: 0 8px 35px rgba(74, 144, 217, 0.25); }
    .bracket-card.ia-chatgpt:hover { box-shadow: 0 8px 35px rgba(91, 184, 125, 0.25); }
    .bracket-card.ia-deepseek:hover { box-shadow: 0 8px 35px rgba(139, 110, 199, 0.25); }

    .bracket-card:hover { transform: translateY(-6px) scale(1.03); }

    .fifa-container {
        opacity: 0;
        animation: fade-in-fast 0.6s ease-out forwards;
        animation-delay: 0.1s;
    }
    .llm-card-1 { animation-delay: 0.5s; }
    .llm-card-2 { animation-delay: 0.6s; }
    .llm-card-3 { animation-delay: 0.7s; }
    .llm-card-4 { animation-delay: 0.8s; }

    @keyframes fade-in-fast {
        from { opacity: 0; transform: scale(0.9) translateY(10px); }
        to { opacity: 1; transform: scale(1) translateY(0); }
    }

    .bracket-card img {
        width: 60px;
        height: 60px;
        max-width: 60px;
        max-height: 60px;
        object-fit: contain;
    }
    .bracket-card p {
        color: var(--text-primary);
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        margin-top: 15px;
        font-size: 1.15em;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .copa-card {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .fifa-container img {
        width: 220px !important;
        height: 220px !important;
        object-fit: contain;
        filter: drop-shadow(0 0 40px rgba(223, 183, 108, 0.15));
        transition: transform 0.3s ease-out;
    }
    .fifa-container img:hover { transform: scale(1.08); }
    </style>
""", unsafe_allow_html=True)

# ---------- ESTILOS CSS BLOQUE 3: Match Cards, Buttons, Responsive, Animations ----------
st.markdown("""
    <style>
    .match-card {
        background: var(--bg-elevated);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.25s ease-out, box-shadow 0.25s ease-out, border-color 0.25s ease-out;
        opacity: 0;
        animation: fade-in-up 0.8s ease-out forwards;
    }
    .match-card:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
    }

    .match-score-line {
        font-family: 'Oswald', sans-serif;
        font-weight: 700;
        font-size: 2.2em;
        text-align: center;
        color: var(--text-primary);
        margin-bottom: 4px;
        letter-spacing: 1px;
    }
    .match-date {
        text-align: center;
        color: var(--text-secondary);
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.9em;
        margin-bottom: 24px;
    }
    .match-predictions {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 10px;
    }

    .ai-badge {
        text-align: center;
        background: rgba(0, 0, 0, 0.25);
        padding: 16px 12px;
        border-radius: 12px;
        width: 23%;
        min-width: 120px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        transition: transform 0.2s ease-out, background 0.2s ease-out, box-shadow 0.2s ease-out;
    }
    .ai-badge:hover { transform: scale(1.04); background: rgba(0, 0, 0, 0.4); }
    .ai-badge.ia-claude:hover { box-shadow: 0 4px 20px rgba(224, 122, 75, 0.2); }
    .ai-badge.ia-gemini:hover { box-shadow: 0 4px 20px rgba(74, 144, 217, 0.2); }
    .ai-badge.ia-chatgpt:hover { box-shadow: 0 4px 20px rgba(91, 184, 125, 0.2); }
    .ai-badge.ia-deepseek:hover { box-shadow: 0 4px 20px rgba(139, 110, 199, 0.2); }

    .ai-badge-name {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 1.15em;
        margin-bottom: 8px;
    }
    .ai-badge-score {
        font-family: 'Oswald', sans-serif;
        font-weight: 600;
        font-size: 1.5em;
        color: var(--text-primary);
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }

    .pts-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-family: 'Oswald', sans-serif;
        font-weight: 600;
        font-size: 0.95em;
        letter-spacing: 0.5px;
    }
    .pts-badge.pts-5 {
        background: linear-gradient(135deg, rgba(223, 183, 108, 0.25), rgba(201, 154, 73, 0.15));
        color: var(--accent-gold);
        border: 1px solid rgba(223, 183, 108, 0.3);
        animation: celebration-pulse 0.6s ease-out 0.8s both;
    }
    .pts-badge.pts-3 {
        background: rgba(201, 154, 73, 0.12);
        color: var(--accent-amber);
        border: 1px solid rgba(201, 154, 73, 0.2);
    }
    .pts-badge.pts-2 {
        background: rgba(255, 255, 255, 0.06);
        color: var(--text-secondary);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .pts-badge.pts-0 {
        background: transparent;
        color: rgba(123, 136, 156, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.04);
        opacity: 0.6;
    }
    @keyframes celebration-pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(223, 183, 108, 0.4); }
        50% { transform: scale(1.15); box-shadow: 0 0 20px 4px rgba(223, 183, 108, 0.2); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(223, 183, 108, 0); }
    }

    .btn-top {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: linear-gradient(135deg, var(--surface), var(--bg-elevated));
        color: var(--accent-gold) !important;
        padding: 12px 24px;
        border-radius: 30px;
        text-decoration: none;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        z-index: 1000;
        transition: all 0.25s ease-out;
        border: 1px solid rgba(223, 183, 108, 0.2);
    }
    .btn-top:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7);
        text-decoration: none;
        border-color: rgba(223, 183, 108, 0.5);
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

    .today-header {
        display: flex;
        align-items: center;
        margin: 20px 0 15px 0;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 1.4em;
        letter-spacing: 1.5px;
    }
    .live-dot {
        width: 10px;
        height: 10px;
        background-color: #ff3b30;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7);
        animation: live-pulse 1.5s infinite;
        display: inline-block;
    }
    @keyframes live-pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(255, 59, 48, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); }
    }
    .live-text {
        color: #ff4d4d;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 77, 77, 0.2);
    }
    .no-matches-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px dashed rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        color: var(--text-secondary);
        font-family: 'IBM Plex Sans', sans-serif;
        font-style: italic;
        margin-bottom: 30px;
    }

    @keyframes fade-in-up {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .reveal-on-scroll {
        opacity: 0;
        animation: fade-in-up 0.8s ease-out forwards;
        animation-delay: 0.2s;
    }

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
        .fifa-container img { width: 180px !important; height: 180px !important; }
        .ai-badge { width: 45% !important; margin-bottom: 10px; }
        .hero-title { font-size: 2em !important; }
        .bracket-card img { width: 50px !important; height: 50px !important; max-width: 50px !important; max-height: 50px !important; }
        .match-score-line { font-size: 1.6em; }
        .section-header { font-size: 1.5em !important; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-delay: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
        .bracket-card, .match-card, .reveal-on-scroll { opacity: 1 !important; transform: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ---------- TYPEWRITER JS via components.html ----------
components.html("""
<script>
    const parentDoc = window.parent.document;
    const typeEl = parentDoc.getElementById("typewriter-text");
    if (typeEl && !typeEl.dataset.started) {
        typeEl.dataset.started = "true";
        const text = "Las IA compiten para ver quién es mejor prediciendo los partidos del mundial 2026";
        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                typeEl.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 40);
            }
        }
        setTimeout(typeWriter, 400);
    }
</script>
""", height=0, width=0)

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
        <h1 class='hero-title' style='font-size: 2.5em; line-height: 1.2; margin-bottom: 30px;'>
            <span id="typewriter-text"></span><span class="typewriter-cursor">|</span>
        </h1>
    """, unsafe_allow_html=True)

# ---------- BRACKET DE IAS (INVERTIDO - AHORA ARRIBA DE LAS REGLAS) ----------
st.markdown("<h2 class='section-header'>🤖 ¿Quién será el mejor pronosticador?</h2>", unsafe_allow_html=True)

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
    <div class="bracket-card llm-card-1 ia-claude">
        <img src="{ias['Claude']}" alt="Claude">
        <p>Claude</p>
    </div>
    <div class="bracket-card llm-card-2 ia-gemini">
        <img src="{ias['Gemini']}" alt="Gemini">
        <p>Gemini</p>
    </div>
    <div class="fifa-container">
        <img src="{logo_url}" alt="FIFA 2026">
    </div>
    <div class="bracket-card llm-card-3 ia-deepseek">
        <img src="{ias['DeepSeek']}" alt="DeepSeek">
        <p>DeepSeek</p>
    </div>
    <div class="bracket-card llm-card-4 ia-chatgpt">
        <img src="{ias['ChatGPT']}" alt="ChatGPT">
        <p>ChatGPT</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- REGLAS DE PUNTUACIÓN (AHORA DEBAJO DE LAS IMÁGENES CON SCROLL REVEAL) ----------
st.markdown("""
    <div class="rules-ticker reveal-on-scroll">
        <strong class="rules-title">REGLAS DE PUNTUACIÓN</strong>
        🎯 Por acierto de marcador exacto suman <span class="pts-value">5 puntos</span><br>
        ✅ Por acertar ganador y diferencia de goles suman <span class="pts-value">3 puntos</span><br>
        ✔️ Por acertar solo el ganador suman <span class="pts-value">2 puntos</span><br>
        ❌ Todo lo demás es <span class="pts-value">0 puntos</span><br>
        <em style="display: block; margin-top: 10px; color: #F0F2F5;">¡Que ruede el balón y veamos quién será la mejor analizadora!</em>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ---------- CARGAR Y MOSTRAR DATOS ----------
df = cargar_datos()
if not df.empty:
    df_procesado = procesar_puntuaciones(df)
    
    # Mostrar tabla principal (sin emoji de trofeo, con scroll reveal)
    st.markdown("<h2 class='section-header reveal-on-scroll'>TABLA DE POSICIONES</h2>", unsafe_allow_html=True)
    
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
    
    # ---------- SCOREBOARD (ELEMENTO FIRMA) via components.html ----------
    ia_colors = {"Claude": "#E07A4B", "DeepSeek": "#8B6EC7", "Gemini": "#4A90D9", "ChatGPT": "#5BB87D"}
    max_score = max(int(resumen['Puntaje'].max()), 1)
    
    # Build scoreboard rows
    sb_rows = ""
    for index, row in resumen.iterrows():
        name = row['IA']
        score = int(row['Puntaje'])
        icon_url = ias.get(name, "")
        color = ia_colors.get(name, "#7B889C")
        pct = round((score / max_score) * 100)
        leader = "leader" if index == 0 else ""
        medal = "🥇" if index == 0 else ("🥈" if index == 1 else ("🥉" if index == 2 else ""))
        
        sb_rows += f'''
        <div class="sb-row {leader}">
            <div class="sb-pos">
                <span class="sb-medal">{medal}</span> {index + 1}
            </div>
            <div class="sb-info">
                <div class="sb-name-row">
                    <img class="sb-icon" src="{icon_url}" alt="{name}">
                    <span class="sb-name">{name}</span>
                </div>
                <div class="sb-progress">
                    <div class="sb-fill" data-width="{pct}%" style="background: linear-gradient(90deg, {color}, {color}aa);"></div>
                </div>
            </div>
            <div class="sb-score" data-target="{score}">0</div>
        </div>
        '''
    
    # Scoreboard CSS (Option C + Leader Gold Blinking)
    sb_css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
        margin: 0;
        padding: 4px 0;
        background: transparent;
        overflow: hidden;
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .sb-container {
        background: #161B22;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
        max-width: 720px;
        margin: 0 auto;
    }

    .sb-header {
        background: linear-gradient(135deg, #DFB76C 0%, #C99A49 100%);
        padding: 14px 24px;
        display: flex;
        align-items: center;
    }

    .sb-header-text {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 1.3em;
        color: #0E1117;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .sb-row {
        display: grid;
        grid-template-columns: 55px 1fr 90px;
        align-items: center;
        padding: 16px 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        transition: background 0.3s ease;
    }
    .sb-row:last-child { border-bottom: none; }

    @keyframes gold-pulse {
        0% { background: linear-gradient(90deg, rgba(223, 183, 108, 0.08) 0%, transparent 70%); }
        50% { background: linear-gradient(90deg, rgba(223, 183, 108, 0.28) 0%, transparent 70%); }
        100% { background: linear-gradient(90deg, rgba(223, 183, 108, 0.08) 0%, transparent 70%); }
    }

    .sb-row.leader {
        border-left: 4px solid #DFB76C;
        padding-left: 20px;
        animation: gold-pulse 2s infinite ease-in-out;
    }

    .sb-pos {
        font-family: 'Oswald', sans-serif;
        font-weight: 700;
        font-size: 1.4em;
        color: #7B889C;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .sb-row.leader .sb-pos { color: #DFB76C; }

    .sb-medal { font-size: 1.1em; }

    .sb-info { display: flex; flex-direction: column; gap: 8px; }

    .sb-name-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .sb-icon {
        width: 28px;
        height: 28px;
        object-fit: contain;
        border-radius: 50%;
        padding: 4px;
        background: rgba(255, 255, 255, 0.08);
    }

    .sb-name {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        font-size: 1.15em;
        color: #F0F2F5;
    }

    .sb-progress {
        width: 100%;
        height: 5px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 3px;
        overflow: hidden;
    }

    .sb-fill {
        height: 100%;
        border-radius: 3px;
        width: 0%;
        transition: width 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }

    .sb-score {
        font-family: 'Oswald', sans-serif;
        font-weight: 700;
        font-size: 2.4em;
        text-align: right;
        color: #F0F2F5;
        line-height: 1;
        font-variant-numeric: tabular-nums;
    }
    .sb-row.leader .sb-score { color: #DFB76C; }

    @media (max-width: 600px) {
        .sb-row { grid-template-columns: 40px 1fr 70px; padding: 12px 16px; }
        .sb-score { font-size: 1.8em; }
        .sb-header { padding: 12px 16px; }
        .sb-header-text { font-size: 1.1em; }
    }

    @media (prefers-reduced-motion: reduce) {
        .sb-fill { transition: none; }
    }
    """
    
    # Scoreboard JS (regular string)
    sb_js = """
    function animateCounter(el, target, duration) {
        const start = performance.now();
        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    setTimeout(function() {
        document.querySelectorAll('.sb-fill').forEach(function(el) {
            var targetWidth = el.getAttribute('data-width');
            if (prefersReducedMotion) { el.style.transition = 'none'; }
            el.style.width = targetWidth;
        });

        document.querySelectorAll('.sb-score').forEach(function(el) {
            var target = parseInt(el.getAttribute('data-target'));
            if (prefersReducedMotion) {
                el.textContent = target;
            } else {
                animateCounter(el, target, 1500);
            }
        });
    }, 300);
    """
    
    # Assemble scoreboard HTML
    scoreboard_component = (
        "<!DOCTYPE html><html><head>"
        "<link href='https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Rajdhani:wght@400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap' rel='stylesheet'>"
        "<style>" + sb_css + "</style>"
        "</head><body>"
        "<div class='sb-container'>"
        "<div class='sb-header'>"
        "<span class='sb-header-text'>TABLA DE POSICIONES</span>"
        "</div>"
        + sb_rows +
        "</div>"
        "<script>" + sb_js + "</script>"
        "</body></html>"
    )
    
    sb_height = len(resumen) * 76 + 68
    components.html(scoreboard_component, height=sb_height)
    
    # ---------- RESULTADOS Y PREDICCIONES POR PARTIDO ----------
    st.markdown("<h2 class='section-header reveal-on-scroll' style='margin-top: 40px;'>RESULTADOS Y PREDICCIONES</h2>", unsafe_allow_html=True)
    
    # Indicator mapping for points
    _ind = {5: "✅", 3: "🟡", 2: "✔️", 0: "❌"}
    
    # Detección y ordenación de partidos por fecha (formato MM/DD/YYYY, ej: 6/30/2026)
    date_col = 'Fecha/Hora' if 'Fecha/Hora' in df_procesado.columns else 'Fecha'
    
    # Parseo robusto de fecha
    df_procesado['datetime_parsed'] = pd.to_datetime(df_procesado[date_col], format='%m/%d/%Y', errors='coerce')
    null_mask = df_procesado['datetime_parsed'].isna()
    if null_mask.any():
        df_procesado.loc[null_mask, 'datetime_parsed'] = pd.to_datetime(df_procesado.loc[null_mask, date_col], errors='coerce')
    
    # Obtener el día de hoy
    today = datetime.now().date()
    
    # Separar partidos de hoy
    today_mask = df_procesado['datetime_parsed'].dt.date == today
    df_today = df_procesado[today_mask]
    
    # Partidos restantes (excluyendo hoy)
    df_remaining = df_procesado[~today_mask].copy()
    df_remaining = df_remaining.sort_values(by='datetime_parsed', ascending=False, na_position='last')
    # Filter only matches that occurred before today (exclude future matches)
    df_past = df_remaining[df_remaining['datetime_parsed'].dt.date < today].copy()
    
    # Render card helper
    def render_match_card(row, idx):
        pc = int(row.get('Pts_Claude', 0))
        pd_ = int(row.get('Pts_DeepSeek', 0))
        pg = int(row.get('Pts_Gemini', 0))
        pch = int(row.get('Pts_ChatGPT', 0))
        display_date = row.get(date_col, '')
        
        st.markdown(f"""
<div class="match-card">
<div class="match-score-line">
{row.get('Local', 'Local')} {row.get('GolesLocal', '-')} : {row.get('GolesVisitante', '-')} {row.get('Visitante', 'Visitante')}
</div>
<div class="match-date">📅 {display_date}</div>
<div class="match-predictions">
<div class="ai-badge ia-claude">
<div class="ai-badge-name" style="color: var(--claude);">Claude</div>
<div class="ai-badge-score">{row.get('Claude_L', '-')} - {row.get('Claude_V', '-')}</div>
<span class="pts-badge pts-{pc}">{_ind.get(pc, "❌")} +{pc} pts</span>
</div>
<div class="ai-badge ia-deepseek">
<div class="ai-badge-name" style="color: var(--deepseek);">DeepSeek</div>
<div class="ai-badge-score">{row.get('DeepSeek_L', '-')} - {row.get('DeepSeek_V', '-')}</div>
<span class="pts-badge pts-{pd_}">{_ind.get(pd_, "❌")} +{pd_} pts</span>
</div>
<div class="ai-badge ia-gemini">
<div class="ai-badge-name" style="color: var(--gemini);">Gemini</div>
<div class="ai-badge-score">{row.get('Gemini_L', '-')} - {row.get('Gemini_V', '-')}</div>
<span class="pts-badge pts-{pg}">{_ind.get(pg, "❌")} +{pg} pts</span>
</div>
<div class="ai-badge ia-chatgpt">
<div class="ai-badge-name" style="color: var(--chatgpt);">ChatGPT</div>
<div class="ai-badge-score">{row.get('ChatGPT_L', '-')} - {row.get('ChatGPT_V', '-')}</div>
<span class="pts-badge pts-{pch}">{_ind.get(pch, "❌")} +{pch} pts</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    # 1. Mostrar partidos de hoy
    st.markdown("""
        <div class="today-header reveal-on-scroll">
            <span class="live-dot"></span><span class="live-text">PARTIDOS DE HOY</span>
        </div>
    """, unsafe_allow_html=True)
    
    if not df_today.empty:
        df_today_sorted = df_today.sort_values(by='datetime_parsed', ascending=True)
        for idx, row in df_today_sorted.iterrows():
            render_match_card(row, idx)
    else:
        st.markdown("""
            <div class="no-matches-card reveal-on-scroll">
                No hay partidos programados para hoy
            </div>
        """, unsafe_allow_html=True)

    # 2. Mostrar los últimos 5 partidos (excluyendo hoy)
    if not df_remaining.empty:
        st.markdown("<h3 class='section-subheader reveal-on-scroll' style='margin-top: 30px;'>ÚLTIMOS 5 PARTIDOS ANTERIORES A HOY</h3>", unsafe_allow_html=True)
        df_last_5 = df_past.iloc[:5]
        for idx, row in df_last_5.iterrows():
            render_match_card(row, idx)
            
        # 3. Mostrar el resto de los partidos en un expansor
        df_rest = df_remaining.iloc[5:]
        if not df_rest.empty:
            with st.expander("VER EL RESTO DE LOS PARTIDOS"):
                for idx, row in df_rest.iterrows():
                    render_match_card(row, idx)

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
            fecha = st.text_input("Fecha y hora (ej: 6/30/2026 15:00)")
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
    <p style="color: var(--text-secondary); font-family: 'IBM Plex Sans', sans-serif; font-size: 14px;">⚽ Datos actualizados en tiempo real · Desarrollado con Streamlit</p>
    <a href="#top" target="_self" class="btn-top">⬆️ Regresar Arriba</a>
</div>
""", unsafe_allow_html=True)
