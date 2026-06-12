from src.router.agent_router import enrutar_peticion

peticiones_de_prueba = [
    "Hazme un post de LinkedIn motivador sobre los lunes",
    "Explícame de forma sencilla cómo funcionan los modelos de lenguaje, basándote en papers científicos",
    "Resúmeme las noticias económicas del día",
    "Escribe un tuit divertido sobre el café",
    "Quiero entender el concepto de transformers en IA",
    "¿Cómo están los mercados hoy?",
]

for peticion in peticiones_de_prueba:
    resultado = enrutar_peticion(peticion)
    print(f"PETICIÓN: {peticion}")
    print(f"→ Agente: {resultado['agente']}")
    print(f"  Justificación: {resultado['justificacion']}")
    print("-" * 50)