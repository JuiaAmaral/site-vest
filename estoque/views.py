from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Produto, FreteBairro, PerfilUsuario

# --- HOME E BUSCA ---
def index(request):
    produtos = Produto.objects.all()
    return render(request, 'index.html', {'produtos': produtos})

def buscar(request):
    termo_busca = request.GET.get('q')
    produtos = Produto.objects.all()
    if termo_busca:
        produtos = Produto.objects.filter(
            Q(nome__icontains=termo_busca) | 
            Q(descricao__icontains=termo_busca)
        )
    return render(request, 'index.html', {'produtos': produtos, 'termo': termo_busca})

# View para listar produtos por categoria
def categoria_produtos(request, categoria_nome):
    # Busca os produtos que pertencem à categoria clicada
    produtos = Produto.objects.filter(categoria__nome__iexact=categoria_nome)
    return render(request, 'categoria.html', {
        'produtos': produtos, 
        'titulo': categoria_nome
    })

# --- AUTENTICAÇÃO E PERFIL ---
def cadastrar(request):
    if request.method == "POST":
        nome_usuario = request.POST.get('usuario')
        email_usuario = request.POST.get('email')
        senha_usuario = request.POST.get('senha')
        
        # Campos do Perfil (Endereço)
        telefone = request.POST.get('telefone')
        cep = request.POST.get('cep')
        bairro = request.POST.get('bairro')
        rua = request.POST.get('logradouro')
        numero = request.POST.get('numero')

        if User.objects.filter(username=nome_usuario).exists():
            return render(request, 'cadastro.html', {'erro': 'Usuário já existe'})
        
        # 1. Cria o Usuário
        novo_user = User.objects.create_user(username=nome_usuario, email=email_usuario, password=senha_usuario)
        
        # 2. Cria o Perfil vinculado ao Usuário
        PerfilUsuario.objects.create(
            user=novo_user,
            telefone=telefone,
            cep=cep,
            bairro=bairro,
            logradouro=rua,
            numero=numero
        )
        
        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect('login')
        
    return render(request, 'cadastro.html')

def logar(request):
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        user = authenticate(request, username=usuario, password=senha)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos'})
    return render(request, 'login.html')

def deslogar(request):
    logout(request)
    return redirect('index')

# --- CARRINHO ---
def adicionar_ao_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    carrinho[produto_id_str] = carrinho.get(produto_id_str, 0) + 1
    request.session['carrinho'] = carrinho
    return redirect('carrinho_detalhe')

def carrinho_detalhe(request):
    carrinho_sessao = request.session.get('carrinho', {})
    itens_carrinho = []
    total = 0
    for produto_id, quantidade in carrinho_sessao.items():
        produto = get_object_or_404(Produto, id=produto_id)
        subtotal = produto.preco * quantidade
        total += subtotal
        itens_carrinho.append({'produto': produto, 'quantidade': quantidade, 'subtotal': subtotal})
    return render(request, 'carrinho.html', {'itens': itens_carrinho, 'total': total})

def remover_do_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    if produto_id_str in carrinho:
        del carrinho[produto_id_str]
        request.session['carrinho'] = carrinho
    return redirect('carrinho_detalhe')

# --- CHECKOUT (FRETE POR BAIRRO) ---
@login_required
def finalizar_compra(request):
    carrinho_sessao = request.session.get('carrinho', {})
    if not carrinho_sessao:
        return redirect('index')

    try:
        perfil = request.user.perfilusuario
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Perfil não encontrado. Complete seu cadastro.")
        return redirect('index')
    
    itens = []
    total_produtos = 0
    for produto_id, quantidade in carrinho_sessao.items():
        produto = get_object_or_404(Produto, id=produto_id)
        subtotal = produto.preco * quantidade
        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal,
        })
        total_produtos += subtotal

    try:
        obj_frete = FreteBairro.objects.get(bairro__iexact=perfil.bairro)
        valor_frete = obj_frete.valor
    except FreteBairro.DoesNotExist:
        messages.error(request, f"Lamentamos, a Vest Lavichy ainda não entrega no bairro {perfil.bairro}.")
        return redirect('carrinho_detalhe')

    total_geral = total_produtos + valor_frete

    return render(request, 'checkout.html', {
        'perfil': perfil,
        'itens': itens,
        'total_produtos': total_produtos,
        'frete': valor_frete,
        'total_geral': total_geral,
    })

def checkout(request):
    total = request.GET.get('total', 0)  # Obtém o total da URL
    return render(request, 'checkout.html', {'total': total})

@login_required
def pagamento(request):
    carrinho_sessao = request.session.get('carrinho', {})
    if not carrinho_sessao:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('carrinho_detalhe')

    try:
        perfil = request.user.perfilusuario
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Perfil não encontrado. Complete seu cadastro para finalizar o pagamento.")
        return redirect('cadastro')

    itens = []
    total_produtos = 0
    for produto_id, quantidade in carrinho_sessao.items():
        produto = get_object_or_404(Produto, id=produto_id)
        subtotal = produto.preco * quantidade
        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal,
        })
        total_produtos += subtotal

    try:
        obj_frete = FreteBairro.objects.get(bairro__iexact=perfil.bairro)
        valor_frete = obj_frete.valor
    except FreteBairro.DoesNotExist:
        messages.error(request, f"Lamentamos, a Vest Lavichy ainda não entrega no bairro {perfil.bairro}.")
        return redirect('carrinho_detalhe')

    total_geral = total_produtos + valor_frete

    return render(request, 'pagamento.html', {
        'perfil': perfil,
        'itens': itens,
        'total_produtos': total_produtos,
        'frete': valor_frete,
        'total_geral': total_geral,
    })