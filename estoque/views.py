from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse  
from .models import Categoria, Pedido, Produto, FreteBairro, PerfilUsuario, Secao, Banner, DestaqueLuxo
import mercadopago
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt

# --- HOME E BUSCA ---

def index(request):
    categorias = Categoria.objects.all()
    secoes = Secao.objects.all()
    produtos_destaque = Produto.objects.filter(destaque=True)
    produtos = Produto.objects.all().order_by('-id')[:8] 
    banners = Banner.objects.filter(ativo=True)
    colecao_luxo = DestaqueLuxo.objects.all() 

    return render(request, 'index.html', {
        'produtos': produtos,
        'produtos_destaque': produtos_destaque, 
        'categorias': categorias,
        'secoes': secoes,
        'banners': banners,       
        'colecao_luxo': colecao_luxo, 
        'modo_busca': False
    })

def buscar(request):
    termo_busca = request.GET.get('q')
    if not termo_busca:
        return redirect('index')

    secoes = Secao.objects.all()
    categorias = Categoria.objects.all()

    produtos = Produto.objects.filter(
        Q(nome__icontains=termo_busca) | 
        Q(descricao__icontains=termo_busca)
    )
    
    return render(request, 'index.html', {
        'produtos': produtos, 
        'termo': termo_busca,
        'secoes': secoes,         
        'categorias': categorias,
        'modo_busca': True,      
        'qtd_resultados': produtos.count()
    })

def categoria_produtos(request, categoria_nome):
    produtos = Produto.objects.filter(categoria__nome__iexact=categoria_nome)
    return render(request, 'categoria.html', {
        'produtos': produtos, 
        'titulo': categoria_nome
    })

# --- AUTENTICAÇÃO E PERFIL --

def cadastrar(request):
    if request.method == "POST":
        nome_usuario = request.POST.get('usuario')
        email_usuario = request.POST.get('email')
        senha_usuario = request.POST.get('senha')
        
        telefone = request.POST.get('telefone')
        cep = request.POST.get('cep')
        bairro = request.POST.get('bairro')
        rua = request.POST.get('logradouro')
        complemento = request.POST.get('complemento')
        numero = request.POST.get('numero')

        if User.objects.filter(username=nome_usuario).exists():
            messages.error(request, "Este nome de usuário já está em uso.")
            return render(request, 'cadastro.html')
        
        try:
            novo_user = User.objects.create_user(
                username=nome_usuario, 
                email=email_usuario, 
                password=senha_usuario
            )
            
            PerfilUsuario.objects.create(
                user=novo_user, 
                telefone=telefone, 
                cep=cep,
                bairro=bairro, 
                logradouro=rua, 
                complemento=complemento, 
                numero=numero
            )
            
            messages.success(request, "Conta criada com sucesso! Faça login.")
            return redirect('login') 

        except Exception as e:
            User.objects.filter(username=nome_usuario).delete()
            messages.error(request, f"Erro ao salvar: {e}")
            return render(request, 'cadastro.html')

    # Garante que sempre retorne a página se não for POST ou se falhar
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

# --- NOVA VIEW PARA VALIDAÇÃO AJAX ---
def verificar_usuario(request):
    usuario = request.GET.get('usuario', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=usuario).exists()
    }
    return JsonResponse(data)

# --- CARRINHO COM SUPORTE A TAMANHO ---
def adicionar_ao_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    cor = request.GET.get('cor', '-')
    tamanho = request.GET.get('tamanho', 'Único')
    item_id = f"{produto_id}-{tamanho}"
    
    if item_id in carrinho:
        carrinho[item_id]['quantidade'] += 1
    else:
        produto = get_object_or_404(Produto, id=produto_id)
        carrinho[item_id] = {
            'produto_id': produto.id,
            'nome': produto.nome,
            'preco': str(produto.preco),
            'tamanho': tamanho,
            'cor': cor,
            'quantidade': 1,
            'imagem': produto.imagens.first().imagem.url if produto.imagens.exists() else ''
        }
        
    request.session['carrinho'] = carrinho
    request.session.modified = True
    return redirect('carrinho_detalhe')

