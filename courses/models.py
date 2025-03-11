# models.py

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone

class Region(models.Model):
    """Modelo para regiones."""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    
    class Meta:
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'
    
    def __str__(self):
        return self.nombre

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

class Course(models.Model):
    """Modelo para los cursos de capacitación."""
    CATEGORY_CHOICES = [
        ('reparacion', 'Reparación'),
        ('instalacion', 'Instalación'),
        ('diagnostico', 'Diagnóstico'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(verbose_name='Descripción', blank=True)
    instructor = models.ForeignKey(
        Instructor, 
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
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('course-detail', kwargs={'slug': self.slug})

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
    """Modelo para secciones informativas dentro de un curso."""
    id = models.AutoField(primary_key=True)
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
        return f"{self.course.name} - Sección: {self.title}"

class Question(models.Model):
    """Modelo para preguntas de los cursos."""
    TYPE_CHOICES = [
        ('multiple', 'Opción Múltiple'),
        ('open', 'Respuesta Abierta'),
        ('true_false', 'Verdadero/Falso'),
    ]
    
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Curso'
    )
    number = models.PositiveIntegerField(verbose_name='Número', default=1)
    text = models.TextField(verbose_name='Texto de la pregunta')
    media = models.FileField(
        upload_to='questions/',
        blank=True,
        null=True,
        verbose_name='Medio (imagen, video)'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='multiple',
        verbose_name='Tipo'
    )
    
    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['course', 'number']
        unique_together = ['course', 'number']
    
    def __str__(self):
        return f"{self.course.name} - Pregunta {self.number}"

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
    
    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        unique_together = ['question', 'number']
    
    def __str__(self):
        return f"Respuesta {self.number} para {self.question}"

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