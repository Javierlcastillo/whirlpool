from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from courses.models import Course, Desempeno, Region, Instructor
from users.models import Technician
from .serializers import (
    CourseSerializer, 
    CourseDetailSerializer,
    TechnicianSerializer, 
    TechnicianDetailSerializer,
    RegionSerializer,
    InstructorSerializer,
    DesempenoSerializer
)

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite ver cursos.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'instructor__id', 'region__id']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'duration_weeks']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

class TechnicianViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite ver técnicos.
    """
    queryset = Technician.objects.all()
    serializer_class = TechnicianSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region__id']
    search_fields = ['name', 'employee_number']
    ordering_fields = ['name', 'employee_number']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TechnicianDetailSerializer
        return TechnicianSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite ver regiones.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']

class InstructorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite ver instructores.
    """
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region__id']
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

class DesempenoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite ver desempeños.
    """
    queryset = Desempeno.objects.all()
    serializer_class = DesempenoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['technician__id', 'course__id', 'estado']
    ordering_fields = ['fecha', 'puntuacion']
    ordering = ['-fecha']