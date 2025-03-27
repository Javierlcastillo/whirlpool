from rest_framework import serializers
from courses.models import Course, Section, Question, Answer, Region, Instructor, Desempeno
from users.models import Technician

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'nombre']

class InstructorSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'region']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'number', 'answer', 'is_correct', 'media']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.media:
            request = self.context.get('request')
            if request is not None:
                representation['media'] = request.build_absolute_uri(instance.media.url)
        return representation

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'number', 'text', 'type', 'media', 'answers']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.media:
            request = self.context.get('request')
            if request is not None:
                representation['media'] = request.build_absolute_uri(instance.media.url)
        return representation

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'title', 'text', 'order', 'image', 'video_url']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            request = self.context.get('request')
            if request is not None:
                representation['image'] = request.build_absolute_uri(instance.image.url)
        return representation

class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'slug', 'description', 'duration_weeks', 'category', 'instructor']

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