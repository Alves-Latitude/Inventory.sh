"""
Comando de setup inicial: cria admin padrão, fabricantes, tipos de componentes e Data Centers.
Uso: python manage.py setup_inicial
"""
from django.core.management.base import BaseCommand
from inventario.models import DataCenter, Fabricante, TipoComponente, Usuario


TIPOS_INICIAIS = [
    ('Disco', TipoComponente.DISCO),
    ('Memória RAM', TipoComponente.RAM),
    ('CPU (Processador)', TipoComponente.CPU),
    ('Fonte de Alimentação (PSU)', TipoComponente.PSU),
]

FABRICANTES_TIPOS = {
    'Crucial':        ['disco', 'ram'],
    'HGST':           ['disco'],
    'Intel':          ['disco', 'cpu'],
    'Kingston':       ['disco', 'ram'],
    'Micron':         ['disco', 'ram'],
    'Samsung':        ['disco', 'ram'],
    'SanDisk':        ['disco'],
    'Seagate':        ['disco'],
    'SK Hynix':       ['disco', 'ram'],
    'Toshiba':        ['disco'],
    'Western Digital':['disco'],
}

DATACENTERS_INICIAIS = {
    'ASH': ('DC Ashburn', 'Ashburn, VA - EUA'),
    'CHI': ('DC Chicago', 'Chicago, IL - EUA'),
    'DAL': ('DC Dallas', 'Dallas, TX - EUA'),
    'FRA': ('DC Frankfurt', 'Frankfurt - Alemanha'),
    'LAX': ('DC Los Angeles', 'Los Angeles, CA - EUA'),
    'LON1': ('DC Londres 1', 'Londres - Reino Unido'),
    'LON2': ('DC Londres 2', 'Londres - Reino Unido'),
    'NYC': ('DC Nova York', 'Nova York, NY - EUA'),
    'SGP': ('DC Singapura', 'Singapura'),
    'SJC': ('DC San Jose', 'San Jose, CA - EUA'),
    'SP1': ('DC São Paulo 1', 'São Paulo, SP - Brasil'),
    'SP2': ('DC São Paulo 2', 'São Paulo, SP - Brasil'),
    'TOR': ('DC Toronto', 'Toronto - Canadá'),
    'TYO': ('DC Tóquio', 'Tóquio - Japão'),
    'AMS': ('DC Amsterdã', 'Amsterdã - Holanda'),
    'BUE': ('DC Buenos Aires', 'Buenos Aires - Argentina'),
    'MEX': ('DC Cidade do México', 'Cidade do México - México'),
    'MIA1': ('DC Miami 1', 'Miami, FL - EUA'),
    'MIA2': ('DC Miami 2', 'Miami, FL - EUA'),
    'SYD': ('DC Sydney', 'Sydney - Austrália'),
    'BGT': ('DC Bogotá', 'Bogotá - Colômbia'),
}


class Command(BaseCommand):
    help = 'Cria dados iniciais: Data Centers, fabricantes, tipos de componentes e usuário admin.'

    def handle(self, *args, **options):
        self.stdout.write('Criando Data Centers...')
        for codigo, (nome, cidade) in DATACENTERS_INICIAIS.items():
            _, created = DataCenter.objects.get_or_create(
                codigo=codigo, defaults={'nome': nome, 'cidade': cidade}
            )
            if created:
                self.stdout.write(f'  + {codigo} — {nome}')

        self.stdout.write('Criando tipos de componentes...')
        for nome, categoria in TIPOS_INICIAIS:
            _, created = TipoComponente.objects.get_or_create(nome=nome, defaults={'categoria': categoria})
            if created:
                self.stdout.write(f'  + {nome}')

        self.stdout.write('Criando fabricantes e associando tipos...')
        for nome, categorias in FABRICANTES_TIPOS.items():
            fab, created = Fabricante.objects.get_or_create(nome=nome)
            tipos_qs = TipoComponente.objects.filter(categoria__in=categorias)
            fab.tipos.set(tipos_qs)
            if created:
                self.stdout.write(f'  + {nome}')

        if not Usuario.objects.filter(username='admin').exists():
            Usuario.objects.create_superuser(
                username='admin',
                email='',
                password='admin123',
                perfil=Usuario.PERFIL_ADMIN,
            )
            self.stdout.write(self.style.SUCCESS(
                '\n  Usuário admin criado. Login: admin / Senha: admin123'
                '\n  IMPORTANTE: Troque a senha imediatamente após o primeiro login!'
            ))
        else:
            self.stdout.write('  Usuário admin já existe.')

        self.stdout.write(self.style.SUCCESS('\nSetup concluído!'))
