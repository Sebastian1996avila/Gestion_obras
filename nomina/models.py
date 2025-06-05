from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from usuarios.models import Usuario
import calendar
from datetime import datetime
from decimal import Decimal

# Create your models here.

class Nomina(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Pagado', 'Pagado'),
        ('Cancelado', 'Cancelado'),
    ]

    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'TRA'})
    periodo = models.CharField(max_length=7)  # Formato: "YYYY-MM"
    dias_trabajados = models.DecimalField(max_digits=5, decimal_places=2)
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2)
    horas_extras = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bonificaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deducciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    ultimo_cambio_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='nominas_modificadas'
    )
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Nómina de {self.empleado} - {self.periodo}"

    class Meta:
        verbose_name = "Nómina"
        verbose_name_plural = "Nóminas"
        ordering = ['-fecha_creacion']
        permissions = [
            ("can_process_nomina", "Puede procesar nóminas"),
            ("can_cancel_nomina", "Puede cancelar nóminas"),
        ]

    def clean(self):
        # Validar formato del período
        try:
            datetime.strptime(self.periodo, '%Y-%m')
        except ValueError:
            raise ValidationError({'periodo': 'El período debe tener el formato YYYY-MM'})

        # Validar días trabajados
        year, month = map(int, self.periodo.split('-'))
        dias_en_mes = calendar.monthrange(year, month)[1]
        if self.dias_trabajados > dias_en_mes:
            raise ValidationError({
                'dias_trabajados': f'Los días trabajados no pueden ser mayores a {dias_en_mes} para el mes seleccionado'
            })

        # Validar sueldo base
        if self.sueldo_base <= 0:
            raise ValidationError({'sueldo_base': 'El sueldo base debe ser mayor a 0'})

        # Validar horas extras
        if self.horas_extras < 0:
            raise ValidationError({'horas_extras': 'Las horas extras no pueden ser negativas'})
        
        # Validar que las horas extras sean razonables (máximo 4 horas por día)
        max_horas_extras = self.dias_trabajados * 4
        if self.horas_extras > max_horas_extras:
            raise ValidationError({
                'horas_extras': f'Las horas extras no pueden ser mayores a {max_horas_extras} para {self.dias_trabajados} días trabajados'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def can_change_state(self, new_state, user):
        if self.estado == 'Pagado' and new_state != 'Pagado':
            return False, 'No se puede modificar una nómina ya pagada'
        if self.estado == 'Cancelado':
            return False, 'No se puede modificar una nómina cancelada'
        if new_state == 'Pagado' and not user.has_perm('nomina.can_process_nomina'):
            return False, 'No tiene permiso para procesar nóminas'
        if new_state == 'Cancelado' and not user.has_perm('nomina.can_cancel_nomina'):
            return False, 'No tiene permiso para cancelar nóminas'
        return True, None

class Pago(models.Model):
    trabajador = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'TRA'})
    horas_trabajadas = models.DecimalField(max_digits=6, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de {self.trabajador} - {self.fecha_pago.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_pago']