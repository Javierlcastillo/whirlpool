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
    EnrollmentSerializer,
    UnityGameCourseSerializer
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
    ordering_fields = ['name', 'created_at', 'duration_hours']
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
    
    @action(detail=True, methods=['get'])
    def available_courses(self, request, pk=None):
        """
        Obtiene los cursos disponibles para un técnico basado en su región.
        """
        technician = self.get_object()
        
        # Encuentra todos los cursos disponibles en la región del técnico
        region = technician.region
        if not region:
            return Response({"detail": "Este técnico no tiene una región asignada."}, status=400)
            
        course_applications = CourseApplication.objects.filter(region=region)
        available_courses = [app.course for app in course_applications]
        
        serializer = CourseSerializer(available_courses, many=True)
        return Response(serializer.data)

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
    queryset = CourseApplication.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        """
        Verifica si un curso está disponible para un técnico basado en su región.
        """
        course = get_object_or_404(Course, pk=pk)
        technician = get_object_or_404(Technician, user=request.user)
        
        # Verificar si el curso está disponible en la región del técnico
        is_available = CourseApplication.objects.filter(
            course=course, region=technician.region
        ).exists()
        
        # Crear o actualizar registro de desempeño si el curso está disponible
        if is_available:
            desempeno, created = Desempeno.objects.get_or_create(
                course=course,
                technician=technician,
                defaults={'estado': 'started'}
            )
        
        return Response({'is_available': is_available})

class UnityGameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para consumir cursos desde un juego en Unity.
    Proporciona solo acceso de lectura a los datos requeridos.
    
    list:
    Devuelve la lista de todos los cursos disponibles en un formato adaptado para Unity.
    
    retrieve:
    Devuelve los detalles completos de un curso específico, incluyendo secciones y preguntas,
    en un formato optimizado para el consumo desde Unity.
    """
    queryset = Course.objects.filter(is_active=True)
    serializer_class = UnityGameCourseSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'instructor__id', 'region__id']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'duration_hours']
    ordering = ['name']
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def user_info(self, request):
        """
        Devuelve información del usuario autenticado para verificación en el juego.
        """
        user = request.user
        try:
            technician = Technician.objects.get(user=user)
            region_name = technician.region.nombre if technician.region else ""
            
            return Response({
                'id': technician.id,
                'employee_number': technician.numero_empleado,
                'name': technician.name,
                'region': region_name,
                'is_active': technician.is_active
            })
        except Technician.DoesNotExist:
            return Response({"detail": "Usuario no es un técnico registrado."}, status=403)
    
    @action(detail=False, methods=['get'])
    def available_courses(self, request):
        """
        Obtiene los cursos disponibles para un técnico basado en su región.
        """
        user = request.user
        try:
            technician = Technician.objects.get(user=user)
            region = technician.region
            
            if not region:
                return Response({"detail": "Este técnico no tiene una región asignada."}, status=400)
                
            course_applications = CourseApplication.objects.filter(region=region)
            available_courses = [app.course for app in course_applications if app.course.is_active]
            
            serializer = self.get_serializer(available_courses, many=True)
            return Response(serializer.data)
            
        except Technician.DoesNotExist:
            return Response({"detail": "Usuario no es un técnico registrado."}, status=403)
    
    @action(detail=True, methods=['post'])
    def submit_progress(self, request, slug=None):
        """
        Recibe y registra el progreso y puntuación del técnico en un curso.
        """
        course = self.get_object()
        user = request.user
        
        try:
            technician = Technician.objects.get(user=user)
            score = request.data.get('score', 0)
            status = request.data.get('status', 'in_progress')
            
            # Actualizar o crear registro de desempeño
            desempeno, created = Desempeno.objects.update_or_create(
                course=course,
                technician=technician,
                defaults={
                    'puntuacion': score,
                    'estado': status
                }
            )
            
            return Response({
                'success': True,
                'message': 'Progreso registrado correctamente',
                'desempeno_id': desempeno.id
            })
            
        except Technician.DoesNotExist:
            return Response({"detail": "Usuario no es un técnico registrado."}, status=403)