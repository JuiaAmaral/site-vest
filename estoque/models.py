from django.db import models
from django.contrib.auth.models import User

class Secao(models.Model):
    nome = models.CharField(max_length=50) 
    def __str__(self): return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=50) 
    def __str__(self): return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    descricao = models.TextField(verbose_name="Descrição Detalhada")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda (R$)")
    quantidade_estoque = models.IntegerField(default=0, verbose_name="Estoque Disponível") 
    alerta_minimo = models.IntegerField(default=5, verbose_name="Alerta de Reposição")
    secao = models.ForeignKey(Secao, on_delete=models.CASCADE, verbose_name="Seção do Produto", null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Categoria do Produto", null=True, blank=True)
    def __str__(self): return self.nome

class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/')
    principal = models.BooleanField(default=False)

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15)
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=255)
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