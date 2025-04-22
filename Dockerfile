FROM python:3.11-slim

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
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/staticfiles /app/media

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput

# Crear script de inicio
RUN echo '#!/bin/bash\n\
while ! nc -z db 5432; do\n\
  sleep 0.1\n\
done\n\
python manage.py migrate\n\
python manage.py runserver 0.0.0.0:3000' > /app/start.sh && \
chmod +x /app/start.sh

# Exponer el puerto
EXPOSE 3000

# Comando de inicio
CMD ["/app/start.sh"]