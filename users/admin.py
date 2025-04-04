from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Technician

class TechnicianInline(admin.StackedInline):
    model = Technician
    can_delete = False
    verbose_name_plural = 'Técnico'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (TechnicianInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_region')
    list_select_related = ('technician',)

    def get_region(self, instance):
        return instance.technician.region
    get_region.short_description = 'Región'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_empleado', 'region', 'is_active')
    list_filter = ('region', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'numero_empleado')
    raw_id_fields = ('user',)