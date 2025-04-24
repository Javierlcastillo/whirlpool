from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.db import transaction
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import JsonResponse
import json

from .models import Course, Question, Answer, Region, Instructor, CourseApplication, Section, CourseContentOrder
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
        
        # Obtener secciones ordenadas por CourseContentOrder
        section_orders = CourseContentOrder.objects.filter(
            course=course,
            content_type='section'
        ).order_by('order')
        
        # Obtener las secciones en el orden correcto
        sections = []
        for order in section_orders:
            try:
                section = Section.objects.get(id=order.content_id)
                sections.append(section)
            except Section.DoesNotExist:
                continue
                
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
    
    # Obtener las secciones ordenadas a través de CourseContentOrder
    section_orders = CourseContentOrder.objects.filter(
        course=course, 
        content_type='section'
    ).order_by('order')
    
    # Construir una lista ordenada de secciones
    sections = []
    for order in section_orders:
        section = Section.objects.filter(id=order.content_id).first()
        if section:
            sections.append(section)
    
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
        # Usamos la misma estrategia que funcionó para las preguntas
        # Evitamos usar el formulario Django para guardar
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        
        # Si hay archivos subidos, los manejamos aparte
        media_file = request.FILES.get('media', None)
        
        print(f"POST data: {request.POST}")
        print(f"Title: {title}")
        print(f"Content: {content[:100]}...")  # Mostrar solo los primeros 100 caracteres
        print(f"Media file: {media_file}")
        
        if title and content:
            try:
                # Crear sección directamente
                section = Section(
                    course=course,
                    title=title,
                    content=content
                )
                
                # Asignar el archivo si existe
                if media_file:
                    section.media = media_file
                    
                section.save()
                
                # El orden ahora se maneja automáticamente con las señales post_save
                print(f"Section created with ID: {section.id}")
                
                messages.success(request, 'Sección añadida exitosamente.')
                return redirect('courses:course-edit-sections', slug=course.slug)
            except Exception as e:
                print(f"Error creating section: {e}")
                messages.error(request, f'Error al crear la sección: {str(e)}')
        else:
            messages.error(request, 'Datos incompletos. Por favor, proporcione título y contenido.')
    
    # Para GET o si POST falla, mostrar el formulario
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
        # Usamos la misma estrategia que funcionó para las preguntas
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        
        # Si hay archivos subidos, los manejamos aparte
        media_file = request.FILES.get('media', None)
        
        print(f"POST data (edit): {request.POST}")
        print(f"Title: {title}")
        print(f"Content: {content[:100]}...")  # Mostrar solo los primeros 100 caracteres
        print(f"Media file: {media_file}")
        
        if title and content:
            try:
                # Actualizar sección
                section.title = title
                section.content = content
                
                # Actualizar archivo si hay uno nuevo
                if media_file:
                    section.media = media_file
                    
                section.save()
                
                print(f"Section updated: {section.id}, order: {section.order}")
                
                messages.success(request, 'Sección actualizada exitosamente.')
                return redirect('courses:course-edit-sections', slug=course.slug)
            except Exception as e:
                print(f"Error updating section: {e}")
                messages.error(request, f'Error al actualizar la sección: {str(e)}')
        else:
            messages.error(request, 'Datos incompletos. Por favor, proporcione título y contenido.')
    
    # Para GET, cargar el formulario con los datos existentes
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
    
    # Obtener las preguntas ordenadas a través de CourseContentOrder
    question_orders = CourseContentOrder.objects.filter(
        course=course, 
        content_type='question'
    ).order_by('order')
    
    # Construir una lista ordenada de preguntas
    questions = []
    for order in question_orders:
        question = Question.objects.filter(id=order.content_id).first()
        if question:
            questions.append(question)
    
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
        # Evitar por completo el uso del formulario Django para el guardado
        # ya que podría estar causando el problema al crear relaciones implícitas
        text = request.POST.get('text', '')
        question_type = request.POST.get('type', 'multiple_choice')
        answers_data = request.POST.getlist('answers')
        is_correct_inputs = request.POST.getlist('is_correct')
        
        print(f"POST data: {request.POST}")
        print(f"Text: {text}")
        print(f"Type: {question_type}")
        print(f"Answers: {answers_data}")
        print(f"Is correct: {is_correct_inputs}")
        
        if text and answers_data:
            try:
                # Crear pregunta directamente
                question = Question(
                    course=course,
                    text=text,
                    type=question_type
                )
                question.save()
                
                # El orden ahora se maneja automáticamente con las señales post_save
                
                # Procesar las respuestas
                for i, answer_text in enumerate(answers_data):
                    if answer_text.strip():  # Solo guardar respuestas no vacías
                        is_correct = False
                        # Verificar si esta respuesta está marcada como correcta
                        if is_correct_inputs and str(i) in is_correct_inputs:
                            is_correct = True
                        
                        # Crear la respuesta
                        Answer.objects.create(
                            question=question,
                            course=course,
                            number=i+1,
                            answer=answer_text,
                            is_correct=is_correct
                        )
                
                messages.success(request, 'Pregunta añadida exitosamente.')
                return redirect('courses:course-edit-questions', slug=course.slug)
            except Exception as e:
                print(f"Error creating question: {e}")
                messages.error(request, f'Error al crear la pregunta: {str(e)}')
        else:
            messages.error(request, 'Datos incompletos. Por favor, proporcione texto y al menos una respuesta.')
    
    # Para GET o si POST falla, mostrar el formulario
    form = QuestionForm()
    
    context = {
        'form': form,
        'course': course
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
    
    if request.method == 'POST':
        # Igual que en add, evitamos el uso de formularios Django
        text = request.POST.get('text', '')
        question_type = request.POST.get('type', 'multiple_choice')
        answers_data = request.POST.getlist('answers')
        is_correct_inputs = request.POST.getlist('is_correct')
        
        print(f"POST data (edit): {request.POST}")
        print(f"Text: {text}")
        print(f"Type: {question_type}")
        print(f"Answers: {answers_data}")
        print(f"Is correct: {is_correct_inputs}")
        
        if text and answers_data:
            try:
                # Actualizar la pregunta directamente
                question.text = text
                question.type = question_type
                question.save()
                
                # Eliminar todas las respuestas existentes
                Answer.objects.filter(question=question).delete()
                
                # Crear nuevas respuestas
                for i, answer_text in enumerate(answers_data):
                    if answer_text.strip():  # Solo crear respuestas no vacías
                        # Determinar si esta respuesta está marcada como correcta
                        is_correct = str(i) in is_correct_inputs
                        
                        answer = Answer(
                            question=question,
                            course=course,
                            answer=answer_text,
                            is_correct=is_correct,
                            number=i + 1
                        )
                        answer.save()
                        print(f"Answer created (edit): {answer_text}, is_correct: {is_correct}")
                
                messages.success(request, 'Pregunta actualizada exitosamente.')
                return redirect('courses:course-edit-questions', slug=course.slug)
            except Exception as e:
                print(f"Error updating question: {e}")
                messages.error(request, f'Error al actualizar la pregunta: {str(e)}')
        else:
            messages.error(request, 'Datos incompletos. Por favor, proporcione texto de pregunta y respuestas.')
    
    # Para GET, cargar el formulario con los datos existentes
    form = QuestionForm(instance=question)
    
    context = {
        'form': form,
        'course': course,
        'question': question,
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

# Añadir estas nuevas vistas para gestionar el orden

@login_required
def course_content_order(request, slug):
    """Vista para ordenar el contenido del curso."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        try:
            # Parsear el JSON desde la solicitud
            data = json.loads(request.body)
            new_order = data.get('order', [])
            
            # Validar que todos los elementos existan
            for item in new_order:
                item_id = item.get('id')
                item_type = item.get('type')
                
                if item_type == 'section':
                    if not Section.objects.filter(id=item_id, course=course).exists():
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Sección con ID {item_id} no encontrada'
                        }, status=400)
                elif item_type == 'question':
                    if not Question.objects.filter(id=item_id, course=course).exists():
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Pregunta con ID {item_id} no encontrada'
                        }, status=400)
            
            # Actualizar el orden de cada elemento
            with transaction.atomic():
                # Eliminar órdenes existentes para este curso
                CourseContentOrder.objects.filter(course=course).delete()
                
                # Crear nuevos registros de orden
                for i, item in enumerate(new_order):
                    CourseContentOrder.objects.create(
                        course=course,
                        content_type=item['type'],
                        content_id=item['id'],
                        order=i
                    )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Orden actualizado con éxito.'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    # Obtener todos los elementos de contenido ordenados
    content_items = course.get_ordered_content()
    
    context = {
        'course': course,
        'content_items': content_items
    }
    return render(request, 'courses/course_content_order.html', context)

@login_required
def course_section_move(request, slug, section_id, direction):
    """Vista para mover una sección del curso arriba o abajo en el orden."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    section = get_object_or_404(Section, id=section_id, course=course)
    
    # Buscar el orden actual
    try:
        current_order = CourseContentOrder.objects.get(
            course=course,
            content_type='section',
            content_id=section_id
        )
    except CourseContentOrder.DoesNotExist:
        # Si no existe, crear uno nuevo
        current_order = CourseContentOrder.objects.create(
            course=course,
            content_type='section',
            content_id=section_id
        )
    
    # Obtener todos los órdenes de contenido del curso
    all_orders = CourseContentOrder.objects.filter(course=course).order_by('order')
    
    # Encontrar el índice actual
    current_index = -1
    for i, order in enumerate(all_orders):
        if order.content_type == 'section' and order.content_id == section.id:
            current_index = i
            break
    
    if current_index == -1:
        messages.error(request, "No se pudo encontrar la sección en el orden actual.")
        return redirect('courses:course-edit-sections', slug=course.slug)
    
    # Determinar el índice de intercambio
    swap_index = -1
    if direction == 'up' and current_index > 0:
        swap_index = current_index - 1
    elif direction == 'down' and current_index < len(all_orders) - 1:
        swap_index = current_index + 1
    
    if swap_index != -1:
        # Intercambiar con el elemento adyacente
        swap_order = all_orders[swap_index]
        
        # Guardar el orden actual temporalmente
        temp_order = current_order.order
        
        # Actualizar los órdenes
        current_order.order = swap_order.order
        swap_order.order = temp_order
        
        # Guardar los cambios
        current_order.save()
        swap_order.save()
        
        messages.success(request, f"Sección movida {'arriba' if direction == 'up' else 'abajo'} exitosamente.")
    else:
        messages.warning(request, f"La sección ya está en el {'inicio' if direction == 'up' else 'final'} de la lista.")
    
    return redirect('courses:course-edit-sections', slug=course.slug)

@login_required
def course_question_move(request, slug, question_id, direction):
    """Vista para mover una pregunta del curso arriba o abajo en el orden."""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, slug=slug)
    question = get_object_or_404(Question, id=question_id, course=course)
    
    # Buscar el orden actual
    try:
        current_order = CourseContentOrder.objects.get(
            course=course,
            content_type='question',
            content_id=question_id
        )
    except CourseContentOrder.DoesNotExist:
        # Si no existe, crear uno nuevo
        current_order = CourseContentOrder.objects.create(
            course=course,
            content_type='question',
            content_id=question_id
        )
    
    # Obtener todos los órdenes de contenido del curso
    all_orders = CourseContentOrder.objects.filter(course=course).order_by('order')
    
    # Encontrar el índice actual
    current_index = -1
    for i, order in enumerate(all_orders):
        if order.content_type == 'question' and order.content_id == question.id:
            current_index = i
            break
    
    if current_index == -1:
        messages.error(request, "No se pudo encontrar la pregunta en el orden actual.")
        return redirect('courses:course-edit-questions', slug=course.slug)
    
    # Determinar el índice de intercambio
    swap_index = -1
    if direction == 'up' and current_index > 0:
        swap_index = current_index - 1
    elif direction == 'down' and current_index < len(all_orders) - 1:
        swap_index = current_index + 1
    
    if swap_index != -1:
        # Intercambiar con el elemento adyacente
        swap_order = all_orders[swap_index]
        
        # Guardar el orden actual temporalmente
        temp_order = current_order.order
        
        # Actualizar los órdenes
        current_order.order = swap_order.order
        swap_order.order = temp_order
        
        # Guardar los cambios
        current_order.save()
        swap_order.save()
        
        messages.success(request, f"Pregunta movida {'arriba' if direction == 'up' else 'abajo'} exitosamente.")
    else:
        messages.warning(request, f"La pregunta ya está en el {'inicio' if direction == 'up' else 'final'} de la lista.")
    
    return redirect('courses:course-edit-questions', slug=course.slug)

@login_required
def course_view_content(request, slug):
    """Vista para ver el contenido del curso."""
    course = get_object_or_404(Course, slug=slug)
    
    # Obtener el contenido ordenado del curso
    content_items = course.get_ordered_content()
    
    context = {
        'course': course,
        'content_items': content_items
    }
    return render(request, 'courses/course_view_content.html', context)

@login_required
def toggle_course_status(request, slug):
    """Alterna el estado activo/inactivo de un curso."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permiso para realizar esta acción'}, status=403)
    
    try:
        course = Course.objects.get(slug=slug)
        course.is_active = not course.is_active
        course.save()
        return JsonResponse({
            'success': True,
            'is_active': course.is_active,
            'message': f'Curso {"activado" if course.is_active else "desactivado"} correctamente'
        })
    except Course.DoesNotExist:
        return JsonResponse({'error': 'Curso no encontrado'}, status=404)

class MetricsDashboardView(LoginRequiredMixin, TemplateView):
    """Vista para mostrar el dashboard de métricas detalladas."""
    template_name = 'courses/metrics_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context