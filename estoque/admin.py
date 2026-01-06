from django.contrib import admin
from .models import (
    Produto, ImagemProduto, Secao, Categoria, 
    FreteBairro, Pedido, Banner, DestaqueLuxo
)

admin.site.register(Categoria) 
admin.site.register(FreteBairro)
admin.site.register(Banner)       
admin.site.register(DestaqueLuxo) 

# Configuração de Imagens Inlines
class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1

# Customização da SEÇÃO 
@admin.register(Secao)
class SecaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tem_imagem')
    
    def tem_imagem(self, obj):
        return bool(obj.imagem)
    tem_imagem.boolean = True
    tem_imagem.short_description = "Possui Ícone?"

# Customização do Produto
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'quantidade_estoque', 'destaque', 'novidade', 'em_alerta') 
    list_editable = ('preco', 'quantidade_estoque', 'destaque', 'novidade')
    list_filter = ('destaque', 'novidade', 'secao', 'categoria')
    inlines = [ImagemProdutoInline]
    
    def em_alerta(self, obj):
        return obj.quantidade_estoque <= obj.alerta_minimo
    em_alerta.boolean = True
    em_alerta.short_description = 'Estoque Baixo'

# Customização do Pedido
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'itens_json', 'total', 'status', 'data_pedido')
    list_filter = ('status', 'data_pedido')
    list_editable = ('status',)
    search_fields = ('usuario__username', 'id')
    ordering = ('-data_pedido',)