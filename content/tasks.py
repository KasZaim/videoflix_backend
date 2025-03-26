import subprocess
import os 
from content.models import Video
from django.conf import settings

# def convert_480p(SOURCE_PATH):
#     base, _ = os.path.splitext(SOURCE_PATH)
#     target = f"{base}_480p.mp4" 
#     source_lin = "/mnt/" + SOURCE_PATH.replace("\\","/").replace("C:", "c")
#     target_lin = "/mnt/" +target.replace("\\","/").replace("C:", "c")
#     # cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source_lin, target_lin)
#     # subprocess.run(cmd,capture_output=True, shell=True) 
#     cmd = [
#         "ffmpeg",
#         "-i", source_lin,
#         "-s", "hd480",
#         "-c:v", "libx264",
#         "-crf", "23",
#         "-c:a", "aac",
#         "-strict", "-2",
#         target_lin
#     ]
    
#     # subprocess.run ausführen
#     try:
#         subprocess.run(cmd, capture_output=True, check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Fehler beim Konvertieren: {e.stderr.decode('utf-8')}")
    
    
# def convert_720p(source):
#     base, _ = os.path.splitext(source)
#     target = f"{base}_720p.mp4" 
#     source_lin = "/mnt/" + source.replace("\\","/").replace("C:", "c")
#     target_lin = "/mnt/" +target.replace("\\","/").replace("C:", "c")
#     cmd = [
#         "ffmpeg",
#         "-i", source_lin,
#         "-s", "hd480",
#         "-c:v", "libx264",
#         "-crf", "23",
#         "-c:a", "aac",
#         "-strict", "-2",
#         target_lin
#     ]
    
#     # subprocess.run ausführen
#     try:
#         subprocess.run(cmd, capture_output=True, check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Fehler beim Konvertieren: {e.stderr.decode('utf-8')}")
    
    
    
def convert_all_qualities(source_path, instance_id):
    resolutions = {
        "1080p": ("hd1080", "videos/1080"),
        "720p": ("hd720", "videos/720p"),
        "480p": ("hd480", "videos/480p"),
    }

    base_filename = os.path.splitext(os.path.basename(source_path))[0]
    source_lin = "/mnt/" + source_path.replace("\\", "/").replace("C:", "c")

    converted_files = {}

    for label, (resolution, folder) in resolutions.items():
        output_dir = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(output_dir, exist_ok=True)  # Ordner erstellen, falls nicht vorhanden

        target_path = os.path.join(output_dir, f"{base_filename}_{label}.mp4")
        target_lin = "/mnt/" + target_path.replace("\\", "/").replace("C:", "c")

        cmd = [
            "ffmpeg",
            "-i", source_lin,
            "-s", resolution,
            "-c:v", "libx264",
            "-crf", "23",
            "-c:a", "aac",
            "-strict", "-2",
            target_lin
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            converted_files[label] = os.path.relpath(target_path, settings.MEDIA_ROOT).replace("\\", "/")
        except subprocess.CalledProcessError as e:
            print(f"Konvertierung für {label} fehlgeschlagen:", e.stderr.decode('utf-8'))

    # Datenbankeintrag aktualisieren
    video = Video.objects.get(pk=instance_id)
    if "1080p" in converted_files:
        video.video_1080p.name = converted_files["1080p"]
    if "720p" in converted_files:
        video.video_720p.name = converted_files["720p"]
    if "480p" in converted_files:
        video.video_480p.name = converted_files["480p"]
    video.save()