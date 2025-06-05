from django.urls import path
from .views import (
    LoginView,
    UsuarioCreateView,
    AsignarRolView,
    CurrentUserView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registro/', UsuarioCreateView.as_view(), name='usuario-create'),
    path('asignar-rol/<int:pk>/', AsignarRolView.as_view(), name='asignar-rol'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]