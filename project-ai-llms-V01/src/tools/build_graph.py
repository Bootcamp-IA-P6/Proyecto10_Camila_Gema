# src/tools/build_graph.py

# =====================================================================
# SCRIPT DE CONSTRUCCIÓN DEL GRAFO DE CONOCIMIENTO
#
# Lee los chunks del vectorstore FAISS (ya construido con arXiv)
# y pide al LLM que extraiga relaciones entre conceptos.
#
# Workflow:
#   1. python build_vectorstore_arxiv.py   (construye vectorstore_ia/)
#   2. python src/tools/build_graph.py     (construye knowledge_graph.pkl)
#
# Requiere: GROQ_API_KEY en .env local
# =====================================================================

import logging
import os
import pickle
import json
import time
import networkx as nx
import requests
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("build_graph")

RAIZ_PROYECTO    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUTA_VECTORSTORE = os.path.join(RAIZ_PROYECTO, "vectorstore_ia")
RUTA_GRAFO       = os.path.join(RAIZ_PROYECTO, "knowledge_graph.pkl")

MAX_CHUNKS = 40


def extraer_relaciones_con_llm(texto: str, groq_key: str) -> list:
    prompt = f"""
    Eres un extractor de conocimiento científico.
    Lee este texto sobre Inteligencia Artificial y extrae las relaciones
    más importantes entre conceptos científicos.

    TEXTO:
    {texto[:1500]}

    INSTRUCCIONES:
    - Extrae entre 3 y 6 relaciones importantes
    - Cada relación debe tener: sujeto, relacion, objeto
    - Los conceptos deben ser términos técnicos concretos
    - Las relaciones deben ser verbos como: es_tipo_de, usa, desarrollado_por,
      base_de, mejora_a, relacionado_con, parte_de, aplicado_en
    - Responde SOLO con un JSON válido, sin explicaciones

    FORMATO EXACTO:
    [
        {{"sujeto": "Transformer", "relacion": "es_tipo_de", "objeto": "Red Neuronal"}},
        {{"sujeto": "BERT", "relacion": "desarrollado_por", "objeto": "Google"}}
    ]
    """
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key.strip()}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0
            },
            timeout=15
        )
        if resp.status_code == 200:
            contenido = resp.json()["choices"][0]["message"]["content"].strip()
            inicio = contenido.find("[")
            fin    = contenido.rfind("]") + 1
            if inicio != -1 and fin > 0:
                return json.loads(contenido[inicio:fin])
    except Exception as e:
        logger.warning(f"  Error extrayendo relaciones: {e}")
    return []


def construir_grafo():
    logger.info("=" * 60)
    logger.info("CONSTRUYENDO GRAFO DESDE VECTORSTORE FAISS")
    logger.info("=" * 60)

    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        logger.error("GROQ_API_KEY no encontrada en .env")
        return

    # ------------------------------------------------------------------
    # PASO 1: Cargar documentos del vectorstore FAISS
    # ------------------------------------------------------------------
    logger.info("PASO 1: Cargando chunks del vectorstore...")

    if not os.path.exists(RUTA_VECTORSTORE):
        logger.error(f"No existe {RUTA_VECTORSTORE} — ejecuta primero build_vectorstore_arxiv.py")
        return

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = FAISS.load_local(RUTA_VECTORSTORE, embeddings, allow_dangerous_deserialization=True)

    # El docstore de FAISS guarda los chunks como dict {id: Document}
    todos_los_chunks = list(vs.docstore._dict.values())
    logger.info(f"PASO 1 OK: {len(todos_los_chunks)} chunks cargados del vectorstore")

    # Usamos chunks más grandes para que el LLM tenga contexto suficiente
    # Re-agrupamos los chunks pequeños (1000 chars) en bloques de 2000
    textos_completos = [c.page_content for c in todos_los_chunks]
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks_grafo = splitter.create_documents(textos_completos)

    chunks_a_procesar = chunks_grafo[:MAX_CHUNKS]
    logger.info(f"Procesaremos {len(chunks_a_procesar)} de {len(chunks_grafo)} chunks")

    # ------------------------------------------------------------------
    # PASO 2: Extraer relaciones con LLM
    # ------------------------------------------------------------------
    logger.info("PASO 2: Extrayendo relaciones con el LLM...")

    todas_las_relaciones = []
    for i, chunk in enumerate(chunks_a_procesar):
        logger.info(f"  Chunk {i+1}/{len(chunks_a_procesar)}...")
        relaciones = extraer_relaciones_con_llm(chunk.page_content, groq_key)
        todas_las_relaciones.extend(relaciones)
        logger.info(f"  {len(relaciones)} relaciones extraídas")
        time.sleep(1)

    logger.info(f"PASO 2 OK: {len(todas_las_relaciones)} relaciones en total")

    # ------------------------------------------------------------------
    # PASO 3: Construir grafo con NetworkX
    # ------------------------------------------------------------------
    logger.info("PASO 3: Construyendo grafo...")

    grafo = nx.DiGraph()
    for rel in todas_las_relaciones:
        try:
            sujeto   = rel.get("sujeto", "").strip()
            relacion = rel.get("relacion", "").strip()
            objeto   = rel.get("objeto", "").strip()
            if sujeto and relacion and objeto:
                grafo.add_edge(sujeto, objeto, label=relacion)
        except Exception:
            continue

    logger.info(f"PASO 3 OK: {grafo.number_of_nodes()} nodos, {grafo.number_of_edges()} aristas")
    for u, v, data in list(grafo.edges(data=True))[:10]:
        logger.info(f"  '{u}' --[{data.get('label','')}]--> '{v}'")

    # ------------------------------------------------------------------
    # PASO 4: Guardar
    # ------------------------------------------------------------------
    with open(RUTA_GRAFO, "wb") as f:
        pickle.dump(grafo, f)

    logger.info(f"Grafo guardado en {RUTA_GRAFO}")
    logger.info("=" * 60)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(override=True)
    construir_grafo()
