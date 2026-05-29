import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
import urllib.parse
from dotenv import load_dotenv

# 1. FORZAMOS a que el .env machaque cualquier caché del sistema
load_dotenv(override=True)

# 2. DEBUG: Imprimimos los primeros 10 caracteres de la clave en tu terminal
# (Así comprobamos qué está leyendo Python exactamente)
clave_actual = os.getenv("LANGCHAIN_API_KEY")
if clave_actual:
    print(f"🛠️ DEBUG - La clave que está usando Python empieza por: {clave_actual[:10]}...")
else:
    print("❌ DEBUG - ERROR: Python dice que la clave está VACÍA. No encuentra el .env")


# Configuración de la página
st.set_page_config(page_title="Generador de Contenido", page_icon="🤖", layout="wide")

# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Configuración del Sistema")
    
    # 1. Selector de LLMs (100% Cloud)
    modelo_seleccionado = st.selectbox(
        "Selecciona el Motor de IA:",
        ("llama-3.1-8b-instant", "mixtral-8x7b-32768")
    )
    
    # NUEVO: Selector de Idioma
    idioma_salida = st.selectbox(
        "🌐 Idioma de generación:",
        ("Castellano", "Inglés", "Francés", "Italiano")
    )
    
    # 2. Contexto de la Empresa / Persona
    st.subheader("Perfil de la Empresa")
    nombre_empresa = st.text_input("Nombre / Marca:", value="Digital Content")
    tono_empresa = st.text_area(
        "Tono y estilo (Ej. formal, desenfadado, técnico):", 
        value="Somos una agencia de marketing moderna. Usamos un tono profesional pero cercano, siempre con algún emoji."
    )
    
    #  Botón de reseteo/limpieza de chat por si se cambia la empresa o el tono y queremos empezar de nuevo sin perder tiempo borrando mensajes uno a uno.
    st.divider() 
    if st.button("🧹 Limpiar Chat y Aplicar Cambios"):
        st.session_state.mensajes = [] 
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🤖 Generador de Contenidos IA")

# Inicializar el motor con el modelo seleccionado en el Sidebar
llm = ChatGroq(
    temperature=0.7,
    model_name=modelo_seleccionado
)

# Inicializar la memoria y configurar el System Prompt dinámico
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Si la memoria está vacía, inyectamos la personalidad usando los datos del Sidebar
if len(st.session_state.mensajes) == 0:
    prompt_sistema = f"""
    Eres un experto creador de contenido. Trabajas para {nombre_empresa}.
    Tu estilo de comunicación debe seguir estrictamente estas reglas: {tono_empresa}
    Adapta siempre el contenido a la plataforma que te pida el usuario.
    REGLA DE IDIOMA OBLIGATORIA: Todo el contenido que generes DEBE estar escrito en {idioma_salida}.
    """
    st.session_state.mensajes.append(SystemMessage(content=prompt_sistema))

# Mostrar el historial (ocultando el SystemMessage)
for mensaje in st.session_state.mensajes:
    if isinstance(mensaje, HumanMessage):
        with st.chat_message("user"):
            st.markdown(mensaje.content)
    elif isinstance(mensaje, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(mensaje.content)

# Capturar nuevo mensaje
if texto_usuario := st.chat_input("Ej: Redacta un post sobre servidores en la nube..."):
    # 1. Mostrar lo que pidió el usuario
    with st.chat_message("user"):
        st.markdown(texto_usuario)
    
    st.session_state.mensajes.append(HumanMessage(content=texto_usuario))

    # 2. El asistente genera y muestra el contenido principal
    with st.chat_message("assistant"):
        with st.spinner(f"Redactando el post con {modelo_seleccionado}... ⏳"):
            # Generamos el texto normal
            respuesta = llm.invoke(st.session_state.mensajes)
            st.markdown(respuesta.content)
            
            
        # --- EL MINI-AGENTE PARA LA IMAGEN (VERSIÓN ESTABLE) ---
            with st.spinner("Buscando imagen contextualizada... 🎨"):
                # 1. Prompt estricto: Le exigimos UNA SOLA PALABRA
                prompt_imagen = f"Analiza esta petición y devuelve UNA ÚNICA palabra clave en INGLÉS que sea un objeto físico relacionado. No escribas nada más. Petición: {texto_usuario}"
                
                respuesta_palabras = llm.invoke(prompt_imagen)
                
                # 2. Sanitización extrema: Limpiamos la respuesta del LLM
                # Quitamos espacios, comillas, puntos y lo pasamos a minúsculas
                palabra_clave = respuesta_palabras.content.strip().replace(".", "").replace('"', '').replace(" ", "").lower()
                
                # 3. URL dinámica y segura
                # Si la palabra es 'server', buscará fotos reales de servidores. Si es 'cloud', nubes.
                url_imagen = f"https://loremflickr.com/800/400/{palabra_clave}/all"
                
                # 4. Renderizamos
                st.image(url_imagen, caption=f"Imagen obtenida de base de datos para la etiqueta: '{palabra_clave}'")
                
                # Guardamos en memoria el post original
                st.session_state.mensajes.append(AIMessage(content=respuesta.content))