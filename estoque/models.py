from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    descricao = models.TextField(verbose_name="Descrição Detalhada")
    preco = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Preço de Venda (R$)")
    quantidade_estoque = models.IntegerField(default=0, verbose_name="Estoque Disponível")
    alerta_minimo = models.IntegerField(default=5, verbose_name="Alerta de Reposição")

    def __str__(self):
        return self.nome
    
class ImagemProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE, 
        related_name='imagens',
        verbose_name="Produto Associado"
    )

    imagem = models.ImageField(
        upload_to='produtos/', # O Django salvará a imagem em 'MEDIA_ROOT/produtos/'
        verbose_name="Arquivo de Imagem"
    )
    
    principal = models.BooleanField(default=False, verbose_name="Imagem Principal?")

    def str(self):
        return f"Imagem de {self.produto.nome} (Principal: {self.principal})"