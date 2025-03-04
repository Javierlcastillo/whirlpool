from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Technician(models.Model):
    """Modelo para técnicos (usuarios del sistema)."""
    REGION_CHOICES = [
        ('norte', 'Norte'),
        ('sur', 'Sur'),
        ('este', 'Este'),
        ('oeste', 'Oeste'),
        ('centro', 'Centro'),
        ('noroeste', 'Noroeste'),
        ('noreste', 'Noreste'),
        ('suroeste', 'Suroeste'),
        ('sureste', 'Sureste'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='technician',
        verbose_name='Usuario'
    )
    employee_number = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Número de empleado'
    )
    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        default='centro',
        verbose_name='Región'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    
    class Meta:
        verbose_name = 'Técnico'
        verbose_name_plural = 'Técnicos'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_number})"
    
    def get_absolute_url(self):
        return reverse('technician-detail', kwargs={'pk': self.pk})
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username