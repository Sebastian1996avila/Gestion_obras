from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Obra
from .serializers import ObraSerializer, ObraCreateUpdateSerializer
from usuarios.models import Usuario
from usuarios.permissions import EsSupervisorOArquitecto
from proyectos.models import Proyecto

class ObraViewSet(viewsets.ModelViewSet):
    queryset = Obra.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ObraCreateUpdateSerializer
        return ObraSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            # Verificar que el proyecto existe
            proyecto_id = request.data.get('proyecto')
            if not Proyecto.objects.filter(id=proyecto_id).exists():
                return Response(
                    {'error': 'El proyecto especificado no existe'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que no existe ya una obra para este proyecto
            if Obra.objects.filter(proyecto_id=proyecto_id).exists():
                return Response(
                    {'error': 'Ya existe una obra para este proyecto'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[EsSupervisorOArquitecto])
    def asignar_supervisor(self, request, pk=None):
        try:
            obra = self.get_object()
            supervisor_id = request.data.get('supervisor_id')
            
            supervisor = Usuario.objects.get(id=supervisor_id, rol='SUP')
            obra.supervisor = supervisor
            obra.save()
            return Response({'status': 'Supervisor asignado'})
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario supervisor no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[EsSupervisorOArquitecto])
    def asignar_trabajador(self, request, pk=None):
        try:
            obra = self.get_object()
            trabajador_id = request.data.get('trabajador_id')
            
            trabajador = Usuario.objects.get(id=trabajador_id, rol='TEC')
            obra.trabajadores.add(trabajador)
            return Response({'status': 'Trabajador asignado'})
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario trabajador no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def mis_obras(self, request):
        try:
            user = request.user
            queryset = Obra.objects.filter(trabajadores=user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )