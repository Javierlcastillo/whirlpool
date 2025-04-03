from rest_framework import serializers
from courses.models import Course, Section, Question, Answer, Region, Instructor, Desempeno, CourseApplication
from users.models import Technician

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']

class InstructorSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'email', 'phone', 'region', 'created_at', 'updated_at']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'answer', 'is_correct', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'course', 'text', 'type', 'answers', 'created_at', 'updated_at']

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'course', 'title', 'content', 'order', 'created_at', 'updated_at']

class CourseSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'slug', 'description', 'instructor', 'region',
            'duration_hours', 'questions', 'sections', 'created_at', 'updated_at'
        ]

class CourseApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseApplication
        fields = ['id', 'course', 'region', 'status', 'created_at', 'updated_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseApplication
        fields = ['id', 'course', 'region', 'status', 'created_at', 'updated_at']

class CourseDetailSerializer(CourseSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['sections', 'questions']

class DesempenoSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Desempeno
        fields = ['id', 'course', 'puntuacion', 'fecha', 'estado']

class TechnicianSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = Technician
        fields = ['id', 'employee_number', 'name', 'region']
        
class TechnicianDetailSerializer(TechnicianSerializer):
    desempenos = DesempenoSerializer(many=True, read_only=True)
    
    class Meta(TechnicianSerializer.Meta):
        fields = TechnicianSerializer.Meta.fields + ['desempenos']