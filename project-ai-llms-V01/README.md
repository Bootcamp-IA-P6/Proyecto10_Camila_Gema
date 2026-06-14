---
title: NexusAI Agent Hub
emoji: ⚡
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# NexusAI — Orquestador de Agentes

Sistema multiagente de IA para generar contenido para redes sociales, divulgación científica con RAG y análisis financiero en tiempo real.

## Agentes disponibles

- **Agente General** — enrutador automático que detecta el tipo de petición
- **Agente Científico** — respuestas basadas en papers académicos con Graph RAG (FAISS + NetworkX)
- **Agente Financiero** — precios de acciones en tiempo real vía yfinance
- **Agente de Contenido Social** — posts optimizados para LinkedIn, Instagram y Twitter/X

## Variables de entorno necesarias

| Variable | Descripción |
|---|---|
| `GROQ_API_KEY` | API key de Groq (obligatoria) |
| `LANGCHAIN_API_KEY` | API key de LangSmith (opcional, para trazabilidad) |
| `UNSPLASH_ACCESS_KEY` | API key de Unsplash (opcional, para imágenes) |
| `LANGCHAIN_TRACING_V2` | `true` para activar trazas en LangSmith |
| `LANGCHAIN_PROJECT` | Nombre del proyecto en LangSmith |

## Stack tecnológico

- **LangChain** — orquestación de agentes
- **Groq** — inferencia LLM ultrarrápida (Llama 3.1, Mixtral)
- **FAISS** — base de datos vectorial local
- **HuggingFace** — modelo de embeddings `all-MiniLM-L6-v2`
- **NetworkX** — grafo de conocimiento
- **yfinance** — datos financieros en tiempo real
- **Streamlit** — interfaz web
