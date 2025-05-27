from django import forms
from .models import ItemCardapio
from django.contrib.auth.models import User
from .models import Empresa
from django import forms

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome_fantasia']
        labels = {'nome_fantasia': 'Nome Fantasia'}


class RegistroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    tipo_usuario = forms.ChoiceField(choices=[('empresa', 'Empresa'), ('cliente', 'Cliente')], widget=forms.RadioSelect)
    nome_fantasia = forms.CharField(required=False, label='Nome da Empresa')

    class Meta:
        model = User
        fields = ['username', 'email']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ItemCardapioForm(forms.ModelForm):
    class Meta:
        model = ItemCardapio
        fields = ['nome', 'descricao', 'preco', 'imagem']
