from django.conf import settings
from django.core.mail import send_mail
from .models import Componente, LimiteEstoque


def verificar_e_enviar_alerta_email(tipo, data_center):
    try:
        limite = LimiteEstoque.objects.get(tipo=tipo, data_center=data_center)
    except LimiteEstoque.DoesNotExist:
        return

    quantidade = Componente.objects.filter(
        tipo=tipo,
        data_center=data_center,
        status=Componente.EM_ESTOQUE,
    ).count()

    if quantidade < limite.minimo and settings.ADMIN_EMAIL_LIST:
        assunto = f'[Inventário] Estoque baixo: {tipo} em {data_center}'
        mensagem = (
            f'Atenção: o estoque de {tipo} no {data_center} está abaixo do mínimo configurado.\n\n'
            f'Quantidade atual: {quantidade}\n'
            f'Mínimo configurado: {limite.minimo}\n'
        )
        send_mail(
            assunto,
            mensagem,
            settings.DEFAULT_FROM_EMAIL,
            settings.ADMIN_EMAIL_LIST,
            fail_silently=True,
        )
