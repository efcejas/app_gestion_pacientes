from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informes', '0002_report_pdf_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='firma_digital',
            field=models.CharField(blank=True, help_text='Representación (demo) de la firma digital del autor', max_length=256),
        ),
    ]