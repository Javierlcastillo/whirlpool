"""
ASGI config for whirlpool project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from django.core.asgi import get_asgi_application

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whirlpool.settings')

application = get_asgi_application() 