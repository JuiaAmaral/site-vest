from django import tribes
from django.contrib.auth.models import User
from .models import PerfilUsuario

class CadastroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    
    class Meta:
        model = PerfilUsuario
        fields = ['telefone', 'cep', 'logradouro', 'numero', 'bairro']

    def signup(self, request, user):
        perfil = self.save(commit=False)
        perfil.user = user
        perfil.save()