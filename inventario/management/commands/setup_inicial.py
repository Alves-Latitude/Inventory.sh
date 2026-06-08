"""
Comando de setup inicial: cria admin padrão, fabricantes e tipos de componentes.
Uso: python manage.py setup_inicial
"""
from django.core.management.base import BaseCommand
from inventario.models import Fabricante, TipoComponente, Usuario


TIPOS_INICIAIS = [
    ('Disco', TipoComponente.DISCO),
    ('Memória RAM', TipoComponente.RAM),
    ('CPU (Processador)', TipoComponente.CPU),
    ('Fonte de Alimentação (PSU)', TipoComponente.PSU),
]

# fabricante -> lista de categorias de tipo a que pertence
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


class Command(BaseCommand):
    help = 'Cria dados iniciais: fabricantes, tipos de componentes e usuário admin.'

    def handle(self, *args, **options):
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
