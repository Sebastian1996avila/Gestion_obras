from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('ARQ', 'Arquitecto'),
        ('SUP', 'Supervisor'),
        ('TRA', 'Trabajador'),
    )
    
    rol = models.CharField(max_length=3, choices=ROLES, default='TRA')
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    fecha_contratacion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    # Relaciones con grupos y permisos
    groups = models.ManyToManyField(
        Group,
        verbose_name='grupos',
        blank=True,
        help_text='Los grupos a los que pertenece este usuario.',
        related_name="usuarios_groups",
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='permisos de usuario',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        related_name="usuarios_permissions",
        related_query_name="usuario",
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        permissions = [
            ('gestionar_usuarios', 'Puede gestionar usuarios'),
            ('gestionar_proyectos', 'Puede gestionar proyectos'),
            ('gestionar_materiales', 'Puede gestionar materiales'),
            ('gestionar_nomina', 'Puede gestionar nómina'),
            ('ver_reportes', 'Puede ver reportes'),
            ('gestionar_asistencias', 'Puede gestionar asistencias'),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    @property
    def es_arquitecto(self):
        return self.rol == 'ARQ'

    @property
    def es_supervisor(self):
        return self.rol == 'SUP'

    @property
    def es_trabajador(self):
        return self.rol == 'TRA'