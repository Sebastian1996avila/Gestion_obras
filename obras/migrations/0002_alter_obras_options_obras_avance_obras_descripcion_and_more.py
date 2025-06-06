# Generated by Django 5.2.1 on 2025-05-30 00:00

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obras', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='obras',
            options={'ordering': ['-fecha_creacion'], 'verbose_name': 'Obra', 'verbose_name_plural': 'Obras'},
        ),
        migrations.AddField(
            model_name='obras',
            name='avance',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='obras',
            name='descripcion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='obras',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='obras',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='obras',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='obras/'),
        ),
        migrations.AddField(
            model_name='obras',
            name='presupuesto',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
