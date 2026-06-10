from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from src.prompts.graph_rag_prompt import graph_rag_template
from src.config import obtener_modelo
from src.graph_rag.graph_builder import construir_grafo
from src.graph_rag.graph_query import consultar_grafo
from src.judge.llm_judge import evaluar_respuesta

load_dotenv()

def generar_divulgacion_graph(tema, nombre_modelo, idioma, cantidad_papers=3):
    grafo, papers = construir_grafo(tema, cantidad_papers=cantidad_papers)

    terminos_busqueda = tema.split()
    resultado_consulta = consultar_grafo(grafo, terminos_busqueda, profundidad=1)
    contexto = "\n".join(resultado_consulta["contexto"])

    if not contexto.strip():
        contexto = "No se encontraron relaciones específicas en el grafo para este tema."

    llm = obtener_modelo(nombre_modelo)
    chain = graph_rag_template | llm | StrOutputParser()

    explicacion = chain.invoke({
        "contexto": contexto,
        "tema": tema,
        "idioma": idioma,
    })

    evaluacion = evaluar_respuesta(contexto, explicacion)

    return {
        "explicacion": explicacion,
        "papers": papers,
        "entidades": resultado_consulta["entidades_encontradas"],
        "contexto_grafo": resultado_consulta["contexto"],
        "evaluacion": evaluacion,
        "stats_grafo": {
            "nodos": grafo.number_of_nodes(),
            "aristas": grafo.number_of_edges(),
        },
    }