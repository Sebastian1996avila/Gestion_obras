from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Proyecto(models.Model):
    ESTADOS = [
        ('PLAN', 'Planificado'),
        ('EJE', 'En Ejecución'),
        ('SUS', 'Suspendido'),
        ('COM', 'Completado'),
        ('CAN', 'Cancelado'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PLAN')
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='proyectos/', null=True, blank=True)
    responsable = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proyectos_responsable'
    )
    asignados = models.ManyToManyField(
        'usuarios.Usuario',
        related_name='proyectos_asignados',
        blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.nombre