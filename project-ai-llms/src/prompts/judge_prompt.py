from langchain.prompts import PromptTemplate

judge_template = PromptTemplate(
    input_variables=["fuentes", "respuesta"],
    template="""Eres un evaluador riguroso de divulgación científica. Tu única tarea es comprobar si una explicación se apoya correctamente en unos extractos de papers.

EXTRACTOS DE PAPERS (la verdad):
{fuentes}

EXPLICACIÓN GENERADA (lo que hay que evaluar):
{respuesta}

CRITERIOS:
- 5 = Toda la información de la explicación aparece en los extractos. No hay invenciones.
- 4 = Casi toda la información se apoya en los extractos. Hay algún detalle menor no respaldado.
- 3 = La explicación tiene partes apoyadas y partes que no están en los extractos.
- 2 = La explicación incluye información importante que no aparece en los extractos.
- 1 = La explicación contradice los extractos o se inventa la mayor parte.

Devuelve EXCLUSIVAMENTE un JSON con este formato exacto, sin texto adicional:
{{"puntuacion": <número del 1 al 5>, "justificacion": "<frase breve explicando por qué>"}}"""
)