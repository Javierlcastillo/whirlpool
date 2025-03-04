# models.py (versión modificada para compatibilidad con la DB existente)

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from users.models import Technician
from django.utils import timezone

class Course(models.Model):
    """Modelo para los cursos de capacitación."""
    CATEGORY_CHOICES = [
        ('reparacion', 'Reparación'),
        ('instalacion', 'Instalación'),
        ('diagnostico', 'Diagnóstico'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(verbose_name='Descripción', blank=True)
    instructor = models.ForeignKey(
        Technician, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='courses_teaching',
        verbose_name='Instructor'
    )
    duration_weeks = models.PositiveSmallIntegerField(verbose_name='Duración (semanas)')
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='reparacion',
        verbose_name='Categoría'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('course-detail', kwargs={'slug': self.slug})


class Section(models.Model):
    """Modelo para secciones informativas dentro de un curso."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='Curso'
    )
    title = models.CharField(max_length=255, verbose_name='Título')
    text = models.TextField(verbose_name='Texto', blank=True)
    image = models.ImageField(
        upload_to='sections/',
        blank=True,
        null=True,
        verbose_name='Imagen'
    )
    video_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='URL de video'
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Orden')
    
    class Meta:
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
        ordering = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - Sección: {self.title}"


# Mantener Question similar a lo que ya existe
class Question(models.Model):
    """Modelo para preguntas de los cursos."""
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Curso'
    )
    title = models.CharField(max_length=255, verbose_name='Título', blank=True)
    text = models.TextField(verbose_name='Texto de la pregunta')
    image = models.ImageField(
        upload_to='questions/',
        blank=True,
        null=True,
        verbose_name='Imagen (opcional)'
    )
    explanation = models.TextField(
        verbose_name='Explicación',
        blank=True,
        help_text='Explicación que se mostrará después de responder',
        null=True
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Orden')
    
    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - Pregunta {self.order}"


class Answer(models.Model):
    """Modelo para respuestas a las preguntas."""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Pregunta'
    )
    text = models.TextField(verbose_name='Texto de la respuesta')
    image = models.ImageField(
        upload_to='answers/',
        blank=True,
        null=True,
        verbose_name='Imagen (opcional)'
    )
    is_correct = models.BooleanField(default=False, verbose_name='Es correcta')
    
    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
    
    def __str__(self):
        return f"Respuesta para {self.question}"


class TechnicianProgress(models.Model):
    """Modelo para registrar el progreso de los técnicos en los cursos."""
    technician = models.ForeignKey(
        Technician,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Técnico'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Curso'
    )
    completed = models.BooleanField(default=False, verbose_name='Completado')
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Calificación'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inicio')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de finalización')
    
    class Meta:
        verbose_name = 'Progreso del técnico'
        verbose_name_plural = 'Progresos de los técnicos'
        unique_together = ['technician', 'course']
    
    def __str__(self):
        return f"{self.technician} - {self.course}"


class QuestionResponse(models.Model):
    """Modelo para registrar las respuestas de los técnicos a las preguntas."""
    technician = models.ForeignKey(
        Technician,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Técnico'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Pregunta'
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Respuesta seleccionada'
    )
    is_correct = models.BooleanField(verbose_name='Es correcta')
    response_time = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de respuesta')
    
    class Meta:
        verbose_name = 'Respuesta del técnico'
        verbose_name_plural = 'Respuestas de los técnicos'
        unique_together = ['technician', 'question']
    
    def __str__(self):
        return f"{self.technician} - {self.question}"
    
    def save(self, *args, **kwargs):
        # Automáticamente marcar si la respuesta es correcta
        self.is_correct = self.answer.is_correct
        super().save(*args, **kwargs)