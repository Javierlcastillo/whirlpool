from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

from .models import Section, Question, CourseContentOrder

@receiver(post_save, sender=Section)
def create_section_order(sender, instance, created, **kwargs):
    """Crear o actualizar el orden de una sección cuando se guarda."""
    if created:
        # Crear registro de orden sin especificar explícitamente el orden
        # Dejar que el método save() del modelo CourseContentOrder calcule automáticamente el orden
        CourseContentOrder.objects.create(
            course=instance.course,
            content_type='section',
            content_id=instance.id
            # No incluimos el order, dejando que el modelo lo calcule automáticamente
        )

@receiver(post_save, sender=Question)
def create_question_order(sender, instance, created, **kwargs):
    """Crear o actualizar el orden de una pregunta cuando se guarda."""
    if created:
        # Crear registro de orden sin especificar explícitamente el orden
        # Dejar que el método save() del modelo CourseContentOrder calcule automáticamente el orden
        CourseContentOrder.objects.create(
            course=instance.course,
            content_type='question',
            content_id=instance.id
            # No incluimos el order, dejando que el modelo lo calcule automáticamente
        ) 