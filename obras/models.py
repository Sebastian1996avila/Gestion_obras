from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from proyectos.models import Proyecto

class Obra(models.Model):
    ESTADO_CHOICES = [
        ('PLAN', 'Planificación'),
        ('PROG', 'En progreso'),
        ('SUSP', 'Suspendido'),
        ('COMP', 'Completado'),
    ]
    
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='obras',
        verbose_name="Proyecto asociado"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la obra")
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    direccion = models.TextField(verbose_name="Dirección")
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'SUP'},
        related_name='obras_supervisadas',
        verbose_name="Supervisor"
    )
    arquitecto = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'ARQ'},
        related_name='obras_disenadas',
        verbose_name="Arquitecto"
    )
    trabajadores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'rol': 'TEC'},
        related_name='obras_asignadas',
        blank=True,
        verbose_name="Trabajadores"
    )
    estado = models.CharField(
        max_length=4,
        choices=ESTADO_CHOICES,
        default='PLAN',
        verbose_name="Estado"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha de finalización"
    )
    presupuesto = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Presupuesto"
    )
    avance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje de avance"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas y observaciones"
    )
    foto = models.ImageField(
        upload_to='obras/',
        null=True,
        blank=True,
        verbose_name="Foto de la obra"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    def __str__(self):
        return f"{self.nombre} - {self.proyecto.nombre}"

    def get_estado_display(self):
        return dict(self.ESTADO_CHOICES).get(self.estado, self.estado)

    def save(self, *args, **kwargs):
        if self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha de finalización no puede ser anterior a la fecha de inicio")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Obra"
        verbose_name_plural = "Obras"
        ordering = ['-fecha_creacion']
        app_label = 'obras'