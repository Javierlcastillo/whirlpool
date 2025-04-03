FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Crear directorios necesarios y establecer permisos
RUN mkdir -p /app/staticfiles /app/media && \
    chmod -R 755 /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Puerto donde se expone la aplicación
EXPOSE 8000

# Crear un script de inicio
RUN echo '#!/bin/bash\n\
echo "Waiting for postgres..."\n\
while ! nc -z db 5432; do\n\
  sleep 0.1\n\
done\n\
echo "PostgreSQL started"\n\
python manage.py migrate --noinput\n\
python manage.py runserver 0.0.0.0:8000' > /app/start.sh && \
chmod +x /app/start.sh

# Usar el script como punto de entrada
ENTRYPOINT ["/bin/bash", "/app/start.sh"]