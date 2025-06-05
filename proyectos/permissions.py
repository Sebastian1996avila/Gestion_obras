from rest_framework import permissions

class EsCreadorDelProyecto(permissions.BasePermission):
    """Permiso que solo permite al creador del proyecto modificarlo"""
    
    def has_object_permission(self, request, view, obj):
        # Los supervisores y arquitectos pueden editar cualquier proyecto
        if request.user.rol in ['SUP', 'ARQ']:
            return True
        # Los trabajadores solo pueden ver proyectos asignados
        return obj.creado_por == request.user