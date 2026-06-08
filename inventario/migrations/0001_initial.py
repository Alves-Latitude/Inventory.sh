import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status')),
                ('username', models.CharField(max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('perfil', models.CharField(choices=[('admin', 'Administrador'), ('user', 'Usuário')], default='user', max_length=10)),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={'verbose_name': 'Usuário', 'verbose_name_plural': 'Usuários'},
            managers=[('objects', django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name='DataCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('codigo', models.CharField(max_length=20, unique=True)),
                ('cidade', models.CharField(max_length=100)),
                ('observacoes', models.TextField(blank=True)),
            ],
            options={'verbose_name': 'Data Center', 'verbose_name_plural': 'Data Centers', 'ordering': ['nome']},
        ),
        migrations.CreateModel(
            name='TipoComponente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('categoria', models.CharField(choices=[('disco', 'Disco (HDD/SSD/NVMe)'), ('ram', 'Memória RAM'), ('cpu', 'CPU (Processador)'), ('psu', 'Fonte de Alimentação (PSU)'), ('custom', 'Personalizado')], default='custom', max_length=10)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Tipo de Componente', 'verbose_name_plural': 'Tipos de Componentes', 'ordering': ['nome']},
        ),
        migrations.CreateModel(
            name='LimiteEstoque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minimo', models.PositiveIntegerField(default=0)),
                ('data_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.datacenter')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.tipocomponente')),
            ],
            options={'verbose_name': 'Limite de Estoque', 'verbose_name_plural': 'Limites de Estoque', 'unique_together': {('tipo', 'data_center')}},
        ),
        migrations.CreateModel(
            name='Componente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fabricante_modelo', models.CharField(max_length=200, verbose_name='Fabricante e Modelo')),
                ('status', models.CharField(choices=[('em_estoque', 'Em estoque'), ('instalado', 'Instalado'), ('defeituoso', 'Defeituoso'), ('descartado', 'Descartado')], default='em_estoque', max_length=20)),
                ('data_entrada', models.DateField(auto_now_add=True)),
                ('observacoes', models.TextField(blank=True)),
                ('servidor_instalado', models.CharField(blank=True, max_length=100, verbose_name='Servidor onde está instalado')),
                ('disco_capacidade', models.CharField(blank=True, choices=[('500GB', '500GB'), ('1TB', '1TB'), ('2TB', '2TB'), ('4TB', '4TB'), ('8TB', '8TB'), ('12TB', '12TB'), ('16TB', '16TB'), ('18TB', '18TB')], max_length=10)),
                ('disco_tipo', models.CharField(blank=True, choices=[('HDD', 'HDD'), ('SSD', 'SSD'), ('NVMe', 'NVMe')], max_length=5)),
                ('disco_interface', models.CharField(blank=True, choices=[('SATA', 'SATA'), ('SAS', 'SAS'), ('NVMe', 'NVMe')], max_length=5)),
                ('ram_capacidade', models.CharField(blank=True, choices=[('8GB', '8GB'), ('16GB', '16GB'), ('32GB', '32GB'), ('64GB', '64GB'), ('128GB', '128GB')], max_length=10)),
                ('ram_tipo', models.CharField(blank=True, choices=[('DDR4', 'DDR4'), ('DDR5', 'DDR5'), ('ECC DDR4', 'ECC DDR4'), ('ECC DDR5', 'ECC DDR5')], max_length=10)),
                ('ram_velocidade', models.CharField(blank=True, choices=[('2133MHz', '2133MHz'), ('2400MHz', '2400MHz'), ('2666MHz', '2666MHz'), ('3200MHz', '3200MHz'), ('4800MHz', '4800MHz')], max_length=10)),
                ('especificacoes', models.TextField(blank=True, verbose_name='Especificações')),
                ('data_center', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventario.datacenter')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventario.tipocomponente')),
            ],
            options={'verbose_name': 'Componente', 'verbose_name_plural': 'Componentes', 'ordering': ['-data_entrada']},
        ),
        migrations.CreateModel(
            name='Movimentacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('entrada', 'Entrada no DC'), ('instalacao', 'Instalação')], max_length=15)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('servidor', models.CharField(blank=True, max_length=100)),
                ('observacoes', models.TextField(blank=True)),
                ('componente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimentacoes', to='inventario.componente')),
                ('componente_substituido', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='substituicoes', to='inventario.componente', verbose_name='Componente substituído')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Movimentação', 'verbose_name_plural': 'Movimentações', 'ordering': ['-data']},
        ),
    ]
