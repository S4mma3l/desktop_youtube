# Usa una imagen base de Python (elige la versión que estés usando)
FROM python:3.11-slim-buster

# Actualiza el sistema e instala dependencias del sistema operativo necesarias para ffmpeg y yt-dlp
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    cron \ # Instala el servicio cron
    nano \ # o vim
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

# Crea un script para limpiar la carpeta temporal
RUN echo "find /app/temp/ -type f -mmin +60 -delete" > /app/clean_temp.sh && chmod +x /app/clean_temp.sh

# Añade la tarea cron al crontab
RUN echo "* * * * * /app/clean_temp.sh" >> /etc/crontab

# Inicia el servicio cron
RUN service cron start

# Asegúrate de que el archivo crontab tenga la sintaxis correcta
RUN crontab /etc/crontab

# Define el comando para ejecutar tu aplicación
CMD ["python", "app.py"]