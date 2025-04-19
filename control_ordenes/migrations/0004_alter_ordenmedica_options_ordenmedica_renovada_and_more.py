# Generated by Django 5.1.7 on 2025-04-17 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control_ordenes', '0003_ordenmedica_delete_controlrecetas'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordenmedica',
            options={'ordering': ['-fecha_emision'], 'verbose_name': 'Orden Médica', 'verbose_name_plural': 'Órdenes Médicas'},
        ),
        migrations.AddField(
            model_name='ordenmedica',
            name='renovada',
            field=models.BooleanField(default=False, verbose_name='¿Renovada?'),
        ),
        migrations.AlterField(
            model_name='ordenmedica',
            name='dias_validez',
            field=models.IntegerField(choices=[(30, '30 días'), (60, '60 días'), (90, '90 días')], default=90, verbose_name='Válido por'),
        ),
    ]
