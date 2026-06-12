from src.generators.rag_generator import generar_divulgacion

tema = "¿Tienen personalidad los modelos de lenguaje?"
explicacion, fuentes = generar_divulgacion(
    tema=tema,
    nombre_modelo="Llama 3.3 70B",
    idioma="español",
)

print("=== EXPLICACIÓN DIVULGATIVA ===")
print(explicacion)
print("\n=== FUENTES USADAS ===")
for f in fuentes:
    print(f"- {f['titulo']}: {f['url']}")