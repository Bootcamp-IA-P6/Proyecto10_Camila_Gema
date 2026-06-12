from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from src.prompts.content_prompt import content_template
from src.config import obtener_modelo

load_dotenv()

def generar_contenido(tema, plataforma, audiencia, tono, nombre_modelo, info_empresa, idioma):
    llm = obtener_modelo(nombre_modelo)
    chain = content_template | llm | StrOutputParser()
    return chain.invoke({
        "tema": tema,
        "plataforma": plataforma,
        "audiencia": audiencia,
        "tono": tono,
        "info_empresa": info_empresa,
        "idioma": idioma,
    })