from django import forms
from .models import ItemCardapio
from django.contrib.auth.models import User
from .models import Empresa
from django import forms

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome_fantasia','logo']
        labels = {'nome_fantasia': 'Nome Fantasia'}


class RegistroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    tipo_usuario = forms.ChoiceField(
        choices=[('empresa', 'Empresa'), ('cliente', 'Cliente')],
        widget=forms.RadioSelect
    )
    nome_fantasia = forms.CharField(required=False, label='Nome da Empresa')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        nome_fantasia = cleaned_data.get('nome_fantasia')

        if tipo_usuario == 'empresa' and not nome_fantasia:
            self.add_error('nome_fantasia', 'Este campo é obrigatório para empresas.')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ItemCardapioForm(forms.ModelForm):
    class Meta:
        model = ItemCardapio
        fields = ['nome', 'descricao', 'preco', 'imagem']
