import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"}

respuesta = requests.get(url, headers=headers)
for modelo in respuesta.json()["data"]:
    print(modelo["id"])