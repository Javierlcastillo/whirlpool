from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from courses.views import dashboard

urlpatterns = [
    # Frontend y administración
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),  # Dashboard como página principal
    path('cursos/', include('courses.urls')),
    path('usuarios/', include('users.urls')),
    
    # API endpoints
    path('api/', include('api.urls')),  # Rutas de la API
    
    # Redireccionar a la documentación de la API
    path('api-docs/', RedirectView.as_view(pattern_name='schema-swagger-ui'), name='api-docs'),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)