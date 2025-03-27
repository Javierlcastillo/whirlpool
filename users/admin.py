from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Technician

class TechnicianInline(admin.StackedInline):
    model = Technician
    can_delete = False
    verbose_name = 'Técnico'
    verbose_name_plural = 'Técnico'

class UserAdmin(BaseUserAdmin):
    inlines = [TechnicianInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_employee_number']
    
    def get_employee_number(self, obj):
        try:
            return obj.technician.employee_number
        except Technician.DoesNotExist:
            return '-'
    
    get_employee_number.short_description = 'Número de Empleado'

# Re-registrar el modelo User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Registrar el modelo Technician directamente si necesitamos acceso rápido
@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_number', 'region']
    list_filter = ['region']
    search_fields = ['employee_number', 'user__first_name', 'user__last_name', 'user__email']