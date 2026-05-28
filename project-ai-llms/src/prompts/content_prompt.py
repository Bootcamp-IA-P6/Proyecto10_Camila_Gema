from langchain.prompts import PromptTemplate

content_template = PromptTemplate(
    input_variables=["tema", "plataforma", "audiencia", "tono", "info_empresa", "idioma"],
    template="""Eres un experto en redacción de contenido digital.

Escribe contenido sobre: {tema}
Plataforma de destino: {plataforma}
Audiencia objetivo: {audiencia}
Tono deseado: {tono}
Idioma: {idioma}
Información sobre la empresa o marca:
{info_empresa}

Adapta la longitud, el formato y el vocabulario a la plataforma y la audiencia indicadas.
Genera únicamente el contenido final, listo para publicar."""
)