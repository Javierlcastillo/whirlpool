from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views

# Configuración de documentación con Swagger/ReDoc
schema_view = get_schema_view(
   openapi.Info(
      title="Whirlpool Courses API",
      default_version='v1',
      description="API para el sistema de capacitación de Whirlpool",
      terms_of_service="https://www.whirlpool.com/terms/",
      contact=openapi.Contact(email="contact@whirlpool.com"),
      license=openapi.License(name="Whirlpool License"),
   ),
   public=True,
   permission_classes=[permissions.IsAuthenticatedOrReadOnly],
)

# Configuración de API v1
router_v1 = DefaultRouter()
router_v1.register(r'courses', views.CourseViewSet)
router_v1.register(r'technicians', views.TechnicianViewSet)
router_v1.register(r'regions', views.RegionViewSet)
router_v1.register(r'instructors', views.InstructorViewSet)
router_v1.register(r'desempenos', views.DesempenoViewSet)

urlpatterns = [
    # Endpoints de API v1
    path('v1/', include([
        path('', include(router_v1.urls)),
        path('token/', obtain_auth_token, name='api_token_auth'),
    ])),
    
    # Para mantener compatibilidad con código existente, enrutar también a la raíz
    path('', include(router_v1.urls)),
    
    # Autenticación de DRF
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # Documentación de la API
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]