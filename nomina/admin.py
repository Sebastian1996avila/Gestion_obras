from django.contrib import admin
from .models import Nomina, Pago

@admin.register(Nomina)
class NominaAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'periodo', 'dias_trabajados', 'sueldo_base', 'total', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'periodo', 'fecha_creacion')
    search_fields = ('empleado__username', 'periodo')
    ordering = ('-fecha_creacion',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'horas_trabajadas', 'fecha_pago')
    list_filter = ('fecha_pago',)
    search_fields = ('trabajador__username',)
    ordering = ('-fecha_pago',)