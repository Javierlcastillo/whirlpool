from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'technicians', views.TechnicianViewSet)
router.register(r'regions', views.RegionViewSet)
router.register(r'instructors', views.InstructorViewSet)
router.register(r'desempenos', views.DesempenoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('token/', obtain_auth_token, name='api_token_auth'),
]