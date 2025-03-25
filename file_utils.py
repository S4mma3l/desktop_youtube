import os

def generar_documento_texto(texto, ruta_destino):
    try:
        print(f"Intentando escribir en el archivo: {ruta_destino}") # Depuración
        with open(ruta_destino, "w", encoding="utf-8") as archivo:
            archivo.write(texto)
        print(f"Archivo {ruta_destino} escrito correctamente.") # Depuración
        return True
    except Exception as e:
        print(f"Error al escribir en el archivo {ruta_destino}: {e}")
        return False

def eliminar_archivo(ruta_archivo):
    try:
        os.remove(ruta_archivo)
        return True
    except Exception as e:
        print(f"Error al eliminar el archivo: {e}")
        return False