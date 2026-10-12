import os
import re
import subprocess
import threading
from typing import Callable, Optional, Dict, Any
from utils import get_ffmpeg_path, format_size, format_time

class VideoSplitter:
    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg_path = ffmpeg_path or get_ffmpeg_path()
        self.current_process: Optional[subprocess.Popen] = None

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Extract video information (duration in seconds, file size, format).
        Returns dict with keys: 'duration', 'size', 'filename', 'extension'.
        """
        if not os.path.isfile(video_path):
            raise FileNotFoundError(f"Không tìm thấy file: {video_path}")

        file_size = os.path.getsize(video_path)
        base_name = os.path.basename(video_path)
        name, ext = os.path.splitext(base_name)

        # Run ffmpeg -i to parse duration
        cmd = [self.ffmpeg_path, '-hide_banner', '-i', video_path]
        
        # Hide console window on Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo
        )
        _, stderr = proc.communicate()

        duration = 0.0
        # Parse Duration: HH:MM:SS.ms
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
        if match:
            hours, minutes, seconds = match.groups()
            duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

        return {
            'filepath': video_path,
            'filename': base_name,
            'name_without_ext': name,
            'extension': ext.lower(),
            'size': file_size,
            'size_str': format_size(file_size),
            'duration': duration,
            'duration_str': format_time(duration) if duration > 0 else "Không xác định"
        }

    def split_video(
        self,
        input_path: str,
        segment_seconds: int,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> str:
        """
        Split video into segments of `segment_seconds` using FFmpeg stream copy (-c copy).
        
        :param input_path: Full path to input video file
        :param segment_seconds: Segment duration in seconds (e.g. 60)
        :param output_dir: Destination folder (if None, creates '[filename]_parts' near input file)
        :param progress_callback: Callable receiving (percentage: float 0-100, status_msg: str)
        :param cancel_event: threading.Event to signal cancellation
        :return: Path to output directory containing split parts
        """
        info = self.get_video_info(input_path)
        total_duration = info['duration']

        if segment_seconds <= 0:
            raise ValueError("Thời lượng đoạn cắt phải lớn hơn 0 giây.")

        # Determine output directory
        if not output_dir or not output_dir.strip():
            parent_dir = os.path.dirname(input_path)
            output_dir = os.path.join(parent_dir, f"{info['name_without_ext']}_parts")
        
        os.makedirs(output_dir, exist_ok=True)

        ext = info['extension']
        if not ext:
            ext = ".mp4"

        # Output template, e.g. part_001.mp4
        output_template = os.path.join(output_dir, f"part_%03d{ext}")

        # FFmpeg command line with stream copy and pipe progress
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-hide_banner',
            '-i', input_path,
            '-c', 'copy',
            '-f', 'segment',
            '-segment_time', str(segment_seconds),
            '-reset_timestamps', '1',
            '-progress', 'pipe:1',
            output_template
        ]

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo
        )

        if progress_callback:
            progress_callback(0.0, "Đang khởi tạo tiến trình...")

        # Monitor progress via pipe:1
        out_time_us = 0
        try:
            while True:
                if cancel_event and cancel_event.is_set():
                    if self.current_process:
                        self.current_process.terminate()
                        self.current_process.wait()
                    if progress_callback:
                        progress_callback(0.0, "Đã hủy tác vụ.")
                    raise InterruptedError("Người dùng đã hủy quá trình cắt video.")

                line = self.current_process.stdout.readline()
                if not line:
                    if self.current_process.poll() is not None:
                        break
                    continue

                line = line.strip()
                if line.startswith("out_time_us="):
                    try:
                        val = int(line.split("=")[1])
                        out_time_us = val
                        current_sec = out_time_us / 1_000_000.0
                        if total_duration > 0:
                            pct = min(100.0, (current_sec / total_duration) * 100.0)
                            msg = f"Đang xử lý: {pct:.1f}% ({format_time(current_sec)} / {format_time(total_duration)})"
                            if progress_callback:
                                progress_callback(pct, msg)
                    except ValueError:
                        pass
                elif line.startswith("progress=end"):
                    if progress_callback:
                        progress_callback(100.0, "Hoàn thành 100%")
                    break

            ret_code = self.current_process.wait()
            if ret_code != 0:
                # Read stderr for error details
                err_output = self.current_process.stderr.read()
                raise RuntimeError(f"Lỗi FFmpeg (Mã lỗi {ret_code}):\n{err_output[-500:]}")

        finally:
            self.current_process = None

        if progress_callback:
            progress_callback(100.0, f"Đã cắt thành công vào thư mục: {os.path.basename(output_dir)}")

        return output_dir
