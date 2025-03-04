from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from users.models import Technician

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


class Question(models.Model):
    """Modelo para preguntas de los cursos."""
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Curso'
    )
    text = models.TextField(verbose_name='Texto de la pregunta')
    image = models.ImageField(
        upload_to='questions/',
        blank=True,
        null=True,
        verbose_name='Imagen (opcional)'
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Orden')
    
    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['order']
    
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
