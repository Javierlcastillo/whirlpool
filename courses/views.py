from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.db.models import Q
from django.urls import reverse_lazy

from .models import Course, Question, Answer, Region, Instructor, CourseApplication, Section
from .forms import CourseForm, QuestionForm, SectionForm, RegionForm, InstructorForm
from users.models import Technician
from courses.models import Desempeno

# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        print(f"[DEBUG] CourseListView.dispatch - User authenticated: {request.user.is_authenticated}")
        if not request.user.is_authenticated:
            print("[DEBUG] CourseListView.dispatch - User not authenticated, redirecting to login")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        print("[DEBUG] CourseListView.get_queryset - Starting")
        queryset = Course.objects.all().select_related('instructor', 'region')
        print(f"[DEBUG] CourseListView.get_queryset - Initial queryset count: {queryset.count()}")
        
        # Filtrar por región si se especifica
        region_slug = self.request.GET.get('region')
        if region_slug:
            print(f"[DEBUG] CourseListView.get_queryset - Filtering by region: {region_slug}")
            queryset = queryset.filter(region__slug=region_slug)
            
        # Filtrar por búsqueda si se especifica
        search_query = self.request.GET.get('search')
        if search_query:
            print(f"[DEBUG] CourseListView.get_queryset - Filtering by search: {search_query}")
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(instructor__name__icontains=search_query)
            )
            
        print(f"[DEBUG] CourseListView.get_queryset - Final queryset count: {queryset.count()}")
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        print("[DEBUG] CourseListView.get_context_data - Starting")
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las regiones para el filtro
        context['regions'] = Region.objects.all()
        print(f"[DEBUG] CourseListView.get_context_data - Regions count: {context['regions'].count()}")
        
        # Obtener la región actual si se está filtrando
        region_slug = self.request.GET.get('region')
        if region_slug:
            print(f"[DEBUG] CourseListView.get_context_data - Current region: {region_slug}")
            context['current_region'] = Region.objects.filter(slug=region_slug).first()
            
        # Obtener la búsqueda actual
        context['search_query'] = self.request.GET.get('search', '')
        print(f"[DEBUG] CourseListView.get_context_data - Search query: {context['search_query']}")
            
        return context

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Obtener preguntas y respuestas
        questions = Question.objects.filter(course=course).prefetch_related('answers')
        context['questions'] = questions
        
        # Obtener secciones
        sections = Section.objects.filter(course=course).order_by('order')
        context['sections'] = sections
        
        # Obtener aplicaciones del curso a regiones
        context['regions'] = CourseApplication.objects.filter(course=course)
        
        # Para propósitos del template, listar todas las regiones disponibles
        context['all_regions'] = Region.objects.all()
        
        # Verificar si el curso está disponible para el técnico basado en su región
        if hasattr(self.request.user, 'technician'):
            try:
                technician = self.request.user.technician
                # Verificar si el curso está disponible en la región del técnico
                context['is_available'] = CourseApplication.objects.filter(
                    course=course, region=technician.region
                ).exists()
                
                # Obtener el desempeño si existe
                try:
                    desempeno = Desempeno.objects.get(
                        course=course, technician=technician
                    )
                    context['progress'] = desempeno
                except Desempeno.DoesNotExist:
                    pass
                
            except Technician.DoesNotExist:
                context['is_available'] = False
        else:
            context['is_available'] = False
        
        return context

