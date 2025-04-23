from django.urls import path
from .api_views import technician_login

urlpatterns = [
    path('tecnicos/login/', technician_login, name='technician_login'),
] 