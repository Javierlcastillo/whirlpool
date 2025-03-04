from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML

from .models import Technician

class CustomAuthenticationForm(AuthenticationForm):
    """Formulario personalizado de autenticación."""
    username = UsernameField(
        label='Número de Empleado',
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Número de Empleado'})
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'login-form'
        self.helper.layout = Layout(
            'username',
            'password',
            Div(
                Submit('submit', 'Ingresar', css_class='btn-whirlpool btn-lg w-100'),
                css_class='d-grid'
            )
        )

class UserForm(forms.ModelForm):
    """Formulario para gestionar usuarios (parte de Django auth)."""
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data

class TechnicianForm(forms.ModelForm):
    """Formulario para técnicos (extensión de User)."""
    
    class Meta:
        model = Technician
        fields = ['employee_number', 'region']
        widgets = {
            'employee_number': forms.TextInput(attrs={'placeholder': 'Número de Empleado'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Row(
                Column('employee_number', css_class='form-group col-md-6 mb-0'),
                Column('region', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url \'technician-list\' %}" class="btn btn-secondary">Cancelar</a>'),
                css_class='text-right'
            )
        )