def carrinho_detalhe(request):
    carrinho_sessao = request.session.get('carrinho', {})
    itens_carrinho = []
    total = 0

    for item_id, dados in carrinho_sessao.items():
        if not isinstance(dados, dict):
            continue
        try:
            produto_obj = get_object_or_404(Produto, id=dados['produto_id'])
            preco = float(dados['preco'])
            subtotal = preco * dados['quantidade']
            total += subtotal
            itens_carrinho.append({
                'produto': produto_obj,
                'quantidade': dados['quantidade'],
                'tamanho': dados.get('tamanho', 'Único'),
                'cor': dados.get('cor', '-'),
                'subtotal': subtotal,
                'item_id': item_id 
            })
        except (KeyError, TypeError):
            continue

    return render(request, 'carrinho.html', {
        'itens_carrinho': itens_carrinho,
        'total': total
    })

def remover_do_carrinho(request, item_id):
    carrinho = request.session.get('carrinho', {})
    if item_id in carrinho:
        del carrinho[item_id]
        request.session['carrinho'] = carrinho
        request.session.modified = True
    return redirect('carrinho_detalhe')

# --- CHECKOUT E PAGAMENTO ---

@login_required
def pagar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    # Só permite pagar se estiver pendente
    if pedido.status != 'pendente':
        return redirect('meus_pedidos')

    try:
        preference = criar_preferencia_mp(pedido)  # sua função do Mercado Pago
        link_pagamento = preference.get("init_point")

        if not link_pagamento:
            raise Exception("Link de pagamento não gerado")

        return redirect(link_pagamento)

    except Exception as e:
        print("ERRO AO GERAR PAGAMENTO:", e)
        return redirect('meus_pedidos')
    
@login_required
def checkout_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    if pedido.status != 'pendente':
        return redirect('meus_pedidos')

    perfil = request.user.perfilusuario
    itens = json.loads(pedido.itens_json)

    total_produtos = sum(item['subtotal'] for item in itens)

    try:
       frete = float(
            FreteBairro.objects.get(bairro__iexact=perfil.bairro).valor
    )
    except FreteBairro.DoesNotExist:
        frete = 0

    total_geral = total_produtos + frete

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": f"Pedido #{pedido.id} - Vest Lavichy",
            "quantity": 1,
            "unit_price": float(total_geral),
        }],
        "external_reference": str(pedido.id),
        "back_urls": {
            "success": "http://127.0.0.1:8000/pagamento/sucesso/",
            "failure": "http://127.0.0.1:8000/pagamento/erro/",
            "pending": "http://127.0.0.1:8000/pagamento/pendente/"
        }
    }

    preference = sdk.preference().create(preference_data)["response"]

    return render(request, 'checkout.html', {
        'pedido': pedido,
        'perfil': perfil,
        'itens': itens,
        'total_produtos': total_produtos,
        'frete': frete,
        'total_geral': total_geral,
        'link_pagamento': preference.get("init_point")
    })
    
# -- FINALIZAÇÃO DE COMPRA --

@login_required
def finalizar_compra(request):
    carrinho_sessao = request.session.get('carrinho', {})
    if not carrinho_sessao:
        messages.error(request, "O carrinho está vazio!")
        return redirect('carrinho_detalhe')

    try:
        perfil = request.user.perfilusuario
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Perfil não encontrado. Complete seu cadastro.")
        return redirect('index')

    itens_lista = []
    total_produtos = 0

    for item_id, dados in carrinho_sessao.items():
        if isinstance(dados, dict):
            produto_obj = get_object_or_404(Produto, id=dados['produto_id'])
            subtotal = float(dados['preco']) * dados['quantidade']
            itens_lista.append({
                'produto': produto_obj,
                'nome': dados['nome'],
                'tamanho': dados.get('tamanho', 'Único'),
                'cor': dados.get('cor', '-'),
                'quantidade': dados['quantidade'],
                'subtotal': subtotal,
            })
            total_produtos += subtotal

    try:
        obj_frete = FreteBairro.objects.get(bairro__iexact=perfil.bairro)
        valor_frete = obj_frete.valor
    except FreteBairro.DoesNotExist:
        messages.error(request, f"A Vest Lavichy ainda não entrega no bairro {perfil.bairro}.")
        return redirect('carrinho_detalhe')

    total_geral = float(total_produtos) + float(valor_frete)

    pedido = Pedido.objects.create(
        usuario=request.user,
        total=total_geral,
        status='pendente',
        itens_json=json.dumps([
            {
                "produto": item["nome"],
                "tamanho": item["tamanho"],
                "quantidade": item["quantidade"],
                "cor": item.get("cor", "-"),
                "subtotal": item["subtotal"]
            } for item in itens_lista
        ])
    )

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": "Pedido Vest Lavichy",
            "quantity": 1,
            "unit_price": float(total_geral),
        }],
        "external_reference": str(pedido.id),
        "back_urls": {
            "success": "http://127.0.0.1:8000/pagamento/sucesso/",
            "failure": "http://127.0.0.1:8000/pagamento/erro/",
            "pending": "http://127.0.0.1:8000/pagamento/pendente/"
        }
    }

    preference_response = sdk.preference().create(preference_data)

    if preference_response.get("status") != 201:
        print("ERRO MERCADO PAGO:", preference_response)
        messages.error(request, "Erro ao criar pagamento.")
        return redirect("carrinho_detalhe")

    preference = preference_response["response"]
    link_pagamento = preference.get("init_point")

    if not link_pagamento:
        messages.error(request, "Erro ao gerar link de pagamento.")
        return redirect("carrinho_detalhe")

    pedido.id_pagamento_mp = preference.get("id")
    pedido.save()

    return render(request, 'checkout.html', {
        'perfil': perfil,
        'itens': itens_lista,
        'total_produtos': total_produtos,
        'frete': valor_frete,
        'total_geral': total_geral,
        'link_pagamento': link_pagamento
    })


