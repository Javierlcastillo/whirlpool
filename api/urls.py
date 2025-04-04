from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import (
    CourseViewSet, RegionViewSet, InstructorViewSet,
    QuestionViewSet, AnswerViewSet, SectionViewSet,
    CourseApplicationViewSet, EnrollmentViewSet
)

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Whirlpool Courses API",
        default_version='v1',
        description="API documentation for Whirlpool Courses",
        terms_of_service="https://www.whirlpool.com/terms/",
        contact=openapi.Contact(email="contact@whirlpool.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'instructors', InstructorViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'course-applications', CourseApplicationViewSet, basename='courseapplication')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]