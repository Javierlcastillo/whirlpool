from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML

from .models import Course, Question, Answer

class CourseForm(forms.ModelForm):
    """Formulario para crear/editar cursos."""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'instructor', 'duration_weeks', 'category']
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
                Column('title', css_class='form-group col-md-8 mb-0'),
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

class QuestionForm(forms.ModelForm):
    """Formulario para crear/editar preguntas."""
    
    class Meta:
        model = Question
        fields = ['text', 'image', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2}),
        }

class AnswerForm(forms.ModelForm):
    """Formulario para crear/editar respuestas."""
    
    class Meta:
        model = Answer
        fields = ['text', 'image', 'is_correct']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2}),
        }

class AnswerInlineFormSet(forms.BaseInlineFormSet):
    """Formset para manejar múltiples respuestas para una pregunta."""
    
    def clean(self):
        """Validar que haya al menos una respuesta correcta por pregunta."""
        super().clean()
        has_correct_answer = False
        
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_correct_answer = True
                    break
        
        if not has_correct_answer:
            raise forms.ValidationError('Debe haber al menos una respuesta correcta.')