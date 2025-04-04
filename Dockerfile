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

# Comando para ejecutar la aplicación
CMD bash -c "echo 'Waiting for postgres...' && \
             while ! nc -z db 5432; do sleep 1; done && \
             echo 'PostgreSQL started' && \
             sleep 5 && \
             echo 'Applying migrations...' && \
             python manage.py migrate --noinput && \
             echo 'Starting server...' && \
             python manage.py runserver 0.0.0.0:8000"