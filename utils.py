import os
import sys
import shutil
import subprocess

def get_ffmpeg_path() -> str:
    """
    Find FFmpeg executable path.
    Checks PyInstaller bundle dir, app directory, and system PATH.
    """
    # 1. Check inside PyInstaller temp bundle directory
    if hasattr(sys, '_MEIPASS'):
        bundle_ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
        if os.path.isfile(bundle_ffmpeg):
            return bundle_ffmpeg
        bundle_ffmpeg_no_ext = os.path.join(sys._MEIPASS, 'ffmpeg')
        if os.path.isfile(bundle_ffmpeg_no_ext):
            return bundle_ffmpeg_no_ext

    # 2. Check current working directory or script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_ffmpeg = os.path.join(script_dir, 'ffmpeg.exe')
    if os.path.isfile(local_ffmpeg):
        return local_ffmpeg

    cwd_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg.exe')
    if os.path.isfile(cwd_ffmpeg):
        return cwd_ffmpeg

    # 3. Check system PATH
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        return system_ffmpeg

    return "ffmpeg"  # Fallback to binary name in case subprocess can resolve it


def get_ffprobe_path() -> str:
    """
    Find FFprobe executable path.
    """
    if hasattr(sys, '_MEIPASS'):
        bundle_ffprobe = os.path.join(sys._MEIPASS, 'ffprobe.exe')
        if os.path.isfile(bundle_ffprobe):
            return bundle_ffprobe

    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_ffprobe = os.path.join(script_dir, 'ffprobe.exe')
    if os.path.isfile(local_ffprobe):
        return local_ffprobe

    system_ffprobe = shutil.which('ffprobe')
    if system_ffprobe:
        return system_ffprobe

    return "ffprobe"


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format (KB, MB, GB)."""
    if size_bytes <= 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"


def format_time(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    total_sec = int(round(seconds))
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def open_folder(path: str):
    """Open folder in OS file explorer."""
    if not os.path.exists(path):
        return
    norm_path = os.path.normpath(path)
    if os.name == 'nt':
        os.startfile(norm_path)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', norm_path])
    else:
        subprocess.Popen(['xdg-open', norm_path])
