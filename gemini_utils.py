import google.generativeai as genai
import logging

def analizar_y_mejorar_texto(texto, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""Actúa como un analista de contenido. Analiza el siguiente texto y mejóralo para que sea más claro, conciso y atractivo. Corrige la gramática, la ortografía y el estilo. Haz sugerencias para mejorar la estructura y la fluidez del texto: {texto}"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error al interactuar con Gemini: {e}")
        return "Error al analizar el texto con Gemini."

def generar_ejemplos_codigo(texto, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""Actúa como un experto en ciberseguridad. Basándote en el siguiente texto, genera ejemplos de código relevantes. Si el texto no contiene información relacionada con código, responde diciendo "No se encontraron ejemplos de código relevantes.": {texto}"""
    try:
        response = model.generate_content(prompt)
        if "No se encontraron ejemplos de código relevantes." in response.text:
            return "No se encontraron ejemplos de código relevantes."
        return response.text
    except Exception as e:
        logging.error(f"Error al interactuar con Gemini: {e}")
        return "No se encontraron ejemplos de código relevantes."