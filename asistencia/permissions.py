from rest_framework import permissions

class PuedeGestionarAsistencias(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario puede gestionar asistencias.
    Solo los supervisores y arquitectos pueden gestionar asistencias.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.es_supervisor or request.user.es_arquitecto)

    def has_object_permission(self, request, view, obj):
        # Verificar si el usuario es supervisor o arquitecto
        if not (request.user.es_supervisor or request.user.es_arquitecto):
            return False
        
        # Si es supervisor o arquitecto, puede gestionar cualquier registro
        return True 