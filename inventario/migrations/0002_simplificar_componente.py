import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        # Adiciona os novos campos
        migrations.AddField(
            model_name='componente',
            name='fabricante',
            field=models.CharField(max_length=100, choices=[
                ('Seagate', 'Seagate'), ('Western Digital', 'Western Digital'),
                ('Toshiba', 'Toshiba'), ('Samsung', 'Samsung'),
                ('Kingston', 'Kingston'), ('Crucial', 'Crucial'),
                ('Micron', 'Micron'), ('HGST', 'HGST'), ('Intel', 'Intel'),
                ('SanDisk', 'SanDisk'), ('SK Hynix', 'SK Hynix'), ('Outro', 'Outro'),
            ], default='Outro'),
        ),
        migrations.AddField(
            model_name='componente',
            name='modelo',
            field=models.CharField(max_length=200, default=''),
            preserve_default=False,
        ),
        # Remove campos antigos
        migrations.RemoveField(model_name='componente', name='fabricante_modelo'),
        migrations.RemoveField(model_name='componente', name='servidor_instalado'),
        migrations.RemoveField(model_name='componente', name='ram_capacidade'),
        migrations.RemoveField(model_name='componente', name='ram_tipo'),
        migrations.RemoveField(model_name='componente', name='ram_velocidade'),
        migrations.RemoveField(model_name='componente', name='especificacoes'),
        # Atualiza choices do status
        migrations.AlterField(
            model_name='componente',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[('em_estoque', 'Em estoque'), ('removido', 'Removido')],
                default='em_estoque',
            ),
        ),
        # Atualiza choices do tipo de movimentação
        migrations.AlterField(
            model_name='movimentacao',
            name='tipo',
            field=models.CharField(
                max_length=10,
                choices=[('entrada', 'Entrada'), ('saida', 'Saída')],
            ),
        ),
        # Remove campo servidor da movimentação
        migrations.RemoveField(model_name='movimentacao', name='servidor'),
        migrations.RemoveField(model_name='movimentacao', name='componente_substituido'),
        # Remove categoria RAM do TipoComponente
        migrations.AlterField(
            model_name='tipocomponente',
            name='categoria',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('disco', 'Disco'),
                    ('ram', 'Memória RAM'),
                    ('cpu', 'CPU (Processador)'),
                    ('psu', 'Fonte de Alimentação (PSU)'),
                    ('custom', 'Personalizado'),
                ],
                default='disco',
            ),
        ),
    ]
