import os
import requests
from dotenv import load_dotenv

load_dotenv()

def obtener_noticias(categoria="general", cantidad=10):
    url = "https://finnhub.io/api/v1/news"
    params = {
        "category": categoria,
        "token": os.environ["FINNHUB_API_KEY"],
    }

    respuesta = requests.get(url, params=params)
    datos = respuesta.json()

    noticias = []
    for noticia in datos[:cantidad]:
        noticias.append({
            "titular": noticia["headline"],
            "resumen": noticia["summary"],
            "fuente": noticia["source"],
            "url": noticia["url"],
        })
    return noticias