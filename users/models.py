# users/models.py

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
    
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='technician',
        verbose_name='Usuario'
    )
    name = models.CharField(max_length=200, verbose_name='Nombre', blank=True)
    employee_number = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Número de empleado'
    )
    region = models.ForeignKey(
        'courses.Region',  # Referencia por string para evitar importación circular
        on_delete=models.SET_NULL,
        null=True,
        related_name='technicians',
        verbose_name='Región'
    )
    password = models.CharField(max_length=128, verbose_name='Contraseña', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    
    class Meta:
        verbose_name = 'Técnico'
        verbose_name_plural = 'Técnicos'
    
    def __str__(self):
        return f"{self.name} ({self.employee_number})"
    
    def get_absolute_url(self):
        return reverse('technician-detail', kwargs={'pk': self.pk})
    
    def get_full_name(self):
        if self.name:
            return self.name
        return self.user.get_full_name() or self.user.username
        
    def save(self, *args, **kwargs):
        # Si no hay nombre asignado, usar el del usuario
        if not self.name and self.user:
            self.name = self.user.get_full_name()
        super().save(*args, **kwargs)