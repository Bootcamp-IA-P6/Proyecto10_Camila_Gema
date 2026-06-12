import networkx as nx
from src.graph_rag.triplet_extractor import extraer_tripletas
from src.rag.arxiv_loader import buscar_papers

def construir_grafo(consulta_arxiv, cantidad_papers=3):
    papers = buscar_papers(consulta_arxiv, cantidad=cantidad_papers)
    grafo = nx.MultiDiGraph()
    papers_procesados = []

    for paper in papers:
        texto = f"{paper['titulo']}. {paper['resumen']}"
        tripletas = extraer_tripletas(texto)

        for sujeto, relacion, objeto in tripletas:
            grafo.add_edge(
                sujeto.strip(),
                objeto.strip(),
                relacion=relacion.strip(),
                fuente=paper["titulo"],
            )

        papers_procesados.append({
            "titulo": paper["titulo"],
            "url": paper["url"],
            "tripletas_extraidas": len(tripletas),
        })

    return grafo, papers_procesados