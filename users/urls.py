from django.urls import path
from . import views

app_name = 'users'  # Añadir namespace para la app

urlpatterns = [
    # URLpatterns como antes
    path('tecnicos/', views.TechnicianListView.as_view(), name='technician-list'),
    path('tecnicos/nuevo/', views.TechnicianCreateView.as_view(), name='technician-create'),
    path('tecnicos/<int:pk>/', views.TechnicianDetailView.as_view(), name='technician-detail'),
    path('tecnicos/<int:pk>/editar/', views.TechnicianUpdateView.as_view(), name='technician-update'),
    path('tecnicos/<int:pk>/eliminar/', views.TechnicianDeleteView.as_view(), name='technician-delete'),
]