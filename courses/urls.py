from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('nuevo/', views.CourseCreateView.as_view(), name='course-create'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<slug:slug>/editar/', views.CourseUpdateView.as_view(), name='course-update'),
    path('<slug:slug>/eliminar/', views.CourseDeleteView.as_view(), name='course-delete'),
    path('<int:course_id>/preguntas/', views.add_questions, name='add-questions'),
]