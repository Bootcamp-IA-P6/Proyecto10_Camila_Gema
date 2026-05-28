from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.rag.ingesta import RUTA_CHROMA, MODELO_EMBEDDINGS

def buscar_trozos_relevantes(pregunta, cantidad=3):
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDINGS)

    biblioteca = Chroma(
        persist_directory=RUTA_CHROMA,
        embedding_function=embeddings,
    )

    resultados = biblioteca.similarity_search(pregunta, k=cantidad)
    return resultados