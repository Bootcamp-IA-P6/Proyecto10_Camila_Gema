import streamlit as st
from src.config import MODELOS_DISPONIBLES
from src.generators.content_generator import generar_contenido
from src.generators.rag_generator import generar_divulgacion
from src.generators.news_generator import generar_newsletter
from src.image_search import buscar_imagenes
from src.router.agent_router import enrutar_peticion

IDIOMAS = {
    "Español": "español",
    "Inglés": "inglés",
    "Francés": "francés",
    "Italiano": "italiano",
}

st.title("Generador de Contenido con IA")
st.write("Crea contenido adaptado a cada plataforma y audiencia.")

tab_auto, tab_manual = st.tabs(["Asistente inteligente", "Modo manual"])

# ============================================================
# PESTAÑA 1: ASISTENTE INTELIGENTE (con enrutador)
# ============================================================
with tab_auto:
    st.write("Escribe lo que quieres conseguir y el sistema elegirá el agente más adecuado.")

    peticion = st.text_area(
        "¿Qué necesitas?",
        placeholder="Ej: explícame cómo funcionan los transformers en IA, o redacta un post de LinkedIn sobre productividad...",
        key="peticion_auto",
    )

    if st.button("Analizar y enrutar", key="btn_enrutar"):
        if peticion.strip():
            with st.spinner("El enrutador está decidiendo..."):
                decision = enrutar_peticion(peticion)
            st.session_state["agente_elegido"] = decision["agente"]
            st.session_state["justificacion_router"] = decision["justificacion"]
            st.session_state["peticion_original"] = peticion
        else:
            st.warning("Por favor, escribe una petición.")

    # Si ya se enrutó, mostrar el agente elegido y el formulario adaptado
    if "agente_elegido" in st.session_state:
        agente = st.session_state["agente_elegido"]
        st.info(f"**Agente elegido:** `{agente}`\n\n{st.session_state['justificacion_router']}")

        st.divider()
        st.subheader("Completa los detalles para este agente:")

        if agente == "contenido_general":
            plataforma = st.selectbox("Plataforma", ["Twitter/X", "LinkedIn", "Instagram", "Blog"], key="auto_plat")
            audiencia = st.text_input("Audiencia", placeholder="Ej: jóvenes profesionales", key="auto_aud")
            tono = st.text_input("Tono", placeholder="Ej: cercano y motivador", key="auto_tono")
            info_empresa = st.text_area("Información de la empresa (opcional)", key="auto_emp")
            idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="auto_idi_gen")
            modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="auto_mod_gen")

            if st.button("Generar", key="btn_auto_gen"):
                if audiencia and tono:
                    info = info_empresa if info_empresa else "No se ha proporcionado información específica de empresa; genera contenido genérico."
                    with st.spinner("Generando..."):
                        resultado = generar_contenido(
                            st.session_state["peticion_original"],
                            plataforma, audiencia, tono, modelo_e, info, IDIOMAS[idioma_e],
                        )
                    st.subheader("Resultado:")
                    st.write(resultado)
                    st.subheader("Imágenes sugeridas:")
                    imgs = buscar_imagenes(st.session_state["peticion_original"], cantidad=3)
                    if imgs:
                        cols = st.columns(len(imgs))
                        for col, img in zip(cols, imgs):
                            with col:
                                st.image(img["url"], use_container_width=True)
                                st.caption(f"Foto de {img['autor']} (Pexels)")
                else:
                    st.warning("Rellena audiencia y tono.")

        elif agente == "divulgacion_rag":
            idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="auto_idi_rag")
            modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="auto_mod_rag")

            if st.button("Generar", key="btn_auto_rag"):
                with st.spinner("Buscando papers y generando..."):
                    explicacion, fuentes, evaluacion = generar_divulgacion(
                        st.session_state["peticion_original"], modelo_e, IDIOMAS[idioma_e],
                    )
                st.subheader("Explicación divulgativa:")
                st.write(explicacion)

                p = evaluacion["puntuacion"]
                if p >= 4:
                    st.success(f"✓ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")
                elif p >= 2:
                    st.warning(f"⚠ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")
                else:
                    st.error(f"✗ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")

                st.subheader("Fuentes:")
                unicas = {f["url"]: f for f in fuentes}.values()
                for f in unicas:
                    st.markdown(f"- [{f['titulo']}]({f['url']})")

        elif agente == "newsletter_financiera":
            idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="auto_idi_news")
            modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="auto_mod_news")
            cantidad = st.slider("Número de noticias", 5, 15, 10, key="auto_cant")

            if st.button("Generar", key="btn_auto_news"):
                with st.spinner("Buscando noticias y redactando..."):
                    newsletter, noticias = generar_newsletter(modelo_e, IDIOMAS[idioma_e], cantidad_noticias=cantidad)
                st.subheader("Newsletter del día:")
                st.write(newsletter)
                st.subheader("Fuentes:")
                for n in noticias:
                    st.markdown(f"- **{n['fuente']}**: [{n['titular']}]({n['url']})")

# ============================================================
# PESTAÑA 2: MODO MANUAL (pestañas viejas anidadas)
# ============================================================
with tab_manual:
    st.write("Si prefieres elegir el agente tú misma, usa estas pestañas.")
    sub_general, sub_rag, sub_news = st.tabs([
        "Contenido general",
        "Divulgación científica (RAG)",
        "Newsletter financiera",
    ])

    with sub_general:
        tema = st.text_input("Tema", placeholder="Ej: los beneficios del café", key="m_tema")
        plataforma = st.selectbox("Plataforma", ["Twitter/X", "LinkedIn", "Instagram", "Blog"], key="m_plat")
        audiencia = st.text_input("Audiencia", placeholder="Ej: jóvenes profesionales", key="m_aud")
        tono = st.text_input("Tono", placeholder="Ej: cercano y motivador", key="m_tono")
        info_empresa = st.text_area("Información de la empresa (opcional)", key="m_emp")
        idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="m_idi_gen")
        modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="m_mod_gen")

        if st.button("Generar contenido", key="m_btn_gen"):
            if tema and audiencia and tono:
                info = info_empresa if info_empresa else "No se ha proporcionado información específica de empresa; genera contenido genérico."
                with st.spinner("Generando..."):
                    resultado = generar_contenido(tema, plataforma, audiencia, tono, modelo_e, info, IDIOMAS[idioma_e])
                st.subheader("Resultado:")
                st.write(resultado)
                st.subheader("Imágenes sugeridas:")
                imgs = buscar_imagenes(tema, cantidad=3)
                if imgs:
                    cols = st.columns(len(imgs))
                    for col, img in zip(cols, imgs):
                        with col:
                            st.image(img["url"], use_container_width=True)
                            st.caption(f"Foto de {img['autor']} (Pexels)")
            else:
                st.warning("Rellena todos los campos.")

    with sub_rag:
        tema_rag = st.text_input("Tema científico", key="m_tema_rag")
        idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="m_idi_rag")
        modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="m_mod_rag")

        if st.button("Generar divulgación", key="m_btn_rag"):
            if tema_rag:
                with st.spinner("Buscando papers y generando..."):
                    explicacion, fuentes, evaluacion = generar_divulgacion(tema_rag, modelo_e, IDIOMAS[idioma_e])
                st.subheader("Explicación divulgativa:")
                st.write(explicacion)

                p = evaluacion["puntuacion"]
                if p >= 4:
                    st.success(f"✓ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")
                elif p >= 2:
                    st.warning(f"⚠ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")
                else:
                    st.error(f"✗ Fiabilidad: {p}/5 — {evaluacion['justificacion']}")

                st.subheader("Fuentes:")
                unicas = {f["url"]: f for f in fuentes}.values()
                for f in unicas:
                    st.markdown(f"- [{f['titulo']}]({f['url']})")

    with sub_news:
        idioma_e = st.selectbox("Idioma", list(IDIOMAS.keys()), key="m_idi_news")
        modelo_e = st.selectbox("Modelo de IA", list(MODELOS_DISPONIBLES.keys()), key="m_mod_news")
        cantidad = st.slider("Número de noticias", 5, 15, 10, key="m_cant")

        if st.button("Generar newsletter", key="m_btn_news"):
            with st.spinner("Buscando noticias y redactando..."):
                newsletter, noticias = generar_newsletter(modelo_e, IDIOMAS[idioma_e], cantidad_noticias=cantidad)
            st.subheader("Newsletter del día:")
            st.write(newsletter)
            st.subheader("Fuentes:")
            for n in noticias:
                st.markdown(f"- **{n['fuente']}**: [{n['titular']}]({n['url']})")