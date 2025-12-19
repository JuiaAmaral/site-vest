from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('buscar/', views.buscar, name='buscar'),
    path('categoria/<str:categoria_nome>/', views.categoria_produtos, name='categoria_url'),
    path('carrinho/', views.carrinho_detalhe, name='carrinho_detalhe'),
    path('carrinho/add/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'), # Rota do checkout
    path('pagamento/', views.pagamento, name='pagamento'),
    path('cadastro/', views.cadastrar, name='cadastro'),
    path('login/', views.logar, name='login'),
    path('logout/', views.deslogar, name='logout'),
]