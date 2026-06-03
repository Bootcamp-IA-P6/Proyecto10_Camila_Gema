# src/tools/rag_engine.py
from langchain_core.tools import tool
from langchain_community.retrievers import ArxivRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

@tool
def investigar_y_sintetizar_ciencia(query: str) -> str:
    """
    Busca papers en arXiv sobre ciencia/IA, los lee por completo y extrae la información 
    exacta usando una arquitectura RAG.
    Útil cuando el usuario hace preguntas complejas que requieren precisión científica.
    """
    try:
        # 1. INGESTA: Descargamos los 2 papers más relevantes de arXiv
        retriever = ArxivRetriever(load_max_docs=2)
        documentos_crudos = retriever.invoke(query)
        
        if not documentos_crudos:
            return "No encontré documentos en arXiv para esta consulta."

        # 2. FRAGMENTACIÓN (Chunking): Troceamos los papers para no saturar al LLM
        # Usamos 1000 caracteres con un solapamiento de 150 para no cortar frases por la mitad
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150
        )
        chunks = text_splitter.split_documents(documentos_crudos)

        # 3. VECTORIZACIÓN (Embeddings): Convertimos el texto a coordenadas matemáticas
        # Usamos un modelo ligero y muy rápido de Hugging Face (descarga automática la primera vez)
        modelo_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # 4. ALMACENAMIENTO TEMPORAL: Creamos la base de datos vectorial en memoria RAM
        vector_store = FAISS.from_documents(chunks, modelo_embeddings)

        # 5. RECUPERACIÓN (Retrieval): Buscamos los 3 trozos que matemáticamente 
        # mejor respondan a la pregunta original del usuario
        chunks_relevantes = vector_store.similarity_search(query, k=3)

        # 6. EMPAQUETADO: Juntamos los mejores trozos para dárselos al LLM
        contexto_final = "He extraído estos fragmentos clave de la literatura científica:\n\n"
        for i, chunk in enumerate(chunks_relevantes):
            contexto_final += f"--- FRAGMENTO RELEVANTE {i+1} ---\n"
            contexto_final += f"{chunk.page_content}\n\n"

        return contexto_final

    except Exception as e:
        return f"Error en el motor RAG: {str(e)}"