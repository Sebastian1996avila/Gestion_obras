from django.contrib import admin
from .models import Material, CategoriaMaterial, Proveedor

@admin.register(CategoriaMaterial)
class CategoriaMaterialAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'orden', 'activa')
    list_filter = ('activa',)
    search_fields = ('codigo', 'nombre', 'descripcion')
    ordering = ('orden', 'nombre')

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'email')
    search_fields = ('nombre', 'contacto', 'email')
    ordering = ('nombre',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'cantidad', 'unidad_medida', 'precio_unitario', 'stock_minimo')
    list_filter = ('categoria', 'unidad_medida')
    search_fields = ('codigo', 'nombre', 'descripcion', 'ubicacion')
    ordering = ('codigo',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')