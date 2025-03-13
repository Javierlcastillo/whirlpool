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
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-8 mb-0'),
                Column('category', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('instructor', css_class='form-group col-md-6 mb-0'),
                Column('duration_weeks', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url \'course-list\' %}" class="btn btn-secondary">Cancelar</a>'),
                css_class='text-right'
            )
        )

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