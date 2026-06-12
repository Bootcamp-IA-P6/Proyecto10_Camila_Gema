"""Construye la biblioteca vectorial de papers de arXiv para el RAG vectorial.

Recorre una lista de temas de IA y, por cada uno, descarga papers de arXiv,
los trocea, los convierte en embeddings y los guarda en chroma_db/.

Se usa tanto en local (para tener una biblioteca rica al desarrollar) como
dentro del Dockerfile (para que producción se reconstruya con los mismos temas).

Uso:  python poblar_biblioteca.py
"""
import shutil
import time

from src.rag.ingesta import construir_biblioteca, RUTA_CHROMA

# Temas que cubre la biblioteca. Añade o quita líneas a tu gusto.
TEMAS = [
    "transformer attention mechanism",
    "large language models",
    "retrieval augmented generation",
    "reinforcement learning from human feedback",
    "diffusion models image generation",
    "knowledge graph embeddings",
    "prompt engineering in context learning",
]

PAPERS_POR_TEMA = 6


def poblar(reiniciar=True):
    """Construye la biblioteca. Si reiniciar=True, parte de cero."""
    if reiniciar:
        shutil.rmtree(RUTA_CHROMA, ignore_errors=True)

    total = 0
    for i, tema in enumerate(TEMAS):
        n = construir_biblioteca(tema, cantidad=PAPERS_POR_TEMA)
        total += n
        print(f"  ✓ {tema}: +{n} trozos (acumulado: {total})")
        # Cortesía con arXiv: pausa entre temas para no toparse con el límite (429)
        if i < len(TEMAS) - 1:
            time.sleep(3)

    print(f"\nBiblioteca lista: {total} trozos de {len(TEMAS)} temas.")
    return total


if __name__ == "__main__":
    poblar()
