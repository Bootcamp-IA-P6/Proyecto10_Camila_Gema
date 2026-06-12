import arxiv

def buscar_papers(consulta, cantidad=3):
    cliente = arxiv.Client(page_size=cantidad, delay_seconds=5, num_retries=2)
    busqueda = arxiv.Search(
        query=consulta,
        max_results=cantidad,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    papers = []
    for resultado in cliente.results(busqueda):
        papers.append({
            "titulo": resultado.title,
            "resumen": resultado.summary,
            "autores": [autor.name for autor in resultado.authors],
            "url": resultado.entry_id,
        })
    return papers