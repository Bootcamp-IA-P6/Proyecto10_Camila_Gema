from src.generators.graph_rag_generator import generar_divulgacion_graph

print("Construyendo grafo y generando explicación (esto tarda)...")
resultado = generar_divulgacion_graph(
    tema="attention mechanism transformer",
    nombre_modelo="Llama 3.3 70B",
    idioma="español",
    cantidad_papers=2,
)

print(f"\nGrafo: {resultado['stats_grafo']['nodos']} nodos, {resultado['stats_grafo']['aristas']} aristas")
print(f"Entidades clave: {resultado['entidades']}")
print(f"\n=== EXPLICACIÓN ===")
print(resultado["explicacion"])
print(f"\n=== EVALUACIÓN DEL JUEZ ===")
print(f"Puntuación: {resultado['evaluacion']['puntuacion']}/5")
print(f"Justificación: {resultado['evaluacion']['justificacion']}")
print(f"\n=== PAPERS USADOS ===")
for p in resultado["papers"]:
    print(f"  • {p['titulo'][:80]}...")