# fue nuestro prototipo: Lo creamos primero para entender cómo conectarnos a la API de arXiv y ver que podíamos descargar texto.
# Pero tenía un problema grave: le pasaba el texto "crudo" al modelo, lo que podía saturarlo.

from langchain_community.retrievers import ArxivRetriever
from langchain_core.tools import tool

@tool
def buscar_papers_arxiv(query: str) -> str:
    """
    Busca documentos científicos y papers académicos en la base de datos de arXiv.
    Útil para responder preguntas sobre ciencia, inteligencia artificial, NLP, física, etc.
    El usuario debe proporcionar un término de búsqueda en inglés (ej: 'Natural Language Processing', 'Transformers').
    """
    try:
        # Configuramos el retriever para traer solo los 3 papers más relevantes y evitar saturar al LLM
        retriever = ArxivRetriever(load_max_docs=3)
        documentos = retriever.invoke(query)
        
        if not documentos:
            return f"No se encontraron papers científicos en arXiv para la búsqueda: {query}."
            
        # Formateamos los resultados para que el LLM los entienda fácilmente
        resultado_texto = "He encontrado los siguientes papers científicos:\n\n"
        for i, doc in enumerate(documentos):
            resultado_texto += f"--- PAPER {i+1} ---\n"
            resultado_texto += f"Título: {doc.metadata.get('Title', 'Sin título')}\n"
            resultado_texto += f"Autores: {doc.metadata.get('Authors', 'Desconocidos')}\n"
            resultado_texto += f"Resumen (Abstract): {doc.page_content}\n\n"
            
        return resultado_texto
        
    except Exception as e:
        return f"Error al conectar con la API de arXiv. Detalle: {str(e)}"