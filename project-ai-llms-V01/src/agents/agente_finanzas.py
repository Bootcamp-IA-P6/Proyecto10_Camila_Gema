# src/agents/agente_finanzas.py

# =====================================================================
# AGENTE ESPECIALIZADO EN FINANZAS Y BOLSA
#
# Este agente solo sabe hacer UNA cosa:
# consultar precios de acciones en tiempo real con yfinance.
#
# Su prompt está muy enfocado en finanzas para que no se distraiga
# con otros temas.
# =====================================================================

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.tools.finance import obtener_precio_accion


def crear_agente_finanzas(llm, nombre_empresa: str, tono_empresa: str, idioma_salida: str):
    """
    Crea y devuelve el agente de finanzas listo para usar.
    
    Recibe el LLM y la configuración de la empresa desde la UI
    para que el tono y el idioma sean consistentes con el resto de la app.
    """

    # Prompt especializado SOLO en finanzas
    # Es más corto y enfocado que el prompt general — el agente
    # no necesita saber nada de ciencia ni de redes sociales
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
        Eres un analista financiero experto que trabaja para {nombre_empresa}.
        Tu estilo de comunicación: {tono_empresa}
        
        REGLA DE IDIOMA: Responde siempre en {idioma_salida}.
        
        TU ÚNICA FUNCIÓN:
        Consultar precios de acciones y mercados financieros usando 
        la herramienta 'obtener_precio_accion'.
        
        REGLAS OBLIGATORIAS:
        - SIEMPRE usa la herramienta para obtener el precio real.
        - NUNCA inventes precios. Si no encuentras el ticker, dilo claramente.
        - Después del precio, añade un breve comentario de mercado.
        
        FORMATO DE RESPUESTA:
        "📈 Análisis de mercado:
        - [Empresa]: [Precio] [Moneda]
        [Comentario breve en el tono de la empresa]"
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Herramientas que puede usar este agente — solo finanzas
    herramientas = [obtener_precio_accion]

    # Construimos el agente
    agente = create_tool_calling_agent(llm, herramientas, prompt)

    # AgentExecutor es el que realmente ejecuta el agente
    # verbose=True hace que imprima los pasos en la terminal (útil para debug)
    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True
    )