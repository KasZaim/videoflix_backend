from django.db import models
from datetime import date
class Video(models.Model):
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    original_video_file = models.FileField(upload_to='videos/originals/', blank=True, null=True)
    video_1080p = models.FileField(upload_to='videos/1080p/', blank=True, null=True)
    video_720p = models.FileField(upload_to='videos/720p/', blank=True, null=True)
    video_480p = models.FileField(upload_to='videos/480p/', blank=True, null=True)
    thumbnail = models.FileField(upload_to='img/thumbnails/', blank=True, null=True, help_text="Erlaubte Bildformate: JPG, PNG, WEBP. Empfohlene Größe: 1280x720px.")
    category = models.CharField(max_length=50 , null=True, blank=True)
    
    def __str__(self):
        return self.title