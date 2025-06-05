from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_api

app_name = 'materiales'

# Router para la API REST
router = DefaultRouter()
router.register(r'categorias', views_api.CategoriaMaterialViewSet)
router.register(r'proveedores', views_api.ProveedorViewSet)
router.register(r'', views_api.MaterialViewSet)

# URLs para la API REST
api_patterns = [
    path('', include(router.urls)),
    path('estadisticas/', views_api.MaterialViewSet.as_view({'get': 'estadisticas'}), name='material-estadisticas'),
]

# URLs para la interfaz web
web_patterns = [
    path('', views.lista_materiales, name='lista'),
    path('nuevo/', views.crear_material, name='crear'),
    path('<int:pk>/', views.detalle_material, name='detalle'),
    path('<int:pk>/editar/', views.editar_material, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_material, name='eliminar'),
]

# Combinar todas las URLs
urlpatterns = api_patterns + web_patterns