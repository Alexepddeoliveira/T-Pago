from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.redirecionar_login, name='home'),
    
    # Empresa
    path('adicionar/', views.adicionar_item, name='adicionar_item'),
    path('listar/', views.listar_itens, name='listar_itens'),
    path('empresa/pedidos/', views.pedidos_recebidos, name='pedidos_recebidos'),
    path('item/<int:item_id>/editar/', views.editar_item, name='editar_item'),
    path('empresa/editar/', views.editar_empresa, name='editar_empresa'),
    path('ler-qr/', views.ler_qr_code, name='ler_qr_code'),
    
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Cliente
    path('cliente/', views.cliente_home, name='cliente_home'),
    path('empresa/<int:empresa_id>/cardapio/', views.ver_cardapio, name='ver_cardapio'),
    path('item/<int:item_id>/detalhes/', views.detalhes_item, name='detalhes_item'),
    path('pedidos/pendentes/', views.pedidos_pendentes_cliente, name='pedidos_pendentes_cliente'),

    
    # Carrinho
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/adicionar/<int:item_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<int:item_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    
    path('finalizar/', views.finalizar_pedido, name='finalizar_pedido'),
    path('verificar/<uuid:codigo>/', views.verificar_pedido, name='verificar_pedido'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.erro_404'
handler500 = 'core.views.erro_500'
handler403 = 'core.views.erro_403'
