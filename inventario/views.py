import csv
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy

from .forms import (
    AdicionarComponentesForm, DataCenterForm, FabricanteForm, FiltroRelatorioForm,
    InstalarComponentesForm, LimiteEstoqueForm, PecaPadraoForm, RemoverComponentesForm,
    ServidorForm, TipoComponenteForm, UsuarioCreateForm, UsuarioEditForm,
)
from .models import (
    Componente, DataCenter, Fabricante, LimiteEstoque, Movimentacao,
    PecaPadrao, Servidor, TipoComponente, Usuario,
)
from .utils import verificar_e_enviar_alerta_email


class AdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin_inventario()


class BloqueiaViewerMixin(UserPassesTestMixin):
    """Blocks the Viewer role from accessing create/edit/delete views."""
    def test_func(self):
        return not self.request.user.is_somente_leitura()

@login_required
def dashboard(request):
    from django.db.models import Q

    totais = {
        'em_estoque': Componente.objects.filter(status=Componente.EM_ESTOQUE).count(),
        'instalado': Componente.objects.filter(status=Componente.INSTALADO).count(),
        'removido': Componente.objects.filter(status=Componente.REMOVIDO).count(),
    }

    datacenters_estoque = DataCenter.objects.annotate(
        total_estoque=Count('componente', filter=Q(componente__status=Componente.EM_ESTOQUE))
    ).filter(total_estoque__gt=0).order_by('-total_estoque')

    breakdown_por_dc = {}
    contagens = (
        Componente.objects.filter(status=Componente.EM_ESTOQUE)
        .values('data_center_id', 'tipo_id', 'tipo__nome')
        .annotate(total=Count('id'))
        .order_by('data_center_id', '-total')
    )
    for c in contagens:
        breakdown_por_dc.setdefault(c['data_center_id'], []).append(
            {'tipo_id': c['tipo_id'], 'tipo': c['tipo__nome'], 'total': c['total']}
        )

    for dc in datacenters_estoque:
        dc.breakdown = breakdown_por_dc.get(dc.pk, [])

    return render(request, 'dashboard.html', {
        'totais': totais,
        'datacenters_estoque': datacenters_estoque,
    })

class UsuarioListView(LoginRequiredMixin, AdminMixin, ListView):
    model = Usuario
    template_name = 'usuarios/lista.html'
    context_object_name = 'usuarios'


class UsuarioCreateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuario_lista')

    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)


class UsuarioUpdateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, UpdateView):
    model = Usuario
    form_class = UsuarioEditForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuario_lista')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)


class UsuarioDeleteView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, DeleteView):
    model = Usuario
    template_name = 'usuarios/confirmar_exclusao.html'
    success_url = reverse_lazy('usuario_lista')

    def form_valid(self, form):
        messages.success(self.request, 'User removed.')
        return super().form_valid(form)


class DataCenterListView(LoginRequiredMixin, ListView):
    model = DataCenter
    template_name = 'datacenters/lista.html'
    context_object_name = 'datacenters'


class DataCenterCreateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, CreateView):
    model = DataCenter
    form_class = DataCenterForm
    template_name = 'datacenters/form.html'
    success_url = reverse_lazy('datacenter_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Data Center created successfully.')
        return super().form_valid(form)


class DataCenterUpdateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, UpdateView):
    model = DataCenter
    form_class = DataCenterForm
    template_name = 'datacenters/form.html'
    success_url = reverse_lazy('datacenter_lista')

class DataCenterDeleteView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, DeleteView):
    model = DataCenter
    template_name = 'datacenters/confirmar_exclusao.html'
    success_url = reverse_lazy('datacenter_lista')

    def form_valid(self, form):
        if self.object.componente_set.exists() or self.object.servidores.exists():
            messages.error(self.request, 'Cannot remove a Data Center with linked components or servers.')
            return redirect('datacenter_lista')
        messages.success(self.request, 'Data Center removed.')
        return super().form_valid(form)


class ServidorListView(LoginRequiredMixin, ListView):
    model = Servidor
    template_name = 'servidores/lista.html'
    context_object_name = 'servidores'

    def get_queryset(self):
        qs = Servidor.objects.select_related('data_center')
        dc = self.request.GET.get('data_center')
        if dc:
            qs = qs.filter(data_center_id=dc)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['datacenters'] = DataCenter.objects.all()
        return ctx


class ServidorCreateView(LoginRequiredMixin, BloqueiaViewerMixin, CreateView):
    model = Servidor
    form_class = ServidorForm
    template_name = 'servidores/form.html'
    success_url = reverse_lazy('servidor_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Server registered successfully.')
        return super().form_valid(form)


class ServidorUpdateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, UpdateView):
    model = Servidor
    form_class = ServidorForm
    template_name = 'servidores/form.html'
    success_url = reverse_lazy('servidor_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Server updated successfully.')
        return super().form_valid(form)


class TipoListView(LoginRequiredMixin, ListView):
    model = TipoComponente
    template_name = 'tipos/lista.html'
    context_object_name = 'tipos'
    queryset = TipoComponente.objects.all()


class TipoCreateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, CreateView):    
    model = TipoComponente
    form_class = TipoComponenteForm
    template_name = 'tipos/form.html'
    success_url = reverse_lazy('tipo_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Type created successfully.')
        return super().form_valid(form)


class TipoUpdateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, UpdateView):
    model = TipoComponente
    form_class = TipoComponenteForm
    template_name = 'tipos/form.html'
    success_url = reverse_lazy('tipo_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Type updated successfully.')
        return super().form_valid(form)


@login_required
def tipo_remover(request, pk):
    if not request.user.is_admin_inventario() or request.user.is_somente_leitura():
        messages.error(request, 'Access denied.')
        return redirect('tipo_lista')

    tipo = get_object_or_404(TipoComponente, pk=pk)
    if not tipo.pode_remover():
        messages.error(request, 'Cannot remove a type with registered components.')
        return redirect('tipo_lista')

    if request.method == 'POST':
        tipo.delete()
        messages.success(request, 'Type removed.')
        return redirect('tipo_lista')

    return render(request, 'tipos/confirmar_exclusao.html', {'tipo': tipo})


class FabricanteListView(LoginRequiredMixin, AdminMixin, ListView):
    model = Fabricante
    template_name = 'fabricantes/lista.html'
    context_object_name = 'fabricantes'


class FabricanteCreateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, CreateView):
    model = Fabricante
    form_class = FabricanteForm
    template_name = 'fabricantes/form.html'
    success_url = reverse_lazy('fabricante_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Manufacturer created successfully.')
        return super().form_valid(form)


class FabricanteUpdateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, UpdateView):
    model = Fabricante
    form_class = FabricanteForm
    template_name = 'fabricantes/form.html'
    success_url = reverse_lazy('fabricante_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Manufacturer updated.')
        return super().form_valid(form)


class FabricanteDeleteView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, DeleteView):
    model = Fabricante
    template_name = 'fabricantes/confirmar_exclusao.html'
    success_url = reverse_lazy('fabricante_lista')

    def form_valid(self, form):
        if self.object.componente_set.exists():
            messages.error(self.request, 'Cannot remove a manufacturer with registered components.')
            return redirect('fabricante_lista')
        messages.success(self.request, 'Manufacturer removed.')
        return super().form_valid(form)


class PecaPadraoListView(LoginRequiredMixin, AdminMixin, ListView):
    model = PecaPadrao
    template_name = 'pecas_padrao/lista.html'
    context_object_name = 'pecas'
    queryset = PecaPadrao.objects.select_related('tipo', 'fabricante')


class PecaPadraoCreateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, CreateView):
    model = PecaPadrao
    form_class = PecaPadraoForm
    template_name = 'pecas_padrao/form.html'
    success_url = reverse_lazy('peca_padrao_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Standard part registered.')
        return super().form_valid(form)


class PecaPadraoUpdateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, UpdateView):
    model = PecaPadrao
    form_class = PecaPadraoForm
    template_name = 'pecas_padrao/form.html'
    success_url = reverse_lazy('peca_padrao_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Standard part updated.')
        return super().form_valid(form)


class PecaPadraoDeleteView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, DeleteView):
    model = PecaPadrao
    template_name = 'pecas_padrao/confirmar_exclusao.html'
    success_url = reverse_lazy('peca_padrao_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Standard part removed.')
        return super().form_valid(form)


class LimiteListView(LoginRequiredMixin, AdminMixin, ListView):
    model = LimiteEstoque
    template_name = 'limites/lista.html'
    context_object_name = 'limites'
    queryset = LimiteEstoque.objects.select_related('tipo', 'data_center')


class LimiteCreateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, CreateView):    
    model = LimiteEstoque
    form_class = LimiteEstoqueForm
    template_name = 'limites/form.html'
    success_url = reverse_lazy('limite_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Limit configured successfully.')
        return super().form_valid(form)


