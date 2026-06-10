from src.graph_rag.graph_builder import construir_grafo
from src.graph_rag.graph_query import consultar_grafo

print("Construyendo grafo (esto tarda un poco)...")
grafo, papers = construir_grafo("attention mechanism transformer", cantidad_papers=2)
print(f"Papers procesados: {len(papers)}")
for p in papers:
    print(f"  • {p['titulo'][:80]}...")
print(f"Grafo listo: {grafo.number_of_nodes()} nodos, {grafo.number_of_edges()} aristas\n")

terminos = ["transformer", "attention"]
print(f"Consultando con términos: {terminos}\n")
resultado = consultar_grafo(grafo, terminos, profundidad=1)

print("ENTIDADES ENCONTRADAS:")
for e in resultado["entidades_encontradas"]:
    print(f"  - {e}")

print("\nCONTEXTO RECUPERADO:")
for c in resultado["contexto"]:
    print(f"  • {c}")