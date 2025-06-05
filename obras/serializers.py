from rest_framework import serializers
from .models import Obra
from proyectos.serializers import ProyectoSerializer
from usuarios.serializers import UserBasicSerializer
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class ObraSerializer(serializers.ModelSerializer):
    proyecto = ProyectoSerializer(read_only=True)
    supervisor = UserBasicSerializer(read_only=True)
    arquitecto = UserBasicSerializer(read_only=True)
    trabajadores = UserBasicSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    foto_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Obra
        fields = [
            'id',
            'nombre',
            'proyecto',
            'direccion',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'presupuesto',
            'estado',
            'estado_display',
            'avance',
            'foto',
            'foto_url',
            'supervisor',
            'arquitecto',
            'trabajadores',
            'notas',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
        extra_kwargs = {
            'supervisor': {'write_only': True},
            'arquitecto': {'write_only': True},
            'trabajadores': {'write_only': True},
            'foto': {
                'validators': [
                    FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
                ]
            }
        }

    def get_foto_url(self, obj):
        if obj.foto:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.foto.url)
            return obj.foto.url
        return None

    def validate_foto(self, value):
        if value:
            # Validar tamaño máximo (5MB)
            if value.size > 5 * 1024 * 1024:
                raise ValidationError("El tamaño máximo permitido es 5MB")
            
            # Validar tipo de archivo
            content_type = value.content_type.split('/')[0]
            if content_type != 'image':
                raise ValidationError("El archivo debe ser una imagen")
        return value

    def validate_presupuesto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El presupuesto debe ser mayor a 0")
        return value

    def validate_avance(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El avance debe estar entre 0 y 100")
        return value

    def validate(self, data):
        if data.get('fecha_fin') and data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError("La fecha de fin no puede ser anterior a la de inicio")
        return data

class ObraCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obra
        fields = [
            'nombre',
            'proyecto',
            'direccion',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'presupuesto',
            'estado',
            'avance',
            'foto',
            'supervisor',
            'arquitecto',
            'trabajadores',
            'notas'
        ]
        extra_kwargs = {
            'foto': {
                'validators': [
                    FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
                ]
            }
        }

    def validate_foto(self, value):
        if value:
            # Validar tamaño máximo (5MB)
            if value.size > 5 * 1024 * 1024:
                raise ValidationError("El tamaño máximo permitido es 5MB")
            
            # Validar tipo de archivo
            content_type = value.content_type.split('/')[0]
            if content_type != 'image':
                raise ValidationError("El archivo debe ser una imagen")
        return value

    def validate_presupuesto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El presupuesto debe ser mayor a 0")
        return value

    def validate_avance(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El avance debe estar entre 0 y 100")
        return value

    def validate(self, data):
        if data.get('fecha_fin') and data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError("La fecha de fin no puede ser anterior a la de inicio")
        return data