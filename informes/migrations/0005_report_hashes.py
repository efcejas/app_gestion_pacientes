from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('informes', '0004_merge_conflict_0003s'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='contenido_hash',
            field=models.CharField(max_length=64, blank=True, help_text='SHA256 del HTML final almacenado'),
        ),
        migrations.AddField(
            model_name='report',
            name='pdf_hash',
            field=models.CharField(max_length=64, blank=True, help_text='SHA256 del archivo PDF generado'),
        ),
    ]
