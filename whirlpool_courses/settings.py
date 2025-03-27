import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-whirlpool-courses-secretkey-changemeinproduction'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',
    'drf_yasg',  # Para documentación de API

    # Custom apps
    'courses.apps.CoursesConfig',
    'users.apps.UsersConfig',
    'api.apps.ApiConfig',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS debe estar antes de CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'whirlpool_courses.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'whirlpool_courses.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bx7ok4oweefajlo8iswk',
        'USER': 'uy9qlsaxossvprwa',
        'PASSWORD': 'hbMplA3R9ru3W7HNztbu',
        'HOST': 'bx7ok4oweefajlo8iswk-mysql.services.clever-cloud.com',
        'PORT': '3306',  # Puerto por defecto de MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Requiere autenticación por defecto
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # Autenticación por token
        'rest_framework.authentication.SessionAuthentication',  # Autenticación por sesión
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # Filtrado
        'rest_framework.filters.SearchFilter',  # Búsqueda
        'rest_framework.filters.OrderingFilter',  # Ordenamiento
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
}

# Configuración CORS (Cross-Origin Resource Sharing)
# En desarrollo puede ser útil permitir todos los orígenes, pero en producción debe ser más restrictivo
if DEBUG:
    # Configuración para desarrollo
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Configuración más segura para producción
    CORS_ALLOWED_ORIGINS = [
        "https://whirlpool-courses.example.com",
        "https://app.whirlpool-courses.example.com",
        # Agregar aquí los dominios de frontend que necesiten acceder a la API
    ]
    CORS_ALLOW_CREDENTIALS = True
    
# Configuración para Swagger/ReDoc
SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Token': {
         'type': 'apiKey',
         'name': 'Authorization',
         'in': 'header'
      }
   },
   'USE_SESSION_AUTH': True,  # Permitir autenticación por sesión en la interfaz de Swagger
   'LOGIN_URL': 'login',
   'LOGOUT_URL': 'logout',
}