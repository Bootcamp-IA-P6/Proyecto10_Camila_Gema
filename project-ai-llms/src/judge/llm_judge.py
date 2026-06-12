import json
from langchain_core.output_parsers import StrOutputParser
from src.prompts.judge_prompt import judge_template
from src.config import obtener_modelo

def evaluar_respuesta(fuentes_texto, respuesta_generada, nombre_modelo="Llama 3.3 70B"):
    llm = obtener_modelo(nombre_modelo)
    chain = judge_template | llm | StrOutputParser()

    salida = chain.invoke({
        "fuentes": fuentes_texto,
        "respuesta": respuesta_generada,
    })

    try:
        datos = json.loads(salida.strip())
        return {
            "puntuacion": int(datos["puntuacion"]),
            "justificacion": datos["justificacion"],
        }
    except (json.JSONDecodeError, KeyError, ValueError):
        return {
            "puntuacion": 0,
            "justificacion": "No se pudo evaluar la respuesta automáticamente.",
        }