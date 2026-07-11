import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_simplificar_componente'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fabricante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Fabricante',
                'verbose_name_plural': 'Fabricantes',
                'ordering': ['nome'],
            },
        ),
        # Adiciona o campo FK temporariamente como nullable
        migrations.AddField(
            model_name='componente',
            name='fabricante_fk',
            field=models.ForeignKey(
                to='inventario.fabricante',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                db_column='fabricante_fk_id',
            ),
        ),
        # Remove o campo CharField antigo
        migrations.RemoveField(model_name='componente', name='fabricante'),
        # Renomeia a FK para 'fabricante'
        migrations.RenameField(
            model_name='componente',
            old_name='fabricante_fk',
            new_name='fabricante',
        ),
        # Torna não-nullable após a renomeação
        migrations.AlterField(
            model_name='componente',
            name='fabricante',
            field=models.ForeignKey(
                to='inventario.fabricante',
                on_delete=django.db.models.deletion.PROTECT,
            ),
        ),
    ]
