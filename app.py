from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from config import Config
from video_utils import descargar_video, convertir_video_a_audio, es_url_youtube
from audio_utils import segmentar_audio, transcribir_segmentos
from gemini_utils import analizar_y_mejorar_texto, generar_ejemplos_codigo
from file_utils import generar_documento_texto, eliminar_archivo
import os
import traceback

app = Flask(__name__, static_folder='static')

# Configurar CORS
origins = ["https://desktopyoutube-production.up.railway.app", "http://localhost:5000"]  # Ajusta esto para tus orígenes
CORS(app, resources={r"/*": {"origins": origins}}, supports_credentials=True)

config = Config()
config.ensure_upload_folder_exists()
UPLOAD_FOLDER = config.UPLOAD_FOLDER

@app.route('/')
@cross_origin(origins=origins, supports_credentials=True)
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
@cross_origin(origins=origins, supports_credentials=True)
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/transcribir', methods=['POST', 'OPTIONS'])  # Permitir OPTIONS
@cross_origin(origins=origins, supports_credentials=True)
def transcribir():
    ruta_audio = None
    ruta_video = None
    ruta_archivo_texto = None
    ruta_archivo_md = None
    ruta_ejemplos_md = None
    transcripcion = ""
    analisis = ""
    ejemplos = ""
    try:
        url_video = request.json['url']
        if not es_url_youtube(url_video):
            return jsonify({'error': 'URL de YouTube inválida.'}), 400

        ruta_video = descargar_video(url_video, config.FFMPEG_PATH, UPLOAD_FOLDER)
        if not ruta_video or not os.path.exists(ruta_video):
            return jsonify({'error': 'Error al descargar o encontrar el video.'}), 400

        video_titulo_sin_extension = os.path.splitext(os.path.basename(ruta_video))[0]
        ruta_archivo_texto = os.path.join(UPLOAD_FOLDER, f"{video_titulo_sin_extension}_transcripcion.txt")
        ruta_archivo_md = os.path.join(UPLOAD_FOLDER, f"{video_titulo_sin_extension}_analisis.md")
        ruta_ejemplos_md = os.path.join(UPLOAD_FOLDER, f"{video_titulo_sin_extension}_ejemplos.md")
        ruta_audio = convertir_video_a_audio(ruta_video, UPLOAD_FOLDER)
        if not ruta_audio:
            return jsonify({'error': 'Error al convertir el video a audio.'}), 400

        segmentos = segmentar_audio(ruta_audio, config.AUDIO_SEGMENT_DURATION * 1000)
        transcripciones = transcribir_segmentos(segmentos, config.TRANSCRIPTION_LANGUAGE, UPLOAD_FOLDER)
        texto_completo = " ".join(transcripciones)
        texto_mejorado = analizar_y_mejorar_texto(texto_completo, config.GEMINI_API_KEY)
        ejemplos_codigo = generar_ejemplos_codigo(texto_completo, config.GEMINI_API_KEY)

        # *** Depuración importante: Imprime el valor de ejemplos_codigo
        print(f"Valor de ejemplos_codigo: {ejemplos_codigo}")

        # Asegúrate de que ejemplos_codigo no sea None antes de guardarlo
        if ejemplos_codigo is None:
            ejemplos_codigo = "No se encontraron ejemplos de código relevantes."

        # Imprime la ruta del archivo antes de intentar crearlo
        print(f"Intentando crear archivo de ejemplos en: {ruta_ejemplos_md}")

        # Imprime el texto que se intentará guardar
        print(f"Texto a guardar en ejemplos.md: {ejemplos_codigo}")

        #** Añadido: Comprueba si la ruta del archivo existe antes de intentar crearlo
        print(f"¿Existe la ruta del archivo antes de crearlo?: {os.path.exists(ruta_ejemplos_md)}")

        # Guarda el contenido en un archivo, incluso si es un mensaje indicando que no hay ejemplos
        generar_documento_texto(ejemplos_codigo, ruta_ejemplos_md)

        #** Añadido: Comprueba si el archivo se creó correctamente
        print(f"¿Se creó el archivo correctamente?: {os.path.exists(ruta_ejemplos_md)}")

        # **Añadido: Imprime el valor de texto_mejorado ANTES de llamar a generar_documento_texto
        print(f"Valor de texto_mejorado antes de guardar analisis.md: {texto_mejorado}")

        # Imprime la ruta y el texto que se utilizarán para generar analisis.md
        print(f"Intentando crear archivo analisis.md en: {ruta_archivo_md}")
        print(f"Texto a guardar en analisis.md: {texto_mejorado}")

        # Guarda el contenido en un archivo, incluso si es un mensaje indicando que no hay ejemplos
        generar_documento_texto(texto_completo, ruta_archivo_texto)

       # Imprime la ruta y el texto que se utilizarán para generar analisis.md
        print(f"Intentando crear archivo analisis.md en: {ruta_archivo_md}")
        print(f"Texto a guardar en analisis.md: {texto_mejorado}")

        generar_documento_texto(texto_mejorado, ruta_archivo_md)

        # Leer el contenido de los archivos
        try:
             print(f"Nombre del archivo (sin extensión): {video_titulo_sin_extension}")
             print(f"Ruta completa al archivo analisis.md: {ruta_archivo_md}")
             if os.path.exists(ruta_archivo_md):
                print(f"El archivo analisis.md existe.")
                with open(ruta_archivo_texto, "r", encoding="utf-8") as archivo:
                    transcripcion = archivo.read()
                with open(ruta_archivo_md, "r", encoding="utf-8") as archivo:
                    analisis = archivo.read()
                # Verificando si analisis está vacío
                if not analisis:
                    print("¡OJO! El archivo analisis.md está vacío.")

                print(f"Contenido de la variable analisis: {analisis}")
                with open(ruta_ejemplos_md, "r", encoding="utf-8") as archivo:
                    ejemplos = archivo.read()
             else:
                print(f"¡El archivo analisis.md NO existe!")
                analisis = "No se pudo encontrar el archivo de análisis."

        except Exception as e:
            print(f"Error al leer los archivos: {e}")
            # Puedes decidir si quieres retornar un error al frontend o continuar con cadenas vacías
            # En este caso, se dejarán las cadenas vacías si falla la lectura

        # Imprimir para depurar
        print(f"Transcripción: {transcripcion}")
        print(f"Análisis: {analisis}")
        print(f"Ejemplos: {ejemplos}")

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # Eliminar archivos solo si se pudieron leer los archivos
        # if ruta_archivo_texto and os.path.exists(ruta_archivo_texto) and transcripcion != "":
        #    eliminar_archivo(ruta_archivo_texto)
        # if ruta_archivo_md and os.path.exists(ruta_archivo_md) and analisis != "":
        #    eliminar_archivo(ruta_archivo_md)
        # if ruta_ejemplos_md and os.path.exists(ruta_ejemplos_md) and ejemplos != "":
        #    eliminar_archivo(ruta_archivo_md)

        if ruta_audio:
            eliminar_archivo(ruta_audio)
        if ruta_video:
            eliminar_archivo(ruta_video)

    return jsonify({'transcripcion': transcripcion, 'analisis': analisis, 'ejemplos': ejemplos})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # app.run(host= 'https://desktopyoutube-production.up.railway.app', port=port)
    app.run(debug=True, host='0.0.0.0', port=port)