from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML

from .models import Course, Section, Question, Answer, Region, Instructor, CourseApplication, Desempeno

class CourseForm(forms.ModelForm):
    """Formulario para crear/editar cursos."""
    
    class Meta:
        model = Course
        fields = ['name', 'description', 'instructor', 'region', 'duration_weeks', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del curso'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Descripción del curso'}),
            'duration_weeks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 52}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'name': 'Nombre del Curso',
            'description': 'Descripción',
            'instructor': 'Instructor',
            'region': 'Región',
            'duration_weeks': 'Duración (semanas)',
            'category': 'Categoría'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que todos los campos tengan el estilo adecuado
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:
                field.widget.attrs['class'] = 'form-control'
                
        # Asegurarse de que los campos select tengan la clase correcta
        for field_name in ['instructor', 'region', 'category']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'form-select'

class SectionForm(forms.ModelForm):
    """Formulario para crear/editar secciones informativas."""
    
    class Meta:
        model = Section
        fields = ['title', 'text', 'image', 'video_url', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

class QuestionForm(forms.ModelForm):
    """Formulario para crear/editar preguntas."""
    
    class Meta:
        model = Question
        fields = ['number', 'text', 'media', 'type']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

class AnswerForm(forms.ModelForm):
    """Formulario para crear/editar respuestas."""
    
    class Meta:
        model = Answer
        fields = ['number', 'answer', 'media', 'is_correct']
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 2}),
        }

class RegionForm(forms.ModelForm):
    """Formulario para crear/editar regiones."""
    
    class Meta:
        model = Region
        fields = ['nombre']

class InstructorForm(forms.ModelForm):
    """Formulario para crear/editar instructores."""
    
    class Meta:
        model = Instructor
        fields = ['name', 'region']

class CourseApplicationForm(forms.ModelForm):
    """Formulario para crear/editar aplicaciones de cursos."""
    
    class Meta:
        model = CourseApplication
        fields = ['course', 'region']

class DesempenoForm(forms.ModelForm):
    """Formulario para crear/editar desempeños."""
    
    class Meta:
        model = Desempeno
        fields = ['technician', 'course', 'puntuacion', 'estado']