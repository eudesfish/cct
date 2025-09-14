from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Pedido, Produto, ItemPedido
from django.db.models import Count
from .forms import ClienteForm, PedidoForm, PedidoUpdateForm
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_POST
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
import os
from django.contrib.staticfiles.finders import find

# Views do Dashboard
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

# Views de Clientes
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista_clientes.html', {'clientes': clientes})

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
    
    context = {
        'form': form,
        'titulo': 'Editar Cliente',
        'cliente': cliente,
        'produtos_cliente': produtos_cliente,
    }

    return render(request, 'clientes/form_cliente.html', context)

def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')
    return render(request, 'clientes/confirmar_exclusao.html', {'objeto': cliente, 'tipo': 'Cliente'})

def detalhe_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'clientes/detalhe_cliente.html', {'cliente': cliente})


# Views de Pedidos
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
    }
    return render(request, 'clientes/lista_pedidos.html', context)

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
            pedido = Pedido.objects.create(
                cliente=cliente,
                status='entrada'
            )
            for item in produtos_dados:
                produto = get_object_or_404(Produto, pk=item['produto_id'])
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item['quantidade']
                )
            return redirect('lista_pedidos')
    
    clientes = Cliente.objects.all()
    return render(request, 'clientes/form_pedido.html', {'clientes': clientes, 'titulo': 'Novo Pedido'})

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
        
        if produtos_dados:
            for item in produtos_dados:
                produto = get_object_or_404(Produto, pk=item['produto_id'])
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item['quantidade']
                )
        return redirect('lista_pedidos')
    
    clientes = Cliente.objects.all()
    itens_pedido = pedido.itempedido_set.all()

    context = {
        'titulo': 'Editar Pedido',
        'clientes': clientes,
        'pedido': pedido,
        'itens_pedido': itens_pedido
    }
    return render(request, 'clientes/form_pedido.html', context)

def detalhe_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        form = PedidoUpdateForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('detalhe_pedido', pk=pedido.pk)
    else:
        form = PedidoUpdateForm(instance=pedido)
    
    context = {
        'pedido': pedido,
        'form': form,
    }
    return render(request, 'clientes/detalhe_pedido.html', context)

def excluir_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        return redirect('lista_pedidos')
    return render(request, 'clientes/confirmar_exclusao.html', {'objeto': pedido, 'tipo': 'Pedido'})

# View para atualizar o status do pedido
@require_POST
def atualizar_status_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoUpdateForm(request.POST, instance=pedido)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'Status atualizado com sucesso!'})
    
    return JsonResponse({'success': False, 'message': 'Erro ao atualizar o status.'}, status=400)


# Views da API
def produtos_por_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    produtos = cliente.produtos.values('id', 'nome_produto')
    return JsonResponse(list(produtos), safe=False)

def exportar_pedido_pdf(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)

    # 1. Encontre o caminho físico da logo no sistema de arquivos
    logo_path = find('images/logo.png')
    
    # 2. Formate o caminho para que o WeasyPrint possa acessá-lo.
    #    'file:///' é o prefixo necessário e 'os.path.normpath' ajusta as barras para o sistema operacional.
    logo_url = 'file:///' + os.path.normpath(logo_path)

    # 3. Adicione o caminho da logo ao contexto que será enviado para o template
    contexto = {
        'pedido': pedido,
        'logo_url': logo_url,
    }

    # Renderiza o template para uma string HTML, passando o novo contexto
    html_string = render_to_string('clientes/pedido_pdf.html', contexto)

    # Converte o HTML em PDF usando WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pedido_{pedido.id}.pdf"'

    HTML(string=html_string).write_pdf(response)
    
    return response