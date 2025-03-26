# START OF FILE app.py

from flask import Flask, request, jsonify, send_from_directory, make_response # Importar make_response
from flask_cors import CORS, cross_origin
from config import Config
from video_utils import descargar_video, convertir_video_a_audio, es_url_youtube
from audio_utils import segmentar_audio, transcribir_segmentos
from gemini_utils import analizar_y_mejorar_texto, generar_ejemplos_codigo
from file_utils import generar_documento_texto, eliminar_archivo
import os
import traceback
import logging
import threading # Importar threading
import uuid      # Importar uuid para generar IDs de trabajo
from time import sleep # Opcional: para simular trabajo o prevenir bucles muy rápidos

# Configura el logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static')

# Configurar CORS
origins = ["https://youtubetranscription-neon.vercel.app"] # , "http://localhost:5000" # Ajusta esto para tus orígenes
CORS(app, resources={r"/*": {"origins": origins}}, supports_credentials=True)

config = Config()
config.ensure_upload_folder_exists()
UPLOAD_FOLDER = config.UPLOAD_FOLDER

# --- Almacenamiento de Estado de Trabajos (Simple en Memoria) ---
# ADVERTENCIA: Este diccionario simple NO funcionará correctamente si ejecutas
# Flask con múltiples workers/procesos (ej. gunicorn -w 4).
# Para multi-proceso, usa un almacenamiento compartido como Redis, Memcached, o una base de datos.
jobs = {}
# --------------------------------------------------------------

# --- Función para la Tarea en Segundo Plano ---
def run_transcription_task(job_id, url_video, config, upload_folder):
    global jobs
    ruta_audio = None
    ruta_video = None
    ruta_archivo_texto = None
    ruta_archivo_md = None
    ruta_ejemplos_md = None

    try:
        jobs[job_id]['status'] = 'processing' # Estado: procesando
        logging.info(f"Trabajo {job_id}: Iniciando procesamiento para URL: {url_video}")

        # --- La lógica central de tu '/transcribir' original ---
        if not es_url_youtube(url_video):
            raise ValueError('URL de YouTube inválida.')

        ruta_video = descargar_video(url_video, upload_folder)
        if not ruta_video or not os.path.exists(ruta_video):
            raise RuntimeError('Error al descargar o encontrar el video.')
        logging.info(f"Trabajo {job_id}: Video descargado en {ruta_video}")

        video_titulo_sin_extension = os.path.splitext(os.path.basename(ruta_video))[0]
        ruta_archivo_texto = os.path.join(upload_folder, f"{video_titulo_sin_extension}_transcripcion.txt")
        ruta_archivo_md = os.path.join(upload_folder, f"{video_titulo_sin_extension}_analisis.md")
        ruta_ejemplos_md = os.path.join(upload_folder, f"{video_titulo_sin_extension}_ejemplos.md")
        ruta_audio = convertir_video_a_audio(ruta_video, upload_folder)
        if not ruta_audio:
            raise RuntimeError('Error al convertir el video a audio.')
        logging.info(f"Trabajo {job_id}: Video convertido a audio {ruta_audio}")

        segmentos = segmentar_audio(ruta_audio, config.AUDIO_SEGMENT_DURATION * 1000)
        logging.info(f"Trabajo {job_id}: Audio segmentado.")
        transcripciones = transcribir_segmentos(segmentos, config.TRANSCRIPTION_LANGUAGE, upload_folder)
        texto_completo = " ".join(transcripciones)
        logging.info(f"Trabajo {job_id}: Transcripción completa.")

        texto_mejorado = analizar_y_mejorar_texto(texto_completo, config.GEMINI_API_KEY)
        logging.info(f"Trabajo {job_id}: Análisis de texto completo.")
        ejemplos_codigo = generar_ejemplos_codigo(texto_completo, config.GEMINI_API_KEY)
        logging.info(f"Trabajo {job_id}: Ejemplos de código generados.")

        if ejemplos_codigo is None:
            ejemplos_codigo = "No se encontraron ejemplos de código relevantes."
        if texto_mejorado is None:
             texto_mejorado = "Error al generar el análisis." # Manejar posible None de Gemini

        # --- Guardar resultados en archivos (Opcional, podría retornarse directamente) ---
        # Sigue guardando en archivos como antes, o adapta para guardar resultados directamente en el dict 'jobs'
        generar_documento_texto(texto_completo, ruta_archivo_texto)
        generar_documento_texto(texto_mejorado, ruta_archivo_md)
        generar_documento_texto(ejemplos_codigo, ruta_ejemplos_md)
        logging.info(f"Trabajo {job_id}: Resultados guardados en archivos.")

        # --- Leer resultados de los archivos ---
        # (O simplemente usar las variables texto_completo, texto_mejorado, ejemplos_codigo)
        transcripcion_final = ""
        analisis_final = ""
        ejemplos_final = ""
        try:
            if os.path.exists(ruta_archivo_texto):
                with open(ruta_archivo_texto, "r", encoding="utf-8") as archivo:
                    transcripcion_final = archivo.read()
            if os.path.exists(ruta_archivo_md):
                with open(ruta_archivo_md, "r", encoding="utf-8") as archivo:
                    analisis_final = archivo.read()
            if os.path.exists(ruta_ejemplos_md):
                with open(ruta_ejemplos_md, "r", encoding="utf-8") as archivo:
                    ejemplos_final = archivo.read()
        except Exception as read_err:
             logging.error(f"Trabajo {job_id}: Error leyendo archivos de resultado: {read_err}")
             # Decide si esto es un error fatal para el trabajo

        # --- Almacenar resultados finales y actualizar estado ---
        jobs[job_id]['status'] = 'complete' # Estado: completado
        jobs[job_id]['result'] = {
            'transcripcion': transcripcion_final,
            'analisis': analisis_final,
            'ejemplos': ejemplos_final
        }
        logging.info(f"Trabajo {job_id}: Procesamiento completado.")

    except Exception as e:
        logging.error(f"Trabajo {job_id}: Error durante el procesamiento: {e}")
        traceback.print_exc()
        jobs[job_id]['status'] = 'error' # Estado: error
        jobs[job_id]['error'] = str(e)

    finally:
        # --- Limpieza ---
        # Importante: La limpieza ocurre *después* de que el trabajo termine o falle
        # Mantén un registro de los archivos a borrar incluso si los errores ocurrieron pronto
        files_to_delete = [ruta_audio, ruta_video, ruta_archivo_texto, ruta_archivo_md, ruta_ejemplos_md]
        for file_path in files_to_delete:
            if file_path and os.path.exists(file_path):
                eliminar_archivo(file_path)
                logging.info(f"Trabajo {job_id}: Limpiado {file_path}")
