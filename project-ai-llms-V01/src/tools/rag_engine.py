# # src/tools/rag_engine.py

# import logging
# import os
# import requests

# from langchain_core.tools import tool
# from langchain_community.document_loaders import ArxivLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s"
# )
# logger = logging.getLogger("rag_engine")


# @tool
# def investigar_y_sintetizar_ciencia(query: str) -> str:
#     """
#     Busca papers científicos en arXiv sobre CUALQUIER tema de ciencia o tecnología
#     y extrae la información más relevante usando una arquitectura RAG.
#     Acepta preguntas en cualquier idioma y traduce al inglés automáticamente.
#     """

#     # ------------------------------------------------------------------
#     # PASO 1: TRADUCCIÓN
#     # ✅ FIX: Ahora le pedimos al LLM que devuelva SOLO 2-3 palabras clave
#     # en inglés, sin saltos de línea ni palabras extra como "arXiv" o
#     # "simple explanation". La query tiene que ser limpia para arXiv.
#     # ------------------------------------------------------------------
#     logger.info(f"RAG iniciado. Query recibida: '{query}'")
#     logger.info("PASO 1: Traduciendo query al inglés...")

#     groq_key = os.getenv("GROQ_API_KEY", "")
#     query_en_ingles = query

#     if groq_key:
#         try:
#             resp_traduccion = requests.post(
#                 "https://api.groq.com/openai/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {groq_key}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": "llama-3.1-8b-instant",
#                     "messages": [{
#                         "role": "user",
#                         "content": (
#                             f"Extract the main scientific topic from this text and translate it to English. "
#                             f"Return ONLY 2 or 3 keywords in English on a SINGLE LINE, "
#                             f"no explanations, no bullet points, no line breaks. "
#                             f"Example input: 'Investiga sobre redes neuronales' → Example output: 'neural networks' "
#                             f"Now translate: '{query}'"
#                         )
#                     }],
#                     "max_tokens": 20,
#                     "temperature": 0
#                 },
#                 timeout=10
#             )
#             if resp_traduccion.status_code == 200:
#                 # ✅ FIX: limpiamos saltos de línea y espacios extra
#                 query_en_ingles = (
#                     resp_traduccion.json()["choices"][0]["message"]["content"]
#                     .strip()
#                     .strip("'\"")
#                     .replace("\n", " ")   # eliminamos saltos de línea
#                     .replace("  ", " ")   # eliminamos espacios dobles
#                 )
#                 logger.info(f"PASO 1 OK: Query traducida a '{query_en_ingles}'")
#             else:
#                 logger.warning(f"PASO 1 WARNING: Groq devolvió status {resp_traduccion.status_code}. Usando query original.")

#         except Exception as e:
#             logger.warning(f"PASO 1 WARNING: Fallo en traducción ({e}). Usando query original.")
#     else:
#         logger.warning("PASO 1 WARNING: No hay GROQ_API_KEY. Usando query original.")

#     # ------------------------------------------------------------------
#     # PASO 2: BÚSQUEDA EN ARXIV con ArxivLoader
#     # ✅ FIX: ArxivLoader internamente usaba http:// y arXiv redirige a
#     # https:// con un 301. Lo solucionamos limpiando la query y dejando
#     # que ArxivLoader gestione la conexión con sus propios parámetros.
#     # ------------------------------------------------------------------
#     logger.info(f"PASO 2: Buscando en arXiv con query '{query_en_ingles}'...")

#     try:
#         loader = ArxivLoader(
#             query=query_en_ingles,
#             load_max_docs=2
#         )
#         documentos_crudos = loader.load()

#         logger.info(f"PASO 2 OK: ArxivLoader encontró {len(documentos_crudos)} documentos")
#         for i, doc in enumerate(documentos_crudos):
#             titulo = doc.metadata.get("Title", "Sin título")
#             logger.info(f"  - Paper {i+1}: '{titulo}'")

#     except Exception as e:
#         logger.error(f"PASO 2 ERROR: ArxivLoader falló → {str(e)}")
#         return f"Error al buscar en arXiv: {str(e)}"

