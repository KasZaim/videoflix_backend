from django.core.management.base import BaseCommand
from django.core.files import File
from content.models import Video  
import os
import glob
from pathlib import Path
from django.conf import settings

class Command(BaseCommand):
    help = 'Register manually uploaded videos in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='videos/',
            help='Path to the videos directory (default: videos/)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )

    def handle(self, *args, **options):
        video_path = options['path']
        dry_run = options['dry_run']
        
        if not os.path.isabs(video_path):
            # Falls der Pfad mit 'media/' beginnt, entferne das Präfix
            if video_path.startswith('media/'): 
                video_path = video_path[len('media/'):]
            video_path = os.path.join(settings.MEDIA_ROOT, video_path)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Check if the directory exists
        if not os.path.exists(video_path):
            self.stdout.write(
                self.style.ERROR(f'Directory {video_path} does not exist')
            )
            return

        # Common video extensions
        video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv', '*.flv']
        
        # Process each quality folder
        qualities = [
            ("1080p", "video_1080p"),
            ("720p", "video_720p"),
            ("480p", "video_480p")
        ]  # Entsprechend der Modellfelder und Ordnerstruktur
        
        # Alle Videos nach Namen sammeln
        video_files_by_name = {}
        for quality_folder, model_field in qualities:
            quality_path = os.path.join(video_path, quality_folder)
            if not os.path.exists(quality_path):
                self.stdout.write(
                    self.style.WARNING(f'Quality folder {quality_path} does not exist')
                )
                continue
            for ext in video_extensions:
                for video_file in glob.glob(os.path.join(quality_path, ext)):
                    filename = os.path.basename(video_file)
                    name_ohne_endung = filename.rsplit('.', 1)[0]
                    relative_path = os.path.relpath(video_file, settings.MEDIA_ROOT)
                    if name_ohne_endung not in video_files_by_name:
                        video_files_by_name[name_ohne_endung] = {}
                    video_files_by_name[name_ohne_endung][model_field] = relative_path
        # Jetzt pro Video-Name ein Objekt anlegen oder aktualisieren
        for name, qualities_dict in video_files_by_name.items():
            if dry_run:
                self.stdout.write(f"Would register: {name} mit Qualitäten: {list(qualities_dict.keys())}")
                continue
            try:
                video = Video.objects.get(title=name)
                for field, path in qualities_dict.items():
                    setattr(video, field, path)
                video.save()
                self.stdout.write(self.style.SUCCESS(f"Updated existing video: {name} mit Qualitäten: {list(qualities_dict.keys())}"))
            except Video.DoesNotExist:
                video_data = {
                    'title': name,
                    'description': f'Auto-imported video: {name}',
                }
                video_data.update(qualities_dict)
                video = Video.objects.create(**video_data)
                self.stdout.write(self.style.SUCCESS(f"Created new video: {name} mit Qualitäten: {list(qualities_dict.keys())}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {name}: {str(e)}"))
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('Video registration complete!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Dry run complete. Use without --dry-run to actually register videos.')
            )