# ------------------------------------------

@app.route('/')
@cross_origin(origins=origins, supports_credentials=True)
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
@cross_origin(origins=origins, supports_credentials=True)
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# --- Endpoint '/transcribir' Modificado ---
@app.route('/transcribir', methods=['POST', 'OPTIONS'])
@cross_origin(origins=origins, supports_credentials=True)
def transcribir_start():
    global jobs
    if request.method == 'OPTIONS':
        # Manejar solicitud CORS preflight
        return _build_cors_preflight_response()

    try:
        url_video = request.json.get('url')
        if not url_video or not es_url_youtube(url_video):
            return jsonify({'error': 'URL de YouTube inválida o faltante.'}), 400

        # Generar un ID de trabajo único
        job_id = str(uuid.uuid4())

        # Guardar estado inicial del trabajo
        jobs[job_id] = {'status': 'pending'} # Estado: pendiente

        # Iniciar la tarea en segundo plano
        thread = threading.Thread(target=run_transcription_task, args=(job_id, url_video, config, UPLOAD_FOLDER))
        thread.daemon = True # Permite que la app salga aunque los hilos sigan corriendo (opcional)
        thread.start()

        logging.info(f"Trabajo {job_id}: Iniciado para URL: {url_video}")
        # Devolver el job ID y estado 202 Accepted inmediatamente
        return jsonify({'job_id': job_id}), 202

    except Exception as e:
        logging.error(f"Error iniciando trabajo: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Error al iniciar la tarea: {str(e)}'}), 500
# ---------------------------------------

# --- Nuevo Endpoint '/status' ---
@app.route('/status/<job_id>', methods=['GET'])
@cross_origin(origins=origins, supports_credentials=True)
def get_status(job_id):
    global jobs
    job = jobs.get(job_id)

    if not job:
        return jsonify({'error': 'Job ID no encontrado.'}), 404

    if job['status'] == 'complete':
        response_data = {
            'status': 'complete',
            'data': job.get('result', {}) # Devuelve data o un dict vacío si no hay resultado
        }
        # Opcionalmente, eliminar el trabajo de la memoria después de recuperarlo
        # del jobs[job_id]
        return jsonify(response_data)
    elif job['status'] == 'error':
        response_data = {
            'status': 'error',
            'message': job.get('error', 'Error desconocido durante el procesamiento.')
        }
        # Opcionalmente, eliminar el trabajo de la memoria después de recuperarlo
        # del jobs[job_id]
        return jsonify(response_data)
    else:
        # El estado es 'pending' o 'processing'
        return jsonify({'status': job['status']})
# -----------------------------

# --- Ayudante para Respuesta CORS Preflight ---
def _build_cors_preflight_response():
    response = make_response()
    # Ajusta los orígenes permitidos si es necesario
    response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization") # Añade otros headers si los usas
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS") # Métodos que soportas
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response
# ------------------------------------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Usa threaded=True para el servidor de desarrollo para manejar mejor las solicitudes concurrentes
    # Para producción, usa un servidor WSGI apropiado como gunicorn o uwsgi
    app.run(host='0.0.0.0', port=port, threaded=True) # Añadido threaded=True
    # app.run(debug=True, host='0.0.0.0', port=port, threaded=True)