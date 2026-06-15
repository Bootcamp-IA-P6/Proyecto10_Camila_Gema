import streamlit as st
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.enrutador import enrutar
from src.agents.agente_ciencia import crear_agente_ciencia
from src.agents.agente_finanzas import crear_agente_finanzas
from src.agents.agente_contenido import crear_agente_contenido
from src.utils.image_gen import generar_imagen_hf
from src.tools.guardarrailes import evaluar_respuesta, mostrar_resultado_evaluacion

load_dotenv(override=True)

_groq_key = os.getenv("GROQ_API_KEY", "")

st.set_page_config(
    page_title="NexusAI — Agent Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-base:        #13131f;
    --bg-card:        #1e1e35;
    --bg-input:       #252545;
    --accent-purple:  #8b7cf8;
    --accent-blue:    #60a5fa;
    --accent-cyan:    #34d399;
    --accent-amber:   #fbbf24;
    --text-primary:   #f0efff;
    --text-secondary: #a8a8c8;
    --text-muted:     #6b6b8f;
    --border:         rgba(139,124,248,0.2);
    --border-bright:  rgba(139,124,248,0.35);
    --glow-purple:    rgba(139,124,248,0.2);
    --linkedin:       #0A66C2;
    --instagram:      #E4405F;
    --twitter:        #1DA1F2;
}

html, body, .stApp {
    background: radial-gradient(ellipse at top left, #1a1535 0%, #13131f 40%, #0f1825 100%) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 20px !important;
    color: var(--text-primary) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1e38 0%, #171728 60%, #13131f 100%) !important;
    border-right: 1px solid var(--border-bright) !important;
    min-width: 320px !important;
}
[data-testid="stSidebar"] > div { padding: 2rem 1.75rem !important; }

[data-testid="stSidebar"] label {
    color: var(--text-secondary) !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background: rgba(37, 37, 69, 0.8) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    font-size: 1.15rem !important;
    padding: 14px 16px !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(37, 37, 69, 0.8) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    font-size: 1.15rem !important;
    min-height: 54px !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(30, 30, 53, 0.9) !important;
    border-radius: 18px !important;
    padding: 8px !important;
    border: 1px solid var(--border-bright) !important;
    gap: 6px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #ffffff !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
    padding: 22px 42px !important;
    border: none !important;
    min-height: 70px !important;
    white-space: nowrap !important;
}
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] div,
.stTabs [data-baseweb="tab"] p,
button[data-baseweb="tab"] span {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #ffffff !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #8b7cf8, #60a5fa) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 16px rgba(139,124,248,0.45) !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: rgba(30, 30, 53, 0.7) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    margin-bottom: 1.25rem !important;
    padding: 2rem 2.25rem !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] ul,
[data-testid="stChatMessage"] ol,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] code {
    color: #e8e8ff !important;
    font-size: 1.25rem !important;
    line-height: 1.9 !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: rgba(37, 37, 69, 0.95) !important;
    border: 2px solid var(--border-bright) !important;
    border-radius: 18px !important;
    padding: 8px !important;
    min-height: 80px !important;
}
[data-testid="stChatInput"] textarea {
    background: rgba(37, 37, 69, 0.95) !important;
    color: #f0efff !important;
    font-size: 1.3rem !important;
    line-height: 1.6 !important;
    border: none !important;
    box-shadow: none !important;
    caret-color: #8b7cf8 !important;
    -webkit-text-fill-color: #f0efff !important;
    padding: 14px 18px !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(168, 168, 200, 0.6) !important;
    -webkit-text-fill-color: rgba(168, 168, 200, 0.6) !important;
    font-size: 1.3rem !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent-purple) !important;
    box-shadow: 0 0 0 3px var(--glow-purple) !important;
}

