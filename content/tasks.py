import subprocess
import os 

def convert_480p(SOURCE_PATH):
    base, _ = os.path.splitext(SOURCE_PATH)
    target = f"{base}_480p.mp4" 
    source_lin = "/mnt/" + SOURCE_PATH.replace("\\","/").replace("C:", "c")
    target_lin = "/mnt/" +target.replace("\\","/").replace("C:", "c")
    # cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source_lin, target_lin)
    # subprocess.run(cmd,capture_output=True, shell=True) 
    cmd = [
        "ffmpeg",
        "-i", source_lin,
        "-s", "hd480",
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "aac",
        "-strict", "-2",
        target_lin
    ]
    
    # subprocess.run ausführen
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Konvertieren: {e.stderr.decode('utf-8')}")
    
    
def convert_720p(source):
    base, _ = os.path.splitext(source)
    target = f"{base}_720p.mp4" 
    source_lin = "/mnt/" + source.replace("\\","/").replace("C:", "c")
    target_lin = "/mnt/" +target.replace("\\","/").replace("C:", "c")
    cmd = [
        "ffmpeg",
        "-i", source_lin,
        "-s", "hd480",
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "aac",
        "-strict", "-2",
        target_lin
    ]
    
    # subprocess.run ausführen
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Konvertieren: {e.stderr.decode('utf-8')}")
    