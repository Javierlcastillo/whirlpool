from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    TemplateView
)
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.db.models import Q

from .models import Technician
from .forms import TechnicianForm, UserForm, CustomAuthenticationForm

# Crear el mixin para restricción a superusuarios
class SuperuserRequiredMixin:
    """Mixin que restringe el acceso solo a superusuarios."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, "Acceso denegado. Solo administradores tienen permiso para acceder.")
            return redirect('users:login')
        return super().dispatch(request, *args, **kwargs)

class CustomLoginView(LoginView):
    """Vista personalizada para login."""
    template_name = 'users/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, f'Bienvenido, {form.get_user().get_full_name()}')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """Vista personalizada para logout."""
    next_page = 'users:login'

class TechnicianListView(SuperuserRequiredMixin, ListView):
    """Vista para listar todos los técnicos."""
    model = Technician
    template_name = 'users/technician_list.html'
    context_object_name = 'technicians'
    paginate_by = 10

class TechnicianDetailView(SuperuserRequiredMixin, DetailView):
    """Vista para ver detalles de un técnico específico."""
    model = Technician
    template_name = 'users/technician_detail.html'
    context_object_name = 'technician'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener los cursos disponibles en la región del técnico
        if self.object.region:
            context['available_courses'] = self.object.region.courses.all()
        else:
            context['available_courses'] = []
        return context

class TechnicianCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo técnico."""
    model = Technician
    form_class = TechnicianForm
    template_name = 'users/technician_form.html'
    success_url = reverse_lazy('users:technician-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nuevo Técnico'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Técnico creado exitosamente')
        return response

class TechnicianUpdateView(SuperuserRequiredMixin, UpdateView):
    """Vista para actualizar un técnico existente."""
    model = Technician
    template_name = 'users/technician_form.html'
    form_class = TechnicianForm
    success_url = reverse_lazy('users:technician-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(instance=self.object)
        if 'user_form' not in context:
            context['user_form'] = UserForm(instance=self.object.user)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        user_form = UserForm(request.POST, instance=self.object.user)
        
        if form.is_valid() and user_form.is_valid():
            user = user_form.save(commit=False)
            
            # Actualizar el nombre de usuario si el número de empleado ha cambiado
            employee_number = form.cleaned_data.get('employee_number')
            if employee_number != self.object.employee_number:
                user.username = employee_number
            
            # Mantener al técnico sin privilegios de superusuario
            user.is_superuser = False
            user.is_staff = False
            user.save()
            
            technician = form.save()
            
            messages.success(request, 'Técnico actualizado exitosamente')
            return redirect(self.success_url)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, user_form=user_form)
            )

class TechnicianDeleteView(SuperuserRequiredMixin, DeleteView):
    """Vista para eliminar un técnico."""
    model = Technician
    template_name = 'users/technician_confirm_delete.html'
    success_url = reverse_lazy('users:technician-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Técnico eliminado exitosamente')
        return super().delete(request, *args, **kwargs)