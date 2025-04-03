from django.urls import path
from .views import (
    # Course views
    CourseListView, CourseDetailView, CourseDeleteView, manage_course,
    enroll_course, complete_section, complete_question,
    course_progress, course_certificate,
    # Region views
    RegionListView, RegionDetailView, RegionCreateView,
    RegionUpdateView, RegionDeleteView,
    # Instructor views
    InstructorListView, InstructorDetailView, InstructorCreateView,
    InstructorUpdateView, InstructorDeleteView,
    # Course region management
    add_region_to_course, remove_region_from_course
)

app_name = 'courses'

urlpatterns = [
    # Course URLs
    path('', CourseListView.as_view(), name='course-list'),
    path('create/', manage_course, name='course-create'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course-detail'),
    path('<slug:slug>/update/', manage_course, name='course-update'),
    path('<slug:slug>/enroll/', enroll_course, name='course-enroll'),
    path('<slug:slug>/complete-section/<int:section_id>/', complete_section, name='complete-section'),
    path('<slug:slug>/complete-question/<int:question_id>/', complete_question, name='complete-question'),
    path('<slug:slug>/progress/', course_progress, name='course-progress'),
    path('<slug:slug>/certificate/', course_certificate, name='course-certificate'),
    path('<slug:slug>/eliminar/', CourseDeleteView.as_view(), name='course-delete'),
    path('<slug:slug>/add-region/', add_region_to_course, name='course-add-region'),
    path('<slug:slug>/remove-region/<int:region_id>/', remove_region_from_course, name='course-remove-region'),

    # Region URLs
    path('regiones/', RegionListView.as_view(), name='region-list'),
    path('regiones/nueva/', RegionCreateView.as_view(), name='region-create'),
    path('regiones/<int:pk>/', RegionDetailView.as_view(), name='region-detail'),
    path('regiones/<int:pk>/editar/', RegionUpdateView.as_view(), name='region-update'),
    path('regiones/<int:pk>/eliminar/', RegionDeleteView.as_view(), name='region-delete'),

    # Instructor URLs
    path('instructores/', InstructorListView.as_view(), name='instructor-list'),
    path('instructores/nuevo/', InstructorCreateView.as_view(), name='instructor-create'),
    path('instructores/<int:pk>/', InstructorDetailView.as_view(), name='instructor-detail'),
    path('instructores/<int:pk>/editar/', InstructorUpdateView.as_view(), name='instructor-update'),
    path('instructores/<int:pk>/eliminar/', InstructorDeleteView.as_view(), name='instructor-delete'),
]