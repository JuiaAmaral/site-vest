from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('buscar/', views.buscar, name='buscar'),
    path('produto/<int:produto_id>/', views.produto_detalhe, name='produto_detalhe'),
    path('categoria/<str:categoria_nome>/', views.categoria_produtos, name='categoria_url'),
    path('carrinho/', views.carrinho_detalhe, name='carrinho_detalhe'),
    path('carrinho/add/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<str:item_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'), # Rota do checkout
    path('cadastro/', views.cadastrar, name='cadastro'),
    path('login/', views.logar, name='login'),
    path('logout/', views.deslogar, name='logout'),
    path('pagamento/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('pagamento/erro/', views.pagamento_erro, name='pagamento_erro'),
    path('pagamento/pendente/', views.pagamento_pendente, name='pagamento_pendente'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('meus-pedidos/<int:pedido_id>/', views.detalhe_pedido, name='detalhe_pedido'),
    path('produtos/', views.vitrine_produtos, name='vitrine_produtos'),
    path('verificar-usuario/', views.verificar_usuario, name='verificar_usuario'),
    path('webhook/mercadopago/', views.webhook_mp, name='webhook_mp'),
    path('pedido/<int:pedido_id>/pagar/', views.pagar_pedido, name='pagar_pedido'),
    path('pedido/<int:pedido_id>/checkout/', views.checkout_pedido, name='checkout_pedido'),
]