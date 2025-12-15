from django.contrib import admin

# aqui é o painel de administração pra ficar bonitinho

from django.contrib import admin
from .models import Produto, ImagemProduto

# permite editar as imagens na página de edição do produto
class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1

# registra o modelo produto e personaliza a exibição
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # campos visiveis na lista de produtos do painel
    list_display = ('nome', 'preco', 'quantidade_estoque', 'em_alerta')
    
    # campos que podem ser editados diretamente na lista
    list_editable = ('preco', 'quantidade_estoque')
    
    # adiciona a sub-seção para editar imagens
    inlines = [ImagemProdutoInline]
    
    # método que define a lógica do alerta de estoque baixo
    def em_alerta(self, obj):
        return obj.quantidade_estoque <= obj.alerta_minimo
    
    # configurações visuais (mostra como um checkmark ou X)
    em_alerta.boolean = True
    em_alerta.short_description = 'Estoque Baixo'