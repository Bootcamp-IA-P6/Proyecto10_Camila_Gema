from src.rag.ingesta import construir_biblioteca

n = construir_biblioteca("large language models", cantidad=3)
print(f"Biblioteca creada con {n} trozos.")