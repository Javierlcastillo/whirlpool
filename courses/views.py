from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib import messages

from .models import Course, Question, Answer, Region, Instructor, CourseApplication, Desempeno, Section
from users.models import Technician
from .forms import CourseForm, QuestionForm, AnswerForm, RegionForm, InstructorForm, SectionForm

@login_required
def dashboard(request):
    """Vista para el dashboard principal."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado. Solo administradores tienen permiso para acceder.")
        return redirect('login')
    
    # Contar elementos principales del sistema
    courses_count = Course.objects.count()
    regions_count = Region.objects.count()
    instructors_count = Instructor.objects.count()
    technicians_count = Technician.objects.count()
    
    # Obtener estadísticas de desempeño
    total_desempenos = Desempeno.objects.count()
    completed_desempenos = Desempeno.objects.filter(estado='completed').count()
    failed_desempenos = Desempeno.objects.filter(estado='failed').count()
    
    # Cálculo de tasas de aprobación
    approval_rate = 0
    if total_desempenos > 0:
        approval_rate = (completed_desempenos / total_desempenos) * 100
    
    context = {
        'courses_count': courses_count,
        'regions_count': regions_count,
        'instructors_count': instructors_count,
        'technicians_count': technicians_count,
        'latest_courses': Course.objects.all().order_by('-created_at')[:5],
        
        # Métricas de desempeño
        'total_desempenos': total_desempenos,
        'completed_desempenos': completed_desempenos,
        'failed_desempenos': failed_desempenos,
        'approval_rate': approval_rate,
    }
    
    return render(request, 'dashboard.html', context)

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
    
    # Para manejar respuestas, necesitaremos procesar datos adicionales
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
            
            # Procesar formsets solo si tenemos un curso
            question_formset = QuestionFormSet(request.POST, request.FILES, instance=created_course)
            section_formset = SectionFormSet(request.POST, request.FILES, instance=created_course)
            
            if question_formset.is_valid() and section_formset.is_valid():
                # Guardar preguntas
                questions = question_formset.save(commit=False)
                for question in questions:
                    question.course = created_course
                    question.save()
                
                question_formset.save_m2m()
                
                # Manejar borrados de preguntas
                for obj in question_formset.deleted_objects:
                    obj.delete()
                
                # Guardar secciones
                sections = section_formset.save(commit=False)
                for section in sections:
                    section.course = created_course
                    section.save()
                
                section_formset.save_m2m()
                
                # Manejar borrados de secciones
                for obj in section_formset.deleted_objects:
                    obj.delete()
                
                # Procesar respuestas para cada pregunta
                # Buscamos en el POST datos con formato 'answer_text_[question_id]_[index]'
                for key in request.POST:
                    if key.startswith('answer_text_'):
                        parts = key.split('_')
                        if len(parts) >= 4:  # answer_text_[question_id]_[index]
                            question_id = parts[2]
                            answer_index = parts[3]
                            
                            # Obtener datos de la respuesta
                            answer_text = request.POST.get(key)
                            is_correct = request.POST.get(f'answer_correct_{question_id}_{answer_index}') == 'on'
                            answer_number = int(answer_index) + 1
                            
                            # Identificar si es una respuesta nueva o existente
                            answer_id = request.POST.get(f'answer_id_{question_id}_{answer_index}')
                            
                            try:
                                question = Question.objects.get(id=question_id)
                                
                                if answer_id and answer_id.isdigit():
                                    # Actualizar respuesta existente
                                    try:
                                        answer = Answer.objects.get(id=answer_id)
                                        answer.answer = answer_text
                                        answer.is_correct = is_correct
                                        answer.save()
                                    except Answer.DoesNotExist:
                                        pass
                                else:
                                    # Crear nueva respuesta
                                    Answer.objects.create(
                                        question=question,
                                        course=created_course,
                                        number=answer_number,
                                        answer=answer_text,
                                        is_correct=is_correct
                                    )
                            except Question.DoesNotExist:
                                pass
                
                messages.success(
                    request, 
                    f'Curso {"actualizado" if not is_new else "creado"} exitosamente'
                )
                return redirect('course-detail', slug=created_course.slug)
            else:
                messages.error(request, 'Por favor corrija los errores en los formularios de preguntas o secciones')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario del curso')
            
    else:
        # GET request
        course_form = CourseForm(instance=course)
        question_formset = QuestionFormSet(instance=course) if course else None
        section_formset = SectionFormSet(instance=course) if course else None
    
    # Obtener preguntas con sus respuestas para la vista
    questions_with_answers = []
    if course:
        questions = Question.objects.filter(course=course).prefetch_related('answers')
        for question in questions:
            questions_with_answers.append({
                'question': question,
                'answers': question.answers.all()
            })
    
    # Obtener todas las regiones para el selector
    regions = Region.objects.all()
    
    return render(request, 'courses/manage_course.html', {
        'course_form': course_form,
        'question_formset': question_formset,
        'section_formset': section_formset,
        'course': course,
        'questions_with_answers': questions_with_answers,
        'regions': regions,
        'is_new': is_new,
        'title': template_title
    })

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
        context['questions'] = self.object.questions.all().prefetch_related('answers')
        context['regions'] = Region.objects.filter(course_applications__course=self.object)
        # Añadir todas las regiones para el modal de agregar
        context['all_regions'] = Region.objects.all()
        return context

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
