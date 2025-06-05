from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, F
from decimal import Decimal
from .models import Material, CategoriaMaterial, Proveedor
from .serializers import MaterialSerializer, CategoriaMaterialSerializer, ProveedorSerializer
import logging
from django.core.exceptions import ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_queryset(self):
        try:
            queryset = Material.objects.all()
            
            # Filtros
            categoria = self.request.query_params.get('categoria', None)
            if categoria:
                queryset = queryset.filter(categoria=categoria)
                
            # Búsqueda por nombre o descripción
            search = self.request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(
                    models.Q(nombre__icontains=search) |
                    models.Q(descripcion__icontains=search) |
                    models.Q(codigo__icontains=search)
                )
                
            return queryset.select_related('categoria', 'proveedor')
        except Exception as e:
            logger.error(f"Error al obtener materiales: {str(e)}")
            raise serializers.ValidationError(f"Error al obtener materiales: {str(e)}")

    def perform_create(self, serializer):
        try:
            if not serializer.validated_data.get('nombre'):
                raise serializers.ValidationError("El nombre es requerido")
            
            # Guardar el material
            material = serializer.save()
            logger.info(f"Material creado exitosamente: {material.nombre}")
            return material
        except DjangoValidationError as e:
            logger.error(f"Error de validación al crear material: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Error al crear material: {str(e)}")
            raise serializers.ValidationError(f"Error al crear el material: {str(e)}")

    def perform_update(self, serializer):
        try:
            if not serializer.validated_data.get('nombre'):
                raise serializers.ValidationError("El nombre es requerido")
            
            # Guardar el material
            material = serializer.save()
            logger.info(f"Material actualizado exitosamente: {material.nombre}")
            return material
        except DjangoValidationError as e:
            logger.error(f"Error de validación al actualizar material: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Error al actualizar material: {str(e)}")
            raise serializers.ValidationError(f"Error al actualizar el material: {str(e)}")

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        try:
            total_materiales = Material.objects.count()
            total_valor = Material.objects.aggregate(
                total=Sum(F('cantidad') * F('precio_unitario'))
            )['total'] or 0
            
            stock_bajo = Material.objects.filter(
                cantidad__lt=F('stock_minimo')
            ).count()
            
            stock_critico = Material.objects.filter(
                cantidad__lt=F('stock_minimo') * Decimal('0.3')
            ).count()
            
            materiales_por_categoria = Material.objects.values(
                'categoria__nombre'
            ).annotate(
                total=Count('id')
            ).order_by('-total')
            
            return Response({
                'total_materiales': total_materiales,
                'total_valor': float(total_valor),  # Convertir Decimal a float para serialización
                'stock_bajo': stock_bajo,
                'stock_critico': stock_critico,
                'materiales_por_categoria': list(materiales_por_categoria)  # Convertir QuerySet a lista
            })
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoriaMaterialViewSet(viewsets.ModelViewSet):
    queryset = CategoriaMaterial.objects.all()
    serializer_class = CategoriaMaterialSerializer

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as e:
            logger.error(f"Error de validación al crear categoría: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Error al crear categoría: {str(e)}")
            raise serializers.ValidationError(f"Error al crear la categoría: {str(e)}")

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as e:
            logger.error(f"Error de validación al actualizar categoría: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Error al actualizar categoría: {str(e)}")
            raise serializers.ValidationError(f"Error al actualizar la categoría: {str(e)}")

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as e:
            logger.error(f"Error de validación al crear proveedor: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Error al crear proveedor: {str(e)}")
            raise serializers.ValidationError(f"Error al crear el proveedor: {str(e)}")

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as e:
            logger.error(f"Error de validación al actualizar proveedor: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Error al actualizar proveedor: {str(e)}")
            raise serializers.ValidationError(f"Error al actualizar el proveedor: {str(e)}")
