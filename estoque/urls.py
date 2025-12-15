from django.urls import path
from . import views

urlpatterns = [
    # Quando o Django ver a URL base ('' - vazia), chama a função lista_produtos
    path('', views.lista_produtos, name='home'),
]