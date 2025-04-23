from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

from .models import Section, Question, CourseContentOrder

@receiver(post_save, sender=Section)
def create_section_order(sender, instance, created, **kwargs):
    """Crear o actualizar el orden de una sección cuando se guarda."""
    if created:
        # Obtener el máximo orden existente
        max_order = CourseContentOrder.objects.filter(course=instance.course).aggregate(models.Max('order'))
        next_order = 1 if max_order['order__max'] is None else max_order['order__max'] + 1
        
        print(f"SIGNAL: Creating order for Section {instance.id} with order {next_order}")
        
        # Crear registro de orden con un valor de orden específico
        CourseContentOrder.objects.create(
            course=instance.course,
            content_type='section',
            content_id=instance.id,
            order=next_order  # Asignar explícitamente el orden
        )

@receiver(post_save, sender=Question)
def create_question_order(sender, instance, created, **kwargs):
    """Crear o actualizar el orden de una pregunta cuando se guarda."""
    if created:
        # Obtener el máximo orden existente
        max_order = CourseContentOrder.objects.filter(course=instance.course).aggregate(models.Max('order'))
        next_order = 1 if max_order['order__max'] is None else max_order['order__max'] + 1
        
        print(f"SIGNAL: Creating order for Question {instance.id} with order {next_order}")
        
        # Crear registro de orden con un valor de orden específico
        CourseContentOrder.objects.create(
            course=instance.course,
            content_type='question',
            content_id=instance.id,
            order=next_order  # Asignar explícitamente el orden
        ) 