from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('nuevo/', views.CourseCreateView.as_view(), name='course-create'),
    
    # Region URLs - Colocadas antes de las URLs genéricas
    path('regiones/', views.RegionListView.as_view(), name='region-list'),
    path('regiones/nueva/', views.RegionCreateView.as_view(), name='region-create'),
    path('regiones/<int:pk>/', views.RegionDetailView.as_view(), name='region-detail'),
    path('regiones/<int:pk>/editar/', views.RegionUpdateView.as_view(), name='region-update'),
    path('regiones/<int:pk>/eliminar/', views.RegionDeleteView.as_view(), name='region-delete'),
    
    # Instructor URLs - Colocadas antes de las URLs genéricas
    path('instructores/', views.InstructorListView.as_view(), name='instructor-list'),
    path('instructores/nuevo/', views.InstructorCreateView.as_view(), name='instructor-create'),
    path('instructores/<int:pk>/', views.InstructorDetailView.as_view(), name='instructor-detail'),
    path('instructores/<int:pk>/editar/', views.InstructorUpdateView.as_view(), name='instructor-update'),
    path('instructores/<int:pk>/eliminar/', views.InstructorDeleteView.as_view(), name='instructor-delete'),
    
    # Preguntas y respuestas
    path('<int:course_id>/preguntas/', views.add_questions, name='add-questions'),
    path('preguntas/<int:question_id>/respuestas/', views.add_answers, name='add-answers'),

    path('nuevo-integral/', views.manage_course, name='course-manage-new'),
    path('<int:course_id>/editar-integral/', views.manage_course, name='course-manage-edit'),
    
    # Course detail URLs - Colocadas al final para evitar capturar otras rutas
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<slug:slug>/editar/', views.CourseUpdateView.as_view(), name='course-update'),
    path('<slug:slug>/eliminar/', views.CourseDeleteView.as_view(), name='course-delete'),
]