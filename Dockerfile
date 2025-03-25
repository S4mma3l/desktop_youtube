# Usa una imagen base de Python (elige la versión que estés usando)
FROM python:3.11-slim-buster

# Actualiza el sistema e instala dependencias del sistema operativo necesarias para ffmpeg y yt-dlp
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu aplicación al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expon el puerto que tu aplicación usa (si aplica)
# EXPOSE 5000

# Define el comando para ejecutar tu aplicación
CMD ["python", "app.py"]