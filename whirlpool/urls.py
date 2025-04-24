from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from users.views import CustomLoginView, CustomLogoutView

# Importar los modelos necesarios para el Dashboard
from courses.models import Course, Region, Instructor, Desempeno
from users.models import Technician

# Crear una vista mejorada para el dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Conteos para las tarjetas principales
        context['courses_count'] = Course.objects.count()
        context['technicians_count'] = Technician.objects.count()
        context['instructors_count'] = Instructor.objects.count()
        context['regions_count'] = Region.objects.count()
        
        # Métricas de desempeño
        desempenos = Desempeno.objects.all()
        context['total_desempenos'] = desempenos.count()
        context['completed_desempenos'] = desempenos.filter(aprobado=True).count()
        context['failed_desempenos'] = desempenos.filter(aprobado=False).count()
        
        # Calcular tasa de aprobación (evitar división por cero)
        if context['total_desempenos'] > 0:
            context['approval_rate'] = (context['completed_desempenos'] / context['total_desempenos']) * 100
        else:
            context['approval_rate'] = 0
        
        # Últimos cursos añadidos
        context['latest_courses'] = Course.objects.all().order_by('-created_at')[:5]
        
        return context

urlpatterns = [
    # Redirigir la raíz a la página de login
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    
    # URLs de autenticación - Usando vistas personalizadas
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Dashboard - Ahora con datos completos
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # URLs de la aplicación
    path('users/', include('users.urls', namespace='users')),
    path('courses/', include('courses.urls', namespace='courses')),
    
    # URLs de la API
    path('api/courses/', include('courses.api_urls')),
    path('api/users/', include('users.api_urls')),
    
    # Panel de administración
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)