class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('courses:course-list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

@login_required
def enroll_course(request, slug):
    """
    Vista para verificar si un técnico tiene acceso a un curso basado en su región.
    Los técnicos automáticamente tienen acceso a cursos disponibles en su región.
    """
    course = get_object_or_404(Course, slug=slug)
    technician = get_object_or_404(Technician, user=request.user)
    
    # Verificar si el curso está disponible en la región del técnico
    if not CourseApplication.objects.filter(course=course, region=technician.region).exists():
        messages.warning(request, "Este curso no está disponible en tu región.")
        return redirect('courses:course-detail', slug=slug)
    
    # Crear o actualizar el registro de desempeño para seguimiento
    desempeno, created = Desempeno.objects.get_or_create(
        course=course,
        technician=technician,
        defaults={'estado': 'started'}
    )
    
    if created:
        messages.success(request, f"Has comenzado el curso {course.name}")
    else:
        messages.info(request, f"Ya tienes acceso al curso {course.name}")
        
    return redirect('courses:course-detail', slug=slug)

@login_required
def complete_section(request, slug, section_id):
    """Vista para marcar una sección como completada."""
    course = get_object_or_404(Course, slug=slug)
    section = get_object_or_404(Section, id=section_id, course=course)
    
    # Verificar si el usuario está inscrito
    enrollment = course.enrollments.filter(user=request.user).first()
    if not enrollment:
        messages.error(request, "Debes estar inscrito en el curso para completar secciones.")
        return redirect('courses:course-detail', slug=slug)
    
    # Marcar la sección como completada
    enrollment.completed_sections.add(section)
    messages.success(request, f"Sección '{section.title}' marcada como completada.")
    return redirect('courses:course-detail', slug=slug)

@login_required
def complete_question(request, slug, question_id):
    """Vista para marcar una pregunta como completada."""
    course = get_object_or_404(Course, slug=slug)
    question = get_object_or_404(Question, id=question_id, course=course)
    
    # Verificar si el usuario está inscrito
    enrollment = course.enrollments.filter(user=request.user).first()
    if not enrollment:
        messages.error(request, "Debes estar inscrito en el curso para completar preguntas.")
        return redirect('courses:course-detail', slug=slug)
    
    # Marcar la pregunta como completada
    enrollment.completed_questions.add(question)
    messages.success(request, f"Pregunta completada correctamente.")
    return redirect('courses:course-detail', slug=slug)

@login_required
def course_progress(request, slug):
    """Vista para mostrar el progreso del curso."""
    course = get_object_or_404(Course, slug=slug)
    enrollment = course.enrollments.filter(user=request.user).first()
    
    if not enrollment:
        messages.error(request, "Debes estar inscrito en el curso para ver tu progreso.")
        return redirect('courses:course-detail', slug=slug)
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'completed_sections': enrollment.completed_sections.all(),
        'completed_questions': enrollment.completed_questions.all(),
    }
    return render(request, 'courses/progress.html', context)

@login_required
def course_certificate(request, slug):
    """Vista para generar el certificado del curso."""
    course = get_object_or_404(Course, slug=slug)
    enrollment = course.enrollments.filter(user=request.user).first()
    
    if not enrollment:
        messages.error(request, "Debes estar inscrito en el curso para obtener el certificado.")
        return redirect('courses:course-detail', slug=slug)
    
    # Verificar si el curso está completado
    if not enrollment.is_completed:
        messages.warning(request, "Debes completar el curso para obtener el certificado.")
        return redirect('courses:course-detail', slug=slug)
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'user': request.user,
    }
    return render(request, 'courses/certificate.html', context)

@login_required
def manage_course(request, slug=None):
    """Vista para crear o editar un curso."""
    # Verificar si el usuario es superusuario
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    # Si es una solicitud GET, redirigir a la vista de edición básica
    if request.method == 'GET':
        if slug:
            return redirect('courses:course-edit', slug=slug)
        else:
            return redirect('courses:course-create')
    
    # Si es una solicitud POST, procesar el formulario
    course = None
    if slug:
        course = get_object_or_404(Course, slug=slug)
    
    form = CourseForm(request.POST, instance=course)
    if form.is_valid():
        course = form.save()
        messages.success(request, 'Información básica del curso guardada exitosamente.')
        return redirect('courses:course-edit-sections', slug=course.slug)
    else:
        messages.error(request, 'Error al guardar la información del curso.')
        return redirect('courses:course-edit', slug=slug) if slug else redirect('courses:course-create')

# Region Views
class RegionListView(LoginRequiredMixin, ListView):
    model = Region
    template_name = 'courses/region_list.html'
    context_object_name = 'regions'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Region.objects.all()
        
        # Buscar por nombre si se especifica
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(nombre__icontains=search_query)
            
        return queryset.order_by('nombre')

class RegionDetailView(LoginRequiredMixin, DetailView):
    model = Region
    template_name = 'courses/region_detail.html'
    context_object_name = 'region'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        region = self.get_object()
        
        # Obtener técnicos de la región
        context['technicians'] = Technician.objects.filter(region=region)
        
        # Obtener cursos aplicados a la región
        context['courses'] = Course.objects.filter(
            Q(region=region) | 
            Q(applications__region=region)
        ).distinct()
        
        # Obtener instructores de la región
        context['instructors'] = Instructor.objects.filter(region=region)
        
        return context

