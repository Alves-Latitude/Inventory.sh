from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .middleware import get_current_user
from .models import Componente, HistoricoAlteracao

CAMPOS_AUDITADOS = [
    'status', 'servidor_id', 'data_center_id',
    'numero_serie', 'codigo_patrimonio', 'observacoes',
]

NOMES_LEGIVEIS = {
    'status': 'status',
    'servidor_id': 'servidor',
    'data_center_id': 'data center',
    'numero_serie': 'número de série',
    'codigo_patrimonio': 'código patrimonial',
    'observacoes': 'observações',
}


@receiver(pre_save, sender=Componente)
def _capturar_estado_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._estado_anterior = Componente.objects.get(pk=instance.pk)
        except Componente.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender=Componente)
def _registrar_historico(sender, instance, created, **kwargs):
    usuario = get_current_user()
    if usuario is not None and not getattr(usuario, 'is_authenticated', False):
        usuario = None

    if created:
        HistoricoAlteracao.objects.create(
            componente=instance, usuario=usuario, campo='criação',
            valor_anterior='', valor_novo=str(instance),
        )
        return

    anterior = getattr(instance, '_estado_anterior', None)
    if anterior is None:
        return

    for campo in CAMPOS_AUDITADOS:
        valor_antigo = getattr(anterior, campo)
        valor_novo = getattr(instance, campo)
        if valor_antigo != valor_novo:
            HistoricoAlteracao.objects.create(
                componente=instance, usuario=usuario,
                campo=NOMES_LEGIVEIS.get(campo, campo),
                valor_anterior=str(valor_antigo) if valor_antigo not in (None, '') else '—',
                valor_novo=str(valor_novo) if valor_novo not in (None, '') else '—',
            )
