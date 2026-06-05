# src/agents/agente_ciencia.py

# =====================================================================
# AGENTE ESPECIALIZADO EN CIENCIA E INTELIGENCIA ARTIFICIAL
#
# Este agente solo sabe hacer UNA cosa:
# buscar información científica en la base de datos vectorial local
# usando el motor RAG y redactar una explicación divulgativa.
#
# IMPORTANTE: No llama a arXiv en tiempo real.
# Usa la base de datos vectorial que construiste con build_vectorstore.py
# =====================================================================

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.tools.rag_engine import investigar_y_sintetizar_ciencia


def crear_agente_ciencia(llm, nombre_empresa: str, tono_empresa: str, idioma_salida: str):
    """
    Crea y devuelve el agente de ciencia listo para usar.
    
    Recibe el LLM y la configuración de la empresa desde la UI
    para que el tono y el idioma sean consistentes con el resto de la app.
    """

    # Prompt especializado SOLO en ciencia y divulgación
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
        Eres un divulgador científico experto que trabaja para {nombre_empresa}.
        Tu estilo de comunicación: {tono_empresa}
        
        REGLA DE IDIOMA: Responde siempre en {idioma_salida}.
        
        TU ÚNICA FUNCIÓN:
        Explicar conceptos científicos y tecnológicos de forma clara
        y comprensible para el público general, usando la herramienta
        'investigar_y_sintetizar_ciencia' para obtener información
        de papers académicos reales.
        
        REGLAS OBLIGATORIAS:
        - SIEMPRE usa la herramienta antes de responder.
        - NUNCA inventes datos científicos.
        - Basa tu respuesta ÚNICAMENTE en el contexto que devuelve la herramienta.
        - Si la herramienta no encuentra información, dilo claramente.
        
        FORMATO DE RESPUESTA:
        - Empieza con una introducción sencilla del concepto
        - Explica los puntos clave en párrafos claros
        - Usa analogías y ejemplos del mundo real
        - Termina con una conclusión breve
        - Usa emojis si el tono de la empresa lo permite
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Herramientas que puede usar este agente — solo el RAG
    herramientas = [investigar_y_sintetizar_ciencia]

    # Construimos el agente
    agente = create_tool_calling_agent(llm, herramientas, prompt)

    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True
    )