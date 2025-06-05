# materiales/serializers.py
from rest_framework import serializers
from .models import Material, CategoriaMaterial, Proveedor
from django.core.validators import MinValueValidator

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
        elif obj.cantidad < obj.stock_minimo * 0.3:
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

    def validate(self, data):
        """Validaciones adicionales que involucran múltiples campos"""
        # Validar que el stock mínimo sea menor que la cantidad actual
        if 'stock_minimo' in data and 'cantidad' in data:
            if data['stock_minimo'] > data['cantidad']:
                raise serializers.ValidationError(
                    "El stock mínimo no puede ser mayor que la cantidad actual"
                )
        return data

    def create(self, validated_data):
        """Personalización del proceso de creación"""
        try:
            # Generar código automáticamente si no se proporciona
            if not validated_data.get('codigo'):
                ultimo_material = Material.objects.order_by('-id').first()
                if ultimo_material and ultimo_material.codigo and ultimo_material.codigo.startswith('MAT'):
                    ultimo_numero = int(ultimo_material.codigo[3:])
                    validated_data['codigo'] = f'MAT{str(ultimo_numero + 1).zfill(3)}'
                else:
                    validated_data['codigo'] = 'MAT001'

            # Asegurarse de que los campos numéricos tengan valores por defecto
            if validated_data.get('cantidad') is None:
                validated_data['cantidad'] = 0
            if validated_data.get('precio_unitario') is None:
                validated_data['precio_unitario'] = 0
            if validated_data.get('stock_minimo') is None:
                validated_data['stock_minimo'] = 0

            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error al crear el material: {str(e)}")

    def update(self, instance, validated_data):
        """Personalización del proceso de actualización"""
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
        except Exception as e:
            raise serializers.ValidationError(f"Error al actualizar el material: {str(e)}")