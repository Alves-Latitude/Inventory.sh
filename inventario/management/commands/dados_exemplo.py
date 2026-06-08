"""
Cria dados de exemplo para testes: 3 DCs + componentes variados.
Uso: python manage.py dados_exemplo
"""
from django.core.management.base import BaseCommand
from inventario.models import Componente, DataCenter, Fabricante, Movimentacao, TipoComponente, Usuario


DCS = [
    {'nome': 'DC São Paulo 01',    'codigo': 'SP01', 'cidade': 'São Paulo, SP'},
    {'nome': 'DC Rio de Janeiro 01', 'codigo': 'RJ01', 'cidade': 'Rio de Janeiro, RJ'},
    {'nome': 'DC Fortaleza 01',    'codigo': 'FOR01', 'cidade': 'Fortaleza, CE'},
]

# (fabricante, modelo, tipo_nome, capacidade, disco_tipo, interface, dc_codigo, qtd)
COMPONENTES = [
    # SP01 — discos HDD SATA
    ('Seagate',        'Exos X18 18TB',      'Disco', '18TB', 'HDD', 'SATA', 'SP01', 4),
    ('Seagate',        'Exos X16 16TB',      'Disco', '16TB', 'HDD', 'SATA', 'SP01', 3),
    ('Western Digital','WD Gold 8TB',        'Disco', '8TB',  'HDD', 'SATA', 'SP01', 5),
    # SP01 — SSD NVMe
    ('Samsung',        '970 EVO Plus 1TB',   'Disco', '1TB',  'NVMe','NVMe', 'SP01', 2),
    # SP01 — RAM
    ('Kingston',       'Server Premier 32GB DDR4 3200MHz', 'Memória RAM', '', '', '', 'SP01', 6),

    # RJ01 — discos SAS
    ('Seagate',        'Exos 10E2400 2TB',   'Disco', '2TB',  'HDD', 'SAS',  'RJ01', 6),
    ('Toshiba',        'MG08 12TB',          'Disco', '12TB', 'HDD', 'SAS',  'RJ01', 4),
    # RJ01 — SSD SATA
    ('Samsung',        '870 EVO 4TB',        'Disco', '4TB',  'SSD', 'SATA', 'RJ01', 3),
    # RJ01 — NVMe
    ('Samsung',        '990 Pro 2TB',        'Disco', '2TB',  'NVMe','NVMe', 'RJ01', 2),
    # RJ01 — RAM
    ('Kingston',       'Server Premier 16GB DDR4 2666MHz', 'Memória RAM', '', '', '', 'RJ01', 8),
    ('Crucial',        'DDR4 32GB ECC 3200MHz',           'Memória RAM', '', '', '', 'RJ01', 4),

    # FOR01 — discos HDD SATA
    ('Western Digital','WD Gold 4TB',        'Disco', '4TB',  'HDD', 'SATA', 'FOR01', 5),
    ('Toshiba',        'MG07 8TB',           'Disco', '8TB',  'HDD', 'SATA', 'FOR01', 3),
    # FOR01 — SSD NVMe
    ('Samsung',        '980 Pro 1TB',        'Disco', '1TB',  'NVMe','NVMe', 'FOR01', 4),
    # FOR01 — RAM
    ('Kingston',       'Server Premier 64GB DDR4 3200MHz', 'Memória RAM', '', '', '', 'FOR01', 2),
]


class Command(BaseCommand):
    help = 'Cria dados de exemplo: 3 DCs e componentes variados para testes.'

    def handle(self, *args, **options):
        admin = Usuario.objects.filter(username='admin').first()

        # Cria DCs
        dcs = {}
        for d in DCS:
            dc, created = DataCenter.objects.get_or_create(
                codigo=d['codigo'],
                defaults={'nome': d['nome'], 'cidade': d['cidade']},
            )
            dcs[d['codigo']] = dc
            self.stdout.write(f'  DC {"criado" if created else "já existe"}: {dc}')

        # Cria componentes
        total = 0
        for fab_nome, modelo, tipo_nome, cap, disco_tipo, interface, dc_cod, qtd in COMPONENTES:
            try:
                fabricante = Fabricante.objects.get(nome=fab_nome)
                tipo = TipoComponente.objects.get(nome=tipo_nome)
                dc = dcs[dc_cod]
            except (Fabricante.DoesNotExist, TipoComponente.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f'  Pulando "{modelo}": {e}'))
                continue

            for _ in range(qtd):
                comp = Componente.objects.create(
                    tipo=tipo,
                    fabricante=fabricante,
                    modelo=modelo,
                    status=Componente.EM_ESTOQUE,
                    data_center=dc,
                    disco_capacidade=cap,
                    disco_tipo=disco_tipo,
                    disco_interface=interface,
                )
                Movimentacao.objects.create(
                    componente=comp,
                    tipo=Movimentacao.ENTRADA,
                    usuario=admin,
                    observacoes='Dado de exemplo.',
                )
            total += qtd
            self.stdout.write(f'  {qtd}x {fab_nome} {modelo} → {dc_cod}')

        self.stdout.write(self.style.SUCCESS(f'\n{total} componentes de exemplo criados!'))
