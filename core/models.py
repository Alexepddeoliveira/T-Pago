from django.db import models
from django.contrib.auth.models import User
import uuid

class Empresa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_fantasia = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)  # NOVO CAMPO

    def __str__(self):
        return self.nome_fantasia

class ItemCardapio(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    imagem = models.ImageField(upload_to='cardapio/')

    def __str__(self):
        return self.nome
    
class Pedido(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    retirado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    item = models.ForeignKey(ItemCardapio, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.quantidade * self.preco_unitario