class LimiteUpdateView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, UpdateView):    
    model = LimiteEstoque
    form_class = LimiteEstoqueForm
    template_name = 'limites/form.html'
    success_url = reverse_lazy('limite_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Limit updated.')
        return super().form_valid(form)


class LimiteDeleteView(LoginRequiredMixin, AdminMixin, BloqueiaViewerMixin, DeleteView):
    model = LimiteEstoque
    template_name = 'limites/confirmar_exclusao.html'
    success_url = reverse_lazy('limite_lista')


class ComponenteListView(LoginRequiredMixin, ListView):
    model = Componente
    template_name = 'componentes/lista.html'
    context_object_name = 'componentes'

    def get_queryset(self):
        self.modo_detalhe = self.request.GET.get('modo') == 'detalhe'
        qs = Componente.objects.select_related('tipo', 'fabricante', 'data_center', 'servidor')
        q = self.request.GET
        if q.get('tipo'):
            qs = qs.filter(tipo_id=q['tipo'])
        if q.get('data_center'):
            qs = qs.filter(data_center_id=q['data_center'])
        if q.get('status'):
            qs = qs.filter(status=q['status'])
        if q.get('busca'):
            qs = qs.filter(_busca_q(q['busca']))
        return qs

    def get_paginate_by(self, queryset):
        return 50 if getattr(self, 'modo_detalhe', False) else None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipos'] = TipoComponente.objects.filter(ativo=True)
        ctx['datacenters'] = DataCenter.objects.all()
        ctx['status_choices'] = Componente.STATUS_CHOICES
        ctx['filtros'] = self.request.GET
        ctx['modo_detalhe'] = self.modo_detalhe

        if not self.modo_detalhe:
            grupos = self.object_list.values(
                'tipo_id', 'tipo__nome',
                'status', 'data_center_id', 'data_center__nome', 'data_center__codigo',
            ).annotate(total=Count('id')).order_by('tipo__nome')
            ctx['grupos'] = grupos

        return ctx


def _busca_q(busca):
    from django.db.models import Q
    return (
        Q(modelo__icontains=busca)
        | Q(fabricante__nome__icontains=busca)
        | Q(numero_serie__icontains=busca)
        | Q(codigo_patrimonio__icontains=busca)
    )


class ComponenteDetailView(LoginRequiredMixin, DetailView):
    model = Componente
    template_name = 'componentes/detalhe.html'
    context_object_name = 'componente'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['historico'] = self.object.historico.select_related('usuario')
        ctx['movimentacoes'] = self.object.movimentacoes.select_related('usuario', 'servidor')
        return ctx


@login_required
def adicionar_componentes(request):
    if request.user.is_somente_leitura():
        messages.error(request, 'Your account has read-only access.')
        return redirect('componente_lista')

    if request.method == 'POST':
        form = AdicionarComponentesForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            quantidade = d['quantidade']
            series = d.get('numeros_serie_lista', [])
            patrimonios = d.get('codigos_patrimonio_lista', [])

            with transaction.atomic():
                for i in range(quantidade):
                    comp = Componente.objects.create(
                        tipo=d['tipo'],
                        fabricante=d['fabricante'],
                        modelo=d['modelo'],
                        status=Componente.EM_ESTOQUE,
                        data_center=d['data_center'],
                        disco_capacidade=d.get('disco_capacidade', ''),
                        disco_tipo=d.get('disco_tipo', ''),
                        disco_interface=d.get('disco_interface', ''),
                        ram_capacidade=d.get('ram_capacidade', ''),
                        ram_tipo=d.get('ram_tipo', ''),
                        ram_interface=d.get('ram_interface', ''),
                        ram_perfil=d.get('ram_perfil', ''),
                        numero_serie=series[i] if i < len(series) else None,
                        codigo_patrimonio=patrimonios[i] if i < len(patrimonios) else None,
                        observacoes=d.get('observacoes', ''),
                    )
                    Movimentacao.objects.create(
                        componente=comp,
                        tipo=Movimentacao.ENTRADA,
                        usuario=request.user,
                        observacoes=d.get('observacoes', ''),
                    )
            verificar_e_enviar_alerta_email(d['tipo'], d['data_center'])
            messages.success(
                request,
                f'{quantidade} component(s) successfully added to stock.'
            )
            return redirect('componente_lista')
    else:
        form = AdicionarComponentesForm()

    fabricantes_por_tipo = {
        str(tipo.pk): list(tipo.fabricantes.values_list('pk', flat=True))
        for tipo in TipoComponente.objects.prefetch_related('fabricantes').filter(ativo=True)
    }

    pecas_padrao_dados = {
        str(peca.pk): {
            'tipo': peca.tipo_id,
            'fabricante': peca.fabricante_id,
            'modelo': peca.modelo,
            'disco_capacidade': peca.disco_capacidade,
            'disco_tipo': peca.disco_tipo,
            'disco_interface': peca.disco_interface,
        }
        for peca in PecaPadrao.objects.filter(ativo=True)
    }

    return render(request, 'componentes/adicionar.html', {
        'form': form,
        'fabricantes_por_tipo_json': json.dumps(fabricantes_por_tipo),
        'pecas_padrao_json': json.dumps(pecas_padrao_dados),
    })


