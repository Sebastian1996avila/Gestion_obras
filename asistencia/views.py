# asistencia/views.py
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from .models import RegistroAsistencia
from .serializers import RegistroAsistenciaSerializer
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from usuarios.models import Usuario
from rest_framework import serializers
from .permissions import PuedeGestionarAsistencias

def index(request):
    return HttpResponse("¡Bienvenido al sistema de asistencia!")  # Mensaje básico
    # O si usas templates:
    # return render(request, 'asistencia/index.html', {})

class RegistroAsistenciaCreateView(generics.CreateAPIView):
    queryset = RegistroAsistencia.objects.all()
    serializer_class = RegistroAsistenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Usar el usuario autenticado
            usuario = request.user

            # Preparar los datos para el serializer
            data = request.data.copy()
            if 'fecha' not in data:
                data['fecha'] = timezone.now().date()
            if 'hora' not in data:
                data['hora'] = timezone.now().time()

            # Validar que no exista un registro similar
            tipo = data.get('tipo')
            fecha = data.get('fecha')
            
            # Convertir la fecha a objeto date si es string
            if isinstance(fecha, str):
                fecha = timezone.datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # Verificar si ya existe un registro
            registro_existente = RegistroAsistencia.objects.filter(
                usuario=usuario,
                fecha=fecha,
                tipo=tipo
            ).first()
            
            if registro_existente:
                return Response(
                    {
                        "error": f"Ya existe un registro de {tipo} para este usuario en esta fecha",
                        "registro_existente": RegistroAsistenciaSerializer(registro_existente).data
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear el registro
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except serializers.ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al crear el registro: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class RegistroAsistenciaListView(generics.ListAPIView):
    serializer_class = RegistroAsistenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        queryset = RegistroAsistencia.objects.filter(usuario=usuario)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
            
        return queryset

class RegistroAsistenciaAdminListView(generics.ListAPIView):
    serializer_class = RegistroAsistenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo supervisores y arquitectos pueden ver todos los registros
        if not (self.request.user.es_supervisor or self.request.user.es_arquitecto):
            return RegistroAsistencia.objects.none()
            
        usuario_id = self.request.query_params.get('usuario_id')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        queryset = RegistroAsistencia.objects.all()
        
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
            
        return queryset

class ResumenAsistenciaView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin') or timezone.now().date()
        
        if not fecha_inicio:
            fecha_inicio = fecha_fin - timedelta(days=30)
            
        registros = RegistroAsistencia.objects.filter(
            fecha__range=[fecha_inicio, fecha_fin]
        )
        
        if not (request.user.es_supervisor or request.user.es_arquitecto):
            registros = registros.filter(usuario=request.user)
            
        resumen = {}
        for registro in registros:
            fecha_str = registro.fecha.strftime('%Y-%m-%d')
            if fecha_str not in resumen:
                resumen[fecha_str] = {
                    'entrada': None,
                    'salida': None,
                    'horas_trabajadas': None
                }
            
            if registro.tipo == 'ENT':
                resumen[fecha_str]['entrada'] = registro.hora.strftime('%H:%M')
            elif registro.tipo == 'SAL':
                resumen[fecha_str]['salida'] = registro.hora.strftime('%H:%M')
                
                # Calcular horas trabajadas si tenemos entrada y salida
                if resumen[fecha_str]['entrada']:
                    entrada = datetime.strptime(resumen[fecha_str]['entrada'], '%H:%M')
                    salida = datetime.strptime(resumen[fecha_str]['salida'], '%H:%M')
                    horas_trabajadas = (salida - entrada).total_seconds() / 3600
                    resumen[fecha_str]['horas_trabajadas'] = round(horas_trabajadas, 2)
        
        return Response(resumen)

class RegistroAsistenciaViewSet(viewsets.ModelViewSet):
    queryset = RegistroAsistencia.objects.all()
    serializer_class = RegistroAsistenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), PuedeGestionarAsistencias()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = RegistroAsistencia.objects.all()
        
        # Si no es supervisor o arquitecto, solo ver sus registros
        if not (self.request.user.es_supervisor or self.request.user.es_arquitecto):
            queryset = queryset.filter(usuario=self.request.user)
            
        # Filtrar por fechas si se proporcionan
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
            
        return queryset.order_by('-fecha', '-hora')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()