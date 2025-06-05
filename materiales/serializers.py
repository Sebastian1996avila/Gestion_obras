from rest_framework import serializers
from .models import Material, CategoriaMaterial, Proveedor
from django.core.validators import MinValueValidator
from decimal import Decimal

class CategoriaMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaMaterial
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'color', 'orden', 'activa']
        read_only_fields = ['id']

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'contacto', 'telefono', 'email', 'direccion']
        read_only_fields = ['id']

class MaterialSerializer(serializers.ModelSerializer):
    # Campos calculados o personalizados
    estado_stock = serializers.SerializerMethodField(read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaMaterial.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Material
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'categoria',
            'categoria_nombre',
            'cantidad',
            'unidad_medida',
            'precio_unitario',
            'stock_minimo',
            'estado_stock',
            'ubicacion',
            'proveedor',
            'proveedor_nombre',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def get_estado_stock(self, obj):
        """Calcula el estado del stock basado en la cantidad y stock mínimo"""
        if obj.cantidad <= 0:
            return 'Agotado'
        elif obj.cantidad < obj.stock_minimo * Decimal('0.3'):
            return 'Crítico'
        elif obj.cantidad < obj.stock_minimo:
            return 'Bajo'
        else:
            return 'Disponible'

    def validate_cantidad(self, value):
        """Valida que la cantidad no sea negativa"""
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa")
        return value

    def validate_precio_unitario(self, value):
        """Valida que el precio unitario no sea negativo"""
        if value < 0:
            raise serializers.ValidationError("El precio unitario no puede ser negativo")
        return value

    def validate_stock_minimo(self, value):
        """Valida que el stock mínimo no sea negativo"""
        if value < 0:
            raise serializers.ValidationError("El stock mínimo no puede ser negativo")
        return value 