from src.rag.arxiv_loader import buscar_papers

papers = buscar_papers("large language models", cantidad=3)
for p in papers:
    print("TÍTULO:", p["titulo"])
    print("AUTORES:", ", ".join(p["autores"]))
    print("RESUMEN:", p["resumen"][:200], "...")
    print("URL:", p["url"])
    print("-" * 40)