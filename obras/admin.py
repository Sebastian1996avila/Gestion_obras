from django.contrib import admin
from .models import Obra

@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'proyecto', 'direccion', 'estado', 'avance', 'supervisor', 'arquitecto')
    list_filter = ('estado', 'avance', 'supervisor', 'arquitecto')
    search_fields = ('nombre', 'proyecto__nombre', 'direccion', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    filter_horizontal = ('trabajadores',)
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'proyecto', 'descripcion', 'direccion', 'estado')
        }),
        ('Personal', {
            'fields': ('supervisor', 'arquitecto', 'trabajadores')
        }),
        ('Fechas y Presupuesto', {
            'fields': ('fecha_inicio', 'fecha_fin', 'presupuesto', 'avance')
        }),
        ('Documentación', {
            'fields': ('notas', 'foto')
        }),
        ('Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )