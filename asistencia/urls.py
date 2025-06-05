from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegistroAsistenciaCreateView,
    RegistroAsistenciaListView,
    RegistroAsistenciaAdminListView,
    ResumenAsistenciaView,
    RegistroAsistenciaViewSet
)

app_name = 'asistencia'  # Namespace opcional para tus URLs

# Router para la API REST
router = DefaultRouter()
router.register(r'registros', RegistroAsistenciaViewSet, basename='registroasistencia')

# URLs para la API REST
api_urlpatterns = [
    path('', include(router.urls)),
    path('registrar/', RegistroAsistenciaCreateView.as_view(), name='registro-asistencia-create'),
    path('mis-registros/', RegistroAsistenciaListView.as_view(), name='mis-registros'),
    path('registros/', RegistroAsistenciaAdminListView.as_view(), name='registros-admin'),
    path('resumen/', ResumenAsistenciaView.as_view(), name='resumen-asistencia'),
    # path('reporte/', views.reporte_asistencia, name='reporte'),
    # Agrega más rutas según necesites
]

# URLs para la interfaz web
web_urlpatterns = [
    # Agrega aquí las URLs para la interfaz web si las necesitas
]

# Combinar todas las URLs
urlpatterns = [
    path('', include(api_urlpatterns)),
    path('web/', include(web_urlpatterns)),
]