# src/tools/guardarrailes.py

# =====================================================================
# GUARDARRAÍLES — evaluación de calidad con LLM-as-Judge
#
# Implementa el patrón LLM-as-Judge:
# Un LLM evalúa la respuesta de otro LLM antes de mostrarla
# al usuario. Esto reduce alucinaciones y mejora la calidad.
#
# Evalúa tres dimensiones:
#   1. Relevancia  — ¿responde lo que preguntó el usuario?
#   2. Calidad     — ¿está bien estructurada y es útil?
#   3. Idioma      — ¿está en el idioma correcto?
#
# Cada dimensión se puntúa de 0 a 10.
# Si la puntuación media es < 6 → se avisa al usuario.
# =====================================================================

import logging
import json
import requests
import os
from langsmith import traceable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("guardarrailes")

# Umbral mínimo de calidad — si la media es menor, avisamos
UMBRAL_CALIDAD = 6.0

# Y decora la función así para LangSmith la tracee y podamos ver las evaluaciones en detalle en el dashboard
@traceable(name="Guardarraíl — LLM Judge")
def evaluar_respuesta(
    pregunta: str,
    respuesta: str,
    idioma_esperado: str,
    groq_key: str
) -> dict:
    """
    Usa el LLM de Groq como juez (LLM-as-Judge) para evaluar
    la calidad de una respuesta antes de mostrarla al usuario.

    Devuelve un diccionario con:
    - puntuacion_relevancia  (0-10)
    - puntuacion_calidad     (0-10)
    - puntuacion_idioma      (0-10)
    - puntuacion_media       (0-10)
    - aprobado               (True/False)
    - razon                  (explicación si no aprueba)
    - detalles               (feedback completo del juez)
    """

    logger.info("🔍 Evaluando respuesta con LLM-as-Judge...")

    prompt_juez = f"""
    Eres un evaluador experto de calidad de respuestas de IA.
    Tu trabajo es evaluar si una respuesta es adecuada y de calidad.

    PREGUNTA DEL USUARIO:
    {pregunta}

    RESPUESTA GENERADA:
    {respuesta[:2000]}

    IDIOMA ESPERADO: {idioma_esperado}

    Evalúa la respuesta en estas tres dimensiones y devuelve
    ÚNICAMENTE un JSON válido con este formato exacto:

    {{
        "relevancia": {{
            "puntuacion": 8,
            "comentario": "La respuesta aborda directamente la pregunta"
        }},
        "calidad": {{
            "puntuacion": 7,
            "comentario": "Bien estructurada pero podría tener más detalle"
        }},
        "idioma": {{
            "puntuacion": 10,
            "comentario": "Respuesta completamente en castellano"
        }},
        "veredicto": "APROBADO",
        "razon": "La respuesta cumple los estándares de calidad"
    }}

    CRITERIOS DE PUNTUACIÓN:
    - Relevancia (0-10): ¿Responde exactamente lo que preguntó el usuario?
      0-3: No responde la pregunta
      4-6: Responde parcialmente
      7-10: Responde completamente y con precisión

    - Calidad (0-10): ¿Está bien estructurada, es útil y tiene suficiente contenido?
      0-3: Respuesta pobre, confusa o demasiado corta
      4-6: Aceptable pero mejorable
      7-10: Clara, bien estructurada y útil

    - Idioma (0-10): ¿Está en {idioma_esperado}?
      0: Idioma completamente incorrecto
      5: Mezcla de idiomas
      10: Completamente en {idioma_esperado}

    - veredicto: "APROBADO" si la media >= 6, "RECHAZADO" si la media < 6

    Responde SOLO con el JSON, sin texto adicional.
    """

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt_juez}],
                "max_tokens": 500,
                "temperature": 0  # temperatura 0 para evaluaciones consistentes
            },
            timeout=15
        )

        if resp.status_code == 200:
            contenido = resp.json()["choices"][0]["message"]["content"].strip()

            # Limpiamos el JSON por si el LLM añade texto extra
            inicio = contenido.find("{")
            fin    = contenido.rfind("}") + 1
            if inicio != -1 and fin > 0:
                json_limpio  = contenido[inicio:fin]
                evaluacion   = json.loads(json_limpio)

                # Calculamos la puntuación media
                p_relevancia = evaluacion["relevancia"]["puntuacion"]
                p_calidad    = evaluacion["calidad"]["puntuacion"]
                p_idioma     = evaluacion["idioma"]["puntuacion"]
                media        = (p_relevancia + p_calidad + p_idioma) / 3

                aprobado = media >= UMBRAL_CALIDAD

                logger.info(f"  Relevancia: {p_relevancia}/10")
                logger.info(f"  Calidad:    {p_calidad}/10")
                logger.info(f"  Idioma:     {p_idioma}/10")
                logger.info(f"  Media:      {media:.1f}/10")
                logger.info(f"  Veredicto:  {'✅ APROBADO' if aprobado else '❌ RECHAZADO'}")

                return {
                    "puntuacion_relevancia": p_relevancia,
                    "puntuacion_calidad":    p_calidad,
                    "puntuacion_idioma":     p_idioma,
                    "puntuacion_media":      round(media, 1),
                    "aprobado":              aprobado,
                    "razon":                 evaluacion.get("razon", ""),
                    "detalles":              evaluacion
                }

    except Exception as e:
        logger.error(f"Error en el evaluador: {e}")

    # Si algo falla, aprobamos por defecto para no bloquear la app
    logger.warning("⚠️ Evaluador falló — aprobando por defecto")
    return {
        "puntuacion_relevancia": 7,
        "puntuacion_calidad":    7,
        "puntuacion_idioma":     7,
        "puntuacion_media":      7.0,
        "aprobado":              True,
        "razon":                 "Evaluación no disponible",
        "detalles":              {}
    }


def mostrar_resultado_evaluacion(evaluacion: dict) -> str:
    """
    Genera el texto que se mostrará al usuario con el resultado
    de la evaluación. Solo se muestra si hay algún problema.
    """
    if evaluacion["aprobado"]:
        return ""  # Si aprueba, no mostramos nada — experiencia limpia

    # Si no aprueba, mostramos un aviso claro
    return f"""
⚠️ **Aviso de calidad**
Esta respuesta no superó nuestros estándares mínimos de calidad.

| Dimensión | Puntuación |
|-----------|-----------|
| Relevancia | {evaluacion['puntuacion_relevancia']}/10 |
| Calidad | {evaluacion['puntuacion_calidad']}/10 |
| Idioma | {evaluacion['puntuacion_idioma']}/10 |
| **Media** | **{evaluacion['puntuacion_media']}/10** |

**Motivo:** {evaluacion['razon']}

*Puedes reformular tu pregunta para obtener una respuesta mejor.*
"""