#     if not documentos_crudos:
#         logger.warning("PASO 2 WARNING: ArxivLoader no devolvió ningún documento")
#         return f"No encontré documentos en arXiv para: '{query_en_ingles}'."

#     # ------------------------------------------------------------------
#     # PASO 3: CHUNKING
#     # Troceamos los textos en fragmentos de 1000 caracteres con
#     # solapamiento de 150 para no cortar frases por la mitad
#     # ------------------------------------------------------------------
#     logger.info("PASO 3: Troceando documentos en chunks...")

#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=150
#     )
#     chunks = text_splitter.split_documents(documentos_crudos)
#     logger.info(f"PASO 3 OK: {len(documentos_crudos)} documentos → {len(chunks)} chunks")

#     # ------------------------------------------------------------------
#     # PASO 4: EMBEDDINGS
#     # Convertimos cada chunk en un vector numérico que representa
#     # su significado semántico
#     # ------------------------------------------------------------------
#     logger.info("PASO 4: Generando embeddings...")

#     try:
#         modelo_embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2"
#         )
#         logger.info("PASO 4 OK: Modelo de embeddings cargado")
#     except Exception as e:
#         logger.error(f"PASO 4 ERROR: Fallo al cargar embeddings → {str(e)}")
#         return f"Error al cargar el modelo de embeddings: {str(e)}"

#     # ------------------------------------------------------------------
#     # PASO 5: BASE DE DATOS VECTORIAL EN MEMORIA (FAISS)
#     # Guardamos todos los vectores para poder buscar por similitud
#     # ------------------------------------------------------------------
#     logger.info("PASO 5: Creando base de datos vectorial FAISS...")

#     try:
#         vector_store = FAISS.from_documents(chunks, modelo_embeddings)
#         logger.info("PASO 5 OK: Base de datos vectorial creada")
#     except Exception as e:
#         logger.error(f"PASO 5 ERROR: Fallo al crear FAISS → {str(e)}")
#         return f"Error al crear la base de datos vectorial: {str(e)}"

#     # ------------------------------------------------------------------
#     # PASO 6: RECUPERACIÓN
#     # Buscamos los 3 chunks más relevantes para la pregunta del usuario
#     # ------------------------------------------------------------------
#     logger.info(f"PASO 6: Buscando chunks más relevantes...")

#     chunks_relevantes = vector_store.similarity_search(query_en_ingles, k=3)
#     logger.info(f"PASO 6 OK: Encontrados {len(chunks_relevantes)} chunks relevantes")

#     # ------------------------------------------------------------------
#     # PASO 7: EMPAQUETADO FINAL
#     # Juntamos los mejores fragmentos para dárselos al LLM como contexto
#     # ------------------------------------------------------------------
#     logger.info("PASO 7: Empaquetando contexto final...")

#     contexto_final = (
#         f"Query buscada en arXiv: '{query_en_ingles}'\n\n"
#         "Fragmentos extraídos de papers científicos reales:\n\n"
#     )
#     for i, chunk in enumerate(chunks_relevantes):
#         contexto_final += f"--- FRAGMENTO {i+1} ---\n{chunk.page_content}\n\n"

#     logger.info(f"PASO 7 OK: RAG completado ✅ ({len(contexto_final)} caracteres de contexto)")

#     return contexto_final

# src/tools/rag_engine.py

import logging
import os

from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Configuramos los logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("rag_engine")

# =====================================================================
# RUTA DE LA BASE DE DATOS VECTORIAL EN DISCO
# Apuntamos a la carpeta vectorstore_ia/ que creó build_vectorstore.py
# os.path.dirname(__file__)  → carpeta de este script (src/tools/)
# "../.."                    → subimos hasta la raíz del proyecto
# =====================================================================
RUTA_VECTORSTORE = os.path.join(
    os.path.dirname(__file__), "..", "..", "vectorstore_ia"
)

