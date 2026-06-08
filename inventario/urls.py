from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Usuários
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_lista'),
    path('usuarios/novo/', views.UsuarioCreateView.as_view(), name='usuario_novo'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario_editar'),
    path('usuarios/<int:pk>/remover/', views.UsuarioDeleteView.as_view(), name='usuario_remover'),

    # Data Centers
    path('datacenters/', views.DataCenterListView.as_view(), name='datacenter_lista'),
    path('datacenters/novo/', views.DataCenterCreateView.as_view(), name='datacenter_novo'),
    path('datacenters/<int:pk>/editar/', views.DataCenterUpdateView.as_view(), name='datacenter_editar'),

    # Fabricantes
    path('fabricantes/', views.FabricanteListView.as_view(), name='fabricante_lista'),
    path('fabricantes/novo/', views.FabricanteCreateView.as_view(), name='fabricante_novo'),
    path('fabricantes/<int:pk>/editar/', views.FabricanteUpdateView.as_view(), name='fabricante_editar'),
    path('fabricantes/<int:pk>/remover/', views.FabricanteDeleteView.as_view(), name='fabricante_remover'),

    # Tipos de Componentes
    path('tipos/', views.TipoListView.as_view(), name='tipo_lista'),
    path('tipos/novo/', views.TipoCreateView.as_view(), name='tipo_novo'),
    path('tipos/<int:pk>/editar/', views.TipoUpdateView.as_view(), name='tipo_editar'),
    path('tipos/<int:pk>/remover/', views.tipo_remover, name='tipo_remover'),

    # Limites de Estoque
    path('limites/', views.LimiteListView.as_view(), name='limite_lista'),
    path('limites/novo/', views.LimiteCreateView.as_view(), name='limite_novo'),
    path('limites/<int:pk>/editar/', views.LimiteUpdateView.as_view(), name='limite_editar'),
    path('limites/<int:pk>/remover/', views.LimiteDeleteView.as_view(), name='limite_remover'),

    # Componentes
    path('componentes/', views.ComponenteListView.as_view(), name='componente_lista'),
    path('componentes/adicionar/', views.adicionar_componentes, name='componente_adicionar'),
    path('componentes/remover/', views.remover_componentes, name='componente_remover'),

    # Relatórios
    path('relatorios/estoque/', views.relatorio_estoque, name='relatorio_estoque'),
    path('relatorios/historico/', views.relatorio_historico, name='relatorio_historico'),
    path('relatorios/removidos/', views.relatorio_removidos, name='relatorio_removidos'),
    path('relatorios/por-dc/', views.relatorio_por_dc, name='relatorio_por_dc'),
]
