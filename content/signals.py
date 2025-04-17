from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
# from .tasks import convert_480p,convert_720p
import glob
import django_rq
from .tasks import convert_all_qualities

@receiver(post_save, sender=Video)
def video_post_Save(sender, instance, created, **kwargs):
    if created and instance.original_video_file:
        print("Neues Video gespeichert – starte Konvertierung...")
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_all_qualities, instance.original_video_file.path, instance.id)
            

@receiver(post_delete, sender=Video)
def auto_delete_files_on_video_delete(sender, instance, **kwargs):
    # Originalvideo löschen
    if instance.original_video_file and os.path.isfile(instance.original_video_file.path):
        os.remove(instance.original_video_file.path)

    # Konvertierte Videos löschen
    for quality_field in ['video_1080p', 'video_720p', 'video_480p']:
        file_field = getattr(instance, quality_field)
        if file_field and os.path.isfile(file_field.path):
            os.remove(file_field.path)
            
    # Thumbnail löschen
    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)