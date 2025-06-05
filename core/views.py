from django.shortcuts import render, redirect, get_object_or_404
from .forms import ItemCardapioForm, EmpresaForm, RegistroForm, LoginForm
from .models import Empresa, ItemCardapio, Pedido, ItemPedido
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.conf import settings 
import qrcode
from io import BytesIO
import base64
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import AnonymousUser

def is_empresa(user):
    return hasattr(user, 'empresa')

def is_cliente(user):
    return not hasattr(user, 'empresa')

@login_required
@user_passes_test(is_empresa)
def ler_qr_code(request):
    return render(request, 'core/ler_qr.html')

@login_required
@user_passes_test(is_cliente)
def pedidos_pendentes_cliente(request):
    pedidos = Pedido.objects.filter(cliente=request.user, retirado=False).order_by('-criado_em')
    return render(request, 'core/pedidos_pendentes.html', {'pedidos': pedidos})

@login_required
def editar_empresa(request):
    try:
        empresa = request.user.empresa
    except Empresa.DoesNotExist:
        return render(request, 'core/erro.html', {'mensagem': 'Apenas empresas podem acessar essa página.'})

    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('listar_itens')
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, 'core/editar_empresa.html', {'form': form, 'empresa': empresa})

def detalhes_item(request, item_id):
    item = get_object_or_404(ItemCardapio, id=item_id)

    usuario_dono = False
    mostrar_botao = True

    if request.user.is_authenticated:
        if hasattr(request.user, 'empresa'):
            if item.empresa == request.user.empresa:
                usuario_dono = True
            mostrar_botao = False  # qualquer empresa não vê o botão

    return render(request, 'core/detalhes_item.html', {
        'item': item,
        'usuario_dono': usuario_dono,
        'mostrar_botao': mostrar_botao
    })
    
@login_required
def editar_item(request, item_id):
    item = get_object_or_404(ItemCardapio, id=item_id)

    try:
        empresa = request.user.empresa
    except Empresa.DoesNotExist:
        return render(request, 'core/erro.html', {'mensagem': 'Apenas empresas podem editar itens.'})

    if item.empresa != empresa:
        return render(request, 'core/erro.html', {'mensagem': 'Você não tem permissão para editar este item.'})

    if request.method == 'POST':
        form = ItemCardapioForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('listar_itens')
    else:
        form = ItemCardapioForm(instance=item)

    return render(request, 'core/editar_item.html', {'form': form, 'item': item})

@login_required
def pedidos_recebidos(request):
    try:
        empresa = request.user.empresa
    except Empresa.DoesNotExist:
        return render(request, 'core/erro.html', {'mensagem': 'Usuário não é uma empresa.'})

    pedidos = Pedido.objects.filter(empresa=empresa).order_by('-criado_em')
    return render(request, 'core/pedidos_recebidos.html', {'pedidos': pedidos})

def redirecionar_login(request):
    return redirect('login')

def home(request):
    return render(request, 'core/home.html')
 
@login_required(login_url='login')
def verificar_pedido(request, codigo):
    try:
        pedido = Pedido.objects.get(codigo=codigo)
    except Pedido.DoesNotExist:
        return render(request, 'core/erro.html', {'mensagem': 'Pedido não encontrado.'})

    # ⚠️ Verifica se o usuário tem uma empresa associada
    if not hasattr(request.user, 'empresa'):
        return render(request, 'core/erro.html', {'mensagem': 'Apenas empresas podem acessar essa página.'})

    # ⚠️ Verifica se a empresa é dona do pedido
    if request.user.empresa != pedido.empresa:
        return render(request, 'core/erro.html', {'mensagem': 'Você não tem permissão para visualizar este pedido.'})

    if request.method == 'POST':
        pedido.retirado = True
        pedido.save()
        return render(request, 'core/pedido_confirmado_empresa.html', {'pedido': pedido, 'confirmado': True})

    return render(request, 'core/pedido_confirmado_empresa.html', {'pedido': pedido, 'confirmado': False})

@login_required
def finalizar_pedido(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        return render(request, 'core/erro.html', {'mensagem': 'Carrinho vazio.'})

    empresa_id = request.session.get('empresa_carrinho')
    try:
        empresa = Empresa.objects.get(id=empresa_id)
    except Empresa.DoesNotExist:
        return render(request, 'core/erro.html', {'mensagem': 'Empresa inválida.'})

    pedido = Pedido.objects.create(cliente=request.user, empresa=empresa)

    for item_id, qtd in carrinho.items():
        item = ItemCardapio.objects.get(id=item_id)
        ItemPedido.objects.create(
            pedido=pedido,
            item=item,
            quantidade=qtd,
            preco_unitario=item.preco
        )

    request.session['carrinho'] = {}
    request.session['empresa_carrinho'] = None

    # ✅ Atualizado para usar a URL do ambiente (local ou produção)
    url = f"{settings.SITE_URL}/verificar/{pedido.codigo}/"
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer)
    imagem_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'core/pedido_confirmado.html', {
        'pedido': pedido,
        'qr_code': imagem_base64
    })

