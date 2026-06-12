# src/tools/build_graph.py

# =====================================================================
# SCRIPT DE CONSTRUCCIÓN DEL GRAFO DE CONOCIMIENTO
#
# Se ejecuta UNA SOLA VEZ desde la raíz del proyecto con:
#   python src/tools/build_graph.py
#
# Lo que hace:
#   1. Lee los PDFs de la carpeta papers_ia/
#   2. Le pide al LLM que extraiga relaciones entre conceptos
#      de cada fragmento de texto
#   3. Construye un grafo con esas relaciones
#   4. Guarda el grafo en disco como knowledge_graph.pkl
#
# Ejemplo de relación que extrae:
#   ("Transformer", "es_tipo_de", "Red Neuronal")
#   ("BERT", "desarrollado_por", "Google")
#   ("Deep Learning", "usa", "Redes Neuronales")
# =====================================================================

import logging
import os
import pickle
import json
import time
import networkx as nx
import requests
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("build_graph")

# =====================================================================
# RUTAS
# =====================================================================
RAIZ_PROYECTO   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CARPETA_PDFS    = os.path.join(RAIZ_PROYECTO, "papers_ia")
RUTA_GRAFO      = os.path.join(RAIZ_PROYECTO, "knowledge_graph.pkl")


def extraer_relaciones_con_llm(texto: str, groq_key: str) -> list:
    """
    Le pide al LLM de Groq que lea un fragmento de texto científico
    y extraiga las relaciones entre conceptos en formato JSON.

    Una relación tiene tres partes:
    - sujeto:   el concepto principal  (ej: "Transformer")
    - relacion: cómo se conectan       (ej: "es_tipo_de")
    - objeto:   el concepto relacionado(ej: "Red Neuronal")
    """
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
                "Authorization": f"Bearer {groq_key}",
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

            # Limpiamos el JSON por si el LLM añade texto extra
            inicio = contenido.find("[")
            fin    = contenido.rfind("]") + 1
            if inicio != -1 and fin > 0:
                json_limpio = contenido[inicio:fin]
                relaciones  = json.loads(json_limpio)
                return relaciones

    except Exception as e:
        logger.warning(f"  Error extrayendo relaciones: {e}")

    return []  # si falla, devolvemos lista vacía


