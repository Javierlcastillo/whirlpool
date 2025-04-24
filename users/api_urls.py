from django.urls import path
from .api_views import TechnicianLoginView

urlpatterns = [
    path('tecnicos/login/', TechnicianLoginView.as_view(), name='technician_login'),
] 