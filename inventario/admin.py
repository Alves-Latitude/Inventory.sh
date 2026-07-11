from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, DataCenter, Servidor, Fabricante, TipoComponente, LimiteEstoque,
    Componente, Movimentacao, PecaPadrao, HistoricoAlteracao,
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'perfil', 'is_active')
    list_filter = ('perfil', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil de acesso', {'fields': ('perfil',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Perfil de acesso', {'fields': ('perfil',)}),
    )


@admin.register(DataCenter)
class DataCenterAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'cidade')
    search_fields = ('nome', 'codigo', 'cidade')


@admin.register(Servidor)
class ServidorAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'data_center', 'ativo')
    list_filter = ('data_center', 'ativo')
    search_fields = ('hostname',)


@admin.register(Fabricante)
class FabricanteAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(TipoComponente)
class TipoComponenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'ativo')
    list_filter = ('categoria', 'ativo')


@admin.register(LimiteEstoque)
class LimiteEstoqueAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'data_center', 'minimo')
    list_filter = ('data_center',)


@admin.register(PecaPadrao)
class PecaPadraoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'fabricante', 'modelo', 'ativo')
    list_filter = ('tipo', 'fabricante', 'ativo')
    search_fields = ('modelo',)


@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = (
        'fabricante', 'modelo', 'tipo', 'numero_serie', 'codigo_patrimonio',
        'status', 'servidor', 'data_center', 'data_entrada',
    )
    list_filter = ('tipo', 'status', 'data_center', 'fabricante')
    search_fields = ('modelo', 'numero_serie', 'codigo_patrimonio')


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'componente', 'servidor', 'usuario', 'data')
    list_filter = ('tipo',)
    readonly_fields = ('data',)


@admin.register(HistoricoAlteracao)
class HistoricoAlteracaoAdmin(admin.ModelAdmin):
    list_display = ('componente', 'campo', 'valor_anterior', 'valor_novo', 'usuario', 'data')
    list_filter = ('campo',)
    search_fields = ('componente__modelo', 'componente__numero_serie')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