@login_required
def instalar_componentes(request):
    if request.user.is_somente_leitura():
        messages.error(request, 'Your account has read-only access.')
        return redirect('componente_lista')

    qs = Componente.objects.filter(status=Componente.EM_ESTOQUE).select_related('tipo', 'data_center')
    filtro_dc = request.GET.get('data_center') or request.POST.get('data_center_filtro')
    filtro_tipo = request.GET.get('tipo') or request.POST.get('tipo_filtro')
    if filtro_dc:
        qs = qs.filter(data_center_id=filtro_dc)
    if filtro_tipo:
        qs = qs.filter(tipo_id=filtro_tipo)

    form = InstalarComponentesForm(request.POST or None)

    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('componentes')
        if not ids_selecionados:
            messages.error(request, 'Select at least one component to install.')
        elif form.is_valid():
            servidor = form.cleaned_data['servidor']
            observacoes = form.cleaned_data['observacoes']
            componentes = Componente.objects.filter(pk__in=ids_selecionados, status=Componente.EM_ESTOQUE)
            with transaction.atomic():
                for comp in componentes:
                    comp.status = Componente.INSTALADO
                    comp.servidor = servidor
                    if observacoes:
                        comp.observacoes = observacoes
                    comp.save()
                    Movimentacao.objects.create(
                        componente=comp,
                        tipo=Movimentacao.INSTALACAO,
                        usuario=request.user,
                        servidor=servidor,
                        observacoes=observacoes,
                    )
            messages.success(request, f'{componentes.count()} component(s) installed on {servidor}.')
            return redirect('componente_lista')

    return render(request, 'componentes/instalar.html', {
        'componentes': qs,
        'form': form,
        'tipos': TipoComponente.objects.filter(ativo=True),
        'datacenters': DataCenter.objects.all(),
        'filtro_dc': filtro_dc,
        'filtro_tipo': filtro_tipo,
    })


@login_required
def remover_componentes(request):
    if request.user.is_somente_leitura():
        messages.error(request, 'Your account has read-only access.')
        return redirect('componente_lista')

    qs = Componente.objects.exclude(status=Componente.REMOVIDO).select_related('tipo', 'data_center')
    filtro_dc = request.GET.get('data_center') or request.POST.get('data_center_filtro')
    filtro_tipo = request.GET.get('tipo') or request.POST.get('tipo_filtro')
    if filtro_dc:
        qs = qs.filter(data_center_id=filtro_dc)
    if filtro_tipo:
        qs = qs.filter(tipo_id=filtro_tipo)

    form = RemoverComponentesForm(request.POST or None)

    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('componentes')
        if not ids_selecionados:
            messages.error(request, 'Select at least one component to remove.')
        elif form.is_valid():
            observacoes = form.cleaned_data['observacoes']
            componentes = Componente.objects.filter(
                pk__in=ids_selecionados
            ).exclude(status=Componente.REMOVIDO)
            with transaction.atomic():
                for comp in componentes:
                    comp.status = Componente.REMOVIDO
                    comp.save()
                    Movimentacao.objects.create(
                        componente=comp,
                        tipo=Movimentacao.SAIDA,
                        usuario=request.user,
                        observacoes=observacoes,
                    )
            messages.success(request, f'{componentes.count()} component(s) removed from stock.')
            return redirect('componente_lista')

    return render(request, 'componentes/remover.html', {
        'componentes': qs,
        'form': form,
        'tipos': TipoComponente.objects.filter(ativo=True),
        'datacenters': DataCenter.objects.all(),
        'filtro_dc': filtro_dc,
        'filtro_tipo': filtro_tipo,
    })


@login_required
def relatorio_estoque(request):
    form = FiltroRelatorioForm(request.GET or None)
    qs = Componente.objects.filter(status=Componente.EM_ESTOQUE).select_related('tipo', 'data_center')

    if form.is_valid():
        if form.cleaned_data.get('data_center'):
            qs = qs.filter(data_center=form.cleaned_data['data_center'])
        if form.cleaned_data.get('tipo'):
            qs = qs.filter(tipo=form.cleaned_data['tipo'])

    if 'exportar' in request.GET:
        return _exportar_csv_componentes(qs, 'estoque_atual')

    return render(request, 'relatorios/estoque.html', {'form': form, 'componentes': qs})


@login_required
def relatorio_historico(request):
    form = FiltroRelatorioForm(request.GET or None)
    qs = Movimentacao.objects.select_related(
        'componente', 'componente__tipo', 'componente__data_center', 'usuario', 'servidor'
    )

    if form.is_valid():
        if form.cleaned_data.get('data_center'):
            qs = qs.filter(componente__data_center=form.cleaned_data['data_center'])
        if form.cleaned_data.get('tipo'):
            qs = qs.filter(componente__tipo=form.cleaned_data['tipo'])
        qs = _filtrar_periodo(qs, form.cleaned_data.get('periodo'), 'data')

    if 'exportar' in request.GET:
        return _exportar_csv_movimentacoes(qs, 'historico')

    return render(request, 'relatorios/historico.html', {'form': form, 'movimentacoes': qs})


@login_required
def relatorio_removidos(request):
    form = FiltroRelatorioForm(request.GET or None)
    qs = Componente.objects.filter(status=Componente.REMOVIDO).select_related('tipo', 'data_center')

    if form.is_valid():
        if form.cleaned_data.get('data_center'):
            qs = qs.filter(data_center=form.cleaned_data['data_center'])
        if form.cleaned_data.get('tipo'):
            qs = qs.filter(tipo=form.cleaned_data['tipo'])

    if 'exportar' in request.GET:
        return _exportar_csv_componentes(qs, 'removidos')

    return render(request, 'relatorios/removidos.html', {'form': form, 'componentes': qs})


@login_required
def relatorio_por_dc(request):
    form = FiltroRelatorioForm(request.GET or None)
    qs = Componente.objects.select_related('tipo', 'data_center', 'servidor')

    if form.is_valid():
        if form.cleaned_data.get('data_center'):
            qs = qs.filter(data_center=form.cleaned_data['data_center'])
        if form.cleaned_data.get('tipo'):
            qs = qs.filter(tipo=form.cleaned_data['tipo'])
        if form.cleaned_data.get('status'):
            qs = qs.filter(status=form.cleaned_data['status'])

    if 'exportar' in request.GET:
        return _exportar_csv_componentes(qs, 'inventario_por_dc')

    return render(request, 'relatorios/por_dc.html', {'form': form, 'componentes': qs})


def _filtrar_periodo(qs, periodo, campo_data):
    hoje = timezone.now()
    if periodo == 'mes':
        return qs.filter(**{f'{campo_data}__gte': hoje - timedelta(days=30)})
    if periodo == 'trimestre':
        return qs.filter(**{f'{campo_data}__gte': hoje - timedelta(days=90)})
    if periodo == 'ano':
        return qs.filter(**{f'{campo_data}__gte': hoje - timedelta(days=365)})
    return qs


def _exportar_csv_componentes(qs, nome_arquivo):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Type', 'Manufacturer', 'Model', 'Serial Number', 'Asset Tag',
        'Capacity', 'Disk Type', 'Interface',
        'Status', 'Server', 'Data Center', 'Date Added', 'Notes',
    ])
    for c in qs:
        writer.writerow([
            c.tipo, c.fabricante, c.modelo, c.numero_serie or '', c.codigo_patrimonio or '',
            c.disco_capacidade, c.disco_tipo, c.disco_interface,
            c.get_status_display(), c.servidor or '', c.data_center, c.data_entrada, c.observacoes,
        ])
    return response


def _exportar_csv_movimentacoes(qs, nome_arquivo):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Manufacturer', 'Model', 'Serial Number', 'Server', 'Data Center', 'User', 'Notes'])
    for m in qs:
        writer.writerow([
            m.data.strftime('%d/%m/%Y %H:%M'),
            m.get_tipo_display(),
            m.componente.fabricante,
            m.componente.modelo,
            m.componente.numero_serie or '',
            m.servidor or '',
            m.componente.data_center,
            m.usuario,
            m.observacoes,
        ])
    return response