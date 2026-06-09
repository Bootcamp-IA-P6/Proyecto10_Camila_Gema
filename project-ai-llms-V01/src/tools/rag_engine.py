# # NOTA: Este archivo es la versión original del RAG.
# # Está reemplazado por graph_rag_engine.py que añade
# # el grafo de conocimiento. Se mantiene como referencia.

# # =====================================================================
# # MOTOR DE GRAPH RAG
# #
# # Combina dos fuentes de conocimiento:
# #   1. FAISS (vectorstore) → fragmentos de texto relevantes
# #   2. NetworkX (grafo)    → conceptos relacionados factualmente
# #
# # El resultado es un contexto más rico que el RAG normal,
# # porque no solo encuentra fragmentos similares sino que también
# # navega las conexiones entre conceptos del grafo.
# # =====================================================================

# import logging
# import os
# import pickle

# import networkx as nx
# from langchain_core.tools import tool
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s"
# )
# logger = logging.getLogger("graph_rag_engine")

# # =====================================================================
# # RUTAS
# # =====================================================================
# # os.path.dirname(__file__)  → carpeta de este script (project-ai-llms-V01/src/)
# # "../.."                    → subimos hasta la raíz del proyecto
# RUTA_VECTORSTORE = os.path.join(
#     os.path.dirname(__file__), "..", "..", "vectorstore_ia"
# )
# RUTA_GRAFO = os.path.join(
#     os.path.dirname(__file__), "..", "knowledge_graph.pkl"
# )

# # =====================================================================
# # CARGAMOS RECURSOS UNA SOLA VEZ AL ARRANCAR LA APP
# # Igual que en rag_engine.py, cargamos fuera de la función
# # para no recargar en cada pregunta
# # =====================================================================
# logger.info("Cargando modelo de embeddings para Graph RAG...")
# try:
#     MODELO_EMBEDDINGS = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2"
#     )
#     logger.info("✅ Modelo de embeddings cargado")
# except Exception as e:
#     logger.error(f"❌ Error cargando embeddings: {e}")
#     MODELO_EMBEDDINGS = None

# logger.info("Cargando grafo de conocimiento desde disco...")
# try:
#     with open(RUTA_GRAFO, "rb") as f:
#         GRAFO = pickle.load(f)
#     logger.info(f"✅ Grafo cargado: {GRAFO.number_of_nodes()} nodos, "
#                 f"{GRAFO.number_of_edges()} aristas")
# except Exception as e:
#     logger.error(f"❌ Error cargando grafo: {e}")
#     GRAFO = None


# def buscar_en_grafo(query: str, max_nodos: int = 5) -> str:
#     """
#     Busca en el grafo de conocimiento los conceptos relacionados
#     con la query del usuario.

#     Estrategia:
#     1. Busca nodos del grafo cuyo nombre aparezca en la query
#     2. Para cada nodo encontrado, recoge sus vecinos (conceptos relacionados)
#     3. Devuelve las relaciones como texto para el LLM

#     Ejemplo:
#     Query: "explícame los transformers"
#     Nodo encontrado: "Transformer"
#     Vecinos: "Red Neuronal" (es_tipo_de), "Atención" (usa), "BERT" (base_de)
#     """
#     if GRAFO is None:
#         return "Grafo de conocimiento no disponible."

#     query_lower = query.lower()
#     contexto_grafo = ""
#     nodos_encontrados = []

#     # Buscamos qué nodos del grafo aparecen mencionados en la query
#     for nodo in GRAFO.nodes():
#         if nodo.lower() in query_lower or query_lower in nodo.lower():
#             nodos_encontrados.append(nodo)

#     # Si no encontramos nodos directos, buscamos por palabras clave
#     if not nodos_encontrados:
#         palabras_query = query_lower.split()
#         for nodo in GRAFO.nodes():
#             nodo_lower = nodo.lower()
#             for palabra in palabras_query:
#                 if len(palabra) > 4 and palabra in nodo_lower:
#                     nodos_encontrados.append(nodo)
#                     break

#     if not nodos_encontrados:
#         logger.info("  No se encontraron nodos relevantes en el grafo para esta query")
#         return ""

#     logger.info(f"  Nodos encontrados en el grafo: {nodos_encontrados[:max_nodos]}")

#     # Para cada nodo encontrado, recogemos sus conexiones
#     contexto_grafo = "Contexto factual del grafo de conocimiento:\n\n"

#     for nodo in nodos_encontrados[:max_nodos]:
#         contexto_grafo += f"Concepto: '{nodo}'\n"

#         # Vecinos de salida — lo que este concepto ES o HACE
#         vecinos_salida = list(GRAFO.successors(nodo))
#         if vecinos_salida:
#             for vecino in vecinos_salida[:4]:
#                 relacion = GRAFO.edges[nodo, vecino].get("label", "relacionado_con")
#                 contexto_grafo += f"  → {relacion} → '{vecino}'\n"