@login_required
def adicionar_ao_carrinho(request, item_id):
    item = get_object_or_404(ItemCardapio, id=item_id)

    try:
        empresa_usuario = request.user.empresa
        if item.empresa != empresa_usuario:
            return render(request, 'core/erro.html', {'mensagem': 'Empresas só podem adicionar itens do seu próprio cardápio.'})
    except Empresa.DoesNotExist:
        # Cliente normal pode adicionar normalmente
        pass

    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        request.session['empresa_carrinho'] = item.empresa.id

    if item.empresa.id != request.session.get('empresa_carrinho'):
        return render(request, 'core/erro.html', {
            'mensagem': 'Você só pode adicionar itens de uma única empresa por vez.'
        })

    carrinho[str(item_id)] = carrinho.get(str(item_id), 0) + 1
    request.session['carrinho'] = carrinho
    return redirect('ver_carrinho')

@login_required
def remover_do_carrinho(request, item_id):
    carrinho = request.session.get('carrinho', {})
    if str(item_id) in carrinho:
        del carrinho[str(item_id)]
        request.session['carrinho'] = carrinho

        if not carrinho:
            request.session.pop('empresa_carrinho', None)

    return redirect('ver_carrinho')

@login_required
def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    itens = []
    total = 0

    for item_id, quantidade in carrinho.items():
        item = ItemCardapio.objects.get(id=item_id)
        item.quantidade = quantidade
        item.subtotal = item.preco * quantidade
        total += item.subtotal
        itens.append(item)

    return render(request, 'core/carrinho.html', {'itens': itens, 'total': total})

@login_required
def ver_cardapio(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    itens = ItemCardapio.objects.filter(empresa=empresa)
    
    usuario_dono = False
    try:
        if request.user.empresa == empresa:
            usuario_dono = True
    except Empresa.DoesNotExist:
        pass

    return render(request, 'core/cardapio_empresa.html', {
        'empresa': empresa,
        'itens': itens,
        'usuario_dono': usuario_dono,
    })

@login_required
def cliente_home(request):
    empresas = Empresa.objects.all()
    return render(request, 'core/cliente_home.html', {'empresas': empresas})

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['senha'])
            user.save()

            tipo = form.cleaned_data['tipo_usuario']
            if tipo == 'empresa':
                nome = form.cleaned_data['nome_fantasia'] or 'Empresa sem nome'
                Empresa.objects.create(user=user, nome_fantasia=nome)

            login(request, user)
            return redirect('listar_itens' if tipo == 'empresa' else 'cliente_home')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                try:
                    user.empresa
                    return redirect('listar_itens')
                except Empresa.DoesNotExist:
                    return redirect('cliente_home')
            else:
                form.add_error(None, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def adicionar_item(request):
    try:
        empresa = request.user.empresa
    except Empresa.DoesNotExist:
        return render(request, 'core/erro.html', {'mensagem': 'Usuário não é uma empresa.'})

    if request.method == 'POST':
        form = ItemCardapioForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.empresa = empresa
            item.save()
            return redirect('listar_itens')
    else:
        form = ItemCardapioForm()
    return render(request, 'core/adicionar_item.html', {'form': form})

@login_required
def listar_itens(request):
    try:
        empresa = request.user.empresa
    except Empresa.DoesNotExist:
        return render(request, 'core/erro.html', {'mensagem': 'Usuário não é uma empresa.'})

    itens = ItemCardapio.objects.filter(empresa=empresa)
    pedidos_pendentes = Pedido.objects.filter(empresa=empresa, retirado=False)

    return render(request, 'core/cardapio_empresa.html', {
        'empresa': empresa,
        'itens': itens,
        'usuario_dono': True,
        'pedidos_pendentes_count': pedidos_pendentes.count(),
        'pedidos_pendentes': pedidos_pendentes
    })

# Handlers para erros
def erro_404(request, exception):
    return render(request, 'core/erro.html', {'mensagem': 'Página não encontrada.'}, status=404)

def erro_500(request):
    return render(request, 'core/erro.html', {'mensagem': 'Erro interno no servidor.'}, status=500)

def erro_403(request, exception):
    return render(request, 'core/erro.html', {'mensagem': 'Acesso proibido.'}, status=403)
