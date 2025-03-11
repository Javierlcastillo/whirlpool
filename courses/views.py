from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.contrib import messages

from .models import Course, Question, Answer, Region, Instructor, CourseApplication, Desempeno
from .forms import CourseForm, QuestionForm, AnswerForm, RegionForm, InstructorForm

@login_required
def dashboard(request):
    """Vista para el dashboard principal."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado. Solo administradores tienen permiso para acceder.")
        return redirect('login')
    
    courses_count = Course.objects.count()
    regions_count = Region.objects.count()
    instructors_count = Instructor.objects.count()
    
    context = {
        'courses_count': courses_count,
        'regions_count': regions_count,
        'instructors_count': instructors_count,
        'latest_courses': Course.objects.all().order_by('-created_at')[:5],
    }
    return render(request, 'dashboard.html', context)

class CourseListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los cursos."""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instructors'] = Instructor.objects.all()
        return context

class CourseDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de un curso específico."""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir preguntas y respuestas al contexto
        context['questions'] = self.object.questions.all().prefetch_related('answers')
        context['regions'] = Region.objects.filter(course_applications__course=self.object)
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

# Views for Region
class RegionListView(LoginRequiredMixin, ListView):
    """Vista para listar todas las regiones."""
    model = Region
    template_name = 'courses/region_list.html'
    context_object_name = 'regions'
    paginate_by = 10

class RegionDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de una región específica."""
    model = Region
    template_name = 'courses/region_detail.html'
    context_object_name = 'region'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir cursos aplicados a esta región
        context['courses'] = Course.objects.filter(applications__region=self.object)
        context['technicians'] = self.object.technicians.all()
        return context

class RegionCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear una nueva región."""
    model = Region
    form_class = RegionForm
    template_name = 'courses/region_form.html'
    success_url = reverse_lazy('region-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Región creada exitosamente')
        return super().form_valid(form)

class RegionUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar una región existente."""
    model = Region
    form_class = RegionForm
    template_name = 'courses/region_form.html'
    success_url = reverse_lazy('region-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Región actualizada exitosamente')
        return super().form_valid(form)

class RegionDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar una región."""
    model = Region
    template_name = 'courses/region_confirm_delete.html'
    success_url = reverse_lazy('region-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Región eliminada exitosamente')
        return super().delete(request, *args, **kwargs)

# Views for Instructor
class InstructorListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los instructores."""
    model = Instructor
    template_name = 'courses/instructor_list.html'
    context_object_name = 'instructors'
    paginate_by = 10

class InstructorDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de un instructor específico."""
    model = Instructor
    template_name = 'courses/instructor_detail.html'
    context_object_name = 'instructor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir cursos que imparte este instructor
        context['courses'] = self.object.courses_teaching.all()
        return context

class InstructorCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo instructor."""
    model = Instructor
    form_class = InstructorForm
    template_name = 'courses/instructor_form.html'
    success_url = reverse_lazy('instructor-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Instructor creado exitosamente')
        return super().form_valid(form)

class InstructorUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar un instructor existente."""
    model = Instructor
    form_class = InstructorForm
    template_name = 'courses/instructor_form.html'
    success_url = reverse_lazy('instructor-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Instructor actualizado exitosamente')
        return super().form_valid(form)

class InstructorDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar un instructor."""
    model = Instructor
    template_name = 'courses/instructor_confirm_delete.html'
    success_url = reverse_lazy('instructor-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Instructor eliminado exitosamente')
        return super().delete(request, *args, **kwargs)

@login_required
def add_questions(request, course_id):
    """Vista para añadir preguntas y respuestas a un curso."""
    course = get_object_or_404(Course, id=course_id)
    
    # Formset para preguntas
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
            
            # Procesar cada pregunta
            for question_form in formset:
                if question_form.cleaned_data and not question_form.cleaned_data.get('DELETE', False):
                    question = question_form.save(commit=False)
                    question.course = course
                    question.save()
            
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
def add_answers(request, question_id):
    """Vista para añadir respuestas a una pregunta."""
    question = get_object_or_404(Question, id=question_id)
    course = question.course
    
    # Formset para respuestas
    AnswerFormSet = inlineformset_factory(
        Question, 
        Answer,
        form=AnswerForm, 
        extra=1, 
        can_delete=True
    )
    
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST, request.FILES, instance=question)
        if formset.is_valid():
            answers = formset.save(commit=False)
            
            # Procesar cada respuesta
            for answer_form in formset:
                if answer_form.cleaned_data and not answer_form.cleaned_data.get('DELETE', False):
                    answer = answer_form.save(commit=False)
                    answer.question = question
                    answer.course = course
                    answer.save()
            
            formset.save()
            messages.success(request, 'Respuestas añadidas exitosamente')
            return redirect('course-detail', slug=course.slug)
    else:
        formset = AnswerFormSet(instance=question)
    
    return render(request, 'courses/add_answers.html', {
        'question': question,
        'course': course,
        'formset': formset
    })