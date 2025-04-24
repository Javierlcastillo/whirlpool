from rest_framework import viewsets, filters, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404

from .models import Course, Desempeno, Region, Instructor, Question, Answer, Section, CourseApplication
from .api_serializers import (
    CourseSerializer, 
    CourseDetailSerializer,
    RegionSerializer,
    RegionDetailSerializer,
    InstructorSerializer,
    DesempenoSerializer,
    QuestionSerializer,
    AnswerSerializer,
    SectionSerializer,
    CourseApplicationSerializer,
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
                        'instructor': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'region': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'duration_hours': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'content': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'type': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Tipo de contenido: 'section' o tipo de pregunta ('multiple_choice', 'true_false')"
                                    ),
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'order': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description="Valor numérico incremental que indica la posición del elemento en el curso (comienza en 1)"
                                    ),
                                    # Propiedades específicas de sección
                                    'title': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Título de la sección (solo presente si type='section')"
                                    ),
                                    'content': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Contenido textual de la sección (solo presente si type='section')"
                                    ),
                                    'media': openapi.Schema(
                                        type=openapi.TYPE_STRING, 
                                        format='uri',
                                        description="URL del archivo multimedia asociado, o null (presente en secciones y respuestas)",
                                        nullable=True
                                    ),
                                    # Propiedades específicas de pregunta
                                    'text': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Texto de la pregunta (solo presente si type es un tipo de pregunta)"
                                    ),
                                    'answers': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        description="Lista de respuestas a la pregunta (solo presente si type es un tipo de pregunta)",
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'number': openapi.Schema(
                                                    type=openapi.TYPE_INTEGER,
                                                    description="Número de la respuesta (1, 2, 3...)"
                                                ),
                                                'answer': openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    description="Texto de la respuesta"
                                                ),
                                                'media': openapi.Schema(
                                                    type=openapi.TYPE_STRING, 
                                                    format='uri',
                                                    description="URL del archivo multimedia asociado, o null",
                                                    nullable=True
                                                ),
                                                'is_correct': openapi.Schema(
                                                    type=openapi.TYPE_BOOLEAN,
                                                    description="Indica si esta es la respuesta correcta"
                                                )
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
        course = self.get_object()
        serializer = CourseCompleteSerializer(course)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Sincroniza el orden de contenido del curso",
        responses={
            200: openapi.Response(
                description="Sincronización exitosa", 
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Estado de la operación, 'success' si fue exitosa"
                        ),
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Mensaje de confirmación con el número de elementos ordenados"
                        )
                    }
                )
            ),
            404: "Curso no encontrado"
        }
    )
    @action(detail=True, methods=['post'])
    def sync_content_order(self, request, slug=None):
        course = self.get_object()
        course.sync_content_order()
        return Response({
            'status': 'success',
            'message': f'Se sincronizó el orden de {course.content.count()} elementos'
        })

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
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RegionDetailSerializer
        return RegionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'courses',
                'instructors'
            )
        return queryset

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
    """
    API endpoint para gestionar preguntas.
    
    list:
    Devuelve la lista de todas las preguntas.
    
    retrieve:
    Devuelve los detalles de una pregunta específica, incluyendo sus respuestas.
    
    create:
    Crea una nueva pregunta (requiere autenticación).
    
    update:
    Actualiza una pregunta existente (requiere autenticación).
    
    partial_update:
    Actualiza parcialmente una pregunta existente (requiere autenticación).
    
    destroy:
    Elimina una pregunta (requiere autenticación).
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

class AnswerViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar respuestas a preguntas.
    
    list:
    Devuelve la lista de todas las respuestas.
    
    retrieve:
    Devuelve los detalles de una respuesta específica.
    
    create:
    Crea una nueva respuesta (requiere autenticación).
    
    update:
    Actualiza una respuesta existente (requiere autenticación).
    
    partial_update:
    Actualiza parcialmente una respuesta existente (requiere autenticación).
    
    destroy:
    Elimina una respuesta (requiere autenticación).
    """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

class SectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar secciones de contenido.
    
    list:
    Devuelve la lista de todas las secciones.
    
    retrieve:
    Devuelve los detalles de una sección específica.
    
    create:
    Crea una nueva sección (requiere autenticación).
    
    update:
    Actualiza una sección existente (requiere autenticación).
    
    partial_update:
    Actualiza parcialmente una sección existente (requiere autenticación).
    
    destroy:
    Elimina una sección (requiere autenticación).
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar aplicaciones de cursos a regiones.
    
    list:
    Devuelve la lista de todas las aplicaciones de cursos.
    
    retrieve:
    Devuelve los detalles de una aplicación específica.
    
    create:
    Crea una nueva aplicación de curso a región (requiere autenticación).
    
    update:
    Actualiza una aplicación existente (requiere autenticación).
    
    partial_update:
    Actualiza parcialmente una aplicación existente (requiere autenticación).
    
    destroy:
    Elimina una aplicación de curso a región (requiere autenticación).
    """
    queryset = CourseApplication.objects.all()
    serializer_class = CourseApplicationSerializer
    permission_classes = [permissions.IsAuthenticated] 