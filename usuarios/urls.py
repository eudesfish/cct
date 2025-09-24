from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/criar/', views.criar_usuario, name='criar_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path("usuarios/excluir/<int:user_id>/", views.excluir_usuario, name="excluir_usuario"),
]
