from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.views import CustomLoginView, CustomLogoutView

# Creamos una vista protegida para el dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

urlpatterns = [
    # Redirigir la raíz a la página de login
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    
    # URLs de autenticación - Usando vistas personalizadas
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Dashboard - Ahora protegido con LoginRequiredMixin
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
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