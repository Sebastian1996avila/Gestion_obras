from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_api

app_name = 'nomina'  # Namespace para las URLs

# Router para la API REST
router = DefaultRouter()
router.register('', views_api.NominaViewSet, basename='nomina')

# URLs para la API REST
api_patterns = [
    path('', include(router.urls)),
]

# URLs para la interfaz web
web_patterns = [
    path('', views.index, name='index'),
    path('registrar/', views.registrar_nomina, name='registrar'),
    path('reporte/', views.reporte_nomina, name='reporte'),
    path('<int:nomina_id>/', views.detalle_nomina, name='detalle'),
    path('<int:nomina_id>/editar/', views.editar_nomina, name='editar'),
    path('<int:nomina_id>/eliminar/', views.eliminar_nomina, name='eliminar'),
]

# Combinar todas las URLs
urlpatterns = api_patterns + web_patterns