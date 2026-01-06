from django.db import models
from django.contrib.auth.models import User

class Secao(models.Model):
    nome = models.CharField(max_length=50) 
    imagem = models.ImageField(upload_to='icones_categorias/', blank=True, null=True, verbose_name="Ícone da Categoria")
    def __str__(self): return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=50) 
    def __str__(self): return self.nome

class Banner(models.Model):
    titulo = models.CharField(max_length=100, help_text="Apenas para identificação")
    imagem = models.ImageField(upload_to='banners/', verbose_name="Imagem do Banner")
    ativo = models.BooleanField(default=True)
    def __str__(self): return self.titulo

class DestaqueLuxo(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Título (Ex: Vestido Elegante)")
    imagem = models.ImageField(upload_to='luxo/', verbose_name="Foto do Card")
    produto_associado = models.ForeignKey('Produto', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Se quiser que a vitrine direcione para um produto, selecione aqui produto desejado.")

    def __str__(self): return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    descricao = models.TextField(verbose_name="Descrição do Produto", blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda (R$)")
    quantidade_estoque = models.IntegerField(default=0, verbose_name="Estoque Disponível") 
    alerta_minimo = models.IntegerField(default=5, verbose_name="Alerta de Reposição")
    secao = models.ForeignKey(Secao, on_delete=models.CASCADE, verbose_name="Seção do Produto", null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Categoria do Produto", null=True, blank=True)
    novidade = models.BooleanField(default=False, verbose_name="É novidade?")
    destaque = models.BooleanField(default=False, verbose_name="Colocar em destaque na tela inicial?")
    tamanhos_disponiveis = models.CharField(
        max_length=50, 
        verbose_name="Tamanhos Disponíveis", 
        help_text="Ex: P, M, G ou 38, 40, 42, Único",
        null=True, 
        blank=True
    )
    def __str__(self): return self.nome
    def get_tamanhos_list(self):
        if self.tamanhos_disponiveis:
        # Divide por vírgula, remove espaços extras e filtra itens vazios
            return [t.strip() for t in self.tamanhos_disponiveis.split(',') if t.strip()]
        return []

class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/')
    principal = models.BooleanField(default=False)

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15)
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100, default="Rio de Janeiro")
    estado = models.CharField(max_length=2, default="RJ")
    def __str__(self): return f"Perfil de {self.user.username}"

class FreteBairro(models.Model):
    bairro = models.CharField(max_length=100, unique=True, verbose_name="Nome do Bairro")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Frete")
    def __str__(self): return f"{self.bairro} - R$ {self.valor}"
    class Meta:
        verbose_name = "Valor de Frete por Bairro"
        verbose_name_plural = "Valores de Frete por Bairro"

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Aguardando Pagamento'),
        ('pago', 'Pagamento Confirmado / Aguardando Envio'),
        ('enviado', 'Pedido Enviado'),
        ('entregue', 'Pedido Entregue'),
        ('cancelado', 'Pedido Cancelado'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    itens_json = models.TextField() 
    id_pagamento_mp = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self): return f"Pedido {self.id} - {self.usuario.username}"