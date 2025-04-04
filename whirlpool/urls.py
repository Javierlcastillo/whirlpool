from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from users.views import CustomLoginView, CustomLogoutView  # Importar las vistas personalizadas

urlpatterns = [
    # Redirigir la raíz a la página de login
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    
    # URLs de autenticación - Usando vistas personalizadas
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    
    # URLs de la aplicación
    path('courses/', include('courses.urls')),
    path('api/', include('api.urls')),
    path('users/', include('users.urls')),
    
    # Panel de administración
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)