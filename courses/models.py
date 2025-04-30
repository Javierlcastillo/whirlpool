# models.py

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import json
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Region(models.Model):
    """Modelo para regiones."""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    
    class Meta:
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'
    
    def __str__(self):
        return self.nombre
        
    def get_absolute_url(self):
        return reverse('courses:region-detail', kwargs={'pk': self.pk})

class Instructor(models.Model):
    """Modelo para instructores."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='instructors',
        verbose_name='Región'
    )
    
    class Meta:
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructores'
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('courses:instructor-detail', kwargs={'pk': self.pk})

class Course(models.Model):
    """Modelo para los cursos de capacitación."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(verbose_name='Descripción', blank=True)
    instructor = models.ForeignKey(
        'Instructor', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='courses_taught',
        verbose_name='Instructor'
    )
    duration_hours = models.PositiveIntegerField(verbose_name='Duración (horas)', default=8)
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='Última actualización')
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='Región Principal'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Asegurar que cada curso tenga un slug único basado en su nombre."""
        if not self.slug:
            # Generar un slug base a partir del nombre
            base_slug = slugify(self.name)
            
            # Verificar si ya existe un curso con ese slug
            existing_slugs = Course.objects.filter(slug__startswith=base_slug).values_list('slug', flat=True)
            
            if base_slug in existing_slugs:
                # Si ya existe, agregar un sufijo numérico
                counter = 1
                while f"{base_slug}-{counter}" in existing_slugs:
                    counter += 1
                self.slug = f"{base_slug}-{counter}"
            else:
                self.slug = base_slug
                
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('courses:course-detail', kwargs={'slug': self.slug})

    def get_ordered_content(self):
        """
        Obtiene el contenido del curso (secciones y preguntas) en el orden correcto.
        """
        # Obtener el orden de contenido
        ordered_content = self.content_order.all().order_by('order')
        
        # Crear una lista para el resultado final
        content_items = []
        
        # Procesar cada elemento ordenado
        for item in ordered_content:
            content_obj = item.content_object
            
            if not content_obj:
                continue
                
            if item.content_type == 'section':
                content_items.append({
                    'type': 'section',
                    'id': content_obj.id,
                    'title': content_obj.title,
                    'content': content_obj.content,
                    'media': content_obj.media.url if content_obj.media else None,
                    'order': item.order
                })
            elif item.content_type == 'question':
                content_items.append({
                    'type': content_obj.type,
                    'id': content_obj.id,
                    'text': content_obj.text,
                    'order': item.order,
                    'answers': [
                        {
                            'id': answer.id,
                            'answer': answer.answer,
                            'is_correct': answer.is_correct,
                            'number': answer.number,
                            'media': answer.media.url if answer.media else None
                        }
                        for answer in content_obj.answers.all()
                    ]
                })
        
        return content_items

    def sync_content_order(self):
        """
        Sincroniza los registros de orden para las secciones y preguntas de este curso.
        Mantiene el orden existente en lugar de reconstruirlo completamente.
        """
        print(f"DEBUG: Starting sync_content_order for course {self.id}")
        
        # Obtener todos los elementos existentes
        sections = self.sections.all()
        questions = self.questions.all()
        print(f"DEBUG: Found {sections.count()} sections and {questions.count()} questions")
        
        # Obtener elementos con orden actual
        existing_orders = dict(
            CourseContentOrder.objects.filter(course=self).values_list(
                'content_type', 'content_id', 'order'
            ).annotate(combined_key=models.functions.Concat(
                'content_type', models.Value('_'), models.functions.Cast('content_id', models.CharField())
            )).values_list('combined_key', 'order')
        )
        print(f"DEBUG: Found {len(existing_orders)} existing orders")
        
        # Crear un conjunto de todos los elementos actuales
        actual_items = set()
        for section in sections:
            actual_items.add(f"section_{section.id}")
        for question in questions:
            actual_items.add(f"question_{question.id}")
        print(f"DEBUG: Total actual items: {len(actual_items)}")
        
        # Crear un conjunto de elementos con orden actual
        ordered_items = set(existing_orders.keys())
        
        # Identificar elementos sin orden
        unordered_items = actual_items - ordered_items
        print(f"DEBUG: Found {len(unordered_items)} items without order")
        
        # Elementos a eliminar (ya no existen pero tienen orden)
        to_delete = ordered_items - actual_items
        print(f"DEBUG: Found {len(to_delete)} items to delete")
        
        # Eliminar órdenes para elementos que ya no existen
        for item_key in to_delete:
            content_type, content_id = item_key.split('_', 1)
            CourseContentOrder.objects.filter(
                course=self,
                content_type=content_type,
                content_id=int(content_id)
            ).delete()
            print(f"DEBUG: Deleted order for {item_key}")
        
        # Obtener el máximo orden existente
        max_order = CourseContentOrder.objects.filter(course=self).aggregate(models.Max('order'))['order__max'] or 0
        print(f"DEBUG: Current max order: {max_order}")
        
        # Crear órdenes para elementos sin orden
        for item_key in unordered_items:
            content_type, content_id = item_key.split('_', 1)
            max_order += 1
            CourseContentOrder.objects.create(
                course=self,
                content_type=content_type,
                content_id=int(content_id),
                order=max_order
            )
            print(f"DEBUG: Created order {max_order} for {item_key}")
        
        print(f"DEBUG: Sync completed. Total items: {len(actual_items)}")
        return len(actual_items)  # Devuelve el número de elementos sincronizados

class CourseApplication(models.Model):
    """Modelo para aplicación de cursos a regiones."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Curso'
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='course_applications',
        verbose_name='Región'
    )
    
    class Meta:
        verbose_name = 'Aplicación de Curso'
        verbose_name_plural = 'Aplicaciones de Cursos'
        unique_together = ['course', 'region']
    
    def __str__(self):
        return f"{self.course} - {self.region}"

