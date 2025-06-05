from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Nomina
from .serializers import NominaSerializer
from decimal import Decimal
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime
from django.db import transaction

class NominaViewSet(viewsets.ModelViewSet):
    queryset = Nomina.objects.all().order_by('-fecha_creacion')
    serializer_class = NominaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'procesar', 'cancelar']:
            return [permissions.IsAuthenticated(), permissions.DjangoModelPermissions()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        try:
            queryset = Nomina.objects.all().order_by('-fecha_creacion')
            periodo = self.request.query_params.get('periodo', None)
            empleado = self.request.query_params.get('empleado', None)
            estado = self.request.query_params.get('estado', None)
            
            if periodo:
                # Validar formato del período
                try:
                    datetime.strptime(periodo, '%Y-%m')
                except ValueError:
                    raise ValidationError('Formato de período inválido. Use YYYY-MM')
                queryset = queryset.filter(periodo=periodo)
                
            if empleado:
                try:
                    empleado_id = int(empleado)
                    queryset = queryset.filter(empleado_id=empleado_id)
                except ValueError:
                    raise ValidationError('ID de empleado inválido')
                    
            if estado:
                if estado not in dict(Nomina.ESTADO_CHOICES):
                    raise ValidationError('Estado inválido')
                queryset = queryset.filter(estado=estado)
                
            return queryset
        except Exception as e:
            raise ValidationError(f"Error al obtener las nóminas: {str(e)}")

    @transaction.atomic
    def perform_create(self, serializer):
        try:
            if not self.request.user.has_perm('usuarios.gestionar_nomina'):
                raise PermissionDenied("No tiene permisos para crear nóminas")

            # Validar período
            periodo = serializer.validated_data.get('periodo')
            if Nomina.objects.filter(empleado=serializer.validated_data['empleado'], periodo=periodo).exists():
                raise ValidationError('Ya existe una nómina para este empleado en el período especificado')

            # Calcular el total antes de guardar
            data = serializer.validated_data
            sueldo_base = Decimal(str(data['sueldo_base']))
            horas_extras = Decimal(str(data.get('horas_extras', 0)))
            bonificaciones = Decimal(str(data.get('bonificaciones', 0)))
            deducciones = Decimal(str(data.get('deducciones', 0)))
            
            # Validar valores negativos
            if any(x < 0 for x in [sueldo_base, horas_extras, bonificaciones, deducciones]):
                raise ValidationError('Los valores no pueden ser negativos')
            
            # Calcular el valor de las horas extras
            valor_hora_normal = sueldo_base / (Decimal('30') * Decimal('8'))
            valor_horas_extras = horas_extras * valor_hora_normal * Decimal('1.5')
            
            # Calcular el total
            total = sueldo_base + valor_horas_extras + bonificaciones - deducciones
            
            if total < 0:
                raise ValidationError('El total no puede ser negativo')
            
            # Guardar con el usuario que realiza la acción
            serializer.save(
                total=total,
                ultimo_cambio_por=self.request.user
            )
        except Exception as e:
            raise ValidationError(f"Error al crear la nómina: {str(e)}")

    @transaction.atomic
    def perform_update(self, serializer):
        try:
            if not self.request.user.has_perm('usuarios.gestionar_nomina'):
                raise PermissionDenied("No tiene permisos para actualizar nóminas")

            instance = serializer.instance
            
            # Verificar si se está cambiando el estado
            if 'estado' in serializer.validated_data:
                nuevo_estado = serializer.validated_data['estado']
                if nuevo_estado not in dict(Nomina.ESTADO_CHOICES):
                    raise ValidationError('Estado inválido')
                
                # Validar transición de estado
                if instance.estado == 'Pagado' and nuevo_estado != 'Pagado':
                    raise ValidationError('No se puede modificar una nómina ya pagada')
            
            # Calcular el total antes de actualizar
            data = serializer.validated_data
            sueldo_base = Decimal(str(data['sueldo_base']))
            horas_extras = Decimal(str(data.get('horas_extras', 0)))
            bonificaciones = Decimal(str(data.get('bonificaciones', 0)))
            deducciones = Decimal(str(data.get('deducciones', 0)))
            
            # Validar valores negativos
            if any(x < 0 for x in [sueldo_base, horas_extras, bonificaciones, deducciones]):
                raise ValidationError('Los valores no pueden ser negativos')
            
            # Calcular el valor de las horas extras
            valor_hora_normal = sueldo_base / (Decimal('30') * Decimal('8'))
            valor_horas_extras = horas_extras * valor_hora_normal * Decimal('1.5')
            
            # Calcular el total
            total = sueldo_base + valor_horas_extras + bonificaciones - deducciones
            
            if total < 0:
                raise ValidationError('El total no puede ser negativo')
            
            # Guardar con el usuario que realiza la acción
            serializer.save(
                total=total,
                ultimo_cambio_por=self.request.user
            )
        except Exception as e:
            raise ValidationError(f"Error al actualizar la nómina: {str(e)}")

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        try:
            if not self.request.user.has_perm('usuarios.ver_reportes'):
                raise PermissionDenied("No tiene permisos para ver estadísticas")

            # Estadísticas generales
            total_nominas = self.get_queryset().count()
            total_pagado = self.get_queryset().filter(estado='Pagado').count()
            total_pendiente = self.get_queryset().filter(estado='Pendiente').count()
            total_cancelado = self.get_queryset().filter(estado='Cancelado').count()
            
            # Totales monetarios
            total_monto = self.get_queryset().aggregate(total=Sum('total'))['total'] or Decimal('0')
            total_pagado_monto = self.get_queryset().filter(estado='Pagado').aggregate(total=Sum('total'))['total'] or Decimal('0')
            total_pendiente_monto = self.get_queryset().filter(estado='Pendiente').aggregate(total=Sum('total'))['total'] or Decimal('0')
            
            # Estadísticas por período
            periodo_actual = timezone.now().strftime('%Y-%m')
            nominas_periodo = self.get_queryset().filter(periodo=periodo_actual)
            total_periodo = nominas_periodo.aggregate(total=Sum('total'))['total'] or Decimal('0')
            
            # Estadísticas por empleado
            empleados_stats = self.get_queryset().values('empleado__username').annotate(
                total_nominas=Count('id'),
                total_monto=Sum('total')
            ).order_by('-total_monto')[:5]
            
            return Response({
                'general': {
                    'total_nominas': total_nominas,
                    'total_pagado': total_pagado,
                    'total_pendiente': total_pendiente,
                    'total_cancelado': total_cancelado
                },
                'montos': {
                    'total_monto': str(total_monto),
                    'total_pagado_monto': str(total_pagado_monto),
                    'total_pendiente_monto': str(total_pendiente_monto)
                },
                'periodo_actual': {
                    'periodo': periodo_actual,
                    'total': str(total_periodo)
                },
                'top_empleados': empleados_stats
            })
        except Exception as e:
            raise ValidationError(f"Error al obtener estadísticas: {str(e)}")

    @action(detail=True, methods=['post'])
    def procesar(self, request, pk=None):
        try:
            if not self.request.user.has_perm('usuarios.gestionar_nomina'):
                raise PermissionDenied("No tiene permisos para procesar nóminas")

            nomina = self.get_object()
            puede_cambiar, mensaje = nomina.can_change_state('Pagado', request.user)
            
            if not puede_cambiar:
                raise PermissionDenied(mensaje)
            
            nomina.estado = 'Pagado'
            nomina.ultimo_cambio_por = request.user
            nomina.save()
            
            serializer = self.get_serializer(nomina)
            return Response(serializer.data)
        except Exception as e:
            raise ValidationError(f"Error al procesar la nómina: {str(e)}")

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        try:
            if not self.request.user.has_perm('usuarios.gestionar_nomina'):
                raise PermissionDenied("No tiene permisos para cancelar nóminas")

            nomina = self.get_object()
            puede_cambiar, mensaje = nomina.can_change_state('Cancelado', request.user)
            
            if not puede_cambiar:
                raise PermissionDenied(mensaje)
            
            nomina.estado = 'Cancelado'
            nomina.ultimo_cambio_por = request.user
            nomina.save()
            
            serializer = self.get_serializer(nomina)
            return Response(serializer.data)
        except Exception as e:
            raise ValidationError(f"Error al cancelar la nómina: {str(e)}") 