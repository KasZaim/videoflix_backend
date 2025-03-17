from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
from .tasks import convert_480p,convert_720p
import glob
import django_rq


@receiver(post_save, sender=Video)
def video_post_Save(sender, instance, created, **kwargs):
    print('video wurde gespeichert')
    if created:
        print('new video created')
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path) #tasks
        queue.enqueue(convert_720p, instance.video_file.path) #tasks
        
        
@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        base_path, _ = os.path.splitext(instance.video_file.path)

        for file_path in glob.glob(f"{base_path}*"):
            if os.path.isfile(file_path):
                os.remove(file_path)