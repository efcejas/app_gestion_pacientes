from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('informes', '0006_report_study_snapshot'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='version',
            field=models.PositiveIntegerField(default=1, help_text='Número de versión secuencial para el mismo estudio_internal_id'),
        ),
        migrations.AlterField(
            model_name='report',
            name='study_instance_uid',
            field=models.CharField(max_length=128, help_text='Study Instance UID (0020,000D)'),
        ),
        migrations.RemoveConstraint(
            model_name='report',
            name='uniq_report_by_internal_study',
        ),
        migrations.AddConstraint(
            model_name='report',
            constraint=models.UniqueConstraint(fields=('study_internal_id', 'version'), name='uniq_report_by_internal_study_version'),
        ),
        migrations.CreateModel(
            name='LogInforme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accion', models.CharField(help_text='draft_save | finalize', max_length=32)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('contenido_hash', models.CharField(blank=True, max_length=64)),
                ('pdf_hash', models.CharField(blank=True, max_length=64)),
                ('report_version', models.PositiveIntegerField(default=1)),
                ('template_version', models.CharField(default='1.0.0', max_length=16)),
                ('pdf_size', models.IntegerField(blank=True, help_text='Tamaño del PDF en bytes al momento del log', null=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='informes.report')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Log de Informe',
                'verbose_name_plural': 'Logs de Informes',
                'ordering': ['-timestamp'],
            },
        ),
    ]
