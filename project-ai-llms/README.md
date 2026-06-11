# 🗼 Faro

> **Luz para tus ideas** — un estudio de contenido multiagente que enruta tu petición al especialista adecuado y la apoya en fuentes reales.

Faro es una aplicación [Streamlit](https://streamlit.io/) que combina **varios agentes de IA** bajo un mismo techo. Escribes lo que necesitas en lenguaje natural y un enrutador LLM decide qué agente lo resuelve mejor: redactar contenido para redes, divulgar ciencia apoyándose en papers de arXiv, o componer una newsletter financiera con noticias del día. Las respuestas basadas en fuentes pasan además por un **juez LLM** que puntúa su fiabilidad.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.50-FF4B4B) ![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C) ![Groq](https://img.shields.io/badge/LLM-Groq-F55036)

---

## ✨ Características

| | Agente | Qué hace | Fuentes / técnica |
|---|---|---|---|
| ✍️ | **Creador de contenido** | Publicaciones para Twitter/X, LinkedIn, Instagram o blog, adaptadas a plataforma, audiencia y tono. Sugiere imágenes. | Generación directa + imágenes de [Pexels](https://www.pexels.com/api/) |
| 🔬 | **Divulgador científico (RAG)** | Explica un concepto científico de forma comprensible, citando papers reales. Dos motores a elegir. | **RAG vectorial** (ChromaDB) o **Graph RAG** (grafo de conocimiento) sobre [arXiv](https://arxiv.org/) |
| 📈 | **Editor financiero** | Redacta una newsletter diaria sobre los mercados a partir de noticias en tiempo real. | API de [Finnhub](https://finnhub.io/) |

Además:

- 🧭 **Enrutador inteligente** — un LLM analiza tu petición y elige el agente adecuado, con justificación. Modo manual disponible si prefieres elegir tú.
- ⚖️ **Juez LLM-as-a-judge** — evalúa de 1 a 5 si la divulgación se apoya fielmente en las fuentes, sin invenciones.
- 🕸️ **Grafo de conocimiento interactivo** — el modo Graph RAG extrae tripletas (sujeto–relación–objeto) de los papers, construye un grafo con NetworkX y lo visualiza con pyvis dentro de la app.
- 🌍 **Multiidioma** — español, inglés, francés e italiano.
- 🤖 **Varios modelos** — Llama 3.3 70B y GPT-OSS 20B vía Groq, seleccionables en la interfaz.
- 🎨 **Tema "Faro"** — interfaz nocturna con logo animado, haces de luz y partículas flotantes.

---

## 🏗️ Arquitectura

```
                          ┌─────────────────────────┐
        Petición  ─────▶  │   Enrutador (LLM)       │
     (lenguaje natural)   │   router/agent_router   │
                          └───────────┬─────────────┘
                                      │  elige 1 de 3
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
   ┌─────────────────┐     ┌────────────────────┐     ┌──────────────────┐
   │ contenido_      │     │ divulgacion_rag    │     │ newsletter_      │
   │ general         │     │                    │     │ financiera       │
   │                 │     │  ┌──────────────┐  │     │                  │
   │ + imágenes      │     │  │ RAG vectorial│  │     │ noticias Finnhub │
   │   (Pexels)      │     │  │ (ChromaDB)   │  │     │ en tiempo real   │
   └─────────────────┘     │  ├──────────────┤  │     └──────────────────┘
                           │  │ Graph RAG    │  │
                           │  │ (NetworkX)   │  │
                           │  └──────┬───────┘  │
                           └─────────┼──────────┘
                                     ▼
                           ┌──────────────────┐
                           │ Juez LLM (1–5)   │
                           └──────────────────┘
```

Todos los modelos se sirven a través de **Groq** (`langchain-groq`). Los embeddings para el RAG vectorial se calculan en local con `sentence-transformers/all-MiniLM-L6-v2`.

---

## 🚀 Puesta en marcha

### 1. Requisitos previos

- Python 3.9 o superior
- Claves de API (ver [Variables de entorno](#-variables-de-entorno))

### 2. Instalación

```bash
# Clona y entra en el proyecto
cd project-ai-llms

# Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# Instala dependencias
pip install -r requirements.txt
```

> 💡 ¿Prefieres no instalar nada en local? Salta a [🐳 Ejecutar con Docker](#-ejecutar-con-docker).

### 3. Variables de entorno

Crea un archivo `.env` en la raíz con tus claves:

```env
GROQ_API_KEY=tu_clave_groq            # Obligatoria — todos los agentes
PEXELS_API_KEY=tu_clave_pexels        # Imágenes del creador de contenido
FINNHUB_API_KEY=tu_clave_finnhub      # Newsletter financiera

# Opcional — trazabilidad con LangSmith
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=tu_clave_langsmith
LANGSMITH_PROJECT=faro
```

| Variable | ¿Para qué? | Dónde conseguirla |
|---|---|---|
| `GROQ_API_KEY` | Inferencia de todos los LLM | [console.groq.com](https://console.groq.com/keys) |
| `PEXELS_API_KEY` | Imágenes sugeridas | [pexels.com/api](https://www.pexels.com/api/) |
| `FINNHUB_API_KEY` | Noticias financieras | [finnhub.io](https://finnhub.io/) |
| `LANGSMITH_*` | Trazas (opcional) | [smith.langchain.com](https://smith.langchain.com/) |

### 4. (Solo RAG vectorial) Construir la biblioteca de papers

El modo **RAG vectorial** lee de una base vectorial local (`chroma_db/`). Para llenarla con papers de arXiv sobre un tema:

```python
from src.rag.ingesta import construir_biblioteca
construir_biblioteca("large language models", cantidad=5)
```

> El modo **Graph RAG** no necesita este paso: construye el grafo en vivo desde arXiv en cada consulta.

### 5. Ejecutar la app

```bash
streamlit run app.py
```

Abre [http://localhost:8501](http://localhost:8501) en tu navegador.

---

## 🐳 Ejecutar con Docker

Si prefieres no instalar dependencias en local, la app está dockerizada. Solo necesitas tener Docker y un archivo `.env` con tus claves (ver [Variables de entorno](#-variables-de-entorno)).

### Con Docker Compose (recomendado)

```bash
docker compose up --build
```

Levanta el contenedor, carga las claves desde tu `.env` y publica la app en [http://localhost:8501](http://localhost:8501). Para pararlo: `docker compose down`.

### Con Docker a secas

```bash
# Construir la imagen
docker build -t faro .

# Ejecutar pasando las claves del .env
docker run --rm -p 8501:8501 --env-file .env faro
```

**Detalles de la imagen:**

- Base `python:3.9-slim` y **torch en versión CPU**, para una imagen lo más ligera posible.
- El modelo de embeddings (`all-MiniLM-L6-v2`) se **pre-descarga durante el build**, así el RAG vectorial funciona sin descargas en el primer arranque.
- La biblioteca vectorial (`chroma_db/`) se monta como volumen: lo que ingestes se conserva en tu máquina.
- Las claves **nunca** se incluyen en la imagen; se pasan al arrancar vía `--env-file` / `env_file`.

> ⚠️ El `.env` está en `.gitignore` y en `.dockerignore`: si clonas el repo en limpio, créalo antes de construir.

---

## 🧠 Cómo funciona cada pieza

### Enrutador (`src/router/`)
Un prompt presenta los tres agentes al LLM, que devuelve un JSON `{"agente", "justificacion"}`. Si la salida no es válida o el agente no existe, cae con seguridad en `contenido_general`.

### Creador de contenido (`src/generators/content_generator.py`)
Genera el texto a partir de tema, plataforma, audiencia, tono, idioma e info opcional de empresa, y acompaña el resultado con imágenes de Pexels.

### Divulgación científica — RAG vectorial (`src/rag/`)
1. **Ingesta**: descarga papers de arXiv, los trocea (`chunk_size=500`) y los indexa en ChromaDB con embeddings de HuggingFace.
2. **Consulta**: busca los trozos más similares al tema y los pasa como contexto al LLM.
3. **Evaluación**: el juez compara explicación y fuentes.

### Divulgación científica — Graph RAG (`src/graph_rag/`)
1. **Construcción**: por cada paper, un LLM extrae tripletas (sujeto–relación–objeto) que forman un `MultiDiGraph` de NetworkX.
2. **Consulta**: localiza entidades que coinciden con los términos de búsqueda y recoge sus relaciones como contexto.
3. **Visualización**: pyvis renderiza el grafo interactivo embebido en la app.
4. **Evaluación**: el mismo juez puntúa la fiabilidad.

### Newsletter financiera (`src/news/`)
Descarga noticias generales de mercado desde Finnhub y el LLM las sintetiza en una newsletter, conservando las fuentes enlazadas.

### Juez (`src/judge/`)
Recibe las fuentes y la respuesta generada y devuelve una puntuación de **1 a 5** con justificación, penalizando información no respaldada.

---

## 📁 Estructura del proyecto

```
project-ai-llms/
├── app.py                      # Interfaz Streamlit (tema "Faro")
├── requirements.txt
├── Dockerfile                  # Imagen de la app (python:3.9-slim + torch CPU)
├── docker-compose.yml          # Arranque con un comando
├── .dockerignore
├── listar_modelos.py           # Utilidad: lista los modelos disponibles en Groq
├── .streamlit/
│   └── config.toml             # Tema oscuro náutico
├── chroma_db/                  # Base vectorial local (generada por la ingesta)
├── src/
│   ├── config.py               # Modelos disponibles y fábrica de LLM (Groq)
│   ├── image_search.py         # Búsqueda de imágenes (Pexels)
│   ├── router/                 # Enrutador multiagente
│   ├── generators/             # Un generador por agente
│   │   ├── content_generator.py
│   │   ├── rag_generator.py
│   │   ├── graph_rag_generator.py
│   │   └── news_generator.py
│   ├── rag/                    # RAG vectorial: arXiv → ChromaDB → consulta
│   ├── graph_rag/              # Graph RAG: tripletas → NetworkX → pyvis
│   ├── news/                   # Cargador de noticias (Finnhub)
│   ├── judge/                  # Juez LLM-as-a-judge
│   └── prompts/                # Plantillas de prompts de cada componente
└── test_*.py                   # Scripts de prueba manuales por módulo
```

---

## 🧪 Pruebas

La raíz incluye scripts de prueba manuales para cada módulo. Ejecuta el que quieras comprobar:

```bash
python test_router.py        # Enrutamiento
python test_rag.py           # RAG vectorial
python test_graph_rag.py     # Graph RAG completo
python test_juez.py          # Juez
python test_newsletter.py    # Newsletter financiera
python test_generador.py     # Creador de contenido
python test_imagenes.py      # Búsqueda de imágenes
# … y más
```

> Necesitan las variables de entorno configuradas y, en el caso del RAG vectorial, la biblioteca ya construida.

---

## 🛠️ Tecnologías

- **Frontend**: Streamlit
- **Orquestación LLM**: LangChain + Groq (Llama 3.3 70B, GPT-OSS 20B)
- **RAG vectorial**: ChromaDB + sentence-transformers (`all-MiniLM-L6-v2`)
- **Graph RAG**: NetworkX + pyvis
- **Fuentes externas**: arXiv (papers), Finnhub (noticias), Pexels (imágenes)
- **Observabilidad**: LangSmith (opcional)
