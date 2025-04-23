from rest_framework import viewsets, filters, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Course, Desempeno, Region, Instructor, Question, Answer, Section, CourseApplication
from users.models import Technician
from .api_serializers import (
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
    TechnicianAuthSerializer,
    CourseCompleteSerializer
)
from .api_permissions import IsAdminUserOrReadOnly

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
    filterset_fields = ['instructor__id', 'region__id']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'duration_hours']
    ordering = ['-created_at']
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    @swagger_auto_schema(
        operation_description="Obtiene la estructura completa de un curso con sus secciones y preguntas "
                            "combinadas en una sola lista ordenada por el campo 'order'",
        responses={
            200: openapi.Response(
                description="Estructura completa del curso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'slug': openapi.Schema(type=openapi.TYPE_STRING),
                        'description': openapi.Schema(type=openapi.TYPE_STRING),
                        'instructor': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'region': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'nombre': openapi.Schema(type=openapi.TYPE_STRING)
                                    }
                                )
                            }
                        ),
                        'duration_hours': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'region': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'nombre': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        ),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'content': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'type': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        enum=['section', 'question']
                                    ),
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'order': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    # Propiedades específicas de sección
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                                    'media': openapi.Schema(type=openapi.TYPE_STRING, format='uri'),
                                    # Propiedades específicas de pregunta
                                    'text': openapi.Schema(type=openapi.TYPE_STRING),
                                    'type': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        enum=['multiple_choice', 'true_false']
                                    ),
                                    'answers': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'number': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'answer': openapi.Schema(type=openapi.TYPE_STRING),
                                                'media': openapi.Schema(type=openapi.TYPE_STRING, format='uri'),
                                                'is_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                                            }
                                        )
                                    )
                                }
                            )
                        )
                    }
                )
            ),
            404: "Curso no encontrado"
        }
    )
    @action(detail=True, methods=['get'])
    def complete_structure(self, request, slug=None):
        """
        Obtiene la estructura completa de un curso, incluyendo:
        - Información básica del curso
        - Contenido: Lista combinada de secciones y preguntas ordenadas por el campo 'order'
        
        Cada elemento en la lista de contenido tiene:
        - type: 'section' o 'question'
        - order: Número de orden para la secuencia
        - id: Identificador único
        
        Para secciones:
        - title: Título de la sección
        - content: Contenido de la sección
        - media: URL del archivo multimedia (si existe)
        
        Para preguntas:
        - text: Texto de la pregunta
        - type: Tipo de pregunta (multiple_choice o true_false)
        - answers: Lista de respuestas, cada una con:
          - number: Número de la respuesta
          - answer: Texto de la respuesta
          - media: URL del archivo multimedia (si existe)
          - is_correct: Indica si es la respuesta correcta
        """
        course = self.get_object()
        serializer = CourseCompleteSerializer(course, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Sincroniza el orden de contenido del curso",
        responses={
            200: openapi.Response("Sincronización exitosa"),
            404: "Curso no encontrado"
        }
    )
    @action(detail=True, methods=['post'])
    def sync_content_order(self, request, slug=None):
        """
        Sincroniza los registros de orden para las secciones y preguntas del curso.
        Útil cuando se migra de la vieja estructura a la nueva.
        """
        course = self.get_object()
        items_count = course.sync_content_order()
        return Response({
            "status": "success", 
            "message": f"Sincronización completada. {items_count} elementos ordenados."
        })

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
    search_fields = ['name', 'numero_empleado']
    ordering_fields = ['name', 'numero_empleado']
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

@swagger_auto_schema(
    method='post',
    request_body=TechnicianAuthSerializer,
    responses={
        200: openapi.Response('Autenticación exitosa'),
        401: openapi.Response('Credenciales inválidas')
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def technician_login(request):
    """
    Endpoint para la autenticación de técnicos.
    
    Recibe:
    - numero_empleado: Número de empleado del técnico
    - password: Contraseña
    
    Devuelve:
    - authenticated: true/false
    - message: Mensaje de estado
    - technician: Datos del técnico (solo si la autenticación es exitosa)
    """
    serializer = TechnicianAuthSerializer(data=request.data)
    
    if serializer.is_valid():
        technician = serializer.validated_data['technician']
        technician_data = TechnicianSerializer(technician).data
        
        return Response({
            'authenticated': True,
            'message': 'Autenticación exitosa',
            'technician': technician_data
        })
    
    return Response({
        'authenticated': False,
        'message': 'Credenciales inválidas'
    }, status=status.HTTP_401_UNAUTHORIZED) 