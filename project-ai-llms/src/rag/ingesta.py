from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.rag.arxiv_loader import buscar_papers

RUTA_CHROMA = "chroma_db"
MODELO_EMBEDDINGS = "sentence-transformers/all-MiniLM-L6-v2"

def construir_biblioteca(tema, cantidad=5):
    papers = buscar_papers(tema, cantidad=cantidad)

    documentos = []
    for paper in papers:
        texto = f"{paper['titulo']}\n\n{paper['resumen']}"
        documentos.append(Document(
            page_content=texto,
            metadata={"titulo": paper["titulo"], "url": paper["url"]},
        ))

    troceador = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    trozos = troceador.split_documents(documentos)

    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDINGS)

    biblioteca = Chroma.from_documents(
        documents=trozos,
        embedding=embeddings,
        persist_directory=RUTA_CHROMA,
    )

    return len(trozos)