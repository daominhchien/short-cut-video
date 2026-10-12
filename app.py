import os
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from video_splitter import VideoSplitter
from utils import get_ffmpeg_path, open_folder, format_time, format_size

# Appearance Settings
ctk.set_appearance_mode("System")  # System, Dark, Light
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"


class VideoSplitterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Video Splitter - Cắt Video Nhanh Không Giảm Chất Lượng")
        self.geometry("760x680")
        self.minsize(700, 620)

        # Splitter Logic Instance
        self.ffmpeg_path = get_ffmpeg_path()
        self.splitter = VideoSplitter(self.ffmpeg_path)

        # State Variables
        self.selected_file: str = ""
        self.video_info: dict = {}
        self.output_dir: str = ""
        self.is_processing: bool = False
        self.cancel_event: threading.Event = threading.Event()

        # Build UI
        self._create_widgets()
        self._check_ffmpeg_warning()

    def _create_widgets(self):
        """Construct the UI layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # -------------------------------------------------------------------
        # 1. Header Section
        # -------------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=24, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🎬 Video Splitter",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Tự động băm nhỏ video thành các đoạn đều nhau siêu tốc bằng FFmpeg Stream Copy",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("gray40", "gray70")
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Theme Switcher
        theme_menu = ctk.CTkOptionMenu(
            header_frame,
            values=["System", "Dark", "Light"],
            command=self._change_theme,
            width=100
        )
        theme_menu.set("System")
        theme_menu.grid(row=0, column=1, rowspan=2, sticky="e")

        # -------------------------------------------------------------------
        # 2. File Selection Section
        # -------------------------------------------------------------------
        self.file_card = ctk.CTkFrame(self, corner_radius=12)
        self.file_card.grid(row=1, column=0, padx=24, pady=10, sticky="ew")
        self.file_card.grid_columnconfigure(0, weight=1)

        # File Drop/Pick Area
        self.drop_area = ctk.CTkButton(
            self.file_card,
            text="📁 Nhấn vào đây để chọn Video từ máy tính\n(Hỗ trợ .mp4, .mkv, .avi, .mov, .webm, ...)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=("gray85", "gray20"),
            hover_color=("gray75", "gray28"),
            text_color=("gray20", "gray90"),
            height=90,
            corner_radius=10,
            command=self._select_file
        )
        self.drop_area.grid(row=0, column=0, padx=16, pady=16, sticky="ew")

        # File Info Frame (hidden until file is selected)
        self.info_frame = ctk.CTkFrame(self.file_card, fg_color="transparent")
        self.info_frame.grid_columnconfigure(1, weight=1)

        self.lbl_filename = ctk.CTkLabel(
            self.info_frame,
            text="File:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.lbl_filename.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.val_filename = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w",
            wraplength=500
        )
        self.val_filename.grid(row=0, column=1, sticky="w")

        self.lbl_meta = ctk.CTkLabel(
            self.info_frame,
            text="Thông số:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.lbl_meta.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(4, 0))

        self.val_meta = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w",
            text_color=("gray30", "gray70")
        )
        self.val_meta.grid(row=1, column=1, sticky="w", pady=(4, 0))

        # -------------------------------------------------------------------
        # 3. Split Configuration Section
        # -------------------------------------------------------------------
        config_card = ctk.CTkFrame(self, corner_radius=12)
        config_card.grid(row=2, column=0, padx=24, pady=10, sticky="ew")
        config_card.grid_columnconfigure(1, weight=1)

        # Duration Entry
        lbl_duration = ctk.CTkLabel(
            config_card,
            text="Thời lượng đoạn (giây):",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        lbl_duration.grid(row=0, column=0, padx=(16, 10), pady=16, sticky="w")

        duration_input_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        duration_input_frame.grid(row=0, column=1, sticky="w")

        self.entry_duration = ctk.CTkEntry(
            duration_input_frame,
            width=90,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            justify="center"
        )
        self.entry_duration.insert(0, "60")
        self.entry_duration.pack(side="left", padx=(0, 10))
        self.entry_duration.bind("<KeyRelease>", self._on_duration_changed)

        # Presets Buttons
        presets_frame = ctk.CTkFrame(duration_input_frame, fg_color="transparent")
        presets_frame.pack(side="left")

        for sec in [30, 60, 90, 180, 300]:
            btn = ctk.CTkButton(
                presets_frame,
                text=f"{sec}s",
                width=45,
                height=28,
                fg_color=("gray80", "gray30"),
                hover_color=("gray70", "gray40"),
                text_color=("black", "white"),
                command=lambda s=sec: self._set_preset_duration(s)
            )
            btn.pack(side="left", padx=2)

        # Estimated Parts Label
        self.lbl_parts_estimate = ctk.CTkLabel(
            config_card,
            text="Dự kiến: -- đoạn video",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("gray40", "gray60")
        )
        self.lbl_parts_estimate.grid(row=0, column=2, padx=16, sticky="e")

        # Output Directory Row
        lbl_output = ctk.CTkLabel(
            config_card,
            text="Thư mục đầu ra:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        lbl_output.grid(row=1, column=0, padx=(16, 10), pady=(0, 16), sticky="w")

        self.entry_output_dir = ctk.CTkEntry(
            config_card,
            placeholder_text="Mặc định: Tự động tạo thư mục [tên_video]_parts",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.entry_output_dir.grid(row=1, column=1, padx=(0, 10), pady=(0, 16), sticky="ew")

        btn_browse_out = ctk.CTkButton(
            config_card,
            text="Chọn Thư Mục",
            width=110,
            command=self._select_output_dir
        )
        btn_browse_out.grid(row=1, column=2, padx=(0, 16), pady=(0, 16), sticky="e")

        # -------------------------------------------------------------------
        # 4. Process Control & Status Section
        # -------------------------------------------------------------------
        status_card = ctk.CTkFrame(self, corner_radius=12)
        status_card.grid(row=3, column=0, padx=24, pady=(10, 20), sticky="nsew")
        status_card.grid_columnconfigure(0, weight=1)
        status_card.grid_rowconfigure(3, weight=1)

        # Main Action Button Bar
        btn_frame = ctk.CTkFrame(status_card, fg_color="transparent")
        btn_frame.grid(row=0, column=0, padx=16, pady=(16, 10), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)

        self.btn_start = ctk.CTkButton(
            btn_frame,
            text="🚀 Bắt Đầu Cắt Video",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            height=44,
            corner_radius=8,
            command=self._start_splitting
        )
        self.btn_start.grid(row=0, column=0, sticky="ew")

        self.btn_cancel = ctk.CTkButton(
            btn_frame,
            text="⏹ Dừng Tác Vụ",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=44,
            width=120,
            fg_color="#d32f2f",
            hover_color="#9a0007",
            corner_radius=8,
            command=self._cancel_splitting
        )
        # Hidden by default

        self.btn_open_folder = ctk.CTkButton(
            btn_frame,
            text="📁 Mở Thư Mục Kết Quả",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=44,
            width=170,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            corner_radius=8,
            command=self._open_output_folder
        )
        # Hidden by default

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(status_card, height=12)
        self.progress_bar.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        self.progress_bar.set(0)

        # Status Message Label
        self.lbl_status = ctk.CTkLabel(
            status_card,
            text="Sẵn sàng.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w"
        )
        self.lbl_status.grid(row=2, column=0, padx=16, pady=(0, 6), sticky="w")

        # Log Text Box
        self.log_box = ctk.CTkTextbox(
            status_card,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            height=90
        )
        self.log_box.grid(row=3, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.log_box.insert("end", "--- Nhật ký ứng dụng ---\n")
        self.log_box.configure(state="disabled")

    # -----------------------------------------------------------------------
    # Helper Methods & Handlers
    # -----------------------------------------------------------------------
    def _check_ffmpeg_warning(self):
        if not self.ffmpeg_path or not os.path.exists(self.ffmpeg_path):
            self._log("⚠️ CẢNH BÁO: Không tìm thấy ffmpeg.exe trong hệ thống.")
            self._log("Vui lòng tải ffmpeg.exe và đặt vào chung thư mục với ứng dụng.")
            self.lbl_status.configure(text="⚠️ Thiếu công cụ FFmpeg!", text_color="orange")
        else:
            self._log(f"✅ Đã kết nối FFmpeg: {self.ffmpeg_path}")

    def _change_theme(self, mode: str):
        ctk.set_appearance_mode(mode)

    def _log(self, message: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_preset_duration(self, seconds: int):
        self.entry_duration.delete(0, "end")
        self.entry_duration.insert(0, str(seconds))
        self._on_duration_changed()

    def _select_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file video cần cắt",
            filetypes=[
                ("Video Files", "*.mp4 *.mkv *.avi *.mov *.webm *.flv *.m4v *.ts *.wmv"),
                ("All Files", "*.*")
            ]
        )
        if not file_path:
            return

        self.selected_file = file_path
        self.drop_area.grid_remove()
        self.info_frame.grid(row=0, column=0, padx=16, pady=16, sticky="ew")

        # Analyze Video File in Background Thread
        self.lbl_status.configure(text="Đang phân tích thông tin video...", text_color=("gray20", "gray80"))
        threading.Thread(target=self._analyze_file_thread, args=(file_path,), daemon=True).start()

    def _analyze_file_thread(self, file_path: str):
        try:
            info = self.splitter.get_video_info(file_path)
            self.after(0, self._update_video_info_ui, info)
        except Exception as e:
            self.after(0, self._handle_analyze_error, str(e))

    def _update_video_info_ui(self, info: dict):
        self.video_info = info
        self.val_filename.configure(text=info['filename'])
        self.val_meta.configure(
            text=f"Thời lượng: {info['duration_str']}  |  Dung lượng: {info['size_str']}  |  Định dạng: {info['extension'].upper()}"
        )
        self._log(f"📁 Đã chọn: {info['filename']} ({info['duration_str']}, {info['size_str']})")
        self.lbl_status.configure(text="Sẵn sàng cắt video.", text_color=("gray20", "gray80"))
        self._on_duration_changed()

    def _handle_analyze_error(self, err_msg: str):
        self._log(f"❌ Lỗi đọc video: {err_msg}")
        messagebox.showerror("Lỗi File", f"Không thể đọc file video:\n{err_msg}")
        self.lbl_status.configure(text="Lỗi đọc file.", text_color="red")

    def _on_duration_changed(self, event=None):
        if not self.video_info or self.video_info.get('duration', 0) <= 0:
            self.lbl_parts_estimate.configure(text="Dự kiến: -- đoạn video")
            return

        try:
            dur = float(self.entry_duration.get().strip())
            if dur > 0:
                total_sec = self.video_info['duration']
                num_parts = int(total_sec // dur) + (1 if total_sec % dur > 0 else 0)
                self.lbl_parts_estimate.configure(
                    text=f"Dự kiến: ~{num_parts} đoạn video ({format_time(dur)}/đoạn)",
                    text_color=("gray20", "gray80")
                )
            else:
                self.lbl_parts_estimate.configure(text="Dự kiến: Phải > 0 giây", text_color="red")
        except ValueError:
            self.lbl_parts_estimate.configure(text="Thời lượng không hợp lệ", text_color="red")

    def _select_output_dir(self):
        folder = filedialog.askdirectory(title="Chọn thư mục lưu video đầu ra")
        if folder:
            self.entry_output_dir.delete(0, "end")
            self.entry_output_dir.insert(0, folder)
            self._log(f"📂 Đã chọn thư mục đầu ra: {folder}")

    # -----------------------------------------------------------------------
    # Splitting Process Execution
    # -----------------------------------------------------------------------
    def _start_splitting(self):
        if not self.selected_file or not os.path.isfile(self.selected_file):
            messagebox.showwarning("Chưa chọn Video", "Vui lòng chọn một tệp video trước khi bắt đầu!")
            return

        try:
            segment_sec = int(float(self.entry_duration.get().strip()))
            if segment_sec <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Thời lượng không hợp lệ", "Vui lòng nhập thời lượng là một số giây nguyên lớn hơn 0.")
            return

        custom_out = self.entry_output_dir.get().strip()

        # Update UI to Processing State
        self.is_processing = True
        self.cancel_event.clear()
        self.btn_start.grid_remove()
        self.btn_cancel.grid(row=0, column=0, sticky="ew")
        self.btn_open_folder.grid_remove()
        self.progress_bar.set(0)
        self.lbl_status.configure(text="Bắt đầu cắt video...", text_color=("gray20", "gray80"))

        self._log(f"▶️ Bắt đầu cắt video: '{os.path.basename(self.selected_file)}' thành các đoạn {segment_sec}s")

        # Run in Background Thread
        threading.Thread(
            target=self._split_video_thread,
            args=(self.selected_file, segment_sec, custom_out),
            daemon=True
        ).start()

    def _split_video_thread(self, input_path: str, segment_sec: int, custom_out: str):
        def progress_cb(pct: float, msg: str):
            self.after(0, self._update_progress_ui, pct, msg)

        try:
            final_out_dir = self.splitter.split_video(
                input_path=input_path,
                segment_seconds=segment_sec,
                output_dir=custom_out,
                progress_callback=progress_cb,
                cancel_event=self.cancel_event
            )
            self.output_dir = final_out_dir
            self.after(0, self._on_splitting_success, final_out_dir)
        except InterruptedError:
            self.after(0, self._on_splitting_canceled)
        except Exception as e:
            self.after(0, self._on_splitting_error, str(e))

    def _update_progress_ui(self, pct: float, msg: str):
        self.progress_bar.set(pct / 100.0)
        self.lbl_status.configure(text=msg, text_color=("gray20", "gray80"))

    def _on_splitting_success(self, out_dir: str):
        self.is_processing = False
        self.progress_bar.set(1.0)
        self.lbl_status.configure(text=f"✅ Cắt video hoàn tất!", text_color="green")
        self._log(f"🎉 HOÀN THÀNH! Các file đã được lưu tại: {out_dir}")

        self.btn_cancel.grid_remove()
        self.btn_start.grid(row=0, column=0, sticky="ew")
        self.btn_open_folder.grid(row=0, column=1, padx=(10, 0), sticky="e")

    def _on_splitting_canceled(self):
        self.is_processing = False
        self.progress_bar.set(0)
        self.lbl_status.configure(text="🛑 Đã hủy tác vụ.", text_color="orange")
        self._log("⏹ Tác vụ cắt video đã bị hủy bởi người dùng.")

        self.btn_cancel.grid_remove()
        self.btn_start.grid(row=0, column=0, sticky="ew")

    def _on_splitting_error(self, err_msg: str):
        self.is_processing = False
        self.progress_bar.set(0)
        self.lbl_status.configure(text="❌ Lỗi trong quá trình cắt video!", text_color="red")
        self._log(f"❌ CÓ LỖI XẢY RA:\n{err_msg}")

        self.btn_cancel.grid_remove()
        self.btn_start.grid(row=0, column=0, sticky="ew")
        messagebox.showerror("Lỗi Cắt Video", f"Đã xảy ra lỗi:\n{err_msg}")

    def _cancel_splitting(self):
        if self.is_processing:
            self.cancel_event.set()
            self.lbl_status.configure(text="Đang gửi lệnh dừng...", text_color="orange")

    def _open_output_folder(self):
        if self.output_dir and os.path.exists(self.output_dir):
            open_folder(self.output_dir)
        else:
            messagebox.showinfo("Thông báo", "Chưa có thư mục đầu ra hợp lệ.")


if __name__ == "__main__":
    app = VideoSplitterApp()
    app.mainloop()