# =====================================================================
# CARGAMOS EL MODELO DE EMBEDDINGS UNA SOLA VEZ AL ARRANCAR
# Esto es importante: si lo cargáramos dentro de la función,
# se recargaría cada vez que el usuario pregunta (muy lento).
# Cargándolo aquí, se carga una vez y queda en memoria.
# =====================================================================
logger.info("Cargando modelo de embeddings en memoria...")
try:
    MODELO_EMBEDDINGS = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    logger.info("✅ Modelo de embeddings cargado correctamente")
except Exception as e:
    logger.error(f"❌ Error cargando modelo de embeddings: {str(e)}")
    MODELO_EMBEDDINGS = None


@tool
def investigar_y_sintetizar_ciencia(query: str) -> str:
    """
    Busca información científica sobre Inteligencia Artificial en una base
    de datos local de papers académicos y devuelve los fragmentos más relevantes.
    Útil para responder preguntas sobre IA, machine learning, deep learning,
    redes neuronales, NLP y temas relacionados.
    """

    logger.info(f"RAG iniciado. Query recibida: '{query}'")

    # ------------------------------------------------------------------
    # PASO 1: COMPROBAMOS QUE LA BASE DE DATOS EXISTE EN DISCO
    # Si el usuario no ha ejecutado build_vectorstore.py todavía,
    # le avisamos con un mensaje claro en vez de dar un error raro
    # ------------------------------------------------------------------
    logger.info("PASO 1: Comprobando que existe la base de datos vectorial...")

    if not os.path.exists(RUTA_VECTORSTORE):
        logger.error(f"PASO 1 ERROR: No existe la carpeta '{RUTA_VECTORSTORE}'")
        return (
            "⚠️ La base de datos científica no está construida todavía. "
            "Ejecuta primero: python src/tools/build_vectorstore.py"
        )

    logger.info(f"PASO 1 OK: Base de datos encontrada en '{RUTA_VECTORSTORE}'")

    # ------------------------------------------------------------------
    # PASO 2: CARGAMOS LA BASE DE DATOS DESDE DISCO
    # allow_dangerous_deserialization=True es necesario para cargar
    # archivos .pkl de FAISS — es seguro porque son nuestros propios archivos
    # ------------------------------------------------------------------
    logger.info("PASO 2: Cargando base de datos vectorial desde disco...")

    try:
        vector_store = FAISS.load_local(
            RUTA_VECTORSTORE,
            MODELO_EMBEDDINGS,
            allow_dangerous_deserialization=True
        )
        logger.info("PASO 2 OK: Base de datos cargada correctamente")

    except Exception as e:
        logger.error(f"PASO 2 ERROR: {str(e)}")
        return f"Error al cargar la base de datos vectorial: {str(e)}"

    # ------------------------------------------------------------------
    # PASO 3: RECUPERACIÓN (Retrieval)
    # Buscamos los 3 chunks cuyo significado sea más similar a la query
    # Esto es instantáneo porque todo está en disco, sin llamadas a internet
    # ------------------------------------------------------------------
    logger.info(f"PASO 3: Buscando chunks más relevantes para '{query}'...")

    try:
        chunks_relevantes = vector_store.similarity_search(query, k=3)
        logger.info(f"PASO 3 OK: Encontrados {len(chunks_relevantes)} chunks relevantes")

    except Exception as e:
        logger.error(f"PASO 3 ERROR: {str(e)}")
        return f"Error al buscar en la base de datos: {str(e)}"

    # ------------------------------------------------------------------
    # PASO 4: EMPAQUETADO FINAL
    # Juntamos los mejores fragmentos en un texto que el LLM usará
    # como contexto para generar su respuesta
    # ------------------------------------------------------------------
    logger.info("PASO 4: Empaquetando contexto final para el LLM...")

    contexto_final = "Fragmentos extraídos de papers científicos sobre IA:\n\n"
    for i, chunk in enumerate(chunks_relevantes):
        titulo = chunk.metadata.get("Title", "Paper científico")
        contexto_final += f"--- FRAGMENTO {i+1} (de: {titulo}) ---\n"
        contexto_final += f"{chunk.page_content}\n\n"

    logger.info(f"PASO 4 OK: RAG completado ✅ ({len(contexto_final)} caracteres de contexto)")

    return contexto_final

