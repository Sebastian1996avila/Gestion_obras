from rest_framework import serializers
from .models import Proyecto
from usuarios.serializers import UsuarioSerializer
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class ProyectoSerializer(serializers.ModelSerializer):
    responsable_info = UsuarioSerializer(source='responsable', read_only=True)
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'estado',
            'presupuesto',
            'activo',
            'foto',
            'foto_url',
            'responsable',
            'responsable_info',
            'asignados',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
        extra_kwargs = {
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
