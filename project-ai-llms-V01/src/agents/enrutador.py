# src/agents/enrutador.py

# =====================================================================
# ENRUTADOR — el cerebro que decide qué agente usar
#
# Recibe el mensaje del usuario y decide:
# - ¿Es una pregunta de finanzas?     → agente_finanzas
# - ¿Es una pregunta de ciencia?      → agente_ciencia
# - ¿Es contenido para redes?         → agente_contenido
# - ¿Es ciencia + redes sociales?     → agente_ciencia → agente_contenido
# =====================================================================

import logging
from langchain_core.prompts import ChatPromptTemplate

from src.agents.agente_ciencia import crear_agente_ciencia
from src.agents.agente_finanzas import crear_agente_finanzas
from src.agents.agente_contenido import crear_agente_contenido

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("enrutador")

# =====================================================================
# PALABRAS CLAVE POR CATEGORÍA
# El enrutador busca estas palabras en el mensaje del usuario
# para decidir a qué agente mandarlo
# =====================================================================
PALABRAS_FINANZAS = [
    "acción", "acciones", "bolsa", "precio", "ticker", "mercado",
    "stock", "cotización", "invertir", "inversión", "apple", "amazon",
    "google", "tesla", "microsoft", "nasdaq", "dow jones", "ibex",
    "dividendo", "portfolio", "cartera"
]

PALABRAS_CIENCIA = [
    "ciencia", "científico", "inteligencia artificial", "machine learning",
    "deep learning", "red neuronal", "algoritmo", "investigación", "paper",
    "estudio", "física", "química", "biología", "neurociencia", "IA", "AI",
    "transformer", "modelo", "datos", "tecnología", "robot", "quantum"
]

PALABRAS_REDES = [
    "instagram", "linkedin", "twitter", "tweet", "post", "publicación",
    "contenido", "redes sociales", "hilo", "caption", "hashtag", "viral",
    "blog", "artículo"
]


def clasificar_mensaje(mensaje: str, llm) -> str:
    """
    Usa el LLM para clasificar el mensaje del usuario en una categoría.
    
    Devuelve una de estas cadenas:
    - "finanzas"          → solo finanzas
    - "ciencia"           → solo ciencia
    - "contenido"         → solo contenido general
    - "ciencia_contenido" → ciencia para publicar en redes
    """
    logger.info(f"Clasificando mensaje: '{mensaje}'")

    # Le pedimos al LLM que clasifique el mensaje
    # Le damos ejemplos muy claros para que no se equivoque
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Eres un clasificador de mensajes. Tu única tarea es clasificar 
        el mensaje del usuario en UNA de estas 4 categorías:
        
        - "finanzas"          → preguntas sobre bolsa, acciones, precios de empresas
        - "ciencia"           → preguntas sobre ciencia, IA, tecnología, investigación
        - "contenido"         → pedir posts, contenido para Instagram, LinkedIn, Twitter
        - "ciencia_contenido" → pedir contenido científico para publicar en redes sociales
        
        EJEMPLOS:
        "¿A cuánto está Apple?"                           → finanzas
        "Explícame qué es el deep learning"               → ciencia  
        "Crea un post de LinkedIn sobre liderazgo"        → contenido
        "Crea un post de Instagram sobre inteligencia artificial" → ciencia_contenido
        "Escribe un hilo de Twitter sobre machine learning"      → ciencia_contenido
        
        Responde ÚNICAMENTE con una de estas palabras exactas:
        finanzas, ciencia, contenido, ciencia_contenido
        
        No escribas nada más. Solo la categoría.
        """),
        ("human", mensaje)
    ])

    try:
        respuesta = llm.invoke(prompt.format_messages(input=mensaje))
        categoria = respuesta.content.strip().lower()
        logger.info(f"Categoría detectada: '{categoria}'")

        # Validamos que la respuesta sea una categoría válida
        categorias_validas = ["finanzas", "ciencia", "contenido", "ciencia_contenido"]
        if categoria not in categorias_validas:
            logger.warning(f"Categoría '{categoria}' no válida. Usando 'contenido' por defecto.")
            categoria = "contenido"

        return categoria

    except Exception as e:
        logger.error(f"Error al clasificar: {str(e)}. Usando 'contenido' por defecto.")
        return "contenido"


def enrutar(mensaje: str, historial: list, llm, nombre_empresa: str, tono_empresa: str, idioma_salida: str) -> str:
    """
    Función principal del enrutador.
    
    Recibe el mensaje del usuario y lo manda al agente correcto.
    Devuelve la respuesta final como texto.
    """

    # PASO 1: Clasificamos el mensaje
    categoria = clasificar_mensaje(mensaje, llm)

    # PASO 2: Mandamos al agente correcto
    if categoria == "finanzas":
        logger.info("→ Mandando a AGENTE FINANZAS")
        agente = crear_agente_finanzas(llm, nombre_empresa, tono_empresa, idioma_salida)
        respuesta = agente.invoke({
            "input": mensaje,
            "chat_history": historial
        })
        return respuesta["output"]

    elif categoria == "ciencia":
        logger.info("→ Mandando a AGENTE CIENCIA")
        agente = crear_agente_ciencia(llm, nombre_empresa, tono_empresa, idioma_salida)
        respuesta = agente.invoke({
            "input": mensaje,
            "chat_history": historial
        })
        return respuesta["output"]

    elif categoria == "ciencia_contenido":
        logger.info("→ Mandando a AGENTE CIENCIA primero, luego AGENTE CONTENIDO")

        # PRIMERO: el agente de ciencia investiga el tema
        logger.info("  Paso 1: Investigando el tema científico...")
        agente_ciencia = crear_agente_ciencia(llm, nombre_empresa, tono_empresa, idioma_salida)
        respuesta_ciencia = agente_ciencia.invoke({
            "input": mensaje,
            "chat_history": historial
        })
        info_cientifica = respuesta_ciencia["output"]
        logger.info("  Paso 1 OK: Información científica obtenida")

        # SEGUNDO: el agente de contenido convierte esa info en un post
        logger.info("  Paso 2: Convirtiendo en contenido para redes...")
        agente_cont = crear_agente_contenido(llm, nombre_empresa, tono_empresa, idioma_salida)

        # Le pasamos la info científica + la petición original del usuario
        mensaje_para_contenido = (
            f"El usuario quiere: {mensaje}\n\n"
            f"Usa esta información científica real para crear el contenido:\n\n"
            f"{info_cientifica}"
        )
        respuesta_contenido = agente_cont.invoke({
            "input": mensaje_para_contenido,
            "chat_history": historial
        })
        logger.info("  Paso 2 OK: Contenido generado")
        return respuesta_contenido["output"]

    else:
        # contenido general
        logger.info("→ Mandando a AGENTE CONTENIDO")
        agente = crear_agente_contenido(llm, nombre_empresa, tono_empresa, idioma_salida)
        respuesta = agente.invoke({
            "input": mensaje,
            "chat_history": historial
        })
        return respuesta["output"]