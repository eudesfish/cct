from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Redireciona a raiz para a página de login
def redirect_to_login(request):
    return redirect('login')  # 'login' deve estar definido em usuarios/urls.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login),  # Acesso à raiz vai para login
    path('conta/', include('usuarios.urls')),  # Rotas do app usuários
    path('clientes/', include('clientes.urls')),  # Rotas do app clientes
]
