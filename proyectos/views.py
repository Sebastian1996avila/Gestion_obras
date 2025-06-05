from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from .models import Proyecto
from .serializers import ProyectoSerializer
from .forms import ProyectoForm
from datetime import datetime
import os

# Vistas para la API REST
class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [AllowAny]  # Cambiado a AllowAny para desarrollo
    
    def get_queryset(self):
        queryset = Proyecto.objects.all()
        
        # Filtros
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
            
        # Búsqueda por nombre o descripción
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(nombre__icontains=search) |
                models.Q(descripcion__icontains=search)
            )
            
        # Filtro por fecha
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_inicio__lte=fecha_fin)
            
        return queryset.order_by('-fecha_inicio')

    def perform_create(self, serializer):
        try:
            # Validaciones adicionales
            data = serializer.validated_data
            if data.get('fecha_fin') and data['fecha_fin'] < data['fecha_inicio']:
                raise ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio')
            
            if data.get('presupuesto', 0) < 0:
                raise ValidationError('El presupuesto no puede ser negativo')
            
            # Asegurarse de que el directorio media/proyectos existe
            media_dir = os.path.join('media', 'proyectos')
            if not os.path.exists(media_dir):
                os.makedirs(media_dir)
                
            serializer.save()
        except DjangoValidationError as e:
            raise ValidationError(str(e))

    def perform_update(self, serializer):
        try:
            # Validaciones adicionales
            data = serializer.validated_data
            if data.get('fecha_fin') and data.get('fecha_inicio') and data['fecha_fin'] < data['fecha_inicio']:
                raise ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio')
            
            if data.get('presupuesto') is not None and data['presupuesto'] < 0:
                raise ValidationError('El presupuesto no puede ser negativo')
            
            # Si hay una nueva foto, eliminar la anterior
            instance = serializer.instance
            if instance and instance.foto and 'foto' in data and data['foto'] != instance.foto:
                if os.path.isfile(instance.foto.path):
                    os.remove(instance.foto.path)
            
            serializer.save()
        except DjangoValidationError as e:
            raise ValidationError(str(e))

    def perform_destroy(self, instance):
        # Eliminar la foto si existe
        if instance.foto:
            if os.path.isfile(instance.foto.path):
                os.remove(instance.foto.path)
        instance.delete()

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        try:
            total_proyectos = Proyecto.objects.count()
            proyectos_por_estado = {
                estado[0]: Proyecto.objects.filter(estado=estado[0]).count()
                for estado in Proyecto.ESTADOS
            }
            
            # Calcular estadísticas adicionales
            proyectos_activos = Proyecto.objects.filter(activo=True).count()
            proyectos_completados = Proyecto.objects.filter(estado='COM').count()
            presupuesto_total = Proyecto.objects.aggregate(
                total=models.Sum('presupuesto')
            )['total'] or 0
            
            return Response({
                'total_proyectos': total_proyectos,
                'proyectos_por_estado': proyectos_por_estado,
                'proyectos_activos': proyectos_activos,
                'proyectos_completados': proyectos_completados,
                'presupuesto_total': presupuesto_total
            })
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Vistas para la interfaz web
def proyecto_list(request):
    try:
        proyectos = Proyecto.objects.all().order_by('-fecha_inicio')
        if request.headers.get('Accept') == 'application/json':
            serializer = ProyectoSerializer(proyectos, many=True, context={'request': request})
            return JsonResponse(serializer.data, safe=False)
        return render(request, 'proyectos/proyecto_list.html', {'proyectos': proyectos})
    except Exception as e:
        messages.error(request, f'Error al cargar los proyectos: {str(e)}')
        return render(request, 'proyectos/proyecto_list.html', {'proyectos': []})

def proyecto_detail(request, pk):
    try:
        proyecto = get_object_or_404(Proyecto, pk=pk)
        if request.headers.get('Accept') == 'application/json':
            serializer = ProyectoSerializer(proyecto)
            return JsonResponse(serializer.data)
        return render(request, 'proyectos/proyecto_detail.html', {'proyecto': proyecto})
    except Exception as e:
        messages.error(request, f'Error al cargar el proyecto: {str(e)}')
        return redirect('proyecto_list')

def proyecto_create(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                proyecto = form.save()
                messages.success(request, 'Proyecto creado exitosamente.')
                return redirect('proyecto_detail', pk=proyecto.pk)
            except Exception as e:
                messages.error(request, f'Error al crear el proyecto: {str(e)}')
    else:
        form = ProyectoForm()
    return render(request, 'proyectos/proyecto_form.html', {'form': form})

def proyecto_update(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Proyecto actualizado exitosamente.')
                return redirect('proyecto_detail', pk=proyecto.pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar el proyecto: {str(e)}')
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'proyectos/proyecto_form.html', {'form': form, 'proyecto': proyecto})

def proyecto_delete(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        try:
            proyecto.delete()
            messages.success(request, 'Proyecto eliminado exitosamente.')
            return redirect('proyecto_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar el proyecto: {str(e)}')
    return render(request, 'proyectos/proyecto_confirm_delete.html', {'proyecto': proyecto})

@api_view(['GET'])
@permission_classes([AllowAny])  # Cambiado a AllowAny para desarrollo
def get_estadisticas(request):
    try:
        total_proyectos = Proyecto.objects.count()
        proyectos_por_estado = {
            estado[0]: Proyecto.objects.filter(estado=estado[0]).count()
            for estado in Proyecto.ESTADOS
        }
        return Response({
            'total_proyectos': total_proyectos,
            'proyectos_por_estado': proyectos_por_estado
        })
    except Exception as e:
        return Response(
            {'error': f'Error al obtener estadísticas: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