def pagamento_sucesso(request):
    return render(request, 'pagamento_sucesso.html')

def pagamento_erro(request):
    return render(request, 'pagamento_erro.html')

def pagamento_pendente(request):
    return render(request, 'pagamento_pendente.html')

@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
    return render(request, 'pedidos.html', {'pedidos': pedidos})

# --- VITRINE E FILTROS ---
def vitrine_produtos(request):
    secoes_ids = request.GET.getlist('secao')
    categorias_ids = request.GET.getlist('categoria')
    tamanhos_selecionados = request.GET.getlist('tamanho')
    busca = request.GET.get('q')
    novidade = request.GET.get('novidade')

    produtos = Produto.objects.all()

    if novidade in ['on', 'true']:
        produtos = produtos.filter(novidade=True)

    if secoes_ids:
        if secoes_ids[0].isdigit():
            produtos = produtos.filter(secao__id__in=secoes_ids)
        else:
            produtos = produtos.filter(secao__nome__in=secoes_ids)
    
    if categorias_ids:
        if categorias_ids[0].isdigit():
            produtos = produtos.filter(categoria__id__in=categorias_ids)
        else:
            produtos = produtos.filter(categoria__nome__in=categorias_ids)

    if tamanhos_selecionados:
        query_tamanho = Q()
        for tam in tamanhos_selecionados:
            query_tamanho |= Q(tamanhos_disponiveis__icontains=tam)
        produtos = produtos.filter(query_tamanho)

    if busca:
        produtos = produtos.filter(nome__icontains=busca)

    context = {
        'produtos': produtos,
        'categorias': Categoria.objects.all(),
        'secoes': Secao.objects.all(),
        'tamanhos_disponiveis': ['P', 'M', 'G', 'GG', '36', '38', '40', '42', 'Único'],
        'secoes_ativas': secoes_ids,
        'cats_ativas': categorias_ids,
        'tams_ativos': tamanhos_selecionados,
        'novidade_ativa': novidade,
    }
    return render(request, 'produtos.html', context)

def produto_detalhe(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    secoes = Secao.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'produto_detalhe.html', {
        'produto': produto,
        'secoes': secoes,
        'categorias': categorias
    })
    
@login_required
def detalhe_pedido(request, pedido_id):
    pedido = get_object_or_404(
        Pedido,
        id=pedido_id,
        usuario=request.user
    )

    itens = json.loads(pedido.itens_json)

    return render(request, 'pedido_detalhe.html', {
        'pedido': pedido,
        'itens': itens
    })
    
# -- WEBHOOK PARA ATUALIZAÇÃO DE PAGAMENTO --
    
@csrf_exempt
def webhook_mp(request):
    data = json.loads(request.body)

    if data.get("type") == "payment":
        payment_id = data["data"]["id"]

        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        payment = sdk.payment().get(payment_id)["response"]

        if payment.get("status") == "approved":
            pedido_id = payment.get("external_reference")
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                pedido.status = "pago"
                pedido.id_pagamento_mp = payment_id
                pedido.save()
            except Pedido.DoesNotExist:
                pass

    return JsonResponse({"status": "ok"})
