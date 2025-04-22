from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a administradores realizar operaciones
    de escritura, mientras que a los usuarios normales se les permite realizar solo
    operaciones de lectura.
    """

    def has_permission(self, request, view):
        # Permitir operaciones GET, HEAD y OPTIONS para cualquier usuario
        if request.method in permissions.SAFE_METHODS:
            return True

        # Las operaciones de escritura solo para administradores
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Permitir operaciones GET, HEAD y OPTIONS para cualquier usuario
        if request.method in permissions.SAFE_METHODS:
            return True

        # Las operaciones de escritura solo para administradores
        return request.user and request.user.is_staff 