def construir_grafo():
    """
    Función principal que construye y guarda el grafo de conocimiento.
    """
    logger.info("=" * 60)
    logger.info("INICIANDO CONSTRUCCIÓN DEL GRAFO DE CONOCIMIENTO")
    logger.info("=" * 60)

    # Comprobamos que tenemos la API key de Groq
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        logger.error("No se encontró GROQ_API_KEY en el .env — necesaria para extraer relaciones")
        return

    # ------------------------------------------------------------------
    # PASO 1: LEER LOS PDFs
    # Igual que en build_vectorstore.py
    # ------------------------------------------------------------------
    logger.info("PASO 1: Leyendo PDFs de papers_ia/...")

    if not os.path.exists(CARPETA_PDFS):
        logger.error(f"No existe la carpeta: {CARPETA_PDFS}")
        return

    archivos_pdf = [f for f in os.listdir(CARPETA_PDFS) if f.endswith(".pdf")]
    if not archivos_pdf:
        logger.error("No hay PDFs en papers_ia/")
        return

    todos_los_documentos = []
    for nombre_pdf in archivos_pdf:
        try:
            loader = PyMuPDFLoader(os.path.join(CARPETA_PDFS, nombre_pdf))
            docs   = loader.load()
            todos_los_documentos.extend(docs)
            logger.info(f"  ✅ '{nombre_pdf}' leído ({len(docs)} páginas)")
        except Exception as e:
            logger.error(f"  ❌ Error leyendo '{nombre_pdf}': {e}")

    logger.info(f"PASO 1 OK: {len(todos_los_documentos)} páginas leídas")

    # ------------------------------------------------------------------
    # PASO 2: CHUNKING
    # Usamos chunks más grandes (2000 chars) para que el LLM tenga
    # suficiente contexto para extraer relaciones significativas
    # ------------------------------------------------------------------
    logger.info("PASO 2: Troceando documentos en chunks...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(todos_los_documentos)

    # Limitamos a 30 chunks para no gastar demasiadas llamadas a la API
    chunks_a_procesar = chunks[:30]
    logger.info(f"PASO 2 OK: Procesaremos {len(chunks_a_procesar)} chunks de {len(chunks)} totales")

    # ------------------------------------------------------------------
    # PASO 3: EXTRAER RELACIONES CON EL LLM
    # Para cada chunk le pedimos al LLM que identifique relaciones
    # entre conceptos científicos
    # ------------------------------------------------------------------
    logger.info("PASO 3: Extrayendo relaciones con el LLM...")
    logger.info("(Esto puede tardar unos minutos — hace una llamada por chunk)")

    todas_las_relaciones = []

    for i, chunk in enumerate(chunks_a_procesar):
        logger.info(f"  Procesando chunk {i+1}/{len(chunks_a_procesar)}...")

        relaciones = extraer_relaciones_con_llm(chunk.page_content, groq_key)
        todas_las_relaciones.extend(relaciones)

        logger.info(f"  ✅ {len(relaciones)} relaciones extraídas de este chunk")

        # Esperamos 1 segundo entre llamadas para no saturar la API de Groq
        time.sleep(1)

    logger.info(f"PASO 3 OK: {len(todas_las_relaciones)} relaciones extraídas en total")

    # ------------------------------------------------------------------
    # PASO 4: CONSTRUIR EL GRAFO CON NETWORKX
    # NetworkX es la librería estándar de Python para grafos.
    # Cada concepto es un nodo y cada relación es una arista (edge)
    # ------------------------------------------------------------------
    logger.info("PASO 4: Construyendo el grafo con NetworkX...")

    # DiGraph = Directed Graph = grafo dirigido
    # "dirigido" significa que las relaciones tienen dirección:
    # "Transformer" → "es_tipo_de" → "Red Neuronal"
    # (no es lo mismo al revés)
    grafo = nx.DiGraph()

    relaciones_añadidas = 0
    for rel in todas_las_relaciones:
        try:
            sujeto   = rel.get("sujeto", "").strip()
            relacion = rel.get("relacion", "").strip()
            objeto   = rel.get("objeto", "").strip()

            # Solo añadimos si los tres campos tienen contenido
            if sujeto and relacion and objeto:
                # add_edge añade automáticamente los nodos si no existen
                # el atributo "label" guarda el tipo de relación
                grafo.add_edge(sujeto, objeto, label=relacion)
                relaciones_añadidas += 1

        except Exception:
            continue

    logger.info(f"PASO 4 OK: Grafo construido con {grafo.number_of_nodes()} nodos "
                f"y {grafo.number_of_edges()} aristas")

    # Mostramos algunos ejemplos de relaciones del grafo
    logger.info("Ejemplos de relaciones encontradas:")
    for u, v, data in list(grafo.edges(data=True))[:10]:
        logger.info(f"  '{u}' --[{data.get('label','')}]--> '{v}'")

    # ------------------------------------------------------------------
    # PASO 5: GUARDAR EL GRAFO EN DISCO
    # Usamos pickle para serializar el objeto de NetworkX
    # ------------------------------------------------------------------
    logger.info("PASO 5: Guardando grafo en disco...")

    with open(RUTA_GRAFO, "wb") as f:
        pickle.dump(grafo, f)

    logger.info(f"PASO 5 OK: Grafo guardado en '{RUTA_GRAFO}'")
    logger.info("=" * 60)
    logger.info("✅ GRAFO DE CONOCIMIENTO CONSTRUIDO CON ÉXITO")
    logger.info(f"   Nodos (conceptos):    {grafo.number_of_nodes()}")
    logger.info(f"   Aristas (relaciones): {grafo.number_of_edges()}")
    logger.info(f"   Guardado en:          knowledge_graph.pkl")
    logger.info("=" * 60)
    logger.info("Ahora ejecuta: python src/tools/build_graph.py")
    logger.info("Y después arranca: uv run streamlit run src/ui/app.py")


if __name__ == "__main__":
    # Cargamos el .env para tener acceso a GROQ_API_KEY
    from dotenv import load_dotenv
    load_dotenv(override=True)
    construir_grafo()