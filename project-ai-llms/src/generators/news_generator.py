from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from src.prompts.news_prompt import news_template
from src.config import obtener_modelo
from src.news.finnhub_loader import obtener_noticias

load_dotenv()

def generar_newsletter(nombre_modelo, idioma, cantidad_noticias=10):
    noticias = obtener_noticias(cantidad=cantidad_noticias)

    bloques = []
    for n in noticias:
        bloque = f"[{n['fuente']}] {n['titular']}\nResumen: {n['resumen']}"
        bloques.append(bloque)
    texto_noticias = "\n\n".join(bloques)

    llm = obtener_modelo(nombre_modelo)
    chain = news_template | llm | StrOutputParser()

    resultado = chain.invoke({
        "noticias": texto_noticias,
        "idioma": idioma,
    })

    return resultado, noticias