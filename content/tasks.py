import subprocess
import os
import shutil
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
    # Prüfen, ob ffmpeg installiert ist
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        print("Fehler: ffmpeg ist nicht installiert oder nicht im PATH verfügbar. Bitte installieren Sie ffmpeg: https://ffmpeg.org/download.html")
        return
    else:
        print(f"Gefundener ffmpeg-Pfad: {ffmpeg_path}")
    
    resolutions = {
        "1080p": ("hd1080", "videos/1080p"),
        "720p": ("hd720", "videos/720p"),
        "480p": ("hd480", "videos/480p"),
    }

    # Pfade im Windows-Format beibehalten
    base_filename = os.path.splitext(os.path.basename(source_path))[0]
    
    # Absoluten Pfad für die Quelldatei sicherstellen
    source_win_abs = os.path.abspath(source_path)
    if not os.path.exists(source_win_abs):
        print(f"Quelldatei nicht gefunden: {source_win_abs}")
        return
    
    print(f"Quell-Videodatei: {source_win_abs}")

    converted_files = {}

    for label, (resolution, folder) in resolutions.items():
        # Ausgabeverzeichnis mit korrekten Windows-Pfadseparatoren erstellen
        output_dir = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(output_dir, exist_ok=True)

        # Zieldatei mit korrekten Windows-Pfadseparatoren erstellen
        target_path = os.path.join(output_dir, f"{base_filename}_{label}.mp4")
        target_abs = os.path.abspath(target_path)
        
        print(f"Zieldatei: {target_abs}")

        cmd = [
            ffmpeg_path,
            "-i", source_win_abs,
            "-s", resolution,
            "-c:v", "libx264",
            "-crf", "23",
            "-c:a", "aac",
            "-strict", "-2",
            target_abs
        ]

        try:
            print(f"Konvertierung für {label} wird ausgeführt mit Befehl: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, check=True)
            print(f"Konvertierung für {label} erfolgreich abgeschlossen")
            
            # Relativen Pfad für Datenbank erzeugen und Backslashes zu Forward-Slashes konvertieren (Django-Standard)
            rel_path = os.path.relpath(target_path, settings.MEDIA_ROOT)
            converted_files[label] = rel_path.replace("\\", "/")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            print(f"Konvertierung für {label} fehlgeschlagen: {error_msg}")
        except Exception as e:
            print(f"Unerwarteter Fehler bei Konvertierung für {label}: {str(e)}")

    # Datenbankeintrag aktualisieren
    try:
        video = Video.objects.get(pk=instance_id)
        if "1080p" in converted_files:
            video.video_1080p.name = converted_files["1080p"]
        if "720p" in converted_files:
            video.video_720p.name = converted_files["720p"]
        if "480p" in converted_files:
            video.video_480p.name = converted_files["480p"] 
        video.save()
        print(f"Videoobjekt mit ID {instance_id} erfolgreich aktualisiert")
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Videoobjekts: {str(e)}")