class RegionCreateView(LoginRequiredMixin, CreateView):
    model = Region
    form_class = RegionForm
    template_name = 'courses/region_form.html'
    success_url = reverse_lazy('courses:region-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Región creada exitosamente')
        return super().form_valid(form)

class RegionUpdateView(LoginRequiredMixin, UpdateView):
    model = Region
    form_class = RegionForm
    template_name = 'courses/region_form.html'
    success_url = reverse_lazy('courses:region-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Región actualizada exitosamente')
        return super().form_valid(form)

class RegionDeleteView(LoginRequiredMixin, DeleteView):
    model = Region
    template_name = 'courses/region_confirm_delete.html'
    success_url = reverse_lazy('courses:region-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Región eliminada exitosamente')
        return super().delete(request, *args, **kwargs)

# Instructor Views
class InstructorListView(LoginRequiredMixin, ListView):
    model = Instructor
    template_name = 'courses/instructor_list.html'
    context_object_name = 'instructors'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Instructor.objects.all()
        
        # Buscar por nombre si se especifica
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
            
        return queryset.order_by('name')

class InstructorDetailView(LoginRequiredMixin, DetailView):
    model = Instructor
    template_name = 'courses/instructor_detail.html'
    context_object_name = 'instructor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instructor = self.get_object()
        
        # Obtener cursos que imparte este instructor
        context['courses'] = Course.objects.filter(instructor=instructor)
        
        return context

class InstructorCreateView(LoginRequiredMixin, CreateView):
    model = Instructor
    form_class = InstructorForm
    template_name = 'courses/instructor_form.html'
    success_url = reverse_lazy('courses:instructor-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Instructor creado exitosamente')
        return super().form_valid(form)

class InstructorUpdateView(LoginRequiredMixin, UpdateView):
    model = Instructor
    form_class = InstructorForm
    template_name = 'courses/instructor_form.html'
    success_url = reverse_lazy('courses:instructor-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Instructor actualizado exitosamente')
        return super().form_valid(form)

class InstructorDeleteView(LoginRequiredMixin, DeleteView):
    model = Instructor
    template_name = 'courses/instructor_confirm_delete.html'
    success_url = reverse_lazy('courses:instructor-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Instructor eliminado exitosamente')
        return super().delete(request, *args, **kwargs)

# Course Region Management
@login_required
def add_region_to_course(request, slug):
    """Agrega una región a un curso."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado. Solo administradores tienen permiso para acceder.")
        return redirect('login')
    
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        region_id = request.POST.get('region')
        if region_id:
            region = get_object_or_404(Region, id=region_id)
            CourseApplication.objects.get_or_create(course=course, region=region)
            messages.success(request, f'Región {region.name} agregada al curso exitosamente.')
        else:
            messages.error(request, 'Debe seleccionar una región válida.')
    
    return redirect('courses:course-detail', slug=slug)

@login_required
def remove_region_from_course(request, slug, region_id):
    """Elimina una región de un curso."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado. Solo administradores tienen permiso para acceder.")
        return redirect('login')
    
    course = get_object_or_404(Course, slug=slug)
    region = get_object_or_404(Region, id=region_id)
    
    try:
        application = CourseApplication.objects.get(course=course, region=region)
        application.delete()
        messages.success(request, f'Región {region.name} eliminada del curso exitosamente.')
    except CourseApplication.DoesNotExist:
        messages.error(request, 'La región no está asociada a este curso.')
    
    return redirect('courses:course-detail', slug=slug)

@login_required
def course_base_edit(request, slug=None):
    """Vista para editar información básica del curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = None
    if slug:
        course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, 'Información del curso guardada exitosamente.')
            return redirect('courses:course-edit-sections', slug=course.slug)
        else:
            messages.error(request, 'Error al guardar la información del curso.')
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form,
        'course': course,
        'is_new': course is None
    }
    return render(request, 'courses/course_edit_basic.html', context)

@login_required
def course_sections_edit(request, slug):
    """Vista para gestionar las secciones del curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    sections = Section.objects.filter(course=course).order_by('order')
    
    context = {
        'course': course,
        'sections': sections
    }
    return render(request, 'courses/course_edit_sections.html', context)

