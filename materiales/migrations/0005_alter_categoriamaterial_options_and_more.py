# Generated by Django 5.2.1 on 2025-06-01 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiales', '0004_alter_material_unidad_medida'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoriamaterial',
            options={'ordering': ['orden', 'nombre'], 'verbose_name': 'Categoría de Material', 'verbose_name_plural': 'Categorías de Materiales'},
        ),
        migrations.AddField(
            model_name='categoriamaterial',
            name='activa',
            field=models.BooleanField(default=True, help_text='Indica si la categoría está activa'),
        ),
        migrations.AddField(
            model_name='categoriamaterial',
            name='codigo',
            field=models.CharField(blank=True, help_text='Código único para identificar la categoría', max_length=10, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='categoriamaterial',
            name='color',
            field=models.CharField(default='#000000', help_text='Color en formato hexadecimal para identificar la categoría', max_length=7),
        ),
        migrations.AddField(
            model_name='categoriamaterial',
            name='orden',
            field=models.IntegerField(default=0, help_text='Orden de visualización de la categoría'),
        ),
    ]
