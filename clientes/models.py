# clientes/models.py

from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=255)
    nome_marca = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_marca

class Produto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='produtos')
    nome_produto = models.CharField(max_length=255)
    codigo_barras = models.CharField(max_length=100)
    numero_processo = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_produto
    
class Pedido(models.Model):
    STATUS_CHOICES = (
        ('entrada', 'Pagamento da Entrada'),
        ('materia_prima', 'Solicitação de Matéria Prima'),
        ('producao', 'Produção'),
        ('envase', 'Envase'),
        ('acabamento', 'Acabamento'),
        ('transporte', 'Solicitação de Transporte'),
        ('envio', 'Envio de Mercadoria'),
        ('entregue', 'Entregue'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produtos = models.ManyToManyField(Produto, through='ItemPedido')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='entrada')
    numero_rastreio = models.CharField(max_length=100, blank=True, null=True)
    nome_transportadora = models.CharField(max_length=255, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.id} de {self.cliente.nome_marca}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.produto.nome_produto} ({self.quantidade})"