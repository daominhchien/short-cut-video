import os
import sys
import subprocess
import customtkinter

# Configure stdout for utf-8 output on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def build_exe():
    """
    Build standalone Windows executable using PyInstaller.
    Bundles CustomTkinter assets and optionally ffmpeg.exe if present in directory.
    """
    print("=== Khoi dong dong goi Video Splitter bang PyInstaller ===")

    # CustomTkinter asset directory
    ctk_dir = os.path.dirname(customtkinter.__file__)
    print(f"CustomTkinter module path: {ctk_dir}")

    # Separator for Windows PyInstaller --add-data is ';'
    sep = ";" if os.name == 'nt' else ":"

    # PyInstaller arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=VideoSplitter",
        f"--add-data={ctk_dir}{sep}customtkinter/",
        "--clean",
    ]

    # Include ffmpeg.exe if present in the current working directory
    local_ffmpeg = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
    if os.path.isfile(local_ffmpeg):
        print(f"Phat hien {local_ffmpeg}, dang nhung vao file .exe...")
        cmd.append(f"--add-binary={local_ffmpeg}{sep}.")

    cmd.append("app.py")

    print("\nDang thuc thi lenh PyInstaller:")
    print(" ".join(cmd))
    print("-" * 60)

    try:
        subprocess.run(cmd, check=True)
        print("-" * 60)
        dist_exe = os.path.join("dist", "VideoSplitter.exe" if os.name == 'nt' else "VideoSplitter")
        if os.path.isfile(dist_exe):
            size_mb = os.path.getsize(dist_exe) / (1024 * 1024)
            print(f"DONG GOI THANH CONG!")
            print(f"File thuc thi (.exe) luu tai: {os.path.abspath(dist_exe)} ({size_mb:.2f} MB)")
        else:
            print("Hoan tat lenh nhung khong tim thay file output trong dist/.")
    except subprocess.CalledProcessError as e:
        print(f"Loi trong qua trinh dong goi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()

