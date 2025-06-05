from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView,     TokenBlacklistView
from rest_framework.views import APIView
from .models import Usuario
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer, UserBasicSerializer
from .permissions import EsSupervisorOArquitecto, PuedeGestionarUsuarios
from django.contrib.auth.models import Group


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Puedes personalizar la respuesta aquí
        return response

class LogoutView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data = {
                'message': 'Logout successful',
                'status': status.HTTP_200_OK
            }
        return response

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def get(self, request, *args, **kwargs):
        return Response({
            'detail': 'Por favor, use el método POST para autenticarse'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                # La información del usuario ya está incluida en la respuesta por el serializer
                return response
            return response
        except Exception as e:
            return Response({
                'detail': 'Error en el proceso de autenticación',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Vista para obtener información del usuario actual
class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserBasicSerializer

    def get_object(self):
        return self.request.user

# Vista para crear usuarios
class UsuarioCreateView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [EsSupervisorOArquitecto, PuedeGestionarUsuarios]

    def perform_create(self, serializer):
        usuario = serializer.save()
        
        # Asignar grupo según el rol
        grupo_nombre = {
            'ARQ': 'Arquitectos',
            'SUP': 'Supervisores',
            'TRA': 'Trabajadores'
        }[usuario.rol]
        
        try:
            grupo = Group.objects.get(name=grupo_nombre)
            usuario.groups.add(grupo)
        except Group.DoesNotExist:
            # Si el grupo no existe, crearlo
            grupo = Group.objects.create(name=grupo_nombre)
            usuario.groups.add(grupo)

# Vista para asignar roles (la que ya tenías)
class AsignarRolView(generics.UpdateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [EsSupervisorOArquitecto, PuedeGestionarUsuarios]
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        usuario = self.get_object()
        nuevo_rol = request.data.get('rol')
        
        # Validar rol
        if nuevo_rol not in dict(Usuario.ROLES).keys():
            return Response(
                {'error': 'Rol no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validar jerarquía de roles
        if request.user.rol == 'SUP' and nuevo_rol == 'ARQ':
            return Response(
                {'error': 'Los supervisores no pueden asignar el rol de arquitecto'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Validar que no se pueda asignar un rol superior al propio
        roles_hierarquia = {'ARQ': 3, 'SUP': 2, 'TRA': 1}
        if roles_hierarquia[nuevo_rol] > roles_hierarquia[request.user.rol]:
            return Response(
                {'error': 'No puedes asignar un rol superior al tuyo'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Actualizar rol y grupo
        usuario.rol = nuevo_rol
        usuario.save()
        
        # Asignar grupo correspondiente
        grupo_nombre = {
            'ARQ': 'Arquitectos',
            'SUP': 'Supervisores',
            'TRA': 'Trabajadores'
        }[nuevo_rol]
        
        grupo = Group.objects.get(name=grupo_nombre)
        usuario.groups.clear()
        usuario.groups.add(grupo)
        
        return Response(
            UsuarioSerializer(usuario).data,
            status=status.HTTP_200_OK
        )