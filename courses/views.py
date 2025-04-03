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

# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        queryset = Course.objects.all().select_related('instructor', 'region')
        
        # Filtrar por región si se especifica
        region_slug = self.request.GET.get('region')
        if region_slug:
            queryset = queryset.filter(region__slug=region_slug)
            
        # Filtrar por búsqueda si se especifica
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(instructor__first_name__icontains=search_query) |
                Q(instructor__last_name__icontains=search_query)
            )
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las regiones para el filtro
        context['regions'] = Region.objects.all()
        
        # Obtener la región actual si se está filtrando
        region_slug = self.request.GET.get('region')
        if region_slug:
            context['current_region'] = Region.objects.filter(slug=region_slug).first()
            
        # Obtener la búsqueda actual
        context['search_query'] = self.request.GET.get('search', '')
        
        # Obtener los cursos en los que el usuario está inscrito
        if self.request.user.is_authenticated:
            enrolled_courses = Course.objects.filter(
                enrollments__user=self.request.user
            ).values_list('id', flat=True)
            context['enrolled_courses'] = enrolled_courses
            
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
        
        # Verificar si el usuario ya está inscrito
        context['is_enrolled'] = course.enrollments.filter(user=self.request.user).exists()
        
        # Obtener el progreso del usuario si está inscrito
        if context['is_enrolled']:
            enrollment = course.enrollments.get(user=self.request.user)
            context['progress'] = enrollment.progress
            context['completed_sections'] = enrollment.completed_sections.all()
            context['completed_questions'] = enrollment.completed_questions.all()
        
        return context

class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course-list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

@login_required
def enroll_course(request, slug):
    """Vista para inscribir a un usuario en un curso."""
    course = get_object_or_404(Course, slug=slug)
    technician = get_object_or_404(Technician, user=request.user)
    
    # Verificar si el usuario ya está inscrito
    if course.enrollments.filter(user=request.user).exists():
        messages.warning(request, "Ya estás inscrito en este curso.")
        return redirect('course-detail', slug=slug)
    
    # Crear la inscripción
    course.enrollments.create(
        user=request.user,
        technician=technician,
        region=technician.region
    )
    
    messages.success(request, f"Te has inscrito exitosamente en el curso {course.name}")
    return redirect('course-detail', slug=slug)

@login_required
def complete_section(request, slug, section_id):
    """Vista para marcar una sección como completada."""
    course = get_object_or_404(Course, slug=slug)
    section = get_object_or_404(Section, id=section_id, course=course)
    
    # Verificar si el usuario está inscrito
    enrollment = course.enrollments.filter(user=request.user).first()
    if not enrollment:
        messages.error(request, "Debes estar inscrito en el curso para completar secciones.")
        return redirect('course-detail', slug=slug)
    
    # Marcar la sección como completada
    enrollment.completed_sections.add(section)
    messages.success(request, f"Sección '{section.title}' marcada como completada.")
    return redirect('course-detail', slug=slug)

@login_required
def complete_question(request, slug, question_id):
    """Vista para marcar una pregunta como completada."""
    course = get_object_or_404(Course, slug=slug)
    question = get_object_or_404(Question, id=question_id, course=course)
    
    # Verificar si el usuario está inscrito
    enrollment = course.enrollments.filter(user=request.user).first()
    if not enrollment:
        messages.error(request, "Debes estar inscrito en el curso para completar preguntas.")
        return redirect('course-detail', slug=slug)
    
    # Marcar la pregunta como completada
    enrollment.completed_questions.add(question)
    messages.success(request, f"Pregunta completada correctamente.")
    return redirect('course-detail', slug=slug)

@login_required
def course_progress(request, slug):
    """Vista para mostrar el progreso del curso."""
    course = get_object_or_404(Course, slug=slug)
    enrollment = course.enrollments.filter(user=request.user).first()
    
    if not enrollment:
        messages.error(request, "Debes estar inscrito en el curso para ver tu progreso.")
        return redirect('course-detail', slug=slug)
    
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
        return redirect('course-detail', slug=slug)
    
    # Verificar si el curso está completado
    if not enrollment.is_completed:
        messages.warning(request, "Debes completar el curso para obtener el certificado.")
        return redirect('course-detail', slug=slug)
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'user': request.user,
    }
    return render(request, 'courses/certificate.html', context)

@login_required
def manage_course(request, slug=None):
    """Vista unificada para crear/editar cursos con preguntas, respuestas y secciones."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado. Solo administradores tienen permiso para acceder.")
        return redirect('login')
    
    # Obtener el curso si existe (edición) o crear uno nuevo
    if slug:
        course = get_object_or_404(Course, slug=slug)
        template_title = f"Editar Curso: {course.name}"
        is_new = False
    else:
        course = None
        template_title = "Nuevo Curso"
        is_new = True
    
    # Formsets para preguntas y secciones
    QuestionFormSet = inlineformset_factory(
        Course, Question, 
        form=QuestionForm,
        extra=1 if not is_new else 0, 
        can_delete=True,
        fields=['number', 'text', 'media', 'type']
    )
    
    SectionFormSet = inlineformset_factory(
        Course, Section,
        form=SectionForm,
        extra=1 if not is_new else 0, 
        can_delete=True,
        fields=['title', 'text', 'image', 'video_url', 'order']
    )
    
    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES, instance=course)
        
        if course_form.is_valid():
            # Guardar el curso primero
            created_course = course_form.save(commit=False)
            
            # Asegurar que esté ligado a una región
            if not created_course.region and created_course.instructor and created_course.instructor.region:
                created_course.region = created_course.instructor.region
                
            created_course.save()
            
            # Si hay región, crear la aplicación del curso a esa región
            if created_course.region:
                CourseApplication.objects.get_or_create(
                    course=created_course,
                    region=created_course.region
                )
            
            if is_new:
                # Si es un curso nuevo, solo guardar el curso básico y redirigir
                messages.success(request, "Curso creado exitosamente. Ahora puede agregar preguntas y secciones.")
                return redirect('course-update', slug=created_course.slug)
            
            # Procesar formsets solo para cursos existentes
            question_formset = QuestionFormSet(request.POST, request.FILES, instance=created_course)
            section_formset = SectionFormSet(request.POST, request.FILES, instance=created_course)
            
            formsets_valid = True
            
            if question_formset.is_bound and question_formset.is_valid():
                question_formset.save()
            else:
                formsets_valid = False
                
            if section_formset.is_bound and section_formset.is_valid():
                section_formset.save()
            else:
                formsets_valid = False
            
            if formsets_valid:
                messages.success(request, f'Curso actualizado exitosamente')
                return redirect('course-detail', slug=created_course.slug)
            else:
                messages.warning(request, 'El curso se ha guardado, pero hay errores en algunos campos. Por favor revise el formulario.')
                
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario del curso')
            
    else:
        # GET request
        course_form = CourseForm(instance=course)
        question_formset = QuestionFormSet(instance=course) if course else None
        section_formset = SectionFormSet(instance=course) if course else None
    
    context = {
        'title': template_title,
        'course_form': course_form,
        'question_formset': question_formset,
        'section_formset': section_formset,
        'is_new': is_new,
    }
    
    return render(request, 'courses/manage_course.html', context)

# Region Views
class RegionListView(LoginRequiredMixin, ListView):
    model = Region
    template_name = 'courses/region_list.html'
    context_object_name = 'regions'
    paginate_by = 10

class RegionDetailView(LoginRequiredMixin, DetailView):
    model = Region
    template_name = 'courses/region_detail.html'
    context_object_name = 'region'

class RegionCreateView(LoginRequiredMixin, CreateView):
    model = Region
    form_class = RegionForm
    template_name = 'courses/region_form.html'
    success_url = reverse_lazy('region-list')

class RegionUpdateView(LoginRequiredMixin, UpdateView):
    model = Region
    form_class = RegionForm
    template_name = 'courses/region_form.html'
    success_url = reverse_lazy('region-list')

class RegionDeleteView(LoginRequiredMixin, DeleteView):
    model = Region
    template_name = 'courses/region_confirm_delete.html'
    success_url = reverse_lazy('region-list')

# Instructor Views
class InstructorListView(LoginRequiredMixin, ListView):
    model = Instructor
    template_name = 'courses/instructor_list.html'
    context_object_name = 'instructors'
    paginate_by = 10

class InstructorDetailView(LoginRequiredMixin, DetailView):
    model = Instructor
    template_name = 'courses/instructor_detail.html'
    context_object_name = 'instructor'

class InstructorCreateView(LoginRequiredMixin, CreateView):
    model = Instructor
    form_class = InstructorForm
    template_name = 'courses/instructor_form.html'
    success_url = reverse_lazy('instructor-list')

class InstructorUpdateView(LoginRequiredMixin, UpdateView):
    model = Instructor
    form_class = InstructorForm
    template_name = 'courses/instructor_form.html'
    success_url = reverse_lazy('instructor-list')

class InstructorDeleteView(LoginRequiredMixin, DeleteView):
    model = Instructor
    template_name = 'courses/instructor_confirm_delete.html'
    success_url = reverse_lazy('instructor-list')

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
    
    return redirect('course-detail', slug=slug)

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
    
    return redirect('course-detail', slug=slug)
