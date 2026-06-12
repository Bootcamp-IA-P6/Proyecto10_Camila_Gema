import json
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from src.prompts.router_prompt import router_template
from src.config import obtener_modelo


load_dotenv()

AGENTES_VALIDOS = {"contenido_general", "divulgacion_rag", "newsletter_financiera"}

def enrutar_peticion(peticion, nombre_modelo="Llama 3.3 70B"):
    llm = obtener_modelo(nombre_modelo)
    chain = router_template | llm | StrOutputParser()

    salida = chain.invoke({"peticion": peticion})

    try:
        datos = json.loads(salida.strip())
        agente = datos["agente"]
        if agente not in AGENTES_VALIDOS:
            return {
                "agente": "contenido_general",
                "justificacion": f"El enrutador devolvió un agente desconocido ('{agente}'). Se usa contenido general por defecto.",
            }
        return {
            "agente": agente,
            "justificacion": datos["justificacion"],
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "agente": "contenido_general",
            "justificacion": "No se pudo interpretar la decisión del enrutador. Se usa contenido general por defecto.",
        }