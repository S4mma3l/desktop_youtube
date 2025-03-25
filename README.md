# YouTube Transcription and Analysis API

API en Flask para transcribir y analizar vídeos de YouTube utilizando `yt-dlp`, `speechRecognition` y Gemini (Google AI).

## Funcionalidades

*   Transcripción de vídeos de YouTube.
*   Análisis de texto transcrito con Gemini.
*   Generación de ejemplos de código.

## Estructura

*   `app.py`: Punto de entrada Flask.
*   `config.py`: Configuración (claves API, rutas).
*   `file_utils.py`: Utilidades de archivos.
*   `video_utils.py`: Descarga/conversión de vídeos.
*   `audio_utils.py`: Segmentación/transcripción de audio.
*   `gemini_utils.py`: Interacción con Gemini.

## Uso

1.  Clonar el repositorio.
2.  Crear un entorno virtual: `python3 -m venv venv && source venv/bin/activate`
3.  Instalar dependencias: `pip install -r requirements.txt`
4.  Crear `.env` con `GEMINI_API_KEY`.
5.  Ejecutar: `python app.py`

Solicitud POST a `/transcribir` con la URL del video.

## Despliegue (Railway)

*   Conectar repo de GitHub a Railway.
*   Configurar variables de entorno (ej: `GEMINI_API_KEY`).
*   Opcional: Usar un Dockerfile (ejemplo a continuación).

## Dockerfile (Ejemplo)

```dockerfile
FROM python:3.11-slim-buster
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg git
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]