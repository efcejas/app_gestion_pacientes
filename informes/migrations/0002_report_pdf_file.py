from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='reportes_pdf/', help_text='Versión PDF generada al finalizar'),
        ),
    ]