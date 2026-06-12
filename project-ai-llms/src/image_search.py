import os
import requests
from dotenv import load_dotenv

load_dotenv()

def buscar_imagenes(consulta, cantidad=3):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": os.environ["PEXELS_API_KEY"]}
    params = {"query": consulta, "per_page": cantidad, "locale": "es-ES"}

    respuesta = requests.get(url, headers=headers, params=params)
    datos = respuesta.json()

    # Si Pexels no devuelve fotos (clave inválida, límite de peticiones...),
    # devolvemos lista vacía y la app simplemente no muestra imágenes.
    if not isinstance(datos, dict) or "photos" not in datos:
        return []

    imagenes = []
    for foto in datos["photos"]:
        imagenes.append({
            "url": foto["src"]["medium"],
            "autor": foto["photographer"],
        })
    return imagenes