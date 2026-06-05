# src/tools/build_vectorstore.py

# =====================================================================
# SCRIPT DE CONSTRUCCIÓN DE LA BASE DE DATOS VECTORIAL
# 
# Este script se ejecuta UNA SOLA VEZ desde la terminal con:
#   python src/tools/build_vectorstore.py
#
# Lo que hace:
#   1. Descarga papers de arXiv sobre Inteligencia Artificial
#   2. Los trocea en fragmentos pequeños (chunks)
#   3. Convierte cada fragmento en vectores numéricos (embeddings)
#   4. Guarda todo en disco en la carpeta "vectorstore_ia/"
#
# La próxima vez que el usuario pregunte algo, el RAG leerá
# directamente de esa carpeta SIN necesitar llamar a arXiv.
# =====================================================================

import logging
import os
from langchain_community.document_loaders import ArxivLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Configuramos los logs para ver qué está pasando
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("build_vectorstore")

# =====================================================================
# CONFIGURACIÓN — aquí defines qué papers descargar
# Puedes añadir más temas simplemente añadiendo más strings a la lista
# =====================================================================
TEMAS_A_DESCARGAR = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "natural language processing",
    "transformer neural networks",
]

# Cuántos papers descargar por tema (2 es suficiente para una PoC)
PAPERS_POR_TEMA = 2

# Dónde guardar la base de datos vectorial en disco
# os.path.dirname(__file__)  → carpeta donde está este script (src/tools/)
# "../.."                    → subimos dos niveles hasta la raíz del proyecto
RUTA_VECTORSTORE = os.path.join(
    os.path.dirname(__file__), "..", "..", "vectorstore_ia"
)


def descargar_papers(tema: str) -> list:
    """
    Descarga papers de arXiv sobre un tema concreto.
    Devuelve una lista de documentos de LangChain.
    """
    logger.info(f"  Descargando papers sobre '{tema}'...")
    try:
        loader = ArxivLoader(
            query=tema,
            load_max_docs=PAPERS_POR_TEMA
        )
        docs = loader.load()
        logger.info(f"  ✅ {len(docs)} papers descargados sobre '{tema}'")
        for doc in docs:
            titulo = doc.metadata.get("Title", "Sin título")
            logger.info(f"     - {titulo}")
        return docs
    except Exception as e:
        logger.error(f"  ❌ Error descargando '{tema}': {str(e)}")
        return []  # si falla un tema, continuamos con los demás


def construir_vectorstore():
    """
    Función principal que construye y guarda la base de datos vectorial.
    """
    logger.info("=" * 60)
    logger.info("INICIANDO CONSTRUCCIÓN DE LA BASE DE DATOS VECTORIAL")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # PASO 1: DESCARGA DE PAPERS
    # Descargamos papers de arXiv para cada tema de la lista
    # Si un tema falla (rate limit, etc.) continuamos con el siguiente
    # ------------------------------------------------------------------
    logger.info(f"PASO 1: Descargando papers de {len(TEMAS_A_DESCARGAR)} temas...")

    todos_los_documentos = []
    for tema in TEMAS_A_DESCARGAR:
        docs = descargar_papers(tema)
        todos_los_documentos.extend(docs)  # añadimos a la lista total

    logger.info(f"PASO 1 OK: Total de documentos descargados: {len(todos_los_documentos)}")

    if not todos_los_documentos:
        logger.error("No se descargó ningún documento. Abortando.")
        return

    # ------------------------------------------------------------------
    # PASO 2: CHUNKING
    # Troceamos todos los documentos en fragmentos de 1000 caracteres
    # ------------------------------------------------------------------
    logger.info("PASO 2: Troceando documentos en chunks...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(todos_los_documentos)

    logger.info(f"PASO 2 OK: {len(todos_los_documentos)} documentos → {len(chunks)} chunks")

    # ------------------------------------------------------------------
    # PASO 3: EMBEDDINGS
    # Convertimos cada chunk en un vector numérico
    # La primera vez descarga el modelo (~90MB), las siguientes es rápido
    # ------------------------------------------------------------------
    logger.info("PASO 3: Cargando modelo de embeddings...")
    logger.info("(La primera vez puede tardar unos minutos descargando el modelo)")

    modelo_embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    logger.info("PASO 3 OK: Modelo de embeddings listo")

    # ------------------------------------------------------------------
    # PASO 4: CREAR Y GUARDAR LA BASE DE DATOS VECTORIAL EN DISCO
    # FAISS.from_documents() crea la base de datos en memoria
    # .save_local() la guarda en disco para usarla después
    # ------------------------------------------------------------------
    logger.info("PASO 4: Creando y guardando la base de datos vectorial...")

    vector_store = FAISS.from_documents(chunks, modelo_embeddings)

    # Creamos la carpeta si no existe
    os.makedirs(RUTA_VECTORSTORE, exist_ok=True)

    # Guardamos en disco — esto crea dos archivos:
    # - index.faiss  (los vectores)
    # - index.pkl    (los textos originales)
    vector_store.save_local(RUTA_VECTORSTORE)

    logger.info(f"PASO 4 OK: Base de datos guardada en '{RUTA_VECTORSTORE}'")
    logger.info("=" * 60)
    logger.info("✅ BASE DE DATOS VECTORIAL CONSTRUIDA CON ÉXITO")
    logger.info(f"   Documentos: {len(todos_los_documentos)}")
    logger.info(f"   Chunks:     {len(chunks)}")
    logger.info(f"   Guardada en: vectorstore_ia/")
    logger.info("=" * 60)
    logger.info("Ahora puedes ejecutar tu app con: streamlit run src/ui/app.py")


# Esto hace que el script se ejecute solo cuando lo llamas directamente
# y no cuando otro archivo lo importa
if __name__ == "__main__":
    construir_vectorstore()