/* ── BOTONES GENERALES ── */
.stButton > button {
    background: linear-gradient(135deg, #8b7cf8 0%, #60a5fa 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 1.2rem !important;
    padding: 1rem 2rem !important;
    min-height: 60px !important;
    box-shadow: 0 4px 16px rgba(139,124,248,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(139,124,248,0.5) !important;
}

/* ── COMPONENTES ── */
.agent-card {
    background: linear-gradient(135deg, rgba(30,30,53,0.9), rgba(37,37,69,0.6));
    border: 1px solid var(--border-bright);
    border-radius: 20px;
    padding: 2rem 2.25rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: linear-gradient(135deg, rgba(37,37,69,0.9), rgba(30,30,53,0.7));
    border: 1px solid var(--border-bright);
    border-radius: 18px;
    padding: 2rem 1.5rem;
    text-align: center;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.5rem;
    font-weight: 600;
    background: linear-gradient(135deg, #8b7cf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label {
    color: #a8a8c8;
    font-size: 1.1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 8px;
}
.badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 16px; border-radius: 22px;
    font-size: 1rem; font-weight: 700;
    letter-spacing: 0.04em; text-transform: uppercase;
}
.badge-active  { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-science { background: rgba(139,124,248,0.15); color: #a78bfa; border: 1px solid rgba(139,124,248,0.3); }
.badge-finance { background: rgba(251,191,36,0.15);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
.badge-content { background: rgba(96,165,250,0.15);  color: #60a5fa; border: 1px solid rgba(96,165,250,0.3); }

.divider {
    border: none; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,124,248,0.3), transparent);
    margin: 1.75rem 0;
}

/* ── BOTONES DE PLATAFORMA ── */
.platform-linkedin, .platform-instagram, .platform-twitter {
    display: flex; align-items: center; gap: 16px;
    padding: 22px 24px; border-radius: 16px;
    cursor: pointer; transition: all 0.25s ease;
    text-decoration: none; width: 100%;
}
.platform-linkedin {
    background: linear-gradient(135deg, #0A66C2, #0052A3);
    border: 2px solid rgba(10,102,194,0.5);
}
.platform-instagram {
    background: linear-gradient(135deg, #E4405F, #C13584, #833AB4);
    border: 2px solid rgba(228,64,95,0.5);
}
.platform-twitter {
    background: linear-gradient(135deg, #1DA1F2, #0D8BD9);
    border: 2px solid rgba(29,161,242,0.5);
}
.platform-linkedin:hover, .platform-instagram:hover, .platform-twitter:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}
.platform-icon { font-size: 2.5rem; line-height: 1; }
.platform-name { font-size: 1.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.01em; }
.platform-desc { font-size: 1rem; color: rgba(255,255,255,0.75); margin-top: 2px; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,124,248,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 2rem;'>
        <div style='display:flex; align-items:center; gap:14px; margin-bottom:16px;'>
            <div style='width:56px; height:56px; border-radius:16px; flex-shrink:0;
                        background:linear-gradient(135deg,#8b7cf8,#60a5fa);
                        display:flex; align-items:center; justify-content:center;
                        font-size:1.6rem; box-shadow:0 6px 20px rgba(139,124,248,0.4);'>⚡</div>
            <div>
                <div style='font-size:1.6rem; font-weight:800; color:#f0efff;'>NexusAI</div>
                <div style='font-size:1rem; color:#6b6b8f; font-weight:500;'>Agent Hub · Enterprise</div>
            </div>
        </div>
        <span class="badge badge-active">● Agente General Activo</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("<div style='font-size:1rem; color:#6b6b8f; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem;'>⚙️ Configuración</div>", unsafe_allow_html=True)

    modelo_seleccionado = st.selectbox("🤖 Motor de IA", ("llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"))
    idioma_salida = st.selectbox("🌐 Idioma de salida", ("Castellano", "Inglés", "Francés", "Italiano"))

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("<div style='font-size:1rem; color:#6b6b8f; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem;'>🏢 Perfil de Empresa</div>", unsafe_allow_html=True)

    nombre_empresa = st.text_input("Nombre / Marca", value="Digital Content")
    tono_empresa = st.text_area("Tono y estilo", value="Agencia de marketing moderna. Tono profesional pero cercano, con emojis.", height=100)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.button("🧹 Limpiar conversación", use_container_width=True):
        for k in ["msgs_chat","msgs_ciencia","msgs_finanzas","msgs_contenido"]:
            st.session_state[k] = []
        st.rerun()

    st.markdown(f"""
    <div style='margin-top:1.25rem; padding:1.25rem; background:rgba(139,124,248,0.08);
                border:1px solid rgba(139,124,248,0.25); border-radius:14px;'>
        <div style='font-size:1rem; color:#6b6b8f; text-transform:uppercase;
                    letter-spacing:0.08em; margin-bottom:12px; font-weight:700;'>Estado del sistema</div>
        <div style='display:flex; flex-direction:column; gap:10px;'>
            <div style='display:flex; justify-content:space-between; font-size:1.1rem;'>
                <span style='color:#a8a8c8;'>Modelo</span>
                <span style='color:#8b7cf8; font-family:JetBrains Mono,monospace;
                             font-size:1rem; font-weight:600;'>{modelo_seleccionado}</span>
            </div>
            <div style='display:flex; justify-content:space-between; font-size:1.1rem;'>
                <span style='color:#a8a8c8;'>Idioma</span>
                <span style='color:#34d399; font-weight:600;'>{idioma_salida}</span>
            </div>
            <div style='display:flex; justify-content:space-between; font-size:1.1rem;'>
                <span style='color:#a8a8c8;'>Empresa</span>
                <span style='color:#60a5fa; font-weight:600;'>{nombre_empresa}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# LLM + SESSION STATE
# ═══════════════════════════════════════════
if not _groq_key:
    st.error("❌ GROQ_API_KEY no encontrada. Añade la variable en tu .env local.", icon="🔑")
    st.stop()

llm = ChatGroq(temperature=0.7, model_name=modelo_seleccionado, api_key=_groq_key)
for k in ["msgs_chat","msgs_ciencia","msgs_finanzas","msgs_contenido"]:
    if k not in st.session_state:
        st.session_state[k] = []


# ═══════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.markdown("""
    <h1 style='font-size:5rem; font-weight:800; color:#f0efff;
               letter-spacing:-0.03em; margin:0;'>Orquestador de Agentes</h1>
    <p style='color:#a8a8c8; font-size:1.3rem; margin:10px 0 0;'>
        Crea y distribuye contenido de alta precisión impulsado por inteligencia artificial.
    </p>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown("""
    <div style='display:flex; gap:10px; justify-content:flex-end;
                align-items:center; padding-top:1rem; flex-wrap:wrap;'>
        <span class="badge badge-science">🔬 Ciencia RAG</span>
        <span class="badge badge-finance">📈 Finanzas</span>
        <span class="badge badge-content">✍️ Social</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════
def renderizar_historial(msgs):
    for msg in msgs:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)


def _ejecutar_y_mostrar(texto, key, resp, imagen=True):
    with st.chat_message("assistant"):

        with st.spinner("Evaluando calidad... 🔍"):
            groq_key   = os.getenv("GROQ_API_KEY", "")
            evaluacion = evaluar_respuesta(
                pregunta=texto,
                respuesta=resp,
                idioma_esperado=idioma_salida,
                groq_key=groq_key
            )

        st.markdown(resp)

        aviso = mostrar_resultado_evaluacion(evaluacion)
        if aviso:
            st.markdown(aviso)

        with st.expander(f"📊 Evaluación de calidad — Media: {evaluacion['puntuacion_media']}/10"):
            col1, col2, col3 = st.columns(3)
            with col1:
                color = "green" if evaluacion["puntuacion_relevancia"] >= 6 else "red"
                st.markdown("**Relevancia**")
                st.markdown(f":{color}[{evaluacion['puntuacion_relevancia']}/10]")
            with col2:
                color = "green" if evaluacion["puntuacion_calidad"] >= 6 else "red"
                st.markdown("**Calidad**")
                st.markdown(f":{color}[{evaluacion['puntuacion_calidad']}/10]")
            with col3:
                color = "green" if evaluacion["puntuacion_idioma"] >= 6 else "red"
                st.markdown("**Idioma**")
                st.markdown(f":{color}[{evaluacion['puntuacion_idioma']}/10]")

            detalles = evaluacion.get("detalles", {})
            if "relevancia" in detalles:
                st.caption(f"💬 {detalles['relevancia'].get('comentario','')}")
            if "calidad" in detalles:
                st.caption(f"💬 {detalles['calidad'].get('comentario','')}")
            if "idioma" in detalles:
                st.caption(f"💬 {detalles['idioma'].get('comentario','')}")

        if imagen:
            with st.spinner("Generando imagen... 🎨"):
                try:
                    p = llm.invoke(
                        f"Generate a SHORT English image prompt of max 8 words "
                        f"for a visual concept about: {texto}"
                    ).content.strip()
                    st.image(generar_imagen_hf(p), caption=f"🎨 {p}")
                except Exception as e:
                    st.caption(f"⚠️ Imagen no disponible: {e}")

    st.session_state[key].append(HumanMessage(content=texto))
    st.session_state[key].append(AIMessage(content=resp))


def traducir_respuesta(texto: str, idioma_salida: str) -> str:
    idiomas_map = {
        "Castellano": "Spanish",
        "Inglés":     "English",
        "Francés":    "French",
        "Italiano":   "Italian"
    }
    idioma_llm = idiomas_map.get(idioma_salida, idioma_salida)

    if idioma_llm == "Spanish":
        return texto

    prompt_traduccion = (
        f"Translate the following text to {idioma_llm}. "
        f"Keep all emojis, hashtags and formatting exactly as they are. "
        f"Return ONLY the translated text, nothing else:\n\n{texto}"
    )

    try:
        resp = llm.invoke(prompt_traduccion)
        return resp.content.strip()
    except Exception:
        return texto


def procesar(texto, key, imagen=True):
    with st.chat_message("user"):
        st.markdown(texto)

    with st.spinner("Procesando con IA... ⚡"):
        resp = enrutar(
            mensaje=texto, historial=st.session_state[key],
            llm=llm, nombre_empresa=nombre_empresa,
            tono_empresa=tono_empresa, idioma_salida=idioma_salida
        )
        resp = traducir_respuesta(resp, idioma_salida)
        st.markdown(resp)

    _ejecutar_y_mostrar(texto, key, resp, imagen)


def procesar_directo(texto, key, agente_fn, categoria_esperada, imagen=True):
    with st.chat_message("user"):
        st.markdown(texto)

    prompt_validacion = f"""
    Classify this message into ONE of these categories:
    - "ciencia": questions about AI, technology, science, research, deep learning
    - "finanzas": questions about stocks, prices, financial markets, tickers
    - "contenido": requests for social media posts, Instagram, LinkedIn, Twitter

    Message: "{texto}"

    Reply with ONLY one word: ciencia, finanzas or contenido
    """

    try:
        categoria_detectada = llm.invoke(prompt_validacion).content.strip().lower()
        for cat in ["ciencia", "finanzas", "contenido"]:
            if cat in categoria_detectada:
                categoria_detectada = cat
                break
    except Exception:
        categoria_detectada = categoria_esperada

    if categoria_detectada != categoria_esperada:
        pestañas = {
            "ciencia":   "🔬 Contenido Científico",
            "finanzas":  "📈 Contenido de Finanzas",
            "contenido": "✍️ Redes Sociales"
        }
        pestaña_correcta = pestañas.get(categoria_detectada, "💬 Contenido General")

        with st.chat_message("assistant"):
            st.warning(f"""
⚠️ **Esta pregunta no corresponde a esta sección.**

Tu pregunta parece ser sobre **{categoria_detectada}**.
Por favor ve a la pestaña **{pestaña_correcta}** para obtener la mejor respuesta.

También puedes usar la pestaña **💬 Contenido General** donde el enrutador
detecta automáticamente qué agente necesitas.
            """)
        return

    with st.spinner("Procesando con IA... ⚡"):
        agente = agente_fn(llm, nombre_empresa, tono_empresa, idioma_salida)
        resultado = agente.invoke({
            "input": texto,
            "chat_history": st.session_state[key]
        })
        resp = resultado["output"]
    resp = traducir_respuesta(resp, idioma_salida)

    _ejecutar_y_mostrar(texto, key, resp, imagen)


# ═══════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Contenido General",
    "🔬 Contenido Científico",
    "📈 Contenido de Finanzas",
    "✍️ Redes Sociales",
    "⚙️ Sistema",
])


# ── TAB 1 ────────────────────────────────
with tab1:
    st.markdown("""
    <div class="agent-card">
        <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
            <div>
                <div style='font-size:2.5rem; font-weight:800; color:#f0efff;'>🧠 Agente General</div>
                <div style='font-size:2rem; color:#a8a8c8; margin-top:8px; line-height:1.7;'>
                    El enrutador detecta automáticamente si tu pregunta es sobre
                    <b style='color:#a78bfa;'>ciencia</b>,
                    <b style='color:#fbbf24;'>finanzas</b> o
                    <b style='color:#60a5fa;'>contenido social</b>
                    y la envía al agente especializado correcto.
                </div>
            </div>
            <span class="badge badge-active" style='flex-shrink:0; margin-left:1.5rem;'>● Activo</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    renderizar_historial(st.session_state.msgs_chat)
    if p := st.chat_input("Describe qué quieres generar...", key="ci1"):
        procesar(p, "msgs_chat")


# ── TAB 2 ────────────────────────────────
with tab2:
    st.markdown("""
    <div class="agent-card" style='border-color:rgba(139,124,248,0.5);
         background:linear-gradient(135deg,rgba(139,124,248,0.1),rgba(30,30,53,0.9));'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
            <div>
                <div style='font-size:2.5rem; font-weight:800; color:#f0efff;'>🔬 Agente Científico</div>
                <div style='font-size:2rem; color:#a8a8c8; margin-top:8px; line-height:1.7;'>
                    Consulta nuestra base de datos de papers académicos sobre
                    <b style='color:#a78bfa;'>Inteligencia Artificial</b>.
                    Respuestas basadas en investigación real, sin alucinaciones.
                </div>
            </div>
            <span class="badge badge-science" style='flex-shrink:0; margin-left:1.5rem;'>RAG Local</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    renderizar_historial(st.session_state.msgs_ciencia)
    if p := st.chat_input("Pregunta sobre IA, deep learning, NLP...", key="ci2"):
        procesar_directo(p, "msgs_ciencia", crear_agente_ciencia, "ciencia")


# ── TAB 3 ────────────────────────────────
with tab3:
    st.markdown("""
    <div class="agent-card" style='border-color:rgba(251,191,36,0.5);
         background:linear-gradient(135deg,rgba(251,191,36,0.08),rgba(30,30,53,0.9));'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
            <div>
                <div style='font-size:2.5rem; font-weight:800; color:#f0efff;'>📈 Agente Financiero</div>
                <div style='font-size:2rem; color:#a8a8c8; margin-top:8px; line-height:1.7;'>
                    Precios de acciones en <b style='color:#fbbf24;'>tiempo real</b> vía yfinance.
                </div>
            </div>
            <span class="badge badge-finance" style='flex-shrink:0; margin-left:1.5rem;'>Tiempo Real</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:1.15rem; color:#6b6b8f; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:1rem;'>⚡ Acceso rápido</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, label, query in [
        (c1, "🍎 Apple",     "¿A cuánto está Apple (AAPL)?"),
        (c2, "🚗 Tesla",     "¿A cuánto está Tesla (TSLA)?"),
        (c3, "📦 Amazon",    "¿A cuánto está Amazon (AMZN)?"),
        (c4, "🏦 Santander", "¿A cuánto está Banco Santander (SAN.MC)?"),
    ]:
        with col:
            if st.button(label, use_container_width=True, key=f"t_{label}"):
                procesar_directo(query, "msgs_finanzas", crear_agente_finanzas, "finanzas", imagen=False)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    renderizar_historial(st.session_state.msgs_finanzas)
    if p := st.chat_input("Pregunta sobre acciones y mercados...", key="ci3"):
        procesar_directo(p, "msgs_finanzas", crear_agente_finanzas, "finanzas", imagen=False)


# ── TAB 4 — REDES SOCIALES ───────────────
with tab4:
    st.markdown("""
    <div class="agent-card" style='border-color:rgba(96,165,250,0.5);
         background:linear-gradient(135deg,rgba(96,165,250,0.08),rgba(30,30,53,0.9));'>
        <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
            <div>
                <div style='font-size:2.5rem; font-weight:800; color:#f0efff;'>✍️ Agente de Contenido Social</div>
                <div style='font-size:2rem; color:#a8a8c8; margin-top:8px; line-height:1.7;'>
                    Posts <b style='color:#60a5fa;'>listos para publicar</b>.
                    Selecciona la plataforma y describe tu contenido.
                </div>
            </div>
            <span class="badge badge-content" style='flex-shrink:0; margin-left:1.5rem;'>3 Plataformas</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:1.15rem; color:#6b6b8f; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:1.25rem;'>🎯 Selecciona plataforma</div>", unsafe_allow_html=True)

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        st.markdown("""
        <div class="platform-linkedin">
            <div class="platform-icon">💼</div>
            <div>
                <div class="platform-name">LinkedIn</div>
                <div class="platform-desc">Optimizado para B2B</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Seleccionar LinkedIn", use_container_width=True, key="btn_li"):
            st.session_state["plataforma"] = "LinkedIn"

    with pc2:
        st.markdown("""
        <div class="platform-instagram">
            <div class="platform-icon">📸</div>
            <div>
                <div class="platform-name">Instagram</div>
                <div class="platform-desc">Visual & Engagement</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Seleccionar Instagram", use_container_width=True, key="btn_ig"):
            st.session_state["plataforma"] = "Instagram"

    with pc3:
        st.markdown("""
        <div class="platform-twitter">
            <div class="platform-icon">🐦</div>
            <div>
                <div class="platform-name">X / Twitter</div>
                <div class="platform-desc">Noticias & Tendencias</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Seleccionar Twitter", use_container_width=True, key="btn_tw"):
            st.session_state["plataforma"] = "Twitter/X"

    if "plataforma" in st.session_state:
        st.markdown(f"""
        <div style='margin:1rem 0; padding:16px 24px; background:rgba(96,165,250,0.1);
                    border:1px solid rgba(96,165,250,0.3); border-radius:14px;
                    font-size:1.2rem; color:#60a5fa; font-weight:700;'>
            ✓ Plataforma activa: <b>{st.session_state["plataforma"]}</b>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    renderizar_historial(st.session_state.msgs_contenido)
    ph = f"Describe el contenido para {st.session_state.get('plataforma','tu red social')}..."
    if p := st.chat_input(ph, key="ci4"):
        plat = st.session_state.get("plataforma", "")
        if plat:
            p = f"Crea contenido para {plat}: {p}"
        procesar_directo(p, "msgs_contenido", crear_agente_contenido, "contenido")


# ── TAB 5 ────────────────────────────────
with tab5:
    st.markdown("""
    <h2 style='font-size:2.5rem; font-weight:800; color:#f0efff; margin:0 0 0.5rem;'>
        ⚙️ Sistema y Arquitectura
    </h2>
    <p style='color:#a8a8c8; font-size:1.2rem; margin:0 0 2rem;'>
        Información técnica del orquestador multiagente.
    </p>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    for col, val, label in [(m1,"3","Agentes IA"),(m2,"3","Plataformas"),(m3,"4","Idiomas"),(m4,"1","Enrutador")]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown("<div style='font-size:1.3rem; font-weight:800; color:#f0efff; margin-bottom:1rem;'>🏗️ Arquitectura</div>", unsafe_allow_html=True)
        st.code("""
Usuario escribe mensaje
        ↓
  Enrutador (LLM clasifica)
        ↓
┌─────────┬─────────┬─────────┐
│Ciencia  │Finanzas │Contenido│
│RAG Local│yfinance │  LLM    │
└─────────┴─────────┴─────────┘
        """, language="text")
    with cb:
        st.markdown("<div style='font-size:1.3rem; font-weight:800; color:#f0efff; margin-bottom:1rem;'>🛠️ Stack Tecnológico</div>", unsafe_allow_html=True)
        for tech, desc, color in [
            ("LangChain","Agentes y RAG","#8b7cf8"),
            ("Groq","Inferencia ultrarrápida","#60a5fa"),
            ("FAISS","Vector DB local","#34d399"),
            ("HuggingFace","Modelo de embeddings","#fbbf24"),
            ("yfinance","Datos financieros","#fbbf24"),
            ("Streamlit","Interfaz web","#60a5fa"),
        ]:
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        padding:14px 0; border-bottom:1px solid rgba(139,124,248,0.12);
                        font-size:1.15rem;'>
                <span style='color:{color}; font-weight:700;
                             font-family:JetBrains Mono,monospace;'>{tech}</span>
                <span style='color:#a8a8c8;'>{desc}</span>
            </div>
            """, unsafe_allow_html=True)
