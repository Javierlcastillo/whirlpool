from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings

from .api_views import (
    CourseViewSet, RegionViewSet, InstructorViewSet,
    DesempenoViewSet, QuestionViewSet, AnswerViewSet,
    SectionViewSet, CourseApplicationViewSet
)

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Whirlpool API",
        default_version='v1',
        description="API para el sistema de capacitación de Whirlpool",
        terms_of_service="https://www.whirlpool.com/terms/",
        contact=openapi.Contact(email="contact@whirlpool.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=settings.BASE_URL,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'instructors', InstructorViewSet)
router.register(r'desempenos', DesempenoViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'applications', CourseApplicationViewSet)

urlpatterns = [
    # Endpoints de la API
    path('', include(router.urls)),
    path('token/', obtain_auth_token, name='api_token_auth'),
    
    # Documentación de la API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('schema.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
] 