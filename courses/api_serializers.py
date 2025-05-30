from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Course, Desempeno, Region, Instructor, Question, Answer, Section, CourseApplication
from django.db.models import Q

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

class RegionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo Region.
    
    Incluye:
    - Información básica de la región
    - Lista de cursos aplicados con información relevante
    - Lista de instructores con información básica
    - Lista de técnicos con información básica
    - Conteos de cada tipo de elemento
    """
    courses = serializers.SerializerMethodField()
    instructors = serializers.SerializerMethodField()
    technicians = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Region
        fields = ['id', 'nombre', 'courses', 'instructors', 'technicians', 'stats']
    
    def get_courses(self, obj):
        courses = Course.objects.filter(
            Q(region=obj) | 
            Q(applications__region=obj)
        ).distinct()
        return [{
            'id': course.id,
            'name': course.name,
            'slug': course.slug,
            'description': course.description,
            'instructor': course.instructor.name if course.instructor else None,
            'duration_hours': course.duration_hours,
            'is_active': course.is_active
        } for course in courses]
    
    def get_instructors(self, obj):
        instructors = Instructor.objects.filter(region=obj)
        return [{
            'id': instructor.id,
            'name': instructor.name,
            'courses_count': instructor.courses_teaching.count()
        } for instructor in instructors]
    
    def get_technicians(self, obj):
        from users.models import Technician
        technicians = Technician.objects.filter(region=obj)
        return [{
            'id': t.id,
            'name': t.user.get_full_name(),
            'numero_empleado': t.numero_empleado,
            'is_active': t.is_active
        } for t in technicians]
    
    def get_stats(self, obj):
        from users.models import Technician
        courses = Course.objects.filter(
            Q(region=obj) | 
            Q(applications__region=obj)
        ).distinct()
        return {
            'courses_count': courses.count(),
            'instructors_count': obj.instructors.count(),
            'technicians_count': Technician.objects.filter(region=obj).count()
        }

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
    """
    course = CourseSerializer(read_only=True)
    instructor = InstructorSerializer(read_only=True)
    
    class Meta:
        model = Desempeno
        fields = [
            'id', 
            'technician', 
            'course',
            'instructor',
            'fecha',
            'duracion_total',
            'respuestas_incorrectas',
            'aprobado'
        ]

class DesempenoCreateSerializer(serializers.ModelSerializer):
    curso_slug = serializers.SlugField(write_only=True)
    numero_empleado = serializers.CharField(write_only=True)
    
    class Meta:
        model = Desempeno
        fields = [
            'numero_empleado',
            'curso_slug',
            'duracion_total',
            'respuestas_incorrectas',
            'aprobado'
        ]
        read_only_fields = ['instructor']

    def create(self, validated_data):
        # Obtener el curso usando el slug
        curso_slug = validated_data.pop('curso_slug')
        try:
            curso = Course.objects.get(slug=curso_slug)
        except Course.DoesNotExist:
            raise serializers.ValidationError({'curso_slug': 'No se encontró el curso con este slug'})

        # Obtener el técnico usando el número de empleado
        numero_empleado = validated_data.pop('numero_empleado')
        try:
            from users.models import Technician
            technician = Technician.objects.get(numero_empleado=numero_empleado)
        except Technician.DoesNotExist:
            raise serializers.ValidationError({'numero_empleado': 'No se encontró el técnico con este número de empleado'})

        # Crear el desempeño con los datos correctos
        return Desempeno.objects.create(
            technician=technician,
            course=curso,
            instructor=curso.instructor,
            **validated_data
        )

class DesempenoMetricsSerializer(serializers.Serializer):
    total_cursos_completados = serializers.IntegerField()
    cursos_aprobados = serializers.IntegerField()
    cursos_reprobados = serializers.IntegerField()
    total_respuestas_incorrectas = serializers.IntegerField()
    duracion_promedio = serializers.FloatField()
    
    # Métricas por instructor
    metricas_instructor = serializers.SerializerMethodField()
    
    # Métricas por curso
    metricas_curso = serializers.SerializerMethodField()
    
    # Métricas por técnico
    metricas_tecnico = serializers.SerializerMethodField()
    
    def get_metricas_instructor(self, obj):
        return {
            instructor.name: {
                'cursos_aprobados': obj['por_instructor'].get(instructor.id, {}).get('aprobados', 0),
                'cursos_reprobados': obj['por_instructor'].get(instructor.id, {}).get('reprobados', 0),
                'respuestas_incorrectas': obj['por_instructor'].get(instructor.id, {}).get('incorrectas', 0),
                'duracion_promedio': obj['por_instructor'].get(instructor.id, {}).get('duracion_promedio', 0)
            } for instructor in Instructor.objects.all()
        }
    
    def get_metricas_curso(self, obj):
        return {
            curso.name: {
                'aprobados': obj['por_curso'].get(curso.id, {}).get('aprobados', 0),
                'reprobados': obj['por_curso'].get(curso.id, {}).get('reprobados', 0),
                'respuestas_incorrectas': obj['por_curso'].get(curso.id, {}).get('incorrectas', 0),
                'duracion_promedio': obj['por_curso'].get(curso.id, {}).get('duracion_promedio', 0)
            } for curso in Course.objects.all()
        }
    
    def get_metricas_tecnico(self, obj):
        return {
            tecnico.user.get_full_name() or tecnico.user.username: {
                'cursos_aprobados': obj['por_tecnico'].get(tecnico.id, {}).get('aprobados', 0),
                'cursos_reprobados': obj['por_tecnico'].get(tecnico.id, {}).get('reprobados', 0),
                'respuestas_incorrectas': obj['por_tecnico'].get(tecnico.id, {}).get('incorrectas', 0),
                'duracion_promedio': obj['por_tecnico'].get(tecnico.id, {}).get('duracion_promedio', 0)
            } for tecnico in Technician.objects.all()
        }

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