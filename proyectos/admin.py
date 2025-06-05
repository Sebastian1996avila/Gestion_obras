from django.contrib import admin
from .models import Proyecto

class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'presupuesto', 'activo', 'responsable')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('estado', 'activo')

admin.site.register(Proyecto, ProyectoAdmin)