class CourseContent(models.Model):
    """Modelo base para el contenido del curso (secciones y preguntas)."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class Section(CourseContent):
    """Modelo para secciones de cursos."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200, verbose_name='Título')
    content = models.TextField(verbose_name='Contenido')
    media = models.FileField(
        upload_to='sections/',
        blank=True,
        null=True,
        verbose_name='Medio (imagen, documento)'
    )
    
    class Meta:
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
    
    def __str__(self):
        return f"{self.title}"

class Question(CourseContent):
    """Modelo para preguntas de cursos."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    QUESTION_TYPES = (
        ('multiple_choice', 'Opción Múltiple'),
        ('true_false', 'Verdadero/Falso'),
    )
    
    text = models.TextField(verbose_name='Texto de la pregunta')
    type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice', verbose_name='Tipo de pregunta')
    
    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
    
    def __str__(self):
        return f"{self.text[:50]}..."
    
    def clean(self):
        super().clean()
        if self.type == 'true_false':
            # Verificar que solo tenga dos respuestas para verdadero/falso
            answers = self.answers.all()
            if answers.count() > 2:
                raise ValidationError('Las preguntas de verdadero/falso solo pueden tener dos respuestas.')
            if answers.count() == 2:
                # Verificar que una sea verdadera y otra falsa
                true_count = answers.filter(is_correct=True).count()
                if true_count != 1:
                    raise ValidationError('Las preguntas de verdadero/falso deben tener exactamente una respuesta verdadera y una falsa.')

class CourseContentOrder(models.Model):
    """Modelo para gestionar el orden de contenido en un curso."""
    CONTENT_TYPES = (
        ('section', 'Sección'),
        ('question', 'Pregunta'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='content_order')
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    content_id = models.PositiveIntegerField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Orden de Contenido'
        verbose_name_plural = 'Orden de Contenidos'
        ordering = ['course', 'order']
        unique_together = ['course', 'content_type', 'content_id']
    
    def __str__(self):
        return f"{self.course} - {self.content_type} {self.content_id} - Orden {self.order}"
    
    def save(self, *args, **kwargs):
        # Siempre calcular el orden para nuevos registros
        if not self.pk:
            # Obtener máximo orden y manejar correctamente el caso None
            max_order_result = CourseContentOrder.objects.filter(course=self.course).aggregate(models.Max('order'))
            max_order = max_order_result['order__max']
            
            # Si no hay registros existentes o el valor es None, comenzar desde 0
            if max_order is None:
                self.order = 1
            else:
                self.order = max_order + 1
                
            print(f"DEBUG: New order calculated for {self.content_type} {self.content_id}: {self.order}")
        
        # Para registros existentes, actualizar sólo si el orden es 0
        elif self.order == 0:
            max_order_result = CourseContentOrder.objects.filter(course=self.course).aggregate(models.Max('order'))
            max_order = max_order_result['order__max'] or 0
            self.order = max_order + 1
            print(f"DEBUG: Updated order for existing {self.content_type} {self.content_id}: {self.order}")
        
        super().save(*args, **kwargs)
    
    @property
    def content_object(self):
        """Obtiene el objeto referenciado (sección o pregunta)."""
        if self.content_type == 'section':
            return Section.objects.filter(id=self.content_id).first()
        elif self.content_type == 'question':
            return Question.objects.filter(id=self.content_id).first()
        return None

class Answer(models.Model):
    """Modelo para respuestas a las preguntas."""
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Pregunta'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Curso'
    )
    number = models.PositiveIntegerField(verbose_name='Número', default=1)
    answer = models.TextField(verbose_name='Texto de la respuesta')
    media = models.FileField(
        upload_to='answers/',
        blank=True,
        null=True,
        verbose_name='Medio (imagen, video)'
    )
    is_correct = models.BooleanField(default=False, verbose_name='Es correcta')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        unique_together = ['question', 'number']
    
    def __str__(self):
        return f"Respuesta {self.number} para {self.question}"

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class Desempeno(models.Model):
    """Modelo para registrar el desempeño de los técnicos en los cursos."""
    id = models.AutoField(primary_key=True)
    technician = models.ForeignKey(
        'users.Technician',
        on_delete=models.CASCADE,
        related_name='desempenos',
        verbose_name='Técnico'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='desempenos',
        verbose_name='Curso'
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='desempenos_instructor',
        verbose_name='Instructor'
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    duracion_total = models.PositiveIntegerField(
        default=0,
        verbose_name='Duración Total (minutos)'
    )
    respuestas_incorrectas = models.PositiveIntegerField(
        default=0,
        verbose_name='Respuestas Incorrectas'
    )
    aprobado = models.BooleanField(
        default=False,
        verbose_name='Aprobado'
    )
    
    class Meta:
        verbose_name = 'Desempeño'
        verbose_name_plural = 'Desempeños'
        ordering = ['-fecha']  # Ordenar por fecha descendente
    
    def __str__(self):
        return f"{self.technician} - {self.course} ({'Aprobado' if self.aprobado else 'Reprobado'})"
    
    def save(self, *args, **kwargs):
        # Asignar automáticamente el instructor del curso si no se especifica
        if not self.instructor and self.course.instructor:
            self.instructor = self.course.instructor
        super().save(*args, **kwargs)

class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress')
    completed_sections = models.ManyToManyField(Section, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(default=timezone.now, verbose_name='Última vez accedido')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')

    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"

    def update_progress(self):
        total_sections = self.course.sections.count()
        completed_count = self.completed_sections.count()
        if total_sections > 0:
            self.score = (completed_count / total_sections) * 100
            self.is_completed = self.score >= 100
            self.save()

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')

    class Meta:
        unique_together = ['user', 'question']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:50]}..."

    def save(self, *args, **kwargs):
        if self.question.type == 'multiple':
            correct_answers = self.question.answers.filter(is_correct=True)
            self.is_correct = any(self.answer == ca.answer for ca in correct_answers)
        elif self.question.type == 'true_false':
            self.is_correct = self.answer.lower() in ['true', 'verdadero', '1']
        super().save(*args, **kwargs)