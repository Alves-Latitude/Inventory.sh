from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, DataCenter, Fabricante, TipoComponente, LimiteEstoque, Componente, Movimentacao


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


@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ('fabricante', 'modelo', 'tipo', 'status', 'data_center', 'data_entrada')
    list_filter = ('tipo', 'status', 'data_center', 'fabricante')
    search_fields = ('fabricante', 'modelo')


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'componente', 'usuario', 'data')
    list_filter = ('tipo',)
    readonly_fields = ('data',)
