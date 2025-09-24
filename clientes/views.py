import os
from django.shortcuts import render, redirect, get_object_or_404
from usuarios.views import is_admin_or_supervisor, is_admin
from .models import Cliente, Pedido, Produto, ItemPedido
from django.db.models import Count
from .forms import ClienteForm, PedidoForm, PedidoUpdateForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from weasyprint import HTML
from django.template.loader import render_to_string
from django.contrib.staticfiles.finders import find
from django.contrib.auth.decorators import login_required, user_passes_test

# Dashboard
@login_required
def dashboard(request):
    total_pedidos = Pedido.objects.count()
    total_clientes = Cliente.objects.count()

    pedidos_por_status = Pedido.objects.values('status').annotate(count=Count('status'))
    pedidos_formatados = []
    for item in pedidos_por_status:
        item['status_display'] = item['status'].replace('_', ' ').title()
        pedidos_formatados.append(item)

    context = {
        'total_pedidos': total_pedidos,
        'total_clientes': total_clientes,
        'pedidos_por_status': pedidos_formatados,
    }

    return render(request, 'clientes/dashboard.html', context)

# Lista clientes
@login_required
@user_passes_test(is_admin_or_supervisor)
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista_clientes.html', {
        'clientes': clientes,
        'is_admin': request.user.groups.filter(name='Administrador').exists() or request.user.is_superuser
    })

# Criar cliente
@login_required
@user_passes_test(is_admin)
def criar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            for key, value in request.POST.items():
                if key.startswith('produto-') and key.endswith('-nome_produto'):
                    index = key.split('-')[1]
                    nome_produto = value
                    codigo_barras = request.POST.get(f'produto-{index}-codigo_barras')
                    numero_processo = request.POST.get(f'produto-{index}-numero_processo')
                    Produto.objects.create(
                        cliente=cliente,
                        nome_produto=nome_produto,
                        codigo_barras=codigo_barras,
                        numero_processo=numero_processo
                    )
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/form_cliente.html', {'form': form, 'titulo': 'Novo Cliente'})

# Editar cliente
@login_required
@user_passes_test(is_admin)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            cliente.produtos.all().delete()
            for key, value in request.POST.items():
                if key.startswith('produto-') and key.endswith('-nome_produto'):
                    index = key.split('-')[1]
                    nome_produto = value
                    codigo_barras = request.POST.get(f'produto-{index}-codigo_barras')
                    numero_processo = request.POST.get(f'produto-{index}-numero_processo')
                    if nome_produto and codigo_barras and numero_processo:
                        Produto.objects.create(
                            cliente=cliente,
                            nome_produto=nome_produto,
                            codigo_barras=codigo_barras,
                            numero_processo=numero_processo
                        )
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)

    produtos_cliente = cliente.produtos.all()
    return render(request, 'clientes/form_cliente.html', {
        'form': form,
        'titulo': 'Editar Cliente',
        'cliente': cliente,
        'produtos_cliente': produtos_cliente,
    })

# Excluir cliente
@login_required
@user_passes_test(is_admin)
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')
    return render(request, 'clientes/confirmar_exclusao.html', {'objeto': cliente, 'tipo': 'Cliente'})

# Detalhe cliente
@login_required
@user_passes_test(is_admin_or_supervisor)
def detalhe_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'clientes/detalhe_cliente.html', {'cliente': cliente})

# Lista pedidos
@login_required
@user_passes_test(is_admin_or_supervisor)
def lista_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-id')
    pedidos_por_status = Pedido.objects.values('status').annotate(count=Count('status'))
    pedidos_formatados = []
    for item in pedidos_por_status:
        item['status_display'] = item['status'].replace('_', ' ').title()
        pedidos_formatados.append(item)
    
    context = {
        'pedidos': pedidos,
        'pedidos_por_status': pedidos_formatados,
        'form': PedidoUpdateForm(),
        'is_admin': is_admin(request.user)
    }
    return render(request, 'clientes/lista_pedidos.html', context)

# Criar pedido
@login_required
@user_passes_test(is_admin)
def criar_pedido(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        produtos_dados = []
        for key, value in request.POST.items():
            if key.startswith('produto-') and key.endswith('-id'):
                index = key.split('-')[1]
                produto_id = value
                quantidade = request.POST.get(f'produto-{index}-quantidade')
                produtos_dados.append({'produto_id': produto_id, 'quantidade': quantidade})

        if cliente_id and produtos_dados:
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            pedido = Pedido.objects.create(cliente=cliente, status='entrada')
            for item in produtos_dados:
                produto = get_object_or_404(Produto, pk=item['produto_id'])
                ItemPedido.objects.create(pedido=pedido, produto=produto, quantidade=item['quantidade'])
            return redirect('lista_pedidos')
    
    clientes = Cliente.objects.all()
    return render(request, 'clientes/form_pedido.html', {'clientes': clientes, 'titulo': 'Novo Pedido'})

# Editar pedido
@login_required
@user_passes_test(is_admin)
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        produtos_dados = []
        for key, value in request.POST.items():
            if key.startswith('produto-') and key.endswith('-id'):
                index = key.split('-')[1]
                produto_id = value
                quantidade = request.POST.get(f'produto-{index}-quantidade')
                produtos_dados.append({'produto_id': produto_id, 'quantidade': quantidade})

        if cliente_id:
            pedido.cliente = get_object_or_404(Cliente, pk=cliente_id)
            pedido.save()

        pedido.itempedido_set.all().delete()
        for item in produtos_dados:
            produto = get_object_or_404(Produto, pk=item['produto_id'])
            ItemPedido.objects.create(pedido=pedido, produto=produto, quantidade=item['quantidade'])

        return redirect('lista_pedidos')

    clientes = Cliente.objects.all()
    itens_pedido = pedido.itempedido_set.all()
    return render(request, 'clientes/form_pedido.html', {
        'titulo': 'Editar Pedido',
        'clientes': clientes,
        'pedido': pedido,
        'itens_pedido': itens_pedido,
    })

# Detalhe pedido
@login_required
@user_passes_test(is_admin_or_supervisor)
def detalhe_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoUpdateForm(instance=pedido)
    return render(request, 'clientes/detalhe_pedido.html', {'pedido': pedido, 'form': form})

# Excluir pedido
@login_required
@user_passes_test(is_admin)
def excluir_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        return redirect('lista_pedidos')
    return render(request, 'clientes/confirmar_exclusao.html', {'objeto': pedido, 'tipo': 'Pedido'})

# Atualizar status do pedido
@login_required
@user_passes_test(is_admin)
@require_POST
def atualizar_status_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoUpdateForm(request.POST, instance=pedido)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'Status atualizado com sucesso!'})
    return JsonResponse({'success': False, 'message': 'Erro ao atualizar o status.'}, status=400)

# Produtos de um cliente (API)
@login_required
@user_passes_test(is_admin_or_supervisor)
def produtos_por_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    produtos = cliente.produtos.values('id', 'nome_produto')
    return JsonResponse(list(produtos), safe=False)

# Exportar pedido PDF
@login_required
@user_passes_test(is_admin_or_supervisor)
def exportar_pedido_pdf(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    logo_path = find('images/logo.png')
    logo_url = 'file:///' + os.path.normpath(logo_path)
    contexto = {'pedido': pedido, 'logo_url': logo_url}
    html_string = render_to_string('clientes/pedido_pdf.html', contexto)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pedido_{pedido.id}.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response
