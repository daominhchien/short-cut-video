# 🎬 Video Splitter - Ứng Dụng Cắt Video Desktop (Python + CustomTkinter)

Ứng dụng Desktop chạy trên máy tính Windows giúp cắt nhỏ mọi video bất kỳ thành các đoạn đều nhau (mặc định 60 giây) mà **không làm giảm chất lượng video** và **tốc độ xử lý cực nhanh** nhờ công nghệ FFmpeg Stream Copy (`-c copy`).

---

## ✨ Tính Năng Nổi Bật

- 🚀 **Siêu Nhanh & Lossless**: Cắt video tức thì trong vài giây mà không cần encode lại video.
- 💻 **Giao diện Desktop Hiện đại**: Xây dựng bằng `CustomTkinter`, giao diện sạch đẹp, tối ưu trải nghiệm, hỗ trợ Chế độ Tối (Dark Mode) và Chế độ Sáng (Light Mode).
- ⚡ **Chạy Ngầm Đa Luồng (Multithreading)**: Không gây đơ/đóng băng giao diện ứng dụng khi đang xử lý video dung lượng lớn.
- 🎯 **Tùy chỉnh linh hoạt**:
  - Chọn thời lượng đoạn cắt tùy ý (giây) hoặc chọn nhanh các mốc phổ biến (30s, 60s, 90s, 180s, 300s).
  - Tự động tính toán dự kiến số lượng file đầu ra.
  - Tự động tạo thư mục đầu ra hoặc chọn thư mục tùy chỉnh theo ý muốn.
- 📁 **Mở thư mục 1-click**: Nút mở trực tiếp thư mục kết quả ngay sau khi cắt xong.
- 🔒 **Bảo mật 100% Offline**: Hoàn toàn xử lý nội bộ trên máy người dùng, không cần kết nối mạng.

---

## 🛠️ Yêu Cầu Môi Trường & Cài Đặt

### 1. Yêu cầu hệ thống
- Hệ điều hành: Windows 10 / 11 (hoặc macOS/Linux).
- Python 3.8+
- Công cụ **FFmpeg**: Đã có sẵn trong PATH hệ thống hoặc file `ffmpeg.exe` đặt chung thư mục với ứng dụng.

### 2. Cài đặt thư viện Python

```bash
pip install customtkinter pyinstaller
```

---

## 🚀 Hướng Dẫn Chạy Ứng Dụng

Chạy trực tiếp file giao diện bằng lệnh:

```bash
py app.py
# hoặc
python app.py
```

---

## 📦 Hướng Dẫn Đóng Gói Ra File Executable (.exe)

Để đóng gói toàn bộ ứng dụng thành 1 file `VideoSplitter.exe` duy nhất có thể chạy trên máy khác không cần cài Python:

Chạy script đóng gói tự động:

```bash
py build.py
```

File executable thu được sẽ nằm trong thư mục:
`dist/VideoSplitter.exe`

---

## 📁 Cấu Trúc Dự Án

```text
tool-cut-short/
├── app.py                # Giao diện chính CustomTkinter (UI, Controller & Multi-threading)
├── video_splitter.py     # Backend xử lý gọi FFmpeg stream copy & parse tiến độ
├── utils.py              # Tiện ích định dạng thời gian, dung lượng, tìm FFmpeg path
├── build.py              # Script tự động đóng gói bằng PyInstaller
├── README.md             # Hướng dẫn sử dụng chi tiết
```
