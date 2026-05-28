import streamlit as st
from src.generators.content_generator import generar_contenido

st.title("Generador de Contenido con IA")
st.write("Crea contenido adaptado a cada plataforma y audiencia.")

tema = st.text_input("Tema", placeholder="Ej: los beneficios del café")
plataforma = st.selectbox(
    "Plataforma",
    ["Twitter/X", "LinkedIn", "Instagram", "Blog"]
)
audiencia = st.text_input("Audiencia", placeholder="Ej: jóvenes profesionales")
tono = st.text_input("Tono", placeholder="Ej: cercano y motivador")

if st.button("Generar contenido"):
    if tema and audiencia and tono:
        with st.spinner("Generando..."):
            resultado = generar_contenido(tema, plataforma, audiencia, tono)
        st.subheader("Resultado:")
        st.write(resultado)
    else:
        st.warning("Por favor, rellena todos los campos.")