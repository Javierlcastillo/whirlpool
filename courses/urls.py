from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('nuevo/', views.manage_course, name='course-create'),

    # Region URLs - Mantenidas sin cambios
    path('regiones/', views.RegionListView.as_view(), name='region-list'),
    path('regiones/nueva/', views.RegionCreateView.as_view(), name='region-create'),
    path('regiones/<int:pk>/', views.RegionDetailView.as_view(), name='region-detail'),
    path('regiones/<int:pk>/editar/', views.RegionUpdateView.as_view(), name='region-update'),
    path('regiones/<int:pk>/eliminar/', views.RegionDeleteView.as_view(), name='region-delete'),

    # Instructor URLs - Mantenidas sin cambios
    path('instructores/', views.InstructorListView.as_view(), name='instructor-list'),
    path('instructores/nuevo/', views.InstructorCreateView.as_view(), name='instructor-create'),
    path('instructores/<int:pk>/', views.InstructorDetailView.as_view(), name='instructor-detail'),
    path('instructores/<int:pk>/editar/', views.InstructorUpdateView.as_view(), name='instructor-update'),
    path('instructores/<int:pk>/eliminar/', views.InstructorDeleteView.as_view(), name='instructor-delete'),

    # Course detail URLs
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<slug:slug>/editar/', views.manage_course, name='course-update'),
    path('<slug:slug>/eliminar/', views.CourseDeleteView.as_view(), name='course-delete'),
]