@login_required
def course_section_add(request, slug):
    """Vista para añadir una sección al curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.course = course
            # Obtener el último orden y sumar 1
            last_order = Section.objects.filter(course=course).order_by('-order').first()
            section.order = (last_order.order + 1) if last_order else 0
            section.save()
            messages.success(request, 'Sección añadida exitosamente.')
            return redirect('courses:course-edit-sections', slug=course.slug)
        else:
            messages.error(request, 'Error al crear la sección.')
    else:
        form = SectionForm()
    
    context = {
        'form': form,
        'course': course
    }
    return render(request, 'courses/course_section_form.html', context)

@login_required
def course_section_edit(request, slug, section_id):
    """Vista para editar una sección del curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    section = get_object_or_404(Section, id=section_id, course=course)
    
    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sección actualizada exitosamente.')
            return redirect('courses:course-edit-sections', slug=course.slug)
        else:
            messages.error(request, 'Error al actualizar la sección.')
    else:
        form = SectionForm(instance=section)
    
    context = {
        'form': form,
        'course': course,
        'section': section
    }
    return render(request, 'courses/course_section_form.html', context)

@login_required
def course_section_delete(request, slug, section_id):
    """Vista para eliminar una sección del curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    section = get_object_or_404(Section, id=section_id, course=course)
    
    if request.method == 'POST':
        section.delete()
        messages.success(request, 'Sección eliminada exitosamente.')
        return redirect('courses:course-edit-sections', slug=course.slug)
    
    context = {
        'course': course,
        'section': section
    }
    return render(request, 'courses/course_section_confirm_delete.html', context)

@login_required
def course_questions_edit(request, slug):
    """Vista para gestionar las preguntas del curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    questions = Question.objects.filter(course=course).order_by('order')
    
    context = {
        'course': course,
        'questions': questions
    }
    return render(request, 'courses/course_edit_questions.html', context)

@login_required
def course_question_add(request, slug):
    """Vista para añadir una pregunta al curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            # Guardar la pregunta primero
            question = form.save(commit=False)
            question.course = course
            question.save()
            
            # Procesar las respuestas
            answers = request.POST.getlist('answers')
            is_correct = request.POST.getlist('is_correct')
            
            # Crear las respuestas
            for i, answer_text in enumerate(answers):
                if answer_text.strip():  # Solo crear respuestas no vacías
                    Answer.objects.create(
                        question=question,
                        course=course,
                        answer=answer_text,
                        is_correct=str(i) in is_correct,
                        number=i + 1
                    )
            
            messages.success(request, 'Pregunta agregada exitosamente.')
            return redirect('courses:course-edit-questions', slug=course.slug)
        else:
            messages.error(request, 'Error al guardar la pregunta.')
    else:
        form = QuestionForm()
    
    context = {
        'form': form,
        'course': course,
        'answers': None,  # No hay respuestas para una nueva pregunta
    }
    
    return render(request, 'courses/course_question_form.html', context)

@login_required
def course_question_edit(request, slug, question_id):
    """Vista para editar una pregunta del curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    question = get_object_or_404(Question, id=question_id, course=course)
    answers = Answer.objects.filter(question=question).order_by('number')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            
            # Eliminar respuestas existentes
            Answer.objects.filter(question=question).delete()
            
            # Procesar nuevas respuestas
            answers_data = request.POST.getlist('answers')
            is_correct_data = request.POST.getlist('is_correct')
            
            for i, answer_text in enumerate(answers_data):
                if answer_text.strip():  # Solo crear respuestas no vacías
                    is_correct = str(i) in is_correct_data
                    Answer.objects.create(
                        question=question,
                        course=course,
                        answer=answer_text,
                        is_correct=is_correct,
                        number=i + 1
                    )
            
            messages.success(request, 'Pregunta actualizada exitosamente.')
            return redirect('courses:course-edit-questions', slug=course.slug)
        else:
            messages.error(request, 'Error al actualizar la pregunta.')
    else:
        form = QuestionForm(instance=question)
    
    context = {
        'form': form,
        'course': course,
        'question': question,
        'answers': answers
    }
    return render(request, 'courses/course_question_form.html', context)

@login_required
def course_question_delete(request, slug, question_id):
    """Vista para eliminar una pregunta del curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    question = get_object_or_404(Question, id=question_id, course=course)
    
    if request.method == 'POST':
        # Eliminar respuestas asociadas
        Answer.objects.filter(question=question).delete()
        # Eliminar la pregunta
        question.delete()
        messages.success(request, 'Pregunta eliminada exitosamente.')
        return redirect('courses:course-edit-questions', slug=course.slug)
    
    context = {
        'course': course,
        'question': question
    }
    return render(request, 'courses/course_question_confirm_delete.html', context)
