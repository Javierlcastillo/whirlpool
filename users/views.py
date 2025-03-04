from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Technician
from .forms import TechnicianForm, UserForm, CustomAuthenticationForm

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
    next_page = 'login'

class TechnicianListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los técnicos."""
    model = Technician
    template_name = 'users/technician_list.html'
    context_object_name = 'technicians'
    paginate_by = 10

class TechnicianDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de un técnico específico."""
    model = Technician
    template_name = 'users/technician_detail.html'
    context_object_name = 'technician'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir cursos que imparte el técnico
        context['courses_teaching'] = self.object.courses_teaching.all()
        return context

class TechnicianCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo técnico."""
    model = Technician
    template_name = 'users/technician_form.html'
    form_class = TechnicianForm
    second_form_class = UserForm
    success_url = reverse_lazy('technician-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class()
        if 'user_form' not in context:
            context['user_form'] = self.second_form_class()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.form_class(request.POST)
        user_form = self.second_form_class(request.POST)
        
        if form.is_valid() and user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            technician = form.save(commit=False)
            technician.user = user
            technician.save()
            
            messages.success(request, 'Técnico creado exitosamente')
            return redirect(self.success_url)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, user_form=user_form)
            )

class TechnicianUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar un técnico existente."""
    model = Technician
    template_name = 'users/technician_form.html'
    form_class = TechnicianForm
    success_url = reverse_lazy('technician-list')
    
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
            user = user_form.save()
            technician = form.save()
            
            messages.success(request, 'Técnico actualizado exitosamente')
            return redirect(self.success_url)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, user_form=user_form)
            )

class TechnicianDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar un técnico."""
    model = Technician
    template_name = 'users/technician_confirm_delete.html'
    success_url = reverse_lazy('technician-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Técnico eliminado exitosamente')
        return super().delete(request, *args, **kwargs)