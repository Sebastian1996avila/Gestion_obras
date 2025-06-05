from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from usuarios.views import (
    LoginView,
    LogoutView,
    CustomTokenObtainPairView
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Sistema de Gestión API",
        default_version='v1',
        description="API para el Sistema de Gestión de Obras",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="soporte@sistema.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Vista para obtener token CSRF
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})

# Redirección para autenticación
@require_http_methods(["GET"])
def auth_redirect(request):
    return JsonResponse({
        'detail': 'Please use POST method for authentication',
        'redirect': '/login'
    }, status=401)

# URLs principales de la aplicación
urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),
    
    # Endpoints de seguridad y autenticación
    path('api/csrf_token/', get_csrf_token, name='csrf_token'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/auth/redirect/', auth_redirect, name='auth_redirect'),
    
    # Documentación de la API
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # APIs de las aplicaciones
    path('api/usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios-api')),
    path('api/proyectos/', include(('proyectos.urls', 'proyectos'), namespace='proyectos-api')),
    path('api/obras/', include(('obras.urls', 'obras'), namespace='obras-api')),
    path('api/asistencia/', include(('asistencia.urls', 'asistencia'), namespace='asistencia-api')),
    path('api/nomina/', include(('nomina.urls', 'nomina'), namespace='nomina-api')),
    path('api/materiales/', include(('materiales.urls', 'materiales'), namespace='materiales-api')),
    
    # Redirección de la raíz a la documentación
    path('', lambda request: redirect('/api/docs/')),
    
    # Captura todas las demás rutas para el frontend React
    re_path(r'^(?!api/|admin/|media/|static/).*$', TemplateView.as_view(template_name='index.html')),
]

# Configuración específica para desarrollo
if settings.DEBUG:
    # Servir archivos estáticos y media
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns