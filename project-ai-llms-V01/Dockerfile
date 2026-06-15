FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# libgomp1 es necesario para torch en Debian slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# torch se instala desde el índice CPU para no arrastrar CUDA (~2GB menos)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Pre-descarga el modelo de embeddings dentro de la imagen
# Así el RAG funciona sin internet en runtime
RUN python -c "from sentence_transformers import SentenceTransformer; \
               SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copia el código y los archivos del proyecto
COPY . .

# Construye el vectorstore FAISS descargando papers de arXiv
# No necesita API keys — usa all-MiniLM-L6-v2 local y la API pública de arXiv
RUN python build_vectorstore_arxiv.py

# Puerto que usa HuggingFace Spaces
EXPOSE 7860

CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
