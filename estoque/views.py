from django.shortcuts import render
from .models import Produto

def lista_produtos(request):    
    # Busca todos os produtos cadastrados e exibe na página inicial,
    # Busca todos os objetos do tipo Produto no banco de dados,
    # ordenando do mais novo para o mais antigo (o '-' antes do 'id').

    produtos = Produto.objects.all().order_by('-id')
    
    # Prepara o contexto para enviar os dados para o template HTML
    contexto = {
        'produtos': produtos
    }
    
    # Renderiza o template 'index.html'
    return render(request, 'index.html', contexto)