#         # Vecinos de entrada — qué otros conceptos apuntan a este
#         vecinos_entrada = list(GRAFO.predecessors(nodo))
#         if vecinos_entrada:
#             for vecino in vecinos_entrada[:4]:
#                 relacion = GRAFO.edges[vecino, nodo].get("label", "relacionado_con")
#                 contexto_grafo += f"  ← '{vecino}' ← {relacion}\n"

#         contexto_grafo += "\n"

#     return contexto_grafo


# @tool
# def investigar_con_graph_rag(query: str) -> str:
#     """
#     Versión mejorada del motor RAG científico que combina:
#     1. Búsqueda vectorial en papers académicos (FAISS)
#     2. Navegación del grafo de conocimiento (NetworkX)

#     Úsala para responder preguntas sobre Inteligencia Artificial,
#     machine learning, deep learning, redes neuronales y temas relacionados.
#     Proporciona respuestas más precisas y con mayor contexto factual
#     que el RAG tradicional.
#     """
#     logger.info(f"Graph RAG iniciado. Query: '{query}'")

#     # ------------------------------------------------------------------
#     # PASO 1: BÚSQUEDA VECTORIAL (igual que rag_engine.py)
#     # Buscamos los fragmentos de texto más relevantes en FAISS
#     # ------------------------------------------------------------------
#     logger.info("PASO 1: Búsqueda vectorial en FAISS...")

#     contexto_vectorial = ""

#     if not os.path.exists(RUTA_VECTORSTORE):
#         logger.error("No existe el vectorstore — ejecuta build_vectorstore.py primero")
#         contexto_vectorial = "Base de datos vectorial no disponible."
#     else:
#         try:
#             vector_store = FAISS.load_local(
#                 RUTA_VECTORSTORE,
#                 MODELO_EMBEDDINGS,
#                 allow_dangerous_deserialization=True
#             )
#             chunks = vector_store.similarity_search(query, k=3)

#             contexto_vectorial = "Fragmentos relevantes de papers científicos:\n\n"
#             for i, chunk in enumerate(chunks):
#                 titulo = chunk.metadata.get("Title", "Paper científico")
#                 contexto_vectorial += f"--- FRAGMENTO {i+1} (de: {titulo}) ---\n"
#                 contexto_vectorial += f"{chunk.page_content}\n\n"

#             logger.info(f"PASO 1 OK: {len(chunks)} fragmentos encontrados en FAISS")

#         except Exception as e:
#             logger.error(f"PASO 1 ERROR: {e}")
#             contexto_vectorial = f"Error en búsqueda vectorial: {e}"

#     # ------------------------------------------------------------------
#     # PASO 2: BÚSQUEDA EN EL GRAFO
#     # Navegamos el grafo para encontrar conceptos relacionados
#     # ------------------------------------------------------------------
#     logger.info("PASO 2: Buscando en el grafo de conocimiento...")

#     contexto_grafo = buscar_en_grafo(query)

#     if contexto_grafo:
#         logger.info("PASO 2 OK: Contexto del grafo obtenido")
#     else:
#         logger.info("PASO 2: No se encontró contexto relevante en el grafo")

#     # ------------------------------------------------------------------
#     # PASO 3: COMBINAR LOS DOS CONTEXTOS
#     # Juntamos el contexto vectorial y el del grafo en un solo texto
#     # que el LLM usará para generar su respuesta
#     # ------------------------------------------------------------------
#     logger.info("PASO 3: Combinando contextos vectorial y de grafo...")

#     contexto_final = "=" * 50 + "\n"
#     contexto_final += "CONTEXTO ENRIQUECIDO (Graph RAG)\n"
#     contexto_final += "=" * 50 + "\n\n"

#     # Primero el contexto del grafo (hechos concretos y relaciones)
#     if contexto_grafo:
#         contexto_final += contexto_grafo
#         contexto_final += "\n" + "-" * 40 + "\n\n"

#     # Luego el contexto vectorial (fragmentos de papers)
#     contexto_final += contexto_vectorial

#     logger.info(f"PASO 3 OK: Contexto final listo ({len(contexto_final)} caracteres) ✅")

#     return contexto_final




# =====================================================================
# MOTOR RAG — Versión original (v1.0)
#
# NOTA: Este archivo es la versión SIMPLE del RAG.
# Está reemplazado por graph_rag_engine.py que añade el grafo
# de conocimiento. Se mantiene como referencia histórica.
#
# Diferencia con graph_rag_engine.py:
#   rag_engine.py       → solo busca en FAISS (vectores)
#   graph_rag_engine.py → busca en FAISS + navega el grafo NetworkX
# =====================================================================

import logging
import os

from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

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
# Si lo cargáramos dentro de la función, se recargaría cada vez
# que el usuario pregunta (muy lento).
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
        logger.error(f"PASO 1 ERROR: No existe '{RUTA_VECTORSTORE}'")
        return (
            "⚠️ La base de datos científica no está construida todavía. "
            "Ejecuta primero: python src/tools/build_vectorstore.py"
        )

    logger.info(f"PASO 1 OK: Base de datos encontrada")

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

    logger.info(f"PASO 4 OK: RAG completado ✅ ({len(contexto_final)} caracteres)")

    return contexto_final