from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from informes.models import Report
from informes.pdf_utils import render_report_to_pdf
from estudios.services import client
from django.conf import settings

class Command(BaseCommand):
    help = "Regenera PDFs (y firma demo si falta) para informes finalizados. Permite filtrar por ID o todos."

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='ID de un Report específico')
        parser.add_argument('--force', action='store_true', help='Forzar regeneración aunque ya exista pdf_file')
        parser.add_argument('--sin-firma', action='store_true', help='No recalcula firma (solo PDF)')
        parser.add_argument('--limit', type=int, help='Limitar cantidad de informes procesados')

    def handle(self, *args, **options):
        report_id = options.get('id')
        force = options.get('force')
        skip_firma = options.get('sin_firma')
        limit = options.get('limit')

        qs = Report.objects.filter(estado=Report.ESTADO_FINAL)
        if report_id:
            qs = qs.filter(id=report_id)
        if limit:
            qs = qs.order_by('id')[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No hay informes que procesar.'))
            return

        self.stdout.write(f"Procesando {total} informe(s)...")
        procesados = 0
        errores = 0
        for r in qs.iterator():
            try:
                with transaction.atomic():
                    # Firma demo
                    if not skip_firma and not r.firma_digital:
                        import hashlib
                        payload = (r.contenido + r.autor.username).encode('utf-8', errors='ignore')
                        r.firma_digital = 'FD-' + hashlib.sha256(payload).hexdigest()[:32]
                        r.save(update_fields=['firma_digital'])
                    # Saltar si ya tiene PDF y no se fuerza
                    if r.pdf_file and not force:
                        self.stdout.write(f"[SKIP] Report {r.id}: ya tiene PDF")
                        continue
                    # Construir study_info
                    pdf_extra = {}
                    try:
                        shared = client.get_study_shared_tags(r.study_internal_id)
                        def val(code):
                            return (shared.get(code, {}) or {}).get('Value') or ''
                        name_raw = val('0010,0010')
                        patient_name = name_raw.replace('^', ' ').strip() if isinstance(name_raw, str) else name_raw
                        pdf_extra['study_info'] = {
                            'patient_name': patient_name,
                            'patient_id': val('0010,0020'),
                            'patient_sex': val('0010,0040'),
                            'birth_date': val('0010,0030'),
                            'study_description': val('0008,1030'),
                            'study_date': val('0008,0020'),
                            'study_time': val('0008,0030'),
                            'accession_number': val('0008,0050'),
                        }
                    except Exception:
                        pass
                    ok, content_file, err = render_report_to_pdf(r, context_extra=pdf_extra)
                    if ok:
                        filename = f"reporte_{r.id}.pdf"
                        r.pdf_file.save(filename, content_file, save=True)
                        self.stdout.write(self.style.SUCCESS(f"[OK] Report {r.id} regenerado"))
                    else:
                        errores += 1
                        self.stdout.write(self.style.ERROR(f"[ERR] Report {r.id}: {err}"))
                procesados += 1
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f"[EXC] Report {r.id}: {e}"))
        self.stdout.write(self.style.SUCCESS(f"Listo. Procesados {procesados}, errores {errores}."))
