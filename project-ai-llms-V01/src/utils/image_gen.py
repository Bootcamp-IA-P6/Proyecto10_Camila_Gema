# # src/tools/image_gen.py

# import requests
# import urllib.parse
# import hashlib


# def generar_imagen_hf(prompt: str) -> bytes:
#     """
#     Genera una imagen contextual para acompañar el contenido.
    
#     Estrategia en cascada — prueba servicios en este orden:
#     1. Pollinations.ai  → imágenes generadas por IA (puede fallar en gratuito)
#     2. Picsum Photos    → fotos reales de alta calidad (100% gratuito, sin límites)
    
#     Usar una imagen real de Picsum es preferible a no mostrar ninguna imagen.
#     Para una PoC esto es perfectamente válido.
#     """

#     # ------------------------------------------------------------------
#     # INTENTO 1: Pollinations.ai (IA generativa)
#     # ------------------------------------------------------------------
#     try:
#         prompt_codificado = urllib.parse.quote(prompt)
#         url_pollinations = (
#             f"https://image.pollinations.ai/prompt/{prompt_codificado}"
#             f"?width=800&height=400&nologo=true&enhance=true"
#         )
#         headers_poll = {
#             "User-Agent": (
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/120.0.0.0 Safari/537.36"
#             ),
#             "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
#             "Referer": "https://pollinations.ai/"
#         }

#         resp = requests.get(url_pollinations, headers=headers_poll, timeout=45)

#         if resp.status_code == 200:
#             content_type = resp.headers.get("Content-Type", "")
#             # ✅ Verificamos que sea realmente una imagen (no un HTML de error)
#             # Una imagen real tiene más de 5000 bytes
#             if "image" in content_type and len(resp.content) > 5000:
#                 return resp.content

#     except Exception:
#         pass  # Si falla, pasamos al siguiente servicio

#     # ------------------------------------------------------------------
#     # INTENTO 2: Picsum Photos (fotos reales, 100% gratuito y sin límites)
#     # Usamos un hash del prompt para que cada tema tenga siempre
#     # la misma imagen (consistencia entre recargas)
#     # ------------------------------------------------------------------
#     try:
#         # Convertimos el prompt en un número entre 1 y 500
#         # para que siempre el mismo tema dé la misma imagen
#         seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 500 + 1

#         url_picsum = f"https://picsum.photos/seed/{seed}/800/400"

#         headers_picsum = {
#             "User-Agent": "Mozilla/5.0 (compatible; ContentBot/1.0)"
#         }

#         resp2 = requests.get(url_picsum, headers=headers_picsum, timeout=15)

#         if resp2.status_code == 200 and len(resp2.content) > 5000:
#             return resp2.content

#     except Exception:
#         pass

#     # Si los dos fallan, lanzamos error descriptivo
#     raise Exception(
#         "No se pudo obtener imagen. "
#         "Tanto Pollinations.ai como Picsum Photos no respondieron. "
#         "Comprueba tu conexión a internet."
#     )

# src/tools/image_gen.py

import requests
import urllib.parse
import os
import hashlib


def generar_imagen_hf(prompt: str) -> bytes:
    """
    Genera una imagen relevante al prompt usando Unsplash API.
    
    Estrategia en cascada:
    1. Unsplash API  → fotos reales muy relevantes (50 req/hora gratis)
    2. Picsum Photos → foto aleatoria como último recurso
    """

    # ------------------------------------------------------------------
    # INTENTO 1: Unsplash API
    # Busca fotos reales por palabras clave — muy relevante al tema
    # ------------------------------------------------------------------
    try:
        unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY", "")

        if unsplash_key:
            # Buscamos fotos relacionadas con el prompt
            url_search = "https://api.unsplash.com/search/photos"
            params = {
                "query": prompt,
                "per_page": 1,
                "orientation": "landscape"
            }
            headers = {
                "Authorization": f"Client-ID {unsplash_key}"
            }

            resp_search = requests.get(
                url_search,
                params=params,
                headers=headers,
                timeout=10
            )

            if resp_search.status_code == 200:
                data = resp_search.json()
                resultados = data.get("results", [])

                if resultados:
                    # Cogemos la URL de la primera foto en tamaño regular
                    url_foto = resultados[0]["urls"]["regular"]

                    # Descargamos la foto
                    resp_foto = requests.get(url_foto, timeout=15)

                    if resp_foto.status_code == 200:
                        return resp_foto.content

    except Exception:
        pass

    # ------------------------------------------------------------------
    # INTENTO 2: Picsum Photos (último recurso)
    # Foto aleatoria pero consistente para el mismo prompt
    # ------------------------------------------------------------------
    try:
        seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 500 + 1
        url_picsum = f"https://picsum.photos/seed/{seed}/800/400"
        headers_picsum = {"User-Agent": "Mozilla/5.0"}
        resp2 = requests.get(url_picsum, headers=headers_picsum, timeout=15)

        if resp2.status_code == 200 and len(resp2.content) > 5000:
            return resp2.content

    except Exception:
        pass

    raise Exception("No se pudo obtener imagen de ningún servicio.")