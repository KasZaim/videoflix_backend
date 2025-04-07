from django.contrib import admin
from .models import Video
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class VideoResource(resources.ModelResource):
    
    class Meta:
        model = Video
    

@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    readonly_fields = ('video_1080p', 'video_720p', 'video_480p')  # Nur anzeigen, nicht bearbeitbar
    fields = ('title', 'description', 'original_video_file', 'video_1080p', 'video_720p', 'video_480p', 'created_at', 'thumbnail', 'category')
    list_display = ('title', 'created_at')

def get_readonly_fields(self, request, obj=None):
    if obj:  # Bearbeiten
        return ('video_1080p', 'video_720p', 'video_480p')
    return []