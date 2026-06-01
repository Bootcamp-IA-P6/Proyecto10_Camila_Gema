# # src/tools/image_gen.py
# import requests
# import os

# def generar_imagen_hf(prompt: str) -> bytes:
#     """
#     Se conecta a la API de Hugging Face para generar una imagen desde cero
#     usando el modelo Stable Diffusion XL.
#     """
#     # Endpoint del modelo de generación de imágenes
#     API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
#     # Cogemos la clave de tu .env
#     hf_token = os.getenv("HUGGINGFACE_API_KEY")
#     if not hf_token:
#         raise ValueError("Falta la clave HUGGINGFACE_API_KEY en el archivo .env")

#     headers = {"Authorization": f"Bearer {hf_token}"}
#     payload = {"inputs": prompt}

#     # Hacemos la petición a la nube
#     response = requests.post(API_URL, headers=headers, json=payload)
    
#     if response.status_code == 200:
#         # Si va bien, devolvemos los bytes (los píxeles crudos) de la imagen
#         return response.content
#     else:
#         raise Exception(f"Error en Hugging Face: {response.text}")

# src/tools/image_gen.py
import requests
import urllib.parse

def generar_imagen_hf(prompt: str) -> bytes:
    """
    Genera una imagen usando Pollinations.ai (Alternativa temporal por bloqueo de DNS).
    Mantenemos el nombre de la función para no romper app.py.
    """
    # Codificamos el texto para que sea una URL válida (ej: espacios -> %20)
    prompt_codificado = urllib.parse.quote(prompt)
    
    # Endpoint libre y directo
    url = f"https://image.pollinations.ai/prompt/{prompt_codificado}?width=800&height=400&nologo=true"
    
    # Hacemos la petición
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Error en la generación alternativa: {response.status_code}")