import yt_dlp as youtube_dl
import os
import re
from moviepy.editor import *
from urllib.parse import urlparse, parse_qs

def limpiar_nombre_archivo(nombre):
    nombre_limpio = re.sub(r'[<>:"/\\|?*\u2600-\u27BF\uD800-\uDBFF\uDC00-\uDFFF｜？]', '', nombre)
    nombre_limpio = nombre_limpio.strip()
    return nombre_limpio

def es_url_youtube(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.netloc in ('www.youtube.com', 'youtube.com', 'm.youtube.com', 'youtu.be'):
            if parsed_url.netloc in ('youtu.be'):
                return True
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return True
    except:
        return False
    return False

'''
def descargar_video(url, ffmpeg_location, ruta_destino="."):
    try:
        if not es_url_youtube(url):
            raise ValueError("La URL no es una URL de YouTube válida.")
        ydl_opts = {
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'simulate': True,
            'writesubtitles': False,
            'allsubtitles': False,
            'subtitleslangs': ['en'],
            'outtmpl': os.path.join(ruta_destino, '%(title)s.%(ext)s'),
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_titulo = info_dict.get('title', None)
            video_titulo_limpio = limpiar_nombre_archivo(video_titulo)
            video_extension = "mp4"
            video_ruta = os.path.join(ruta_destino, f'{video_titulo_limpio}.{video_extension}')
        ydl_opts = {
            'outtmpl': video_ruta,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'verbose': True,
            'ffmpeg_location': ffmpeg_location,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return video_ruta
    except youtube_dl.utils.DownloadError as e:
        print(f"Error al descargar el video: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al descargar el video: {e}")
        return None
'''

def descargar_video(url, ruta_destino="."):
    try:
        if not es_url_youtube(url):
            raise ValueError("La URL no es una URL de YouTube válida.")
        ydl_opts = {
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'simulate': True,
            'writesubtitles': False,
            'allsubtitles': False,
            'subtitleslangs': ['en'],
            'outtmpl': os.path.join(ruta_destino, '%(title)s.%(ext)s'),
            'retries': 5,  # Reintentar la descarga varias veces
            'fragment_retries': 5, # Reintentar la descarga de fragmentos varias veces
            'continuedl': True #Reanudar descargas interrumpidas
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_titulo = info_dict.get('title', None)
            video_titulo_limpio = limpiar_nombre_archivo(video_titulo)
            video_extension = "mp4"
            video_ruta = os.path.join(ruta_destino, f'{video_titulo_limpio}.{video_extension}')
        ydl_opts = {
            'outtmpl': video_ruta,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'verbose': True,
            # 'ffmpeg_location': ffmpeg_location, #Eliminar esta linea
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return video_ruta
    except youtube_dl.utils.DownloadError as e:
        print(f"Error al descargar el video: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al descargar el video: {e}")
        return None

def convertir_video_a_audio(ruta_video, ruta_destino="."):
    try:
        ruta_video = os.path.abspath(ruta_video)
        video = VideoFileClip(ruta_video)
        audio_ruta = os.path.join(ruta_destino, os.path.splitext(os.path.basename(ruta_video))[0] + ".wav")
        video.audio.write_audiofile(audio_ruta)
        video.close()
        return audio_ruta
    except Exception as e:
        print(f"Error al convertir el video a audio: {e}")
        return None

'''
def descargar_video(url, ruta_destino="."):
    try:
        if not es_url_youtube(url):
            raise ValueError("La URL no es una URL de YouTube válida.")

        # Opcional: Ruta al archivo de cookies. Puedes obtenerla de Config o una variable de entorno.
        # Asegúrate de que este archivo exista en tu entorno de ejecución (especialmente en Docker)
        # cookie_file_path = Config.COOKIES_FILE_PATH # Asumiendo que lo añades en config.py
        cookie_file_path = os.getenv('YTDLP_COOKIES_FILE', 'cookies.txt') # O usa una variable de entorno

        ydl_opts = {
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'simulate': False, # Si usas simulate=True, no descargará realmente
            'writesubtitles': False,
            'allsubtitles': False,
            'subtitleslangs': ['en'],
            'outtmpl': os.path.join(ruta_destino, '%(title)s.%(ext)s'),
            'retries': 5,
            'fragment_retries': 5,
            'continuedl': True,
            'cookiefile': cookie_file_path if os.path.exists(cookie_file_path) else None, # Añadir esta línea
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', # Mover aquí para que se aplique desde el principio
            'verbose': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_titulo = info_dict.get('title', None)
            video_titulo_limpio = limpiar_nombre_archivo(video_titulo)
            video_extension = "mp4"
            video_ruta = os.path.join(ruta_destino, f'{video_titulo_limpio}.{video_extension}')

        # Realizar la descarga ahora que la ruta final está definida
        ydl_opts['outtmpl'] = video_ruta
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return video_ruta
    except youtube_dl.utils.DownloadError as e:
        print(f"Error al descargar el video: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al descargar el video: {e}")
        return None
'''