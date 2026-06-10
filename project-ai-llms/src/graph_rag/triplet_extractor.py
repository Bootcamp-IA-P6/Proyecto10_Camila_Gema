import json
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from src.prompts.triplet_prompt import triplet_template
from src.config import obtener_modelo

load_dotenv()

def extraer_tripletas(texto, nombre_modelo="Llama 3.3 70B"):
    llm = obtener_modelo(nombre_modelo)
    chain = triplet_template | llm | StrOutputParser()

    salida = chain.invoke({"texto": texto})

    try:
        datos = json.loads(salida.strip())
        tripletas_crudas = datos.get("tripletas", [])
        # Validamos que cada tripleta tenga 3 elementos y todos sean strings
        tripletas_limpias = []
        for t in tripletas_crudas:
            if isinstance(t, list) and len(t) == 3 and all(isinstance(x, str) for x in t):
                tripletas_limpias.append(tuple(t))
        return tripletas_limpias
    except (json.JSONDecodeError, KeyError):
        return []