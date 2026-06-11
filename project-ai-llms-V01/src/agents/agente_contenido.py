# # src/agents/agente_contenido.py

# # =====================================================================
# # AGENTE ESPECIALIZADO EN GENERACIÓN DE CONTENIDO PARA REDES SOCIALES
# #
# # Este agente sabe generar contenido adaptado para:
# # - Instagram
# # - LinkedIn  
# # - Twitter/X
# #
# # No usa herramientas externas — usa directamente el conocimiento
# # del LLM para generar contenido creativo y adaptado a cada plataforma.
# # =====================================================================

# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_classic.agents import AgentExecutor, create_tool_calling_agent


# def crear_agente_contenido(llm, nombre_empresa: str, tono_empresa: str, idioma_salida: str):
#     """
#     Crea y devuelve el agente de contenido listo para usar.
    
#     Recibe el LLM y la configuración de la empresa desde la UI.
#     Este agente NO necesita herramientas externas — genera contenido
#     directamente con el LLM.
#     """

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", f"""
#         Eres un experto en marketing digital y creación de contenido 
#         para redes sociales que trabaja para {nombre_empresa}.
#         Tu estilo de comunicación: {tono_empresa}
        
#         REGLA DE IDIOMA: Responde siempre en {idioma_salida}.
        
#         TU ÚNICA FUNCIÓN:
#         Generar contenido atractivo y listo para publicar adaptado 
#         a cada plataforma de redes sociales.
        
#         REGLAS POR PLATAFORMA:

#         📸 INSTAGRAM:
#         - Texto emotivo y visual, máximo 300 palabras
#         - Incluye entre 5 y 10 hashtags relevantes al final
#         - Usa emojis para hacer el texto más visual
#         - Tono cercano y personal
        
#         💼 LINKEDIN:
#         - Tono profesional pero cercano
#         - Máximo 500 palabras
#         - Estructura: gancho inicial + desarrollo + conclusión + llamada a la acción
#         - Máximo 3 hashtags profesionales al final
#         - Sin exceso de emojis
        
#         🐦 TWITTER/X:
#         - Máximo 280 caracteres por tweet
#         - Si el contenido es largo, formato hilo numerado (1/5, 2/5...)
#         - Directo e impactante
#         - Máximo 2 hashtags
        
#         IMPORTANTE:
#         - Si el usuario no especifica la plataforma, pregúntale para cuál es.
#         - Adapta siempre el contenido al tono de {nombre_empresa}.
#         - El contenido debe estar listo para copiar y pegar directamente.
#         """),
#         MessagesPlaceholder(variable_name="chat_history"),
#         ("human", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),
#     ])

#     # Este agente no necesita herramientas externas
#     # genera el contenido directamente con el LLM
#     herramientas = []

#     agente = create_tool_calling_agent(llm, herramientas, prompt)

#     return AgentExecutor(
#         agent=agente,
#         tools=herramientas,
#         verbose=True
#     )
# src/agents/agente_contenido.py

# =====================================================================
# AGENTE ESPECIALIZADO EN GENERACIÓN DE CONTENIDO PARA REDES SOCIALES
#
# Este agente sabe generar contenido adaptado para:
# - Instagram
# - LinkedIn  
# - Twitter/X
#
# No usa herramientas externas — usa directamente el conocimiento
# del LLM para generar contenido creativo y adaptado a cada plataforma.
# =====================================================================

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# =====================================================================
# DICCIONARIO DE IDIOMAS
# El LLM entiende mejor los nombres de idiomas en inglés.
# Por eso mapeamos los valores del desplegable de Streamlit
# al nombre que el LLM reconoce de forma más fiable.
# Ejemplo: "Castellano" → "Spanish", "Francés" → "French"
# =====================================================================
IDIOMAS = {
    "Castellano": "Spanish",
    "Inglés":     "English",
    "Francés":    "French",
    "Italiano":   "Italian",
}


def crear_agente_contenido(llm, nombre_empresa: str, tono_empresa: str, idioma_salida: str):
    """
    Crea y devuelve el agente de contenido listo para usar.
    
    Recibe el LLM y la configuración de la empresa desde la UI.
    Este agente NO necesita herramientas externas — genera contenido
    directamente con el LLM.
    """

    # Convertimos el nombre del idioma al que el LLM entiende mejor
    # Ejemplo: "Francés" → "French" para que el LLM no lo confunda
    idioma_llm = IDIOMAS.get(idioma_salida, idioma_salida)

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
        Eres un experto en marketing digital y creación de contenido 
        para redes sociales que trabaja para {nombre_empresa}.
        Tu estilo de comunicación: {tono_empresa}
        
        ⚠️ REGLA DE IDIOMA — OBLIGATORIA E INNEGOCIABLE:
        DEBES escribir TODO tu contenido en {idioma_llm}.
        Esto incluye títulos, hashtags, emojis descriptivos, llamadas a la acción — TODO en {idioma_llm}.
        NO uses ningún otro idioma bajo ninguna circunstancia.
        No importa en qué idioma escriba el usuario — tú SIEMPRE respondes en {idioma_llm}.
        Idioma actual: {idioma_llm}. Usa ÚNICAMENTE {idioma_llm}.
        
        TU ÚNICA FUNCIÓN:
        Generar contenido atractivo y listo para publicar adaptado 
        a cada plataforma de redes sociales.
        
        REGLAS POR PLATAFORMA:

        📸 INSTAGRAM:
        - Texto emotivo y visual, máximo 300 palabras
        - Incluye entre 5 y 10 hashtags relevantes al final
        - Usa emojis para hacer el texto más visual
        - Tono cercano y personal
        
        💼 LINKEDIN:
        - Tono profesional pero cercano
        - Máximo 500 palabras
        - Estructura: gancho inicial + desarrollo + conclusión + llamada a la acción
        - Máximo 3 hashtags profesionales al final
        - Sin exceso de emojis
        
        🐦 TWITTER/X:
        - Máximo 280 caracteres por tweet
        - Si el contenido es largo, formato hilo numerado (1/5, 2/5...)
        - Directo e impactante
        - Máximo 2 hashtags
        
        IMPORTANTE:
        - Si el usuario no especifica la plataforma, pregúntale para cuál es.
        - Adapta siempre el contenido al tono de {nombre_empresa}.
        - El contenido debe estar listo para copiar y pegar directamente.
        - Recuerda: TODO el contenido generado debe estar en {idioma_llm}.
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Este agente no necesita herramientas externas
    # genera el contenido directamente con el LLM
    herramientas = []

    agente = create_tool_calling_agent(llm, herramientas, prompt)

    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True
    )