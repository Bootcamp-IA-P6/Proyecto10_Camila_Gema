import streamlit as st
import streamlit.components.v1 as components
from src.config import MODELOS_DISPONIBLES
from src.generators.content_generator import generar_contenido
from src.generators.rag_generator import generar_divulgacion
from src.generators.news_generator import generar_newsletter
from src.generators.graph_rag_generator import generar_divulgacion_graph
from src.image_search import buscar_imagenes
from src.router.agent_router import enrutar_peticion
from src.graph_rag.graph_visualizer import visualizar_grafo

st.set_page_config(
    page_title="Faro",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# ESTILOS PERSONALIZADOS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,400..700&family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Paleta del faro: noche en alta mar */
    :root {
        --luz: #FFC04D;
        --luz-viva: #F2A53A;
        --ambar: #FFC65C;
        --dorado: #FFD98A;
        --crema: #F2EADB;
        --bruma: #B9C6D2;
        --noche: #081320;
        --halo: rgba(255, 198, 92, 0.35);
        --mar: #4E8FA0;
    }

    /* ---------- Fondo: noche en alta mar ---------- */
    .stApp {
        background:
            radial-gradient(ellipse 70% 40% at 50% -10%, rgba(255, 198, 92, 0.14), transparent 60%),
            radial-gradient(ellipse 90% 50% at 50% 115%, rgba(46, 110, 124, 0.22), transparent 65%),
            linear-gradient(180deg, #060D16 0%, #0C1B2A 50%, #0E2233 100%);
        background-attachment: fixed;
    }
    header[data-testid="stHeader"] { background: transparent; }

    /* ---------- Tipografía ---------- */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--crema);
    }
    .stApp p, .stApp li, .stApp label { color: var(--crema); }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Fraunces', Georgia, serif !important;
        color: var(--crema) !important;
        letter-spacing: -0.3px;
    }
    h5 { font-weight: 400 !important; color: var(--bruma) !important; }
    a { color: var(--ambar) !important; text-decoration: none; }
    a:hover { color: var(--dorado) !important; text-shadow: 0 0 12px rgba(255, 210, 122, 0.5); }
    ::selection { background: rgba(255, 198, 92, 0.4); }

    /* ---------- Luciérnagas sobre el mar ---------- */
    .destellos { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
    .destellos span {
        position: absolute;
        bottom: -12px;
        width: 5px; height: 5px;
        border-radius: 50%;
        background: radial-gradient(circle, #FFE9B0 0%, #FFB347 70%);
        box-shadow: 0 0 10px 2px rgba(255, 198, 92, 0.55);
        opacity: 0;
        animation: subir linear infinite;
    }
    .destellos span:nth-child(3n)  { width: 3px; height: 3px; }
    .destellos span:nth-child(4n)  { width: 7px; height: 7px; filter: blur(1px); }
    @keyframes subir {
        0%   { transform: translateY(0) translateX(0) scale(1); opacity: 0; }
        6%   { opacity: 0.9; }
        50%  { transform: translateY(-50vh) translateX(2vw) scale(0.7); opacity: 0.7; }
        100% { transform: translateY(-104vh) translateX(-2vw) scale(0.15); opacity: 0; }
    }

    /* ---------- Cabecera ---------- */
    .hero-faro { display: flex; align-items: center; gap: 22px; padding: 18px 0 6px 0; position: relative; }
    .logo-wrap { filter: drop-shadow(0 0 18px rgba(255, 198, 92, 0.55)); }
    .logo-wrap .luz-faro { animation: latido 2.4s ease-in-out infinite; transform-origin: 32px 16px; }
    @keyframes latido {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%      { opacity: 0.65; transform: scale(0.82); }
    }
    .logo-wrap .haz { animation: barrido 4.5s ease-in-out infinite; }
    .logo-wrap .haz-der { animation-delay: 2.25s; }
    @keyframes barrido {
        0%, 100% { opacity: 0.10; }
        50%      { opacity: 0.55; }
    }
    .logo-wrap .estrella { animation: titilar 3s ease-in-out infinite; }
    @keyframes titilar {
        0%, 100% { opacity: 0.25; }
        50%      { opacity: 1; }
    }
    .titulo-faro {
        margin: 0; padding: 0;
        font-family: 'Fraunces', serif;
        font-size: 54px; font-weight: 700; line-height: 1.05;
        background: linear-gradient(90deg, #FFE9B0 0%, #FFC04D 35%, #F2A53A 60%, #FFE9B0 85%);
        background-size: 250% auto;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fluir 7s linear infinite;
    }
    @keyframes fluir { to { background-position: 250% center; } }
    .tagline {
        margin: 4px 0 0 2px;
        color: var(--bruma);
        font-style: italic; font-size: 16px;
        font-family: 'Fraunces', serif;
        letter-spacing: 0.5px;
    }
    .divisoria-luz {
        height: 2px; border: none; margin: 4px 0 18px 0;
        background: linear-gradient(90deg, transparent, var(--luz) 18%, var(--dorado) 50%, var(--luz) 82%, transparent);
        opacity: 0.5;
    }

    /* ---------- Pestañas: píldoras de cristal ---------- */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(245, 233, 220, 0.14);
        border-radius: 999px;
        padding: 10px 22px;
        color: var(--bruma);
        font-weight: 600;
        backdrop-filter: blur(4px);
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        border-color: var(--halo);
        color: var(--crema);
        transform: translateY(-1px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FFC04D 0%, #E89B2D 100%) !important;
        color: #2A1C06 !important;
        border-color: transparent !important;
        box-shadow: 0 0 22px rgba(255, 198, 92, 0.45);
    }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

    /* ---------- Botones: metal fundido ---------- */
    .stButton button {
        position: relative; overflow: hidden;
        background: linear-gradient(135deg, #FFC04D 0%, #E89B2D 100%);
        color: #2A1C06;
        border: none; border-radius: 14px;
        padding: 12px 28px;
        font-weight: 700; font-family: 'Inter', sans-serif;
        letter-spacing: 0.3px;
        transition: all 0.25s ease;
        box-shadow: 0 0 18px rgba(255, 187, 77, 0.35), 0 4px 16px rgba(0, 0, 0, 0.4);
    }
    .stButton button::before {
        content: '';
        position: absolute; top: 0; left: -80%;
        width: 50%; height: 100%;
        background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.35), transparent);
        transform: skewX(-20deg);
        animation: destello 3.2s ease-in-out infinite;
    }
    @keyframes destello { 0%, 55% { left: -80%; } 100% { left: 130%; } }
    .stButton button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 0 34px rgba(255, 187, 77, 0.65), 0 6px 20px rgba(0, 0, 0, 0.45);
    }
    .stButton button:active { transform: translateY(0) scale(0.99); }

    /* ---------- Inputs: cristal oscuro ---------- */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(245, 233, 220, 0.18) !important;
        border-radius: 12px !important;
        color: var(--crema) !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--luz) !important;
        box-shadow: 0 0 0 3px rgba(255, 198, 92, 0.22) !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: rgba(217, 199, 178, 0.45) !important;
    }
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(245, 233, 220, 0.18) !important;
        border-radius: 12px !important;
        color: var(--crema) !important;
    }
    [data-baseweb="popover"] ul {
        background: #122334 !important;
        border: 1px solid rgba(255, 192, 77, 0.25) !important;
    }
    [data-baseweb="popover"] li { color: var(--crema) !important; }
    [data-baseweb="popover"] li:hover { background: rgba(255, 198, 92, 0.15) !important; }

    /* ---------- Alertas, expanders, métricas ---------- */
    .stAlert { border-radius: 14px; backdrop-filter: blur(4px); }
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(245, 233, 220, 0.12) !important;
        border-radius: 14px !important;
    }
    [data-testid="stExpander"] summary { color: var(--crema) !important; font-weight: 600; }
    [data-testid="stExpander"] summary:hover { color: var(--ambar) !important; }
    [data-testid="stMetric"] {
        background: linear-gradient(160deg, rgba(255, 192, 77, 0.10), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 192, 77, 0.25);
        border-radius: 16px;
        padding: 14px 18px;
        box-shadow: inset 0 0 24px rgba(255, 198, 92, 0.05);
    }
    [data-testid="stMetricValue"] { color: var(--dorado) !important; font-family: 'Fraunces', serif !important; }
    [data-testid="stMetricLabel"] { color: var(--bruma) !important; }
    [data-testid="stImage"] img { border-radius: 14px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45); }
    [data-testid="stCaptionContainer"] { color: var(--bruma) !important; }

    /* ---------- Divider y scrollbar ---------- */
    hr {
        border: none !important; height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255, 192, 77, 0.5), transparent) !important;
    }
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: var(--noche); }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #FFC04D, #8A5E14);
        border-radius: 99px;
    }

    /* ---------- Animación de entrada para resultados ---------- */
    @keyframes aparecer {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .resultado-anim { animation: aparecer 0.5s ease-out; }

    /* ---------- Badge de nivel ---------- */
    .badge-nivel {
        display: inline-block;
        background: linear-gradient(135deg, #FFC65C, #E8A33D);
        color: #2A1A0A;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 11px; font-weight: 800;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.8px;
        margin-left: 8px;
        vertical-align: middle;
        animation: pulso 2.6s ease-in-out infinite;
    }
    @keyframes pulso {
        0%, 100% { box-shadow: 0 0 8px rgba(255, 198, 92, 0.3); }
        50%      { box-shadow: 0 0 20px rgba(255, 198, 92, 0.6); }
    }
    .badge-experto {
        background: linear-gradient(135deg, #7FC8A9, #4E9678);
        color: #0C2018;
    }

    /* ---------- Tarjeta del agente: cristal incandescente ---------- */
    .tarjeta-agente {
        background: linear-gradient(160deg, rgba(255, 192, 77, 0.12), rgba(255, 255, 255, 0.03));
        border: 1px solid rgba(255, 192, 77, 0.30);
        border-left: 4px solid var(--luz);
        padding: 18px 22px;
        border-radius: 14px;
        margin: 14px 0;
        backdrop-filter: blur(6px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35), inset 0 0 30px rgba(255, 198, 92, 0.05);
        animation: aparecer 0.5s ease-out;
    }
    .tarjeta-agente-titulo {
        color: var(--crema);
        font-weight: 700; font-size: 17px;
        font-family: 'Fraunces', serif;
        margin-bottom: 4px;
    }
    .tarjeta-agente-texto { color: var(--bruma); font-size: 14px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CABECERA CON LOGO
# ============================================================
def cabecera():
    destellos = "".join(
        f'<span style="left:{izq}%; animation-duration:{dur}s; animation-delay:{ret}s;"></span>'
        for izq, dur, ret in [
            (4, 11, 0), (12, 14, 3), (19, 9, 6), (27, 13, 1), (34, 10, 5),
            (42, 15, 2), (51, 9, 7), (58, 12, 4), (66, 10, 0.5), (73, 14, 6.5),
            (81, 11, 2.5), (88, 13, 5.5), (94, 9, 1.5), (47, 16, 8),
        ]
    )
    st.markdown(f"""
    <div class="destellos">{destellos}</div>
    <div class="hero-faro">
        <div class="logo-wrap">
        <svg width="84" height="84" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="torre-grad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#F7EEDC"/>
                    <stop offset="100%" stop-color="#C9BDA4"/>
                </linearGradient>
                <linearGradient id="haz-izq-grad" x1="100%" y1="0%" x2="0%" y2="0%">
                    <stop offset="0%" stop-color="#FFD98A"/>
                    <stop offset="100%" stop-color="#FFD98A" stop-opacity="0"/>
                </linearGradient>
                <linearGradient id="haz-der-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#FFD98A"/>
                    <stop offset="100%" stop-color="#FFD98A" stop-opacity="0"/>
                </linearGradient>
            </defs>
            <!-- Haces de luz que barren -->
            <path class="haz" d="M 29 16 L 2 8 L 2 28 Z" fill="url(#haz-izq-grad)"/>
            <path class="haz haz-der" d="M 35 16 L 62 8 L 62 28 Z" fill="url(#haz-der-grad)"/>
            <!-- Estrellas -->
            <circle class="estrella" cx="12" cy="6" r="1.2" fill="#FFE9B0"/>
            <circle class="estrella" cx="52" cy="4" r="1" fill="#FFE9B0" style="animation-delay: 1.2s"/>
            <circle class="estrella" cx="58" cy="32" r="1.3" fill="#FFE9B0" style="animation-delay: 2s"/>
            <circle class="estrella" cx="6" cy="34" r="1" fill="#FFE9B0" style="animation-delay: 0.6s"/>
            <!-- Linterna -->
            <path d="M 26.5 12 L 37.5 12 L 32 6 Z" fill="#E2603F"/>
            <rect x="28" y="12" width="8" height="8" rx="1" fill="#1B2A3A" stroke="#FFC04D" stroke-width="0.8"/>
            <circle class="luz-faro" cx="32" cy="16" r="2.6" fill="#FFE9B0"/>
            <!-- Balcón -->
            <rect x="26" y="20" width="12" height="2" rx="1" fill="#1B2A3A"/>
            <!-- Torre con franjas -->
            <path d="M 28 22 L 36 22 L 40 52 L 24 52 Z" fill="url(#torre-grad)"/>
            <path d="M 26.9 31 L 37.1 31 L 37.8 36 L 26.2 36 Z" fill="#23415C"/>
            <path d="M 25.5 41 L 38.5 41 L 39.2 46 L 24.8 46 Z" fill="#23415C"/>
            <!-- Roca -->
            <ellipse cx="32" cy="53" rx="13" ry="3.5" fill="#16283A"/>
            <!-- Olas -->
            <path d="M 6 57 Q 11 54 16 57 T 26 57 T 36 57 T 46 57 T 56 57" stroke="#4E8FA0" stroke-width="1.6" fill="none" opacity="0.8"/>
            <path d="M 10 61 Q 15 58 20 61 T 30 61 T 40 61 T 50 61" stroke="#4E8FA0" stroke-width="1.4" fill="none" opacity="0.45"/>
        </svg>
        </div>
        <div>
            <h1 class="titulo-faro">Faro</h1>
            <p class="tagline">Luz para tus ideas</p>
        </div>
    </div>
    <hr class="divisoria-luz"/>
    """, unsafe_allow_html=True)


cabecera()

IDIOMAS = {
    "Español": "español",
    "Inglés": "inglés",
    "Francés": "francés",
    "Italiano": "italiano",
}

# Iconos para cada agente
AGENTES_INFO = {
    "contenido_general": {"icono": "✍️", "nombre": "Creador de contenido", "color": "#FFC04D"},
    "divulgacion_rag": {"icono": "🔬", "nombre": "Divulgador científico", "color": "#7FC8A9"},
    "newsletter_financiera": {"icono": "📈", "nombre": "Editor financiero", "color": "#FFD98A"},
}


def mostrar_evaluacion(evaluacion):
    p = evaluacion["puntuacion"]
    if p >= 4:
        st.success(f"✓ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")
    elif p >= 2:
        st.warning(f"⚠ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")
    else:
        st.error(f"✗ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")


def mostrar_resultado_rag_vectorial(explicacion, fuentes, evaluacion):
    st.markdown('<div class="resultado-anim">', unsafe_allow_html=True)
    st.markdown("### 📖 Explicación divulgativa")
    st.write(explicacion)
    mostrar_evaluacion(evaluacion)
    st.markdown("### 📚 Fuentes")
    unicas = {f["url"]: f for f in fuentes}.values()
    for f in unicas:
        st.markdown(f"- [{f['titulo']}]({f['url']})")
    st.markdown('</div>', unsafe_allow_html=True)


def mostrar_resultado_graph_rag(resultado):
    st.markdown('<div class="resultado-anim">', unsafe_allow_html=True)
    st.markdown("### 🕸️ Explicación divulgativa (Graph RAG)")
    st.write(resultado["explicacion"])
    mostrar_evaluacion(resultado["evaluacion"])

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nodos del grafo", resultado["stats_grafo"]["nodos"])
    with col2:
        st.metric("Relaciones", resultado["stats_grafo"]["aristas"])

    with st.expander("🔍 Ver relaciones del grafo usadas como contexto"):
        if resultado["contexto_grafo"]:
            for rel in resultado["contexto_grafo"]:
                st.markdown(f"- {rel}")
        else:
            st.info("No se encontraron coincidencias directas entre los términos de búsqueda y las entidades del grafo. El grafo se construyó pero la consulta no extrajo contexto específico.")

    with st.expander("🌐 Ver grafo de conocimiento interactivo"):
        html_grafo = visualizar_grafo(resultado["grafo"])
        components.html(html_grafo, height=520, scrolling=False)

    st.markdown("### 📚 Papers usados")
    for paper in resultado["papers"]:
        st.markdown(f"- [{paper['titulo']}]({paper['url']})")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PESTAÑAS PRINCIPALES
# ============================================================
tab_auto, tab_manual = st.tabs(["✨  Asistente inteligente", "🎛️  Modo manual"])

# ============================================================
# PESTAÑA 1: ASISTENTE INTELIGENTE (multiagente)
# ============================================================
with tab_auto:
    st.markdown('<span class="badge-nivel badge-experto">EXPERTO · MULTIAGENTE</span>', unsafe_allow_html=True)
    st.markdown("##### Escribe lo que quieres conseguir y el sistema elegirá el agente más adecuado.")

    peticion = st.text_area(
        "¿Qué necesitas?",
        placeholder="Ej: explícame cómo funcionan los transformers, o redacta un post de LinkedIn sobre productividad...",
        key="peticion_auto",
        height=100,
    )

    if st.button("🔆 Analizar y enrutar", key="btn_enrutar"):
        if peticion.strip():
            with st.spinner("El enrutador está decidiendo..."):
                decision = enrutar_peticion(peticion)
            st.session_state["agente_elegido"] = decision["agente"]
            st.session_state["justificacion_router"] = decision["justificacion"]
            st.session_state["peticion_original"] = peticion
        else:
            st.warning("Por favor, escribe una petición.")

    if "agente_elegido" in st.session_state:
        agente = st.session_state["agente_elegido"]
        info = AGENTES_INFO.get(agente, {"icono": "🤖", "nombre": agente, "color": "#6B5443"})

        st.markdown(f"""
        <div class="tarjeta-agente" style="border-left-color: {info['color']};">
            <div class="tarjeta-agente-titulo">{info['icono']}  Agente elegido: {info['nombre']}</div>
            <div class="tarjeta-agente-texto">{st.session_state['justificacion_router']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Completa los detalles para este agente")

        if agente == "contenido_general":
            col1, col2 = st.columns(2)
            with col1:
                plataforma = st.selectbox("Plataforma", ["Twitter/X", "LinkedIn", "Instagram", "Blog"], key="auto_plat")
                audiencia = st.text_input("Audiencia", placeholder="Ej: jóvenes profesionales", key="auto_aud")
                tono = st.text_input("Tono", placeholder="Ej: cercano y motivador", key="auto_tono")
            with col2:
                idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="auto_idi_gen")
                modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="auto_mod_gen")

            info_empresa = st.text_area("Información de la empresa (opcional)", key="auto_emp", height=80)

            if st.button("🔆 Generar contenido", key="btn_auto_gen"):
                if audiencia and tono:
                    info_emp = info_empresa if info_empresa else "No se ha proporcionado información específica de empresa; genera contenido genérico."
                    with st.spinner("Generando..."):
                        resultado = generar_contenido(
                            st.session_state["peticion_original"],
                            plataforma, audiencia, tono, modelo_e, info_emp, IDIOMAS[idioma_e],
                        )
                    st.markdown('<div class="resultado-anim">', unsafe_allow_html=True)
                    st.markdown("### ✍️ Resultado")
                    st.write(resultado)
                    st.markdown("### 🖼️ Imágenes sugeridas")
                    imgs = buscar_imagenes(st.session_state["peticion_original"], cantidad=3)
                    if imgs:
                        cols = st.columns(len(imgs))
                        for col, img in zip(cols, imgs):
                            with col:
                                st.image(img["url"], use_container_width=True)
                                st.caption(f"Foto de {img['autor']} (Pexels)")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("Rellena audiencia y tono.")

        elif agente == "divulgacion_rag":
            modo_rag = st.radio(
                "Modo de divulgación",
                ["RAG vectorial (papers indexados)", "Graph RAG (grafo de conocimiento)"],
                key="auto_modo_rag",
                help="Vectorial busca por significado en papers ya indexados. Graph RAG construye un grafo de conocimiento en vivo desde arXiv.",
                horizontal=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="auto_idi_rag")
            with col2:
                modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="auto_mod_rag")

            if st.button("🔆 Generar divulgación", key="btn_auto_rag"):
                if modo_rag.startswith("RAG vectorial"):
                    with st.spinner("Buscando papers indexados y generando..."):
                        explicacion, fuentes, evaluacion = generar_divulgacion(
                            st.session_state["peticion_original"], modelo_e, IDIOMAS[idioma_e],
                        )
                    mostrar_resultado_rag_vectorial(explicacion, fuentes, evaluacion)
                else:
                    with st.spinner("Construyendo grafo de conocimiento desde arXiv (puede tardar)..."):
                        resultado = generar_divulgacion_graph(
                            st.session_state["peticion_original"], modelo_e, IDIOMAS[idioma_e], cantidad_papers=2,
                        )
                    mostrar_resultado_graph_rag(resultado)

        elif agente == "newsletter_financiera":
            col1, col2 = st.columns(2)
            with col1:
                idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="auto_idi_news")
            with col2:
                modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="auto_mod_news")
            cantidad = st.slider("Número de noticias a analizar", 5, 15, 10, key="auto_cant")

            if st.button("🔆 Generar newsletter", key="btn_auto_news"):
                with st.spinner("Buscando noticias y redactando..."):
                    newsletter, noticias = generar_newsletter(modelo_e, IDIOMAS[idioma_e], cantidad_noticias=cantidad)
                st.markdown('<div class="resultado-anim">', unsafe_allow_html=True)
                st.markdown("### 📈 Newsletter del día")
                st.write(newsletter)
                st.markdown("### 📰 Fuentes")
                for n in noticias:
                    st.markdown(f"- **{n['fuente']}**: [{n['titular']}]({n['url']})")
                st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PESTAÑA 2: MODO MANUAL
# ============================================================
with tab_manual:
    st.markdown("##### Si prefieres elegir el agente tú misma, usa estas pestañas.")
    sub_general, sub_rag, sub_news = st.tabs([
        "✍️  Contenido general",
        "🔬  Divulgación científica (RAG)",
        "📈  Newsletter financiera",
    ])

    with sub_general:
        tema = st.text_input("Tema", placeholder="Ej: los beneficios del café", key="m_tema")
        col1, col2 = st.columns(2)
        with col1:
            plataforma = st.selectbox("Plataforma", ["Twitter/X", "LinkedIn", "Instagram", "Blog"], key="m_plat")
            audiencia = st.text_input("Audiencia", placeholder="Ej: jóvenes profesionales", key="m_aud")
            tono = st.text_input("Tono", placeholder="Ej: cercano y motivador", key="m_tono")
        with col2:
            idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="m_idi_gen")
            modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="m_mod_gen")
        info_empresa = st.text_area("Información de la empresa (opcional)", key="m_emp", height=80)

        if st.button("🔆 Generar contenido", key="m_btn_gen"):
            if tema and audiencia and tono:
                info_emp = info_empresa if info_empresa else "No se ha proporcionado información específica de empresa; genera contenido genérico."
                with st.spinner("Generando..."):
                    resultado = generar_contenido(tema, plataforma, audiencia, tono, modelo_e, info_emp, IDIOMAS[idioma_e])
                st.markdown('<div class="resultado-anim">', unsafe_allow_html=True)
                st.markdown("### ✍️ Resultado")
                st.write(resultado)
                st.markdown("### 🖼️ Imágenes sugeridas")
                imgs = buscar_imagenes(tema, cantidad=3)
                if imgs:
                    cols = st.columns(len(imgs))
                    for col, img in zip(cols, imgs):
                        with col:
                            st.image(img["url"], use_container_width=True)
                            st.caption(f"Foto de {img['autor']} (Pexels)")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Rellena todos los campos.")

    with sub_rag:
        st.markdown('<span class="badge-nivel">AVANZADO + EXPERTO</span>', unsafe_allow_html=True)
        tema_rag = st.text_input("Tema científico", key="m_tema_rag")
        modo_rag_m = st.radio(
            "Modo de divulgación",
            ["RAG vectorial (papers indexados)", "Graph RAG (grafo de conocimiento)"],
            key="m_modo_rag",
            horizontal=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="m_idi_rag")
        with col2:
            modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="m_mod_rag")

        if st.button("🔆 Generar divulgación", key="m_btn_rag"):
            if tema_rag:
                if modo_rag_m.startswith("RAG vectorial"):
                    with st.spinner("Buscando papers y generando..."):
                        explicacion, fuentes, evaluacion = generar_divulgacion(tema_rag, modelo_e, IDIOMAS[idioma_e])
                    mostrar_resultado_rag_vectorial(explicacion, fuentes, evaluacion)
                else:
                    with st.spinner("Construyendo grafo de conocimiento desde arXiv (puede tardar)..."):
                        resultado = generar_divulgacion_graph(tema_rag, modelo_e, IDIOMAS[idioma_e], cantidad_papers=2)
                    mostrar_resultado_graph_rag(resultado)

    with sub_news:
        st.markdown('<span class="badge-nivel">AVANZADO</span>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="m_idi_news")
        with col2:
            modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="m_mod_news")
        cantidad = st.slider("Número de noticias a analizar", 5, 15, 10, key="m_cant")

        if st.button("🔆 Generar newsletter", key="m_btn_news"):
            with st.spinner("Buscando noticias y redactando..."):
                newsletter, noticias = generar_newsletter(modelo_e, IDIOMAS[idioma_e], cantidad_noticias=cantidad)
            st.markdown('<div class="resultado-anim">', unsafe_allow_html=True)
            st.markdown("### 📈 Newsletter del día")
            st.write(newsletter)
            st.markdown("### 📰 Fuentes")
            for n in noticias:
                st.markdown(f"- **{n['fuente']}**: [{n['titular']}]({n['url']})")
            st.markdown('</div>', unsafe_allow_html=True)