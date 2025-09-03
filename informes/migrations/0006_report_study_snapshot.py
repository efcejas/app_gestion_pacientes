from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('informes', '0005_report_hashes'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='study_snapshot',
            field=models.JSONField(blank=True, null=True, help_text='Copia inmutable de datos paciente/estudio al finalizar'),
        ),
    ]
