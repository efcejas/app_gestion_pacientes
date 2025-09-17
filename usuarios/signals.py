from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

Usuario = get_user_model()


def _delete_file(file_field):
    try:
        if file_field and getattr(file_field, 'name', None):
            storage = file_field.storage
            name = file_field.name
            if storage.exists(name):
                storage.delete(name)
    except Exception:
        # No interrumpir el flujo si falla el borrado
        pass


@receiver(pre_save, sender=Usuario)
def delete_old_signature_on_change(sender, instance, **kwargs):
    """Si el usuario tiene una firma previa y está cambiando el archivo, borrar la anterior."""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    old_file = getattr(old, 'signature_image', None)
    new_file = getattr(instance, 'signature_image', None)
    # Si hay archivo anterior y el nombre cambió, borrar el viejo
    if old_file and new_file and old_file.name != new_file.name:
        _delete_file(old_file)


@receiver(post_delete, sender=Usuario)
def delete_signature_on_user_delete(sender, instance, **kwargs):
    """Al eliminar el usuario, borrar la firma asociada si existe."""
    file_field = getattr(instance, 'signature_image', None)
    if file_field:
        _delete_file(file_field)
