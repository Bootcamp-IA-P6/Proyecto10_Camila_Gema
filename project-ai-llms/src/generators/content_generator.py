from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from src.prompts.content_prompt import content_template

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")

# La cadena: plantilla -> modelo -> texto limpio
chain = content_template | llm | StrOutputParser()

def generar_contenido(tema, plataforma, audiencia, tono):
    return chain.invoke({
        "tema": tema,
        "plataforma": plataforma,
        "audiencia": audiencia,
        "tono": tono,
    })