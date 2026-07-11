from django.db.models import Count
from .models import LimiteEstoque, Componente


def alertas_estoque(request):
    if not request.user.is_authenticated:
        return {'alertas_estoque': []}

    alertas = []
    for limite in LimiteEstoque.objects.select_related('tipo', 'data_center').filter(minimo__gt=0):
        quantidade = Componente.objects.filter(
            tipo=limite.tipo,
            data_center=limite.data_center,
            status=Componente.EM_ESTOQUE,
        ).count()
        if quantidade < limite.minimo:
            alertas.append({
                'data_center': limite.data_center,
                'tipo': limite.tipo,
                'quantidade': quantidade,
                'minimo': limite.minimo,
            })

    return {'alertas_estoque': alertas}
