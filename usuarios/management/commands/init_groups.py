from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Inicializa los grupos y permisos básicos del sistema'

    def handle(self, *args, **kwargs):
        # Crear grupos
        grupos = {
            'Arquitectos': ['gestionar_usuarios', 'gestionar_proyectos', 'gestionar_materiales', 'gestionar_nomina', 'ver_reportes'],
            'Supervisores': ['gestionar_materiales', 'gestionar_nomina', 'ver_reportes'],
            'Trabajadores': ['ver_reportes']
        }

        for nombre_grupo, permisos in grupos.items():
            grupo, created = Group.objects.get_or_create(name=nombre_grupo)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{nombre_grupo}" creado'))
            
            # Asignar permisos al grupo
            for permiso in permisos:
                try:
                    perm = Permission.objects.get(codename=permiso)
                    grupo.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Permiso "{permiso}" no encontrado'))

        self.stdout.write(self.style.SUCCESS('Grupos y permisos inicializados correctamente')) 