import streamlit as st
from src.generators.content_generator import generar_contenido
from src.config import MODELOS_DISPONIBLES

st.title("Generador de Contenido con IA")
st.write("Crea contenido adaptado a cada plataforma y audiencia.")

tema = st.text_input("Tema", placeholder="Ej: los beneficios del café")
plataforma = st.selectbox(
    "Plataforma",
    ["Twitter/X", "LinkedIn", "Instagram", "Blog"]
)
audiencia = st.text_input("Audiencia", placeholder="Ej: jóvenes profesionales")
tono = st.text_input("Tono", placeholder="Ej: cercano y motivador")

info_empresa = st.text_area(
    "Información de la empresa (opcional)",
    placeholder="Ej: Somos una cafetería artesanal de Madrid, tono cercano y sostenible..."
)

modelo = st.selectbox(
    "Modelo de IA",
    list(MODELOS_DISPONIBLES.keys())
)

info = info_empresa if info_empresa else "No se ha proporcionado información específica de empresa; genera contenido genérico."

if st.button("Generar contenido"):
    if tema and audiencia and tono:
        with st.spinner("Generando..."):
            resultado = generar_contenido(tema, plataforma, audiencia, tono, modelo, info)
        st.subheader("Resultado:")
        st.write(resultado)
    else:
        st.warning("Por favor, rellena todos los campos.")