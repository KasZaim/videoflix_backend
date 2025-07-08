import os
import django
import glob
import re

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'videoflix.settings')
django.setup()

from content.models import Video
from django.conf import settings

def extract_base_name(filename, quality_folder):
    """Extract the base name from a filename, removing quality suffixes"""
    base_name = filename.rsplit('.', 1)[0]  # Remove extension
    
    # Remove quality suffixes like _1080p, _720p, _480p
    if quality_folder != 'originals':
        # Remove common quality patterns
        patterns = [
            f'_{quality_folder}',  # e.g., _1080p
            f'-{quality_folder}',  # e.g., -1080p
            '_1080p', '_720p', '_480p',  # explicit patterns
            '-1080p', '-720p', '-480p'
        ]
        
        for pattern in patterns:
            if base_name.endswith(pattern):
                base_name = base_name[:-len(pattern)]
                break
    
    return base_name

def register_videos():
    video_path = os.path.join(settings.MEDIA_ROOT, 'videos')
    
    # Quality folders mapping to model fields
    quality_mapping = {
        'originals': 'original_video_file',
        '1080p': 'video_1080p',
        '720p': 'video_720p',
        '480p': 'video_480p'
    }
    
    # Collect all videos by their base name
    videos_by_base_name = {}
    
    print("🔍 Scanning for videos...")
    print(f"📁 Video directory: {video_path}")
    
    for quality_folder, field_name in quality_mapping.items():
        quality_path = os.path.join(video_path, quality_folder)
        
        if not os.path.exists(quality_path):
            print(f'⚠️  Skipping {quality_folder} - folder does not exist: {quality_path}')
            continue
            
        print(f'\n📂 Scanning {quality_folder} in: {quality_path}')
        
        # Find all video files
        video_files = []
        for ext in ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv', '*.flv', '*.webm']:
            video_files.extend(glob.glob(os.path.join(quality_path, ext)))
        
        print(f'   Found {len(video_files)} files')
        
        for video_file in video_files:
            filename = os.path.basename(video_file)
            
            # Extract base name (remove quality suffix)
            base_name = extract_base_name(filename, quality_folder)
            
            # Create relative path from MEDIA_ROOT
            relative_path = os.path.relpath(video_file, settings.MEDIA_ROOT)
            
            if base_name not in videos_by_base_name:
                videos_by_base_name[base_name] = {}
            
            videos_by_base_name[base_name][field_name] = relative_path
            print(f'   📄 {filename} -> base: {base_name} (field: {field_name})')
    
    if not videos_by_base_name:
        print('❌ No videos found!')
        return
    
    print(f'\n🎬 Found {len(videos_by_base_name)} unique video groups:')
    for base_name, qualities in videos_by_base_name.items():
        quality_names = [k.replace('video_', '').replace('original_video_file', 'original') for k in qualities.keys()]
        print(f'   📽️  {base_name}: {quality_names}')
    
    print('\n🔄 Processing videos...\n')
    
    # Process each video group
    for base_name, quality_paths in videos_by_base_name.items():
        print(f'Processing: {base_name}')
        
        # Try to get existing video or create new one
        video, created = Video.objects.get_or_create(
            title=base_name,
            defaults={
                'description': f'Auto-imported: {base_name}',
                'category': 'imported'
            }
        )
        
        # Update ALL quality paths for this video
        updated_qualities = []
        for field_name, path in quality_paths.items():
            setattr(video, field_name, path)
            display_name = field_name.replace('video_', '').replace('original_video_file', 'original')
            updated_qualities.append(display_name)
        
        video.save()
        
        action = '✅ Created' if created else '🔄 Updated'
        print(f'{action} video: {base_name} with qualities: {", ".join(updated_qualities)}')
    
    print(f'\n🎉 Done! Total videos in database: {Video.objects.count()}')
    
    # Show detailed summary
    videos_with_originals = Video.objects.exclude(original_video_file='').count()
    videos_with_1080p = Video.objects.exclude(video_1080p='').count()
    videos_with_720p = Video.objects.exclude(video_720p='').count()
    videos_with_480p = Video.objects.exclude(video_480p='').count()
    
    print(f'\n📊 Quality distribution:')
    print(f'   Videos with originals: {videos_with_originals}')
    print(f'   Videos with 1080p: {videos_with_1080p}')
    print(f'   Videos with 720p: {videos_with_720p}')
    print(f'   Videos with 480p: {videos_with_480p}')

if __name__ == '__main__':
    try:
        register_videos()
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()