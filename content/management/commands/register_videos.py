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
        
        for quality_folder, model_field in qualities:
            quality_path = os.path.join(video_path, quality_folder)
            
            if not os.path.exists(quality_path):
                self.stdout.write(
                    self.style.WARNING(f'Quality folder {quality_path} does not exist')
                )
                continue
                
            self.stdout.write(f'Processing {quality_folder} quality videos...')
            
            # Find all video files in this quality folder
            video_files = []
            for ext in video_extensions:
                video_files.extend(glob.glob(os.path.join(quality_path, ext)))
            
            for video_file in video_files:
                filename = os.path.basename(video_file)
                relative_path = os.path.relpath(video_file, settings.MEDIA_ROOT)
                
                if dry_run:
                    self.stdout.write(f'Would register: {filename} ({quality_folder})')
                    continue
                
                # Try to find existing video record
                try:
                    video = Video.objects.get(title=filename.rsplit('.', 1)[0])
                    
                    # Update the video file path based on quality
                    setattr(video, model_field, relative_path)
                    video.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated existing video: {filename} ({quality_folder})')
                    )
                    
                except Video.DoesNotExist:
                    # Create new video record
                    video_data = {
                        'title': filename.rsplit('.', 1)[0],  # Remove extension
                        'description': f'Auto-imported video: {filename}',
                        model_field: relative_path
                    }
                    
                    video = Video.objects.create(**video_data)
                    self.stdout.write(
                        self.style.SUCCESS(f'Created new video: {filename} ({quality_folder})')
                    )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {filename}: {str(e)}')
                    )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('Video registration complete!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Dry run complete. Use without --dry-run to actually register videos.')
            )