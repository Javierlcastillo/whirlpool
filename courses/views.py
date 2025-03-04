from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.contrib import messages

from .models import Course, Question, Answer, FAQ
from .forms import CourseForm, QuestionForm, AnswerForm

@login_required
def dashboard(request):
    """Vista para el dashboard principal."""
    courses_count = Course.objects.count()
    context = {
        'courses_count': courses_count,
    }
    return render(request, 'dashboard.html', context)

class CourseListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los cursos."""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10

class CourseDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de un curso específico."""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir preguntas y respuestas al contexto
        context['questions'] = self.object.questions.all().prefetch_related('answers')
        return context

class CourseCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo curso."""
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Curso creado exitosamente')
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar un curso existente."""
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Curso actualizado exitosamente')
        return super().form_valid(form)

class CourseDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar un curso."""
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Curso eliminado exitosamente')
        return super().delete(request, *args, **kwargs)

@login_required
def add_questions(request, course_id):
    """Vista para añadir preguntas y respuestas a un curso."""
    course = get_object_or_404(Course, id=course_id)
    
    # Formset para preguntas y respuestas
    QuestionFormSet = inlineformset_factory(
        Course, 
        Question,
        form=QuestionForm, 
        extra=1, 
        can_delete=True
    )
    
    if request.method == 'POST':
        formset = QuestionFormSet(request.POST, request.FILES, instance=course)
        if formset.is_valid():
            questions = formset.save(commit=False)
            
            # Procesar cada pregunta y sus respuestas
            for question_form in formset:
                if question_form.cleaned_data and not question_form.cleaned_data.get('DELETE', False):
                    question = question_form.save(commit=False)
                    question.course = course
                    question.save()
                    
                    # Aquí iría la lógica para las respuestas
            
            formset.save()
            messages.success(request, 'Preguntas añadidas exitosamente')
            return redirect('course-detail', slug=course.slug)
    else:
        formset = QuestionFormSet(instance=course)
    
    return render(request, 'courses/add_questions.html', {
        'course': course,
        'formset': formset
    })

@login_required
def faq(request):
    """Vista para mostrar las preguntas frecuentes."""
    faqs = FAQ.objects.all()
    return render(request, 'faq.html', {'faqs': faqs})