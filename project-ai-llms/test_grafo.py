from src.graph_rag.graph_builder import construir_grafo

grafo, papers = construir_grafo("attention mechanism transformer", cantidad_papers=2)

print(f"Papers procesados: {len(papers)}")
for p in papers:
    print(f"  • {p['titulo'][:80]}... ({p['tripletas_extraidas']} tripletas)")
print(f"\nNodos: {grafo.number_of_nodes()}")
print(f"Aristas: {grafo.number_of_edges()}")
print("-" * 50)
print("Algunas relaciones del grafo:")
for sujeto, objeto, datos in list(grafo.edges(data=True))[:15]:
    print(f"  {sujeto}  ──[{datos['relacion']}]──>  {objeto}")