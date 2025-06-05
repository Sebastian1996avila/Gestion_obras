from rest_framework import serializers
from .models import Nomina
from usuarios.serializers import UsuarioSerializer
from datetime import datetime
import calendar
from decimal import Decimal

class NominaSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()
    ultimo_cambio_por_nombre = serializers.SerializerMethodField()
    valor_horas_extras = serializers.SerializerMethodField()
    periodo_display = serializers.SerializerMethodField()
    empleado_id = serializers.IntegerField(source='empleado.id', read_only=True)
    
    class Meta:
        model = Nomina
        fields = [
            'id',
            'empleado',
            'empleado_id',
            'empleado_nombre',
            'periodo',
            'periodo_display',
            'dias_trabajados',
            'sueldo_base',
            'horas_extras',
            'valor_horas_extras',
            'bonificaciones',
            'deducciones',
            'total',
            'estado',
            'comentario',
            'ultimo_cambio_por',
            'ultimo_cambio_por_nombre',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = [
            'total',
            'valor_horas_extras',
            'ultimo_cambio_por',
            'fecha_creacion',
            'fecha_actualizacion',
            'empleado_id'
        ]
    
    def get_empleado_nombre(self, obj):
        try:
            if obj.empleado:
                return f"{obj.empleado.get_full_name()} ({obj.empleado.get_rol_display()})"
            return str(obj.empleado)
        except Exception:
            return str(obj.empleado)
    
    def get_ultimo_cambio_por_nombre(self, obj):
        try:
            if obj.ultimo_cambio_por:
                return obj.ultimo_cambio_por.get_full_name()
            return None
        except Exception:
            return None
    
    def get_valor_horas_extras(self, obj):
        try:
            if obj.sueldo_base and obj.horas_extras:
                valor_hora_normal = Decimal(str(obj.sueldo_base)) / (Decimal('30') * Decimal('8'))
                return obj.horas_extras * valor_hora_normal * Decimal('1.5')
            return Decimal('0')
        except Exception:
            return Decimal('0')
    
    def get_periodo_display(self, obj):
        try:
            fecha = datetime.strptime(obj.periodo, '%Y-%m')
            return fecha.strftime('%B %Y').capitalize()
        except Exception:
            return obj.periodo
    
    def validate_periodo(self, value):
        try:
            datetime.strptime(value, '%Y-%m')
        except ValueError:
            raise serializers.ValidationError('El período debe tener el formato YYYY-MM')
        return value
    
    def validate_dias_trabajados(self, value):
        if value <= 0:
            raise serializers.ValidationError('Los días trabajados deben ser mayores a 0')
        return value
    
    def validate_sueldo_base(self, value):
        if value <= 0:
            raise serializers.ValidationError('El sueldo base debe ser mayor a 0')
        return value
    
    def validate_horas_extras(self, value):
        if value < 0:
            raise serializers.ValidationError('Las horas extras no pueden ser negativas')
        return value
    
    def validate(self, data):
        # Validar días trabajados según el mes
        if 'periodo' in data and 'dias_trabajados' in data:
            try:
                year, month = map(int, data['periodo'].split('-'))
                dias_en_mes = calendar.monthrange(year, month)[1]
                if data['dias_trabajados'] > dias_en_mes:
                    raise serializers.ValidationError({
                        'dias_trabajados': f'Los días trabajados no pueden ser mayores a {dias_en_mes} para el mes seleccionado'
                    })
            except (ValueError, AttributeError):
                pass
        
        # Validar horas extras según días trabajados
        if 'dias_trabajados' in data and 'horas_extras' in data:
            max_horas = data['dias_trabajados'] * 4  # Máximo 4 horas extras por día
            if data['horas_extras'] > max_horas:
                raise serializers.ValidationError({
                    'horas_extras': f'Las horas extras no pueden ser mayores a {max_horas} para {data["dias_trabajados"]} días trabajados'
                })
        
        return data 