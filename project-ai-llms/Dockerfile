# Faro — imagen de la aplicación Streamlit
# Base ligera con el mismo Python del proyecto
FROM python:3.9-slim

# Entorno: sin .pyc, logs sin buffer, sin caché de pip y caché de modelos en el proyecto
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# Dependencia de sistema mínima que torch necesita en Debian slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Dependencias de Python.
# torch se resuelve a la build CPU (--extra-index-url) para no arrastrar CUDA
# y mantener la imagen mucho más ligera.
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Pre-descarga del modelo de embeddings para que el RAG vectorial funcione
# en el primer arranque sin tener que bajarlo en caliente.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Código de la aplicación
COPY . .

# Construir la biblioteca vectorial (papers de arXiv) dentro de la imagen.
# Solo usa embeddings locales + arXiv, no requiere claves de API, y evita
# tener que versionar binarios de Chroma en git.
RUN python poblar_biblioteca.py

EXPOSE 8501

# Comprobación de salud propia de Streamlit
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health').status==200 else 1)" || exit 1

# Arranque en modo servidor accesible desde fuera del contenedor
CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]
