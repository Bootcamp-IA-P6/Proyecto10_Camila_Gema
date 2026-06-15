"""
Construye el vectorstore FAISS descargando abstracts de arXiv.
Se ejecuta durante el docker build — no necesita PDFs locales ni API keys.
"""
import time
import os
import arxiv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

TEMAS = [
    "survey artificial intelligence machine learning deep learning",
    "transformer attention mechanism natural language processing BERT GPT",
    "deep learning convolutional neural networks image classification survey",
    "large language models GPT instruction tuning RLHF survey",
    "neural network training optimization backpropagation gradient descent",
]
PAPERS_POR_TEMA = 4
RUTA_VECTORSTORE = "vectorstore_ia"


def descargar_papers(tema):
    cliente = arxiv.Client(page_size=PAPERS_POR_TEMA, delay_seconds=3, num_retries=2)
    busqueda = arxiv.Search(query=tema, max_results=PAPERS_POR_TEMA)
    docs = []
    for r in cliente.results(busqueda):
        texto = f"{r.title}\n\n{r.summary}"
        docs.append(Document(
            page_content=texto,
            metadata={"Title": r.title, "url": r.entry_id}
        ))
    return docs


def construir():
    print("=" * 55)
    print("CONSTRUYENDO VECTORSTORE DESDE ARXIV")
    print("=" * 55)

    todos = []
    for i, tema in enumerate(TEMAS):
        print(f"\n[{i+1}/{len(TEMAS)}] {tema[:50]}...")
        docs = descargar_papers(tema)
        todos.extend(docs)
        for d in docs:
            print(f"    + {d.metadata['Title'][:60]}")
        if i < len(TEMAS) - 1:
            time.sleep(3)

    print(f"\nTotal: {len(todos)} papers descargados")

    print("\nTroceando en chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(todos)
    print(f"Chunks generados: {len(chunks)}")

    print("\nCargando modelo de embeddings (all-MiniLM-L6-v2)...")
    modelo = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("Construyendo FAISS y guardando en disco...")
    vs = FAISS.from_documents(chunks, modelo)
    os.makedirs(RUTA_VECTORSTORE, exist_ok=True)
    vs.save_local(RUTA_VECTORSTORE)

    print(f"\n✅ Vectorstore guardado en {RUTA_VECTORSTORE}/")
    print("=" * 55)


if __name__ == "__main__":
    construir()
