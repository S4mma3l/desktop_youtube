import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", True)  # Habilita el modo debug por defecto
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    FFMPEG_PATH = os.getenv("FFMPEG_PATH")
    TRANSCRIPTION_LANGUAGE = os.getenv("TRANSCRIPTION_LANGUAGE", "es-ES") # Default spanish transcription
    AUDIO_SEGMENT_DURATION = int(os.getenv("AUDIO_SEGMENT_DURATION", 30))  # Duración del segmento en segundos
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "temp") #Carpeta temporal para guardar los archivos

    def __init__(self):
        if not self.GEMINI_API_KEY:
            raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")
        if not self.FFMPEG_PATH:
            raise ValueError("La variable de entorno FFMPEG_PATH no está configurada.")

    @staticmethod
    def ensure_upload_folder_exists():
        upload_folder = Config.UPLOAD_FOLDER
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)