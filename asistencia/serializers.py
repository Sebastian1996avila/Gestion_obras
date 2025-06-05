from rest_framework import serializers
from .models import RegistroAsistencia
from usuarios.serializers import UserBasicSerializer
from django.utils import timezone
from usuarios.models import Usuario

class RegistroAsistenciaSerializer(serializers.ModelSerializer):
    usuario = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = RegistroAsistencia
        fields = [
            'id', 'usuario', 'fecha', 'hora', 
            'tipo', 'ubicacion', 'observaciones', 'creado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'usuario']

    def validate(self, data):
        # Validar que no se registre más de una entrada o salida por día
        fecha = data.get('fecha')
        tipo = data.get('tipo')
        
        # Convertir la fecha a objeto date si es string
        if isinstance(fecha, str):
            try:
                fecha = timezone.datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                raise serializers.ValidationError("Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Validar el tipo de registro
        if tipo not in dict(RegistroAsistencia.TIPOS_REGISTRO):
            raise serializers.ValidationError(f"Tipo de registro inválido. Debe ser uno de: {', '.join(dict(RegistroAsistencia.TIPOS_REGISTRO).keys())}")
        
        return data

    def create(self, validated_data):
        try:
            # Asegurarse de que la fecha sea un objeto date
            if 'fecha' not in validated_data:
                validated_data['fecha'] = timezone.now().date()
            elif isinstance(validated_data['fecha'], str):
                validated_data['fecha'] = timezone.datetime.strptime(validated_data['fecha'], '%Y-%m-%d').date()
            
            # Asegurarse de que la hora sea un objeto time
            if 'hora' not in validated_data:
                validated_data['hora'] = timezone.now().time()
            elif isinstance(validated_data['hora'], str):
                try:
                    validated_data['hora'] = timezone.datetime.strptime(validated_data['hora'], '%H:%M:%S').time()
                except ValueError:
                    try:
                        validated_data['hora'] = timezone.datetime.strptime(validated_data['hora'], '%H:%M').time()
                    except ValueError:
                        raise serializers.ValidationError("Formato de hora inválido. Use HH:MM o HH:MM:SS")
            
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error al crear el registro: {str(e)}") 