from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Envía un email de prueba y muestra configuración SMTP (redactada) para diagnóstico."

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            required=True,
            help="Dirección de correo destino para la prueba",
        )
        parser.add_argument(
            "--subject",
            default="Prueba SMTP",
            help="Asunto del correo de prueba",
        )
        parser.add_argument(
            "--message",
            default=(
                "Este es un correo de prueba enviado por la app Django (comando send_test_email).\n"
                "Si recibiste este mensaje, el backend SMTP está funcionando."
            ),
            help="Cuerpo del correo de prueba",
        )

    def handle(self, *args, **options):
        to_addr = options["to"]

        # Preparar resumen de configuración (sin exponer secretos)
        safe_summary = {
            "EMAIL_BACKEND": getattr(settings, "EMAIL_BACKEND", None),
            "EMAIL_HOST": getattr(settings, "EMAIL_HOST", None),
            "EMAIL_PORT": getattr(settings, "EMAIL_PORT", None),
            "EMAIL_USE_TLS": getattr(settings, "EMAIL_USE_TLS", None),
            "EMAIL_USE_SSL": getattr(settings, "EMAIL_USE_SSL", None),
            "EMAIL_HOST_USER": (getattr(settings, "EMAIL_HOST_USER", None) or "")[:2] + "***" if getattr(settings, "EMAIL_HOST_USER", None) else None,
            "DEFAULT_FROM_EMAIL": getattr(settings, "DEFAULT_FROM_EMAIL", None),
            "EMAIL_TIMEOUT": getattr(settings, "EMAIL_TIMEOUT", None),
            "DEBUG": getattr(settings, "DEBUG", None),
        }

        self.stdout.write(self.style.NOTICE("Resumen SMTP (redactado):"))
        for k, v in safe_summary.items():
            self.stdout.write(f"- {k}: {v}")

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)
        if not from_email:
            raise CommandError("DEFAULT_FROM_EMAIL o EMAIL_HOST_USER no configurados.")

        try:
            sent = send_mail(
                subject=options["subject"],
                message=options["message"],
                from_email=from_email,
                recipient_list=[to_addr],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"OK: send_mail retornó {sent}. Se intentó enviar a {to_addr}"))
        except Exception as e:
            # Mostrar excepción clara para diagnóstico (SMTPAuthenticationError, timeout, etc.)
            raise CommandError(f"Error enviando correo: {e}")
