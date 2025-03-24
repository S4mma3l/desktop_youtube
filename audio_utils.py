from pydub import AudioSegment
import speech_recognition as sr
import os

def segmentar_audio(ruta_audio, duracion_segmento=30 * 1000):
    audio = AudioSegment.from_wav(ruta_audio)
    longitud_total = len(audio)
    segmentos = []
    inicio = 0
    while inicio < longitud_total:
        fin = inicio + duracion_segmento
        segmento = audio[inicio:fin]
        segmentos.append(segmento)
        inicio = fin
    return segmentos

def transcribir_segmentos(segmentos, language="es-ES", ruta_destino="."):
    transcripciones = []
    reconocedor = sr.Recognizer()
    for i, segmento in enumerate(segmentos):
        ruta_segmento = os.path.join(ruta_destino, f"segmento_{i}.wav")
        segmento.export(ruta_segmento, format="wav")
        with sr.AudioFile(ruta_segmento) as fuente:
            audio_data = reconocedor.record(fuente)
            try:
                texto = reconocedor.recognize_google(audio_data, language=language)
                transcripciones.append(texto)
            except sr.UnknownValueError:
                transcripciones.append("[Segmento no reconocido]")
            except sr.RequestError as e:
                transcripciones.append(f"[Error de la API de Google: {e}]")
        os.remove(ruta_segmento)
    return transcripciones