# ArgusMS

Đồ án Trí tuệ nhân tạo của **Nguyễn Quốc Anh, Nguyễn Hoàng Linh và Nguyễn Đoàn Đại Phong**.

ArgusMS hướng tới hệ thống giám sát và phát hiện ngã qua camera cho hộ gia đình có người cao tuổi. Backend xử lý video và AI trên máy tính; ứng dụng Android hiển thị camera, trạng thái và nhận cảnh báo.

## Trạng thái hiện tại

Repo đang ở giai đoạn chuẩn bị triển khai, gồm tài liệu thiết kế, weights YOLO11n/YOLO11m pose, các bản export OpenVINO trong `models/` và script export thử nghiệm `test.py`.

Backend và app Flutter chưa được triển khai. `requirements.txt` hiện chưa có nội dung; chưa có bộ dependency đã khóa hay quy trình chạy toàn hệ thống được kiểm chứng. Cây thư mục bên dưới là cấu trúc đích, được bổ sung dần theo tiến độ.

## Phạm vi MVP

- Một camera RTSP, một vùng theo dõi và một người mục tiêu tại một thời điểm.
- Backend đọc video, trích xuất pose, phân tích chuyển động theo thời gian và xác nhận sự kiện nghi ngã.
- App Android ghép với backend bằng khóa thiết bị, không yêu cầu tài khoản người dùng.
- Xem camera qua MJPEG, nhận trạng thái/sự kiện qua WebSocket và push qua Firebase Cloud Messaging (FCM).
- Có xử lý chống cảnh báo lặp, âm thanh và xác nhận đã xem cảnh báo.
- Demo trong mạng LAN; iOS, desktop, nhiều camera và truy cập camera từ Internet nằm ngoài MVP.

YOLO pose cung cấp vị trí cơ thể và các điểm khớp. Việc xác định ngã cần thêm đặc trưng chuyển động, lịch sử quan sát và máy trạng thái xác nhận.

## Kiến trúc dự kiến

```text
Camera RTSP → Backend: đọc frame → YOLO pose → phân tích chuỗi → xác nhận ngã

Backend → HTTP/MJPEG + WebSocket → App Flutter Android
Backend → lưu sự kiện + outbox → FCM → App Flutter Android
```

Backend phải hoạt động trong suốt thời gian giám sát. Khi máy backend tắt hoặc sleep, hệ thống ngừng phân tích video. Khi mất Internet nhưng LAN còn hoạt động, xử lý AI và kết nối nội bộ có thể tiếp tục; push qua FCM phụ thuộc Internet.

| Thành phần | Công nghệ dự kiến |
| --- | --- |
| Backend | Python 3.11, FastAPI, Uvicorn một worker |
| Đọc camera | OpenCV với FFmpeg |
| Pose | YOLO11n-pose làm baseline; YOLO11m-pose để thử nghiệm |
| Suy luận pose | PyTorch hoặc OpenVINO, chọn sau khi đo trên máy backend |
| Nhánh AI B | Pose pretrained kết hợp luật theo thời gian; baseline chính |
| Nhánh AI A | Pose đóng băng kết hợp TCN nhỏ tự huấn luyện |
| Lưu trữ | SQLite, outbox cho thông báo |
| Ứng dụng | Flutter/Dart, Android |
| Thông báo | Firebase Cloud Messaging |

## Cấu trúc thư mục đích

