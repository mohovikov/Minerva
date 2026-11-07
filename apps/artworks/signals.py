from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Artwork


@receiver(post_delete, sender=Artwork)
def delete_files_on_artwork_delete(sender, instance, **kwargs):
    """
    Удаляет физические файлы с диска при удалении записи Artwork.
    Срабатывает при удалении через сайт, через админку или через код.
    """
    if instance.original_file:
        instance.original_file.delete(save=False)
    if instance.thumbnail_file:
        instance.thumbnail_file.delete(save=False)
