from django.contrib import admin
from .models import Produto, ImagemProduto, Secao, Categoria
from .models import FreteBairro

# Registrar as categorias e seções para você conseguir cadastrá-las
admin.site.register(Secao)
admin.site.register(Categoria)
admin.site.register(FreteBairro)

class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'quantidade_estoque', 'em_alerta') 
    list_editable = ('preco', 'quantidade_estoque')
    inlines = [ImagemProdutoInline]
    
    def em_alerta(self, obj):
        # Aqui também deve ser 'quantidade_estoque'
        return obj.quantidade_estoque <= obj.alerta_minimo
    em_alerta.boolean = True
    em_alerta.short_description = 'Estoque Baixo'