```text
ArgusMS/
├── README.md
├── AGENTS.md                     # Quy tắc cho AI hỗ trợ lập trình
├── .gitignore
├── .env.example                  # Biến môi trường mẫu, không chứa secret
├── pyproject.toml                # Cấu hình package Python và test
├── requirements.txt
├── requirements.lock.txt         # Dependency khóa sau khi kiểm chứng
├── docs/
│   ├── AI_Midterm_Project.md
│   ├── monitoring-system-plan.md
│   └── ai-usage/                 # Nhật ký sử dụng AI
├── configs/
│   ├── app.yaml                  # Cấu hình backend
│   ├── ai.yaml                   # Model, thiết bị suy luận, ngưỡng
│   └── train.yaml                # Cấu hình huấn luyện
├── backend/
│   ├── main.py                   # Khởi tạo FastAPI và vòng đời dịch vụ
│   ├── config.py
│   ├── contracts.py              # Kiểu dữ liệu dùng chung
│   ├── pipeline.py               # Điều phối camera → AI → sự kiện
│   ├── auth.py
│   ├── pairing.py
│   ├── storage.py
│   ├── schema.sql
│   ├── camera/
│   │   ├── reader.py             # Đọc RTSP/video/webcam
│   │   └── latest.py             # Bộ đệm frame mới nhất
│   ├── ai/
│   │   ├── interface.py
│   │   ├── factory.py
│   │   ├── mock.py               # AI giả để thử tích hợp
│   │   ├── pose.py               # Chạy model pose
│   │   ├── buffer.py
│   │   ├── features.py
│   │   ├── pretrained.py         # Nhánh B: luật theo thời gian
│   │   ├── trained.py            # Nhánh A: suy luận TCN
│   │   ├── tcn.py                # Kiến trúc TCN
│   │   └── state_machine.py      # Xác nhận ngã, phục hồi, chống lặp
│   ├── api/
│   │   ├── routes.py
│   │   ├── ws.py
│   │   └── stream.py             # MJPEG
│   └── alerts/
│       ├── events.py
│       ├── outbox.py
│       └── fcm.py
├── models/                       # Weights và model đã export
│   ├── README.md                 # Nguồn tải và cách tái tạo model
│   ├── yolo11n-pose.pt
│   ├── yolo11m-pose.pt
│   ├── yolo11n-pose_openvino_model/
│   └── yolo11m-pose_openvino_model/
├── training/                     # Xử lý dữ liệu và huấn luyện riêng
│   ├── manifest.py
│   ├── extract.py
│   ├── dataset.py
│   ├── train.py
│   └── evaluate.py
├── data/
│   ├── raw/                      # Video nguồn
│   ├── manifests/                # Danh sách và nguồn dữ liệu
│   ├── labels/                   # Nhãn khoảng thời gian ngã
│   ├── splits.json               # Train/validation/test
│   └── features/                 # Đặc trưng đã trích xuất
├── evaluation/                   # Ca kiểm thử và kết quả đo
├── scripts/
│   ├── export_model.py           # Vị trí đích của script export
│   ├── ai_smoke.py
│   ├── test_push.py
│   └── measure_e2e.py
├── tests/                        # Test Python
├── deploy/
│   └── mediamtx.yml              # Cấu hình RTSP thử nghiệm
├── runtime/                      # SQLite và log khi chạy
└── mobile/
    ├── pubspec.yaml
    ├── pubspec.lock
    ├── lib/
    │   ├── main.dart
    │   ├── config.dart
    │   ├── models.dart           # DTO Dart, không phải model AI
    │   ├── services/             # HTTP, WS, FCM, lưu khóa, âm thanh
    │   ├── screens/              # Ghép thiết bị, trang chủ, cảnh báo
    │   └── widgets/
    ├── assets/audio/
    ├── android/
    ├── test/
    └── integration_test/
```

Các package Python bổ sung `__init__.py` khi triển khai. Skeleton Flutter/Android được sinh bằng công cụ Flutter; không tạo thủ công các file build.

## Tổ chức code và model

- `backend/ai/` chứa code pose, đặc trưng và phát hiện ngã; không phụ thuộc route API hay Firebase.
- `backend/pipeline.py` điều phối các bước xử lý. Route API không chứa thuật toán phân loại ngã và không chạy inference chặn event loop.
- `backend/alerts/` nhận sự kiện đã xác nhận để lưu và gửi thông báo; không mở thêm luồng đọc camera.
- `training/` phục vụ chuẩn bị dữ liệu, train và đánh giá; không chạy huấn luyện trong luồng giám sát.
- `models/` dùng chung cho backend, training và script export. Đường dẫn model được cấu hình và quy đổi theo root project.
- `mobile/` phụ trách giao diện, kết nối và thông báo; AI chạy tại backend.

File `.pt` là model PyTorch, đồng thời là nguồn để export. Mỗi thư mục OpenVINO chứa `.xml`, `.bin` và `metadata.yaml`; giữ nguyên bộ file khi di chuyển. Khi triển khai, chọn artifact tương ứng với runtime sử dụng.

Hiện `test.py` vẫn nằm ở root và dùng tên model tương đối. Khi chuyển thành `scripts/export_model.py`, cần cập nhật đường dẫn tới `models/` để dùng đúng weights đã có.

## Quy ước dữ liệu và kiểm chứng

- Quy ước đích là không commit secrets, URL RTSP chứa mật khẩu, dữ liệu video lớn, cache đặc trưng, weights/model export, runtime DB/log và sản phẩm build. `.gitignore` cần được bổ sung theo quy ước này; hiện mới loại `.venv/`.
- Giữ hướng dẫn tải/export, nguồn, giấy phép và checksum thích hợp để tái tạo artifact. Với file đã được Git theo dõi, thêm `.gitignore` không tự loại file khỏi lịch sử hay index.
- Khóa phiên bản thư viện sau khi kiểm tra import, đọc frame và chạy suy luận thành công. Không xem các lệnh cài đặt trong kế hoạch là một môi trường đã kiểm chứng.
- Test Python cần bao phủ lỗi camera/reconnect, chuỗi pose bị gián đoạn, chống cảnh báo lặp, ghép thiết bị và hợp đồng API. Dùng fake/mock cho các test không cần phần cứng thật.
- Push, âm thanh và vòng đời app cần kiểm tra trên điện thoại Android thật. Các chỉ tiêu hiệu năng trong kế hoạch là mục tiêu thử nghiệm, chưa phải kết quả đạt được.
- Ghi nhật ký sử dụng AI theo yêu cầu học phần: lưu prompt/phản hồi, đánh giá, quyết định sử dụng và cách kiểm chứng; không tạo lịch sử giả.

## Tài liệu

- [Kế hoạch phát triển hệ thống](docs/monitoring-system-plan.md): kiến trúc, API, pipeline AI, phân công, kiểm thử và tiêu chí MVP.
- [Đề bài học phần](docs/AI_Midterm_Project.md): sản phẩm cần nộp và yêu cầu AI Usage Log.

Hướng dẫn cài đặt và chạy demo sẽ được bổ sung cùng các thành phần đã triển khai và kiểm thử.
