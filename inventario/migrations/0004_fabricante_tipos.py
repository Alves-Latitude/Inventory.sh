from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0003_fabricante'),
    ]

    operations = [
        migrations.AddField(
            model_name='fabricante',
            name='tipos',
            field=models.ManyToManyField(
                blank=True,
                related_name='fabricantes',
                to='inventario.tipocomponente',
            ),
        ),
    ]
