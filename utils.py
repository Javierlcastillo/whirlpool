from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin que restringe el acceso solo a superusuarios."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, "Acceso denegado. Solo administradores tienen permiso para acceder.")
        return redirect('login')