from django.urls import path
from .views import (
    # Course views
    CourseListView, CourseDetailView, CourseDeleteView, manage_course,
    enroll_course, complete_section, complete_question,
    course_progress, course_certificate, course_view_content,
    # Region views
    RegionListView, RegionDetailView, RegionCreateView,
    RegionUpdateView, RegionDeleteView,
    # Instructor views
    InstructorListView, InstructorDetailView, InstructorCreateView,
    InstructorUpdateView, InstructorDeleteView,
    # Course region management
    add_region_to_course, remove_region_from_course,
    # New course management URLs
    course_base_edit, course_sections_edit, course_section_add, course_section_edit,
    course_section_delete, course_questions_edit, course_question_add, course_question_edit,
    course_question_delete, course_content_order, course_section_move, course_question_move
)

app_name = 'courses'

urlpatterns = [
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

    # Course URLs
    path('', CourseListView.as_view(), name='course-list'),
    path('create/', course_base_edit, name='course-create'),
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
    path('<slug:slug>/view-content/', course_view_content, name='course_view_content'),

    # New course management URLs
    path('<slug:slug>/edit/', course_base_edit, name='course-edit'),
    path('<slug:slug>/sections/', course_sections_edit, name='course-edit-sections'),
    path('<slug:slug>/section/add/', course_section_add, name='course-section-add'),
    path('<slug:slug>/section/<int:section_id>/edit/', course_section_edit, name='course-section-edit'),
    path('<slug:slug>/section/<int:section_id>/delete/', course_section_delete, name='course-section-delete'),
    path('<slug:slug>/questions/', course_questions_edit, name='course-edit-questions'),
    path('<slug:slug>/question/add/', course_question_add, name='course-question-add'),
    path('<slug:slug>/question/<int:question_id>/edit/', course_question_edit, name='course-question-edit'),
    path('<slug:slug>/question/<int:question_id>/delete/', course_question_delete, name='course-question-delete'),
    path('<slug:slug>/order/', course_content_order, name='course-content-order'),
    path('<slug:slug>/section/<int:section_id>/move/<str:direction>/', course_section_move, name='course-section-move'),
    path('<slug:slug>/question/<int:question_id>/move/<str:direction>/', course_question_move, name='course-question-move'),
]