from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from courses.models import Course, Desempeno, Region, Instructor, Question, Answer, Section, CourseApplication
from users.models import Technician
from .serializers import (
    CourseSerializer, 
    CourseDetailSerializer,
    TechnicianSerializer, 
    TechnicianDetailSerializer,
    RegionSerializer,
    InstructorSerializer,
    DesempenoSerializer,
    QuestionSerializer,
    AnswerSerializer,
    SectionSerializer,
    CourseApplicationSerializer,
    EnrollmentSerializer
)
from .permissions import IsAdminUserOrReadOnly

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar cursos.
    
    list:
    Devuelve la lista de todos los cursos disponibles.
    
    retrieve:
    Devuelve los detalles completos de un curso específico.
    
    create:
    Crea un nuevo curso (solo administradores).
    
    update:
    Actualiza un curso existente (solo administradores).
    
    partial_update:
    Actualiza parcialmente un curso existente (solo administradores).
    
    destroy:
    Elimina un curso (solo administradores).
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'instructor__id', 'region__id']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'duration_weeks']
    ordering = ['-created_at']
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

class TechnicianViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar técnicos.
    
    list:
    Devuelve la lista de todos los técnicos.
    
    retrieve:
    Devuelve los detalles de un técnico específico, incluyendo su desempeño.
    
    Las operaciones de escritura solo están disponibles para administradores.
    """
    queryset = Technician.objects.all()
    serializer_class = TechnicianSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region__id']
    search_fields = ['name', 'employee_number']
    ordering_fields = ['name', 'employee_number']
    ordering = ['name']
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TechnicianDetailSerializer
        return TechnicianSerializer

class RegionViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar regiones.
    
    Las operaciones de escritura solo están disponibles para administradores.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']
    permission_classes = [IsAdminUserOrReadOnly]

class InstructorViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar instructores.
    
    Las operaciones de escritura solo están disponibles para administradores.
    """
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region__id']
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    permission_classes = [IsAdminUserOrReadOnly]

class DesempenoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar desempeños.
    
    Las operaciones de escritura solo están disponibles para administradores.
    """
    queryset = Desempeno.objects.all()
    serializer_class = DesempenoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['technician__id', 'course__id', 'estado']
    ordering_fields = ['fecha', 'puntuacion']
    ordering = ['-fecha']
    permission_classes = [IsAdminUserOrReadOnly]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseApplicationViewSet(viewsets.ModelViewSet):
    queryset = CourseApplication.objects.all()
    serializer_class = CourseApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = CourseApplication.objects.all()  # Usamos CourseApplication como Enrollment
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        technician = get_object_or_404(Technician, user=request.user)
        
        enrollment, created = CourseApplication.objects.get_or_create(
            course=course,
            region=technician.region
        )
        
        if created:
            return Response({'status': 'enrolled'})
        return Response({'status': 'already enrolled'})
