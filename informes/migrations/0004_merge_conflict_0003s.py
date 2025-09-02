from django.db import migrations

class Migration(migrations.Migration):
    """Merge de las dos migraciones 0003 para resolver conflicto de ramas.
    No realiza operaciones nuevas: simplemente une los nodos leaf
    (0003_report_firma_digital y 0003_report_uniq_report_by_internal_study).
    Estado final del modelo ya contempla ambos cambios.
    """

    dependencies = [
        ('informes', '0003_report_firma_digital'),
        ('informes', '0003_report_uniq_report_by_internal_study'),
    ]

    operations = []
