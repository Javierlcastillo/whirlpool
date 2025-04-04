from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML

from .models import Technician
from courses.models import Region

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
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Contraseña')
    numero_empleado = forms.CharField(max_length=20, required=True, label='Número de empleado')
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=True,
        label='Región'
    )

    class Meta:
        model = Technician
        fields = ['numero_empleado', 'region']

    def save(self, commit=True):
        technician = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['numero_empleado'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        technician.user = user
        if commit:
            technician.save()
        return technician
