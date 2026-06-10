from src.generators.rag_generator import generar_divulgacion
from src.judge.llm_judge import evaluar_respuesta
from src.rag.consulta import buscar_trozos_relevantes

tema = "¿Tienen personalidad los modelos de lenguaje?"
explicacion, fuentes = generar_divulgacion(tema, "Llama 3.3 70B", "español")

trozos = buscar_trozos_relevantes(tema, cantidad=3)
fuentes_texto = "\n\n---\n\n".join([t.page_content for t in trozos])

evaluacion = evaluar_respuesta(fuentes_texto, explicacion)

print("=== EXPLICACIÓN ===")
print(explicacion[:500], "...\n")
print("=== EVALUACIÓN DEL JUEZ ===")
print(f"Puntuación: {evaluacion['puntuacion']}/5")
print(f"Justificación: {evaluacion['justificacion']}")