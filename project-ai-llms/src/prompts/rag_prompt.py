from langchain.prompts import PromptTemplate

rag_template = PromptTemplate(
    input_variables=["contexto", "tema", "idioma"],
    template="""Eres un divulgador científico experto. Tu tarea es explicar un tema científico de forma clara y comprensible para el público general, basándote ÚNICAMENTE en los siguientes extractos de papers científicos reales.

REGLAS IMPORTANTES:
- No inventes información que no esté en los extractos.
- Si los extractos no contienen suficiente información, indícalo honestamente.
- Usa analogías y lenguaje accesible.
- Menciona ideas concretas de los extractos cuando sea relevante.

Extractos de papers:
{contexto}

Tema a explicar de forma divulgativa: {tema}

IMPORTANTE: redacta toda la explicåación en {idioma}.

Genera la explicación divulgativa basada en los extractos."""
)