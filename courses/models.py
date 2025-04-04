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

class Section(models.Model):
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
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
    
    def __str__(self):
        return f"{self.title}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Si es una nueva sección
            # Obtener el último orden y sumar 1
            last_order = Section.objects.filter(course=self.course).order_by('-order').first()
            self.order = (last_order.order + 1) if last_order else 0
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class Question(models.Model):
    """Modelo para preguntas de cursos."""
    
    QUESTION_TYPES = (
        ('multiple_choice', 'Opción Múltiple'),
        ('true_false', 'Verdadero/Falso'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name='Texto de la pregunta')
    type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice', verbose_name='Tipo de pregunta')
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['order']
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
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Si es una nueva pregunta
            # Obtener el último orden y sumar 1
            last_order = Question.objects.filter(course=self.course).order_by('-order').first()
            self.order = (last_order.order + 1) if last_order else 0
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

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
    STATUS_CHOICES = [
        ('started', 'Iniciado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('failed', 'Reprobado'),
    ]
    
    id = models.AutoField(primary_key=True)
    technician = models.ForeignKey(
        'users.Technician',  # Referencia por string para evitar importación circular
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
    puntuacion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Puntuación'
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    estado = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='started',
        verbose_name='Estado'
    )
    
    class Meta:
        verbose_name = 'Desempeño'
        verbose_name_plural = 'Desempeños'
        unique_together = ['technician', 'course']
    
    def __str__(self):
        return f"{self.technician} - {self.course}"

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