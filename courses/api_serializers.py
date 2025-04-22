from rest_framework import serializers
from .models import Course, Section, Question, Answer, Region, Instructor, Desempeno, CourseApplication
from users.models import Technician
from django.contrib.auth import authenticate

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
        """Obtiene la URL del archivo multimedia si existe, o None si no existe."""
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
    - order: Orden de la pregunta en el curso
    - answers: Lista de respuestas asociadas
    """
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'course', 'text', 'type', 'order', 'answers']

class SectionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Section.
    
    Campos:
    - id: Identificador único de la sección
    - course: ID del curso asociado
    - title: Título de la sección
    - content: Contenido de la sección
    - media: URL del archivo multimedia (si existe)
    - order: Orden de la sección en el curso
    """
    media = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = ['id', 'course', 'title', 'content', 'media', 'order']
    
    def get_media(self, obj):
        """Obtiene la URL del archivo multimedia si existe, o None si no existe."""
        if obj.media:
            return self.context['request'].build_absolute_uri(obj.media.url)
        return None

class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Course.
    
    Campos:
    - id: Identificador único del curso
    - name: Nombre del curso
    - slug: Slug único del curso
    - description: Descripción del curso
    - instructor: ID del instructor asociado
    - region: ID de la región asociada
    - duration_hours: Duración del curso en horas
    - is_active: Indica si el curso está activo
    """
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'slug', 'description', 'instructor', 'region',
            'duration_hours', 'is_active'
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

class TechnicianSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Technician.
    
    Campos:
    - id: Identificador único del técnico
    - numero_empleado: Número de empleado único
    - name: Nombre del técnico
    - region: Información de la región asociada
    - is_active: Indica si el técnico está activo
    - created_at: Fecha de creación
    - updated_at: Fecha de última actualización
    """
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = Technician
        fields = ['id', 'numero_empleado', 'name', 'region', 'is_active', 'created_at', 'updated_at']
        
class TechnicianDetailSerializer(TechnicianSerializer):
    """
    Serializer detallado para el modelo Technician.
    Incluye información adicional como desempeños.
    
    Hereda todos los campos de TechnicianSerializer y agrega:
    - desempenos: Lista de desempeños del técnico
    """
    desempenos = DesempenoSerializer(many=True, read_only=True)
    
    class Meta(TechnicianSerializer.Meta):
        fields = TechnicianSerializer.Meta.fields + ['desempenos']

class TechnicianAuthSerializer(serializers.Serializer):
    """
    Serializer para la autenticación de técnicos.
    Recibe numero_empleado y password, y valida la autenticación.
    
    Campos:
    - numero_empleado: Número de empleado del técnico
    - password: Contraseña del técnico
    """
    numero_empleado = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, data):
        numero_empleado = data.get('numero_empleado')
        password = data.get('password')
        
        if numero_empleado and password:
            # Autenticar usando el número de empleado como username
            user = authenticate(username=numero_empleado, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Usuario desactivado.')
                
                # Verificar que el usuario es un técnico
                try:
                    technician = Technician.objects.get(user=user)
                    if not technician.is_active:
                        raise serializers.ValidationError('Este técnico está desactivado.')
                    
                    # Añadir los datos del técnico a los datos validados
                    data['technician'] = technician
                    return data
                except Technician.DoesNotExist:
                    raise serializers.ValidationError('Este usuario no es un técnico registrado.')
            else:
                raise serializers.ValidationError('Credenciales incorrectas.')
        else:
            raise serializers.ValidationError('Debe proporcionar número de empleado y contraseña.') 