from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from src.prompts.rag_prompt import rag_template
from src.config import obtener_modelo
from src.rag.consulta import buscar_trozos_relevantes

load_dotenv()

def generar_divulgacion(tema, nombre_modelo, idioma, cantidad_trozos=3):
    trozos = buscar_trozos_relevantes(tema, cantidad=cantidad_trozos)
    contexto = "\n\n---\n\n".join([trozo.page_content for trozo in trozos])

    llm = obtener_modelo(nombre_modelo)
    chain = rag_template | llm | StrOutputParser()

    resultado = chain.invoke({
        "contexto": contexto,
        "tema": tema,
        "idioma": idioma,
    })

    fuentes = [{"titulo": t.metadata["titulo"], "url": t.metadata["url"]} for t in trozos]
    return resultado, fuentes