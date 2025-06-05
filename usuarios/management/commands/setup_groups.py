from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from Usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Configura los grupos y permisos por defecto del sistema'

    def handle(self, *args, **kwargs):
        # Crear grupos
        arquitectos, _ = Group.objects.get_or_create(name='Arquitectos')
        supervisores, _ = Group.objects.get_or_create(name='Supervisores')
        trabajadores, _ = Group.objects.get_or_create(name='Trabajadores')

        # Obtener todos los permisos del modelo Usuario
        content_type = ContentType.objects.get_for_model(Usuario)
        permisos = Permission.objects.filter(content_type=content_type)

        # Asignar permisos a grupos
        # Arquitectos tienen todos los permisos
        for permiso in permisos:
            arquitectos.permissions.add(permiso)

        # Supervisores pueden gestionar proyectos y materiales
        supervisores.permissions.add(
            Permission.objects.get(codename='gestionar_proyectos'),
            Permission.objects.get(codename='gestionar_materiales'),
            Permission.objects.get(codename='ver_reportes')
        )

        # Trabajadores solo pueden ver reportes
        trabajadores.permissions.add(
            Permission.objects.get(codename='ver_reportes')
        )

        self.stdout.write(self.style.SUCCESS('Grupos y permisos configurados exitosamente')) 