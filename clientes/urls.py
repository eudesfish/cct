# clientes/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/novo/', views.criar_cliente, name='criar_cliente'),
    path('clientes/<int:pk>/', views.detalhe_cliente, name='detalhe_cliente'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:pk>/excluir/', views.excluir_cliente, name='excluir_cliente'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/novo/', views.criar_pedido, name='criar_pedido'),
    path('pedidos/<int:pk>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('pedidos/<int:pk>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedidos/<int:pk>/excluir/', views.excluir_pedido, name='excluir_pedido'),
    path('api/clientes/<int:pk>/produtos/', views.produtos_por_cliente, name='produtos_por_cliente'),
    path('pedidos/atualizar-status/<int:pk>/', views.atualizar_status_pedido, name='atualizar_status_pedido'),
    path('pedidos/exportar-pdf/<int:pk>/', views.exportar_pedido_pdf, name='exportar_pedido_pdf'),
]