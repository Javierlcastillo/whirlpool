from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Permite acceso de lectura a cualquier usuario autenticado,
    pero requiere ser administrador para operaciones de escritura.
    """

    def has_permission(self, request, view):
        # Permitir operaciones de lectura (GET, HEAD, OPTIONS) para usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Requerir ser administrador para operaciones de escritura
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite a un técnico acceder a sus propios datos, o a administradores acceder a cualquier dato.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permitir acceso a administradores
        if request.user.is_superuser:
            return True
            
        # Permitir que los técnicos accedan a sus propios datos
        # Este método asume que hay una relación entre el objeto y el usuario
        # Ajustar según la estructura específica de los modelos
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'technician') and hasattr(obj.technician, 'user'):
            return obj.technician.user == request.user
            
        return False