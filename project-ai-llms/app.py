import streamlit as st
from src.generators.content_generator import generar_contenido
from src.config import MODELOS_DISPONIBLES
from src.image_search import buscar_imagenes
from src.generators.rag_generator import generar_divulgacion
from src.generators.news_generator import generar_newsletter



IDIOMAS = {
    "Español": "español",
    "Inglés": "inglés",
    "Francés": "francés",
    "Italiano": "italiano",
}

st.title("Generador de Contenido con IA")
st.write("Crea contenido adaptado a cada plataforma y audiencia.")

tab_general, tab_rag, tab_news = st.tabs([
    "Contenido general",
    "Divulgación científica (RAG)",
    "Newsletter financiera",
])

with tab_general:
    tema = st.text_input("Tema", placeholder="Ej: los beneficios del café", key="tema_gen")
    plataforma = st.selectbox(
        "Plataforma",
        ["Twitter/X", "LinkedIn", "Instagram", "Blog"],
        key="plataforma_gen",
    )
    audiencia = st.text_input("Audiencia", placeholder="Ej: jóvenes profesionales", key="aud_gen")
    tono = st.text_input("Tono", placeholder="Ej: cercano y motivador", key="tono_gen")
    info_empresa = st.text_area(
        "Información de la empresa (opcional)",
        placeholder="Ej: Somos una cafetería artesanal de Madrid...",
        key="empresa_gen",
    )
    idioma_elegido = st.selectbox("Idioma", list(IDIOMAS.keys()), key="idioma_gen")
    idioma = IDIOMAS[idioma_elegido]
    modelo = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="modelo_gen")

    if st.button("Generar contenido", key="btn_gen"):
        if tema and audiencia and tono:
            info = info_empresa if info_empresa else "No se ha proporcionado información específica de empresa; genera contenido genérico."
            with st.spinner("Generando..."):
                resultado = generar_contenido(tema, plataforma, audiencia, tono, modelo, info, idioma)
            st.subheader("Resultado:")
            st.write(resultado)
            st.subheader("Imágenes sugeridas:")
            imagenes = buscar_imagenes(tema, cantidad=3)
            if imagenes:
                columnas = st.columns(len(imagenes))
                for columna, img in zip(columnas, imagenes):
                    with columna:
                        st.image(img["url"], use_container_width=True)
                        st.caption(f"Foto de {img['autor']} (Pexels)")
            else:
                st.info("No se encontraron imágenes para este tema.")
        else:
            st.warning("Por favor, rellena todos los campos.")

with tab_rag:
    st.write("Genera explicaciones divulgativas apoyadas en papers reales de arXiv.")
    tema_rag = st.text_input(
        "Tema científico",
        placeholder="Ej: ¿Tienen personalidad los modelos de lenguaje?",
        key="tema_rag",
    )
    idioma_rag_elegido = st.selectbox("Idioma", list(IDIOMAS.keys()), key="idioma_rag")
    idioma_rag = IDIOMAS[idioma_rag_elegido]
    modelo_rag = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="modelo_rag")

    if st.button("Generar divulgación", key="btn_rag"):
        if tema_rag:
            with st.spinner("Buscando papers y generando..."):
                explicacion, fuentes, evaluacion = generar_divulgacion(tema_rag, modelo_rag, idioma_rag)
            st.subheader("Explicación divulgativa:")
            st.write(explicacion)

            puntuacion = evaluacion["puntuacion"]
            if puntuacion >= 4:
                st.success(f"✓ Fiabilidad: {puntuacion}/5 — {evaluacion['justificacion']}")
            elif puntuacion >= 2:
                st.warning(f"⚠ Fiabilidad: {puntuacion}/5 — {evaluacion['justificacion']}")
            else:
                st.error(f"✗ Fiabilidad: {puntuacion}/5 — {evaluacion['justificacion']}")

            st.subheader("Fuentes:")
            fuentes_unicas = {f["url"]: f for f in fuentes}.values()
            for f in fuentes_unicas:
                st.markdown(f"- [{f['titulo']}]({f['url']})")
        else:
            st.warning("Por favor, escribe un tema científico.")

with tab_news:
    st.write("Genera una newsletter diaria de mercados financieros basada en noticias actuales.")
    idioma_news_elegido = st.selectbox("Idioma", list(IDIOMAS.keys()), key="idioma_news")
    idioma_news = IDIOMAS[idioma_news_elegido]
    modelo_news = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="modelo_news")
    cantidad = st.slider("Número de noticias a analizar", min_value=5, max_value=15, value=10, key="cantidad_news")

    if st.button("Generar newsletter", key="btn_news"):
        with st.spinner("Buscando noticias y redactando..."):
            newsletter, noticias = generar_newsletter(modelo_news, idioma_news, cantidad_noticias=cantidad)
        st.subheader("Newsletter del día:")
        st.write(newsletter)
        st.subheader("Fuentes:")
        for n in noticias:
            st.markdown(f"- **{n['fuente']}**: [{n['titular']}]({n['url']})")