from langchain.prompts import PromptTemplate

triplet_template = PromptTemplate(
    input_variables=["texto"],
    template="""Eres un experto en extracción de conocimiento de textos científicos. Tu tarea es leer el siguiente texto y extraer las relaciones más importantes en forma de tripletas (sujeto, relación, objeto).

REGLAS:
- Cada tripleta debe ser una afirmación clara y autocontenida.
- Sujetos y objetos deben ser entidades concretas (personas, organizaciones, conceptos, técnicas, modelos, datasets), no frases largas.
- La relación debe ser un verbo o frase verbal corta (ej: "desarrolló", "se basa en", "supera a", "es un tipo de").
- Extrae como máximo 10 tripletas, priorizando las más informativas.
- Si el texto no contiene información factual extraíble, devuelve una lista vacía.

TEXTO:
{texto}

Devuelve EXCLUSIVAMENTE un JSON con este formato exacto, sin texto adicional ni explicaciones:
{{"tripletas": [["sujeto1", "relacion1", "objeto1"], ["sujeto2", "relacion2", "objeto2"]]}}"""
)