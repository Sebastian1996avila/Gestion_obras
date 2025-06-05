from rest_framework import permissions

class BaseRolPermission(permissions.BasePermission):
    roles_permitidos = []
    
    def has_permission(self, request, view):
        return request.user.rol in self.roles_permitidos

class EsArquitecto(BaseRolPermission):
    roles_permitidos = ['ARQ']

class EsSupervisor(BaseRolPermission):
    roles_permitidos = ['SUP']

class EsTrabajador(BaseRolPermission):
    roles_permitidos = ['TRA']

class EsSupervisorOArquitecto(BaseRolPermission):
    roles_permitidos = ['SUP', 'ARQ']

class TienePermisoEspecifico(permissions.BasePermission):
    def __init__(self, permiso_requerido):
        self.permiso_requerido = permiso_requerido

    def has_permission(self, request, view):
        return request.user.has_perm(self.permiso_requerido)

class PuedeGestionarUsuarios(TienePermisoEspecifico):
    def __init__(self):
        super().__init__('usuarios.gestionar_usuarios')

class PuedeGestionarProyectos(TienePermisoEspecifico):
    def __init__(self):
        super().__init__('usuarios.gestionar_proyectos')

class PuedeGestionarMateriales(TienePermisoEspecifico):
    def __init__(self):
        super().__init__('usuarios.gestionar_materiales')

class PuedeGestionarNomina(TienePermisoEspecifico):
    def __init__(self):
        super().__init__('usuarios.gestionar_nomina')

class PuedeVerReportes(TienePermisoEspecifico):
    def __init__(self):
        super().__init__('usuarios.ver_reportes')

class PuedeGestionarAsistencias(TienePermisoEspecifico):
    def __init__(self):
        super().__init__('usuarios.gestionar_asistencias')