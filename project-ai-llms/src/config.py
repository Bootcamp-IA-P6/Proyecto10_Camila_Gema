from langchain_groq import ChatGroq

# Diccionario que mapea un nombre amigable -> el modelo real de Groq
MODELOS_DISPONIBLES = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
}

def obtener_modelo(nombre_modelo):
    modelo_real = MODELOS_DISPONIBLES[nombre_modelo]
    return ChatGroq(model=modelo_real)