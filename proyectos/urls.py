from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuración del Router API
router = DefaultRouter()
router.register('', views.ProyectoViewSet, basename='proyecto')

# URLs para API REST
api_patterns = [
    path('', include(router.urls)),
    path('estadisticas/', views.get_estadisticas, name='estadisticas'),
]

# URLs para interfaz web
web_patterns = [
    path('', views.proyecto_list, name='web-proyecto-list'),
    path('nuevo/', views.proyecto_create, name='web-proyecto-create'),
    path('<int:pk>/', views.proyecto_detail, name='web-proyecto-detail'),
    path('<int:pk>/editar/', views.proyecto_update, name='web-proyecto-update'),
    path('<int:pk>/eliminar/', views.proyecto_delete, name='web-proyecto-delete'),
]

# Combinar todas las URLs
urlpatterns = api_patterns + web_patterns