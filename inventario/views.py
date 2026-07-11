import csv
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
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


@login_required
def dashboard(request):
    totais = {
        'em_estoque': Componente.objects.filter(status=Componente.EM_ESTOQUE).count(),
        'instalado': Componente.objects.filter(status=Componente.INSTALADO).count(),
        'removido': Componente.objects.filter(status=Componente.REMOVIDO).count(),
    }
    ultimas_movimentacoes = Movimentacao.objects.select_related(
        'componente', 'usuario', 'servidor', 'componente__data_center'
    )[:10]
    return render(request, 'dashboard.html', {
        'totais': totais,
        'ultimas_movimentacoes': ultimas_movimentacoes,
    })


class UsuarioListView(LoginRequiredMixin, AdminMixin, ListView):
    model = Usuario
    template_name = 'usuarios/lista.html'
    context_object_name = 'usuarios'


class UsuarioCreateView(LoginRequiredMixin, AdminMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuario_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Usuário criado com sucesso.')
        return super().form_valid(form)


class UsuarioUpdateView(LoginRequiredMixin, AdminMixin, UpdateView):
    model = Usuario
    form_class = UsuarioEditForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuario_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Usuário atualizado com sucesso.')
        return super().form_valid(form)


class UsuarioDeleteView(LoginRequiredMixin, AdminMixin, DeleteView):
    model = Usuario
    template_name = 'usuarios/confirmar_exclusao.html'
    success_url = reverse_lazy('usuario_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Usuário removido.')
        return super().form_valid(form)


class DataCenterListView(LoginRequiredMixin, ListView):
    model = DataCenter
    template_name = 'datacenters/lista.html'
    context_object_name = 'datacenters'


class DataCenterCreateView(LoginRequiredMixin, AdminMixin, CreateView):
    model = DataCenter
    form_class = DataCenterForm
    template_name = 'datacenters/form.html'
    success_url = reverse_lazy('datacenter_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Data Center criado com sucesso.')
        return super().form_valid(form)


class DataCenterUpdateView(LoginRequiredMixin, AdminMixin, UpdateView):
    model = DataCenter
    form_class = DataCenterForm
    template_name = 'datacenters/form.html'
    success_url = reverse_lazy('datacenter_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Data Center atualizado com sucesso.')
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


class ServidorCreateView(LoginRequiredMixin, CreateView):
    model = Servidor
    form_class = ServidorForm
    template_name = 'servidores/form.html'
    success_url = reverse_lazy('servidor_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Servidor cadastrado com sucesso.')
        return super().form_valid(form)


class ServidorUpdateView(LoginRequiredMixin, AdminMixin, UpdateView):
    model = Servidor
    form_class = ServidorForm
    template_name = 'servidores/form.html'
    success_url = reverse_lazy('servidor_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Servidor atualizado com sucesso.')
        return super().form_valid(form)


class TipoListView(LoginRequiredMixin, ListView):
    model = TipoComponente
    template_name = 'tipos/lista.html'
    context_object_name = 'tipos'
    queryset = TipoComponente.objects.all()


class TipoCreateView(LoginRequiredMixin, AdminMixin, CreateView):
    model = TipoComponente
    form_class = TipoComponenteForm
    template_name = 'tipos/form.html'
    success_url = reverse_lazy('tipo_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Tipo criado com sucesso.')
        return super().form_valid(form)


class TipoUpdateView(LoginRequiredMixin, AdminMixin, UpdateView):
    model = TipoComponente
    form_class = TipoComponenteForm
    template_name = 'tipos/form.html'
    success_url = reverse_lazy('tipo_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Tipo atualizado com sucesso.')
        return super().form_valid(form)


@login_required
def tipo_remover(request, pk):
    if not request.user.is_admin_inventario():
        messages.error(request, 'Acesso negado.')
        return redirect('tipo_lista')

    tipo = get_object_or_404(TipoComponente, pk=pk)
    if not tipo.pode_remover():
        messages.error(request, 'Não é possível remover um tipo com componentes cadastrados.')
        return redirect('tipo_lista')

    if request.method == 'POST':
        tipo.delete()
        messages.success(request, 'Tipo removido.')
        return redirect('tipo_lista')

    return render(request, 'tipos/confirmar_exclusao.html', {'tipo': tipo})


class FabricanteListView(LoginRequiredMixin, AdminMixin, ListView):
    model = Fabricante
    template_name = 'fabricantes/lista.html'
    context_object_name = 'fabricantes'


class FabricanteCreateView(LoginRequiredMixin, AdminMixin, CreateView):
    model = Fabricante
    form_class = FabricanteForm
    template_name = 'fabricantes/form.html'
    success_url = reverse_lazy('fabricante_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Fabricante criado com sucesso.')
        return super().form_valid(form)


class FabricanteUpdateView(LoginRequiredMixin, AdminMixin, UpdateView):
    model = Fabricante
    form_class = FabricanteForm
    template_name = 'fabricantes/form.html'
    success_url = reverse_lazy('fabricante_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Fabricante atualizado.')
        return super().form_valid(form)


class FabricanteDeleteView(LoginRequiredMixin, AdminMixin, DeleteView):
    model = Fabricante
    template_name = 'fabricantes/confirmar_exclusao.html'
    success_url = reverse_lazy('fabricante_lista')

    def form_valid(self, form):
        if self.object.componente_set.exists():
            messages.error(self.request, 'Não é possível remover um fabricante com componentes cadastrados.')
            return redirect('fabricante_lista')
        messages.success(self.request, 'Fabricante removido.')
        return super().form_valid(form)


class PecaPadraoListView(LoginRequiredMixin, AdminMixin, ListView):
    model = PecaPadrao
    template_name = 'pecas_padrao/lista.html'
    context_object_name = 'pecas'
    queryset = PecaPadrao.objects.select_related('tipo', 'fabricante')


class PecaPadraoCreateView(LoginRequiredMixin, AdminMixin, CreateView):
    model = PecaPadrao
    form_class = PecaPadraoForm
    template_name = 'pecas_padrao/form.html'
    success_url = reverse_lazy('peca_padrao_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Peça padrão cadastrada.')
        return super().form_valid(form)


class PecaPadraoUpdateView(LoginRequiredMixin, AdminMixin, UpdateView):
    model = PecaPadrao
    form_class = PecaPadraoForm
    template_name = 'pecas_padrao/form.html'
    success_url = reverse_lazy('peca_padrao_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Peça padrão atualizada.')
        return super().form_valid(form)


class PecaPadraoDeleteView(LoginRequiredMixin, AdminMixin, DeleteView):
    model = PecaPadrao
    template_name = 'pecas_padrao/confirmar_exclusao.html'
    success_url = reverse_lazy('peca_padrao_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Peça padrão removida.')
        return super().form_valid(form)


class LimiteListView(LoginRequiredMixin, AdminMixin, ListView):
    model = LimiteEstoque
    template_name = 'limites/lista.html'
    context_object_name = 'limites'
    queryset = LimiteEstoque.objects.select_related('tipo', 'data_center')


class LimiteCreateView(LoginRequiredMixin, AdminMixin, CreateView):
    model = LimiteEstoque
    form_class = LimiteEstoqueForm
    template_name = 'limites/form.html'
    success_url = reverse_lazy('limite_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Limite configurado com sucesso.')
        return super().form_valid(form)


class LimiteUpdateView(LoginRequiredMixin, AdminMixin, UpdateView):
    model = LimiteEstoque
    form_class = LimiteEstoqueForm
    template_name = 'limites/form.html'
    success_url = reverse_lazy('limite_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Limite atualizado.')
        return super().form_valid(form)


class LimiteDeleteView(LoginRequiredMixin, AdminMixin, DeleteView):
    model = LimiteEstoque
    template_name = 'limites/confirmar_exclusao.html'
    success_url = reverse_lazy('limite_lista')


class ComponenteListView(LoginRequiredMixin, ListView):
    model = Componente
    template_name = 'componentes/lista.html'
    context_object_name = 'componentes'
    paginate_by = 50

    def get_queryset(self):
        qs = Componente.objects.select_related('tipo', 'data_center', 'servidor')
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipos'] = TipoComponente.objects.filter(ativo=True)
        ctx['datacenters'] = DataCenter.objects.all()
        ctx['status_choices'] = Componente.STATUS_CHOICES
        ctx['filtros'] = self.request.GET
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
                f'{quantidade} componente(s) adicionado(s) ao estoque com sucesso.'
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
            messages.error(request, 'Selecione ao menos um componente para instalar.')
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
            messages.success(request, f'{componentes.count()} componente(s) instalado(s) em {servidor}.')
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
            messages.error(request, 'Selecione ao menos um componente para remover.')
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
            messages.success(request, f'{componentes.count()} componente(s) removido(s) do estoque.')
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
        'Tipo', 'Fabricante', 'Modelo', 'Número de Série', 'Código Patrimonial',
        'Capacidade', 'Tipo Disco', 'Interface',
        'Status', 'Servidor', 'Data Center', 'Data Entrada', 'Observações',
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
    writer.writerow(['Data', 'Tipo', 'Fabricante', 'Modelo', 'Número de Série', 'Servidor', 'Data Center', 'Usuário', 'Observações'])
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
