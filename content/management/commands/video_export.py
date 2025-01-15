from django.core.management.base import BaseCommand
from import_export import resources
from content.models import Video
from ...admin import VideoResource
import os



class Command(BaseCommand):
    help = "Exportiert Video-Daten in eine CSV-Datei"

    def handle(self, *args, **kwargs):
        dataset = VideoResource().export()
        export_path = os.path.join(os.getcwd(), "video_export.json")
        with open(export_path, "w", encoding="utf-8") as file:
            file.write(dataset.json)
        self.stdout.write(self.style.SUCCESS(f"Videos erfolgreich exportiert nach {export_path}"))
