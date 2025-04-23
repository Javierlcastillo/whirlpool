from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Fieldset, Field

from .models import Course, Section, Question, Answer, Region, Instructor, CourseApplication, Desempeno

User = get_user_model()

class CourseForm(forms.ModelForm):
    """Formulario para crear/editar cursos."""
    
    class Meta:
        model = Course
        fields = ['name', 'description', 'instructor', 'region', 'duration_hours']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'instructor': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'instructor': 'Instructor',
            'region': 'Región',
            'duration_hours': 'Duración (horas)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Información del Curso',
                Row(
                    Column('name', css_class='col-md-12'),
                ),
                Row(
                    Column('instructor', css_class='col-md-4'),
                    Column('region', css_class='col-md-4'),
                    Column('duration_hours', css_class='col-md-4'),
                ),
                Row(
                    Column('description', css_class='col-md-12'),
                ),
            ),
        )
        
        # Hacer que todos los campos tengan el estilo adecuado
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:
                field.widget.attrs['class'] = 'form-control'
                
        # Asegurarse de que los campos select tengan la clase correcta
        for field_name in ['instructor', 'region']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'form-select'
        
        # Personalizar el queryset del campo instructor
        if 'instructor' in self.fields:
            self.fields['instructor'].queryset = Instructor.objects.all().order_by('name')
            self.fields['instructor'].label_from_instance = lambda obj: f"{obj.name}"

class SectionForm(forms.ModelForm):
    """Formulario para crear/editar secciones."""
    
    class Meta:
        model = Section
        fields = ['title', 'content', 'media']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la sección'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Contenido de la sección'
            }),
            'media': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'title': 'Título',
            'content': 'Contenido',
            'media': 'Medio (imagen, documento)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Información de la Sección',
                Row(
                    Column('title', css_class='col-md-12'),
                ),
                Row(
                    Column('content', css_class='col-md-12'),
                ),
                Row(
                    Column('media', css_class='col-md-12'),
                ),
            ),
        )
        
        # Hacer que todos los campos tengan el estilo adecuado
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:
                field.widget.attrs['class'] = 'form-control'

class AnswerForm(forms.ModelForm):
    """Formulario para crear/editar respuestas."""
    
    class Meta:
        model = Answer
        fields = ['answer', 'is_correct']
        widgets = {
            'answer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Escriba la respuesta aquí'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'answer': '',
            'is_correct': 'Respuesta correcta',
        }

class QuestionForm(forms.ModelForm):
    """Formulario para crear/editar preguntas."""
    
    class Meta:
        model = Question
        fields = ['text', 'type']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escriba la pregunta aquí'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'text': 'Pregunta',
            'type': 'Tipo de pregunta',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Información de la Pregunta',
                Row(
                    Column('text', css_class='col-md-12'),
                ),
                Row(
                    Column('type', css_class='col-md-6'),
                ),
            ),
        )
        
        # Hacer que todos los campos tengan el estilo adecuado
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:
                field.widget.attrs['class'] = 'form-control'
                
        # Asegurarse de que los campos select tengan la clase correcta
        if 'type' in self.fields:
            self.fields['type'].widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('type')
        
        if question_type == 'true_false':
            # Asegurarse de que las preguntas verdadero/falso tengan exactamente dos respuestas
            if hasattr(self.instance, 'answers'):
                answers = self.instance.answers.all()
                if answers.count() > 2:
                    raise ValidationError('Las preguntas de verdadero/falso solo pueden tener dos respuestas.')
                if answers.count() == 2:
                    true_count = answers.filter(is_correct=True).count()
                    if true_count != 1:
                        raise ValidationError('Las preguntas de verdadero/falso deben tener exactamente una respuesta verdadera.')
        
        return cleaned_data

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