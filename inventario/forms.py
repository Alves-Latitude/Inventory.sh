from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    Usuario, DataCenter, Servidor, TipoComponente, LimiteEstoque,
    Componente, Fabricante, PecaPadrao,
)


class UsuarioCreateForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'perfil', 'is_active')


class UsuarioEditForm(UserChangeForm):
    password = None

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'perfil', 'is_active')


class DataCenterForm(forms.ModelForm):
    class Meta:
        model = DataCenter
        fields = ('nome', 'codigo', 'cidade', 'observacoes')
        widgets = {'observacoes': forms.Textarea(attrs={'rows': 3})}


class ServidorForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = ('hostname', 'data_center', 'observacoes', 'ativo')
        widgets = {
            'hostname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g.: web-server-01'}),
            'data_center': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TipoComponenteForm(forms.ModelForm):
    class Meta:
        model = TipoComponente
        fields = ('nome', 'categoria')


class FabricanteForm(forms.ModelForm):
    class Meta:
        model = Fabricante
        fields = ('nome', 'tipos')
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipos': forms.CheckboxSelectMultiple(),
        }


class LimiteEstoqueForm(forms.ModelForm):
    class Meta:
        model = LimiteEstoque
        fields = ('tipo', 'data_center', 'minimo')


class PecaPadraoForm(forms.ModelForm):
    class Meta:
        model = PecaPadrao
        fields = ('tipo', 'fabricante', 'modelo', 'disco_capacidade', 'disco_tipo', 'disco_interface', 'ativo')
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fabricante': forms.Select(attrs={'class': 'form-select'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'disco_capacidade': forms.Select(
                choices=[('', '—')] + Componente.CAPACIDADE_DISCO_CHOICES,
                attrs={'class': 'form-select'},
            ),
            'disco_tipo': forms.Select(
                choices=[('', '—')] + Componente.DISCO_TIPO_CHOICES,
                attrs={'class': 'form-select'},
            ),
            'disco_interface': forms.Select(
                choices=[('', '—')] + Componente.INTERFACE_CHOICES,
                attrs={'class': 'form-select'},
            ),
        }


class AdicionarComponentesForm(forms.Form):
    peca_padrao = forms.ModelChoiceField(
        queryset=PecaPadrao.objects.filter(ativo=True).select_related('tipo', 'fabricante'),
        required=False,
        empty_label='— Select standard part (auto-fills the fields below) —',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_peca_padrao'}),
        label='Standard replacement/purchase part',
    )
    fabricante = forms.ModelChoiceField(
        queryset=Fabricante.objects.all(),
        empty_label='Select the manufacturer',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    modelo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g.: Exos X18 18TB',
            'id': 'id_modelo',
        }),
    )
    data_center = forms.ModelChoiceField(
        queryset=DataCenter.objects.all(),
        empty_label='Select the Data Center',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    tipo = forms.ModelChoiceField(
        queryset=TipoComponente.objects.filter(ativo=True),
        empty_label='Select the type',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo'}),
    )
    disco_capacidade = forms.ChoiceField(
        choices=[('', 'Select')] + Componente.CAPACIDADE_DISCO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Capacity',
    )
    disco_tipo = forms.ChoiceField(
        choices=[('', 'Select')] + Componente.DISCO_TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Type (HDD / SSD / NVMe)',
    )
    disco_interface = forms.ChoiceField(
        choices=[('', 'Select')] + Componente.INTERFACE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Interface (SATA / SAS / NVMe)',
    )
    ram_capacidade = forms.ChoiceField(
        choices=[('', 'Select')] + Componente.RAM_CAPACIDADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Capacity',
    )
    ram_tipo = forms.ChoiceField(
        choices=[('', 'Select')] + Componente.RAM_TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Type (UDIMM / RDIMM)',
    )
    ram_interface = forms.ChoiceField(
        choices=[('', 'Select')] + Componente.RAM_INTERFACE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Interface (DDR4 / DDR5)',
    )
    ram_perfil = forms.ChoiceField(
        choices=[('', 'Select')] + Componente.RAM_PERFIL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Form factor (VLP / LP)',
    )
    quantidade = forms.IntegerField(
        min_value=1,
        max_value=500,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Number of identical units to register.',
    )
    numeros_serie = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 3,
            'placeholder': 'One serial number per line (optional — leave blank if not tracking yet).',
        }),
        label='Serial number(s)',
    )
    codigos_patrimonio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 3,
            'placeholder': 'One asset tag per line (optional).',
        }),
        label='Asset tag(s)',
    )
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )

    def _parse_lista(self, texto, quantidade, campo, label):
        linhas = [l.strip() for l in (texto or '').splitlines() if l.strip()]
        if not linhas:
            return []
        if len(linhas) != quantidade:
            self.add_error(campo, f'Please provide exactly {quantidade} {label} (one per line) or leave it blank.')
        if len(linhas) != len(set(linhas)):
            self.add_error(campo, 'There are duplicate values in this list.')
        return linhas

    def clean(self):
        cleaned = super().clean()
        quantidade = cleaned.get('quantidade') or 0

        series = self._parse_lista(cleaned.get('numeros_serie'), quantidade, 'numeros_serie', 'serial numbers')
        patrimonios = self._parse_lista(
            cleaned.get('codigos_patrimonio'), quantidade, 'codigos_patrimonio', 'asset tags'
        )

        if series:
            existentes = Componente.objects.filter(numero_serie__in=series)
            if existentes.exists():
                self.add_error(
                    'numeros_serie',
                    f'Component(s) already registered with the serial number(s): '
                    f'{", ".join(existentes.values_list("numero_serie", flat=True))}'
                )
        if patrimonios:
            existentes = Componente.objects.filter(codigo_patrimonio__in=patrimonios)
            if existentes.exists():
                self.add_error(
                    'codigos_patrimonio',
                    f'Component(s) already registered with the asset tag(s): '
                    f'{", ".join(existentes.values_list("codigo_patrimonio", flat=True))}'
                )

        cleaned['numeros_serie_lista'] = series
        cleaned['codigos_patrimonio_lista'] = patrimonios

        peca = cleaned.get('peca_padrao')
        if peca:
            cleaned['tipo'] = peca.tipo
            cleaned['fabricante'] = peca.fabricante
            cleaned['modelo'] = peca.modelo
            cleaned['disco_capacidade'] = peca.disco_capacidade
            cleaned['disco_tipo'] = peca.disco_tipo
            cleaned['disco_interface'] = peca.disco_interface

        return cleaned


class RemoverComponentesForm(forms.Form):
    observacoes = forms.CharField(
        label='Reason for removal',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'E.g.: Disk with SMART failure, sent for disposal.',
        }),
        help_text='Describe the reason for removal. It will be logged in each component\'s history.',
    )


class InstalarComponentesForm(forms.Form):
    servidor = forms.ModelChoiceField(
        queryset=Servidor.objects.filter(ativo=True).select_related('data_center'),
        empty_label='Select the server',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    observacoes = forms.CharField(
        required=False,
        label='Notes',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )


class FiltroRelatorioForm(forms.Form):
    data_center = forms.ModelChoiceField(
        queryset=DataCenter.objects.all(),
        required=False,
        empty_label='All DCs',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    tipo = forms.ModelChoiceField(
        queryset=TipoComponente.objects.filter(ativo=True),
        required=False,
        empty_label='All types',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    status = forms.ChoiceField(
        choices=[('', 'All statuses')] + Componente.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    periodo = forms.ChoiceField(
        choices=[
            ('', 'All time'),
            ('mes', 'Last month'),
            ('trimestre', 'Last quarter'),
            ('ano', 'Last year'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )