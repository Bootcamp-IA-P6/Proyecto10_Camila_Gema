from src.rag.consulta import buscar_trozos_relevantes

pregunta = "¿Pueden los modelos de lenguaje tener personalidad?"
resultados = buscar_trozos_relevantes(pregunta, cantidad=3)

for i, doc in enumerate(resultados, 1):
    print(f"--- Trozo {i} ---")
    print("De:", doc.metadata["titulo"])
    print(doc.page_content[:200], "...")
    print()