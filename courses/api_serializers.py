from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Course, Desempeno, Region, Instructor, Question, Answer, Section, CourseApplication

class RegionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Region.
    
    Campos:
    - id: Identificador único de la región
    - nombre: Nombre de la región
    """
    class Meta:
        model = Region
        fields = ['id', 'nombre']

class InstructorSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Instructor.
    
    Campos:
    - id: Identificador único del instructor
    - name: Nombre del instructor
    - region: Información de la región asociada
    """
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'region']

class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Answer.
    
    Campos:
    - id: Identificador único de la respuesta
    - question: ID de la pregunta asociada
    - course: ID del curso asociado
    - number: Número de la respuesta
    - answer: Texto de la respuesta
    - media: URL del archivo multimedia (si existe)
    - is_correct: Indica si la respuesta es correcta
    """
    media = serializers.SerializerMethodField()
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'course', 'number', 'answer', 'media', 'is_correct']
    
    def get_media(self, obj):
        if obj.media:
            return self.context['request'].build_absolute_uri(obj.media.url)
        return None

class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Question.
    
    Campos:
    - id: Identificador único de la pregunta
    - course: ID del curso asociado
    - text: Texto de la pregunta
    - type: Tipo de pregunta (multiple_choice o true_false)
    - answers: Lista de respuestas asociadas
    """
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'course', 'text', 'type', 'answers']

class SectionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Section.
    
    Campos:
    - id: Identificador único de la sección
    - course: ID del curso asociado
    - title: Título de la sección
    - content: Contenido de la sección
    - media: URL del archivo multimedia (si existe)
    """
    media = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = ['id', 'course', 'title', 'content', 'media']
    
    def get_media(self, obj):
        if obj.media:
            return self.context['request'].build_absolute_uri(obj.media.url)
        return None

class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Course.
    
    Campos:
    - id: Identificador único del curso
    - name: Nombre del curso
    - slug: Slug único para URLs
    - description: Descripción del curso
    - instructor: Información del instructor
    - region: Información de la región
    - duration_hours: Duración en horas
    - is_active: Indica si el curso está activo
    """
    instructor = InstructorSerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'slug', 'description', 'instructor', 'region',
            'duration_hours', 'is_active', 'created_at', 'updated_at'
        ]

class CourseApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo CourseApplication.
    
    Campos:
    - id: Identificador único de la aplicación
    - course: ID del curso asociado
    - region: ID de la región asociada
    """
    class Meta:
        model = CourseApplication
        fields = ['id', 'course', 'region']

class CourseDetailSerializer(CourseSerializer):
    """
    Serializer detallado para el modelo Course.
    Incluye información adicional como secciones y preguntas.
    
    Hereda todos los campos de CourseSerializer y agrega:
    - sections: Lista de secciones del curso
    - questions: Lista de preguntas del curso
    """
    sections = SectionSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['sections', 'questions']

class DesempenoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Desempeno.
    
    Campos:
    - id: Identificador único del desempeño
    - course: Información del curso asociado
    - technician: ID del técnico asociado
    - puntuacion: Puntuación obtenida
    - fecha: Fecha del desempeño
    - estado: Estado del desempeño (started, in_progress, completed, failed)
    """
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Desempeno
        fields = ['id', 'course', 'technician', 'puntuacion', 'fecha', 'estado']

class CourseCompleteSerializer(CourseSerializer):
    """
    Serializer para obtener la estructura completa de un curso con sus secciones y preguntas
    combinadas en una sola lista ordenada por el campo 'order'.
    
    Incluye:
    - Información básica del curso
    - Contenido: Lista combinada de secciones y preguntas ordenadas por 'order'
      - Cada elemento tiene un campo 'type' que indica:
        - 'section': Para secciones
        - 'multiple_choice' o 'true_false': Para preguntas según su tipo
    """
    content = serializers.SerializerMethodField()
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['content']
    
    def get_content(self, instance):
        # Obtener todas las secciones y preguntas del curso
        sections = instance.sections.all()
        questions = instance.questions.all()
        
        # Obtener el orden de cada elemento
        content_order = instance.content_order.all()
        
        # Crear un diccionario para mapear IDs a órdenes
        order_map = {item.content_id: item.order for item in content_order}
        
        # Combinar y ordenar el contenido
        combined_content = []
        
        # Agregar secciones
        for section in sections:
            combined_content.append({
                'type': 'section',
                'id': section.id,
                'order': order_map.get(section.id, 0),
                'title': section.title,
                'content': section.content,
                'media': section.media.url if section.media else None
            })
        
        # Agregar preguntas
        for question in questions:
            combined_content.append({
                'type': question.type,
                'id': question.id,
                'order': order_map.get(question.id, 0),
                'text': question.text,
                'answers': [
                    {
                        'id': answer.id,
                        'number': answer.number,
                        'answer': answer.answer,
                        'media': answer.media.url if answer.media else None,
                        'is_correct': answer.is_correct
                    }
                    for answer in question.answers.all()
                ]
            })
        
        # Ordenar por el campo 'order'
        combined_content.sort(key=lambda x: x['order'])
        
        return combined_content 