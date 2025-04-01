FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    grep \
    && rm -rf /var/lib/apt/lists/*

# Instalar Django y otras dependencias básicas explícitamente
RUN pip install --upgrade pip && \
    pip install Django==4.2.7 \
    djangorestframework==3.14.0 \
    django-crispy-forms==2.0 \
    crispy-bootstrap5==0.7 \
    django-cors-headers==4.3.0 \
    django-filter==23.3 \
    drf-yasg==1.21.7 \
    whitenoise==6.5.0 \
    mysqlclient==2.2.0 \
    Pillow==10.0.0

# Copiar proyecto
COPY . .

# Puerto donde se expone la aplicación
EXPOSE 8000

# Comandos para iniciar la aplicación
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    python manage.py runserver 0.0.0.0:8000