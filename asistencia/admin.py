from django.contrib import admin
from .models import RegistroAsistencia

@admin.register(RegistroAsistencia)
class RegistroAsistenciaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'hora', 'tipo', 'ubicacion', 'creado_en')
    list_filter = ('tipo', 'fecha', 'usuario')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'ubicacion')
    date_hierarchy = 'fecha'
    ordering = ('-fecha', '-hora')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si el usuario es supervisor o arquitecto, puede ver todos los registros
        if request.user.es_supervisor or request.user.es_arquitecto:
            return qs
        # Si no, solo puede ver sus propios registros
        return qs.filter(usuario=request.user)
