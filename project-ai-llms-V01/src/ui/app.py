# src/ui/app.py
import streamlit as st
import os
import sys
from dotenv import load_dotenv

# --- FIX DE RUTAS (PATH) ---
# Le decimos a Python que la carpeta raíz del proyecto está dos niveles más arriba
# para que entienda qué significa "from src.tools..."
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(ruta_raiz)

# LangChain / Classic Imports
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# IMPORTACIONES MODULARES (Ahora Python sí encontrará estas rutas)
from src.tools.finance import obtener_precio_accion
from src.tools.image_gen import generar_imagen_hf
from src.prompts.system_prompts import obtener_prompt_agente

# 1. FORZAMOS a que el .env machaque cualquier caché del sistema
load_dotenv(override=True)

# Lista oficial de herramientas que usará el Agente
herramientas = [obtener_precio_accion]

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Generador de Contenido", page_icon="🤖", layout="wide")

# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Configuración del Sistema")
    
    modelo_seleccionado = st.selectbox(
        "Selecciona el Motor de IA:",
        ("llama-3.1-8b-instant", "mixtral-8x7b-32768")
    )
    
    idioma_salida = st.selectbox(
        "🌐 Idioma de generación:",
        ("Castellano", "Inglés", "Francés", "Italiano")
    )
    
    st.subheader("Perfil de la Empresa")
    nombre_empresa = st.text_input("Nombre / Marca:", value="Digital Content")
    tono_empresa = st.text_area(
        "Tono y estilo:", 
        value="Somos una agencia de marketing moderna. Usamos un tono profesional pero cercano, siempre con algún emoji."
    )
    
    st.divider() 
    if st.button("🧹 Limpiar Chat y Aplicar Cambios"):
        st.session_state.mensajes = [] 
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🤖 Generador de Contenidos IA")

# Inicializar el motor LLM
llm = ChatGroq(
    temperature=0.7,
    model_name=modelo_seleccionado
)

# Inicializar la memoria en la sesión de Streamlit
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- CONFIGURACIÓN DEL AGENTE ---
# Inyectamos el prompt modular pasándole el estado actual de la UI
prompt_agente = obtener_prompt_agente(nombre_empresa, tono_empresa, idioma_salida)

# Conexión de la infraestructura del Agente
agente = create_tool_calling_agent(llm, herramientas, prompt_agente)
agent_executor = AgentExecutor(agent=agente, tools=herramientas, verbose=True)

# Renderizar el historial de conversación existente
for mensaje in st.session_state.mensajes:
    if isinstance(mensaje, HumanMessage):
        with st.chat_message("user"):
            st.markdown(mensaje.content)
    elif isinstance(mensaje, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(mensaje.content)

# --- BUCLE DE INTERACCIÓN EN TIEMPO REAL ---
if texto_usuario := st.chat_input("Ej: ¿A cuánto están las acciones de Apple y Amazon?"):
    
    # 1. Imprimir la entrada del usuario
    with st.chat_message("user"):
        st.markdown(texto_usuario)
    
    # 2. Orquestación del Agente
    with st.chat_message("assistant"):
        with st.spinner(f"Consultando fuentes y redactando con {modelo_seleccionado}... ⏳"):
            
            # Ejecución del pipeline del agente con histórico y entrada actual
            respuesta_agente = agent_executor.invoke({
                "input": texto_usuario,
                "chat_history": st.session_state.mensajes
            })
            
            texto_respuesta = respuesta_agente["output"]
            st.markdown(texto_respuesta)
        # --- SUB-PROCESO: GENERACIÓN DE IMAGEN CONTEXTUAL CON HUGGING FACE ---
        with st.spinner("Pintando imagen con Inteligencia Artificial... 🎨"):
            try:
                # 1. Le pedimos al LLM que invente un prompt descriptivo en inglés para la imagen
                prompt_creativo = f"Escribe un prompt en inglés de máximo 20 palabras para generar una imagen hiperrealista que acompañe a este texto. Solo el prompt, nada más. Texto: {texto_respuesta}"
                respuesta_hf_prompt = llm.invoke(prompt_creativo)
                prompt_imagen_limpio = respuesta_hf_prompt.content.strip()
                
                # 2. Llamamos a nuestra nueva herramienta de Hugging Face
                imagen_bytes = generar_imagen_hf(prompt_imagen_limpio)
                
                # 3. Streamlit renderiza directamente los bytes de la imagen generada
                st.image(imagen_bytes, caption=f"Prompt utilizado: '{prompt_imagen_limpio}'")
                
            except Exception as e:
                st.warning(f"No se pudo generar la imagen: {e}")
            
        # --- SUB-PROCESO: GENERACIÓN DE IMAGEN CONTEXTUAL ---
        # with st.spinner("Buscando imagen contextualizada... 🎨"):
        #     prompt_imagen = f"Analiza esta petición y devuelve UNA ÚNICA palabra clave en INGLÉS que sea un objeto físico relacionado. No escribas nada más. Petición: {texto_usuario}"
        #     respuesta_palabras = llm.invoke(prompt_imagen)
            
        #     palabra_clave = respuesta_palabras.content.strip().replace(".", "").replace('"', '').replace(" ", "").lower()
        #     url_imagen = f"https://loremflickr.com/800/400/{palabra_clave}/all"
            
        #     st.image(url_imagen, caption=f"Imagen para la etiqueta: '{palabra_clave}'")
            
        # 3. Persistencia en la memoria del sistema
        st.session_state.mensajes.append(HumanMessage(content=texto_usuario))
        st.session_state.mensajes.append(AIMessage(content=texto_respuesta))