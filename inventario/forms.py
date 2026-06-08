from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    Usuario, DataCenter, TipoComponente, LimiteEstoque,
    Componente, Fabricante,
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


class AdicionarComponentesForm(forms.Form):
    fabricante = forms.ModelChoiceField(
        queryset=Fabricante.objects.all(),
        empty_label='Selecione o fabricante',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    modelo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Exos X18 18TB',
            'id': 'id_modelo',
        }),
    )
    data_center = forms.ModelChoiceField(
        queryset=DataCenter.objects.all(),
        empty_label='Selecione o Data Center',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    tipo = forms.ModelChoiceField(
        queryset=TipoComponente.objects.filter(ativo=True),
        empty_label='Selecione o tipo',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo'}),
    )
    disco_capacidade = forms.ChoiceField(
        choices=[('', 'Selecione')] + Componente.CAPACIDADE_DISCO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Capacidade',
    )
    disco_tipo = forms.ChoiceField(
        choices=[('', 'Selecione')] + Componente.DISCO_TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo (HDD / SSD / NVMe)',
    )
    disco_interface = forms.ChoiceField(
        choices=[('', 'Selecione')] + Componente.INTERFACE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Interface (SATA / SAS / NVMe)',
    )
    quantidade = forms.IntegerField(
        min_value=1,
        max_value=500,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Número de unidades idênticas a cadastrar.',
    )
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )


class RemoverComponentesForm(forms.Form):
    observacoes = forms.CharField(
        label='Motivo da saída',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ex: Disco com falha SMART, enviado para descarte.',
        }),
        help_text='Descreva o motivo da saída. Será registrado no histórico de cada componente.',
    )


class FiltroRelatorioForm(forms.Form):
    data_center = forms.ModelChoiceField(
        queryset=DataCenter.objects.all(),
        required=False,
        empty_label='Todos os DCs',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    tipo = forms.ModelChoiceField(
        queryset=TipoComponente.objects.filter(ativo=True),
        required=False,
        empty_label='Todos os tipos',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Componente.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    periodo = forms.ChoiceField(
        choices=[
            ('', 'Todo o período'),
            ('mes', 'Último mês'),
            ('trimestre', 'Último trimestre'),
            ('ano', 'Último ano'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
