# ArgusMS

Đồ án Trí tuệ nhân tạo của **Nguyễn Quốc Anh, Nguyễn Hoàng Linh và Nguyễn Đoàn Đại Phong**.

ArgusMS hướng tới hệ thống giám sát và phát hiện ngã qua camera cho hộ gia đình có người cao tuổi. Backend xử lý video và AI trên máy tính; ứng dụng Android hiển thị camera, trạng thái và nhận cảnh báo.

## Trạng thái hiện tại

Đã có phần code SV1 tuần 1: contract/interface, mock, YOLO pose, buffer theo timestamp, smoke script và công cụ manifest/split/trích xuất cache. Xem [hướng dẫn bàn giao SV1](#bàn-giao-sv1--tuần-1) để chạy và [hướng dẫn dữ liệu](#dữ-liệu-sv1-tuần-1) để bổ sung clip/nhãn thật.

API backend và app Flutter chưa được triển khai; scorer luật và state machine thuộc tuần 2. Phiên bản dependency đã chạy smoke được ghi ở phần bàn giao bên dưới; chưa có lockfile toàn hệ thống. Dataset/nhãn/split đánh giá thật đang chờ bổ sung. Cây thư mục bên dưới là cấu trúc đích, được bổ sung dần theo tiến độ.

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

- Không commit secrets, URL RTSP chứa mật khẩu, dữ liệu video lớn, cache đặc trưng, weights/model export, runtime DB/log và sản phẩm build; các mục này đã được khai báo trong `.gitignore`.
- Giữ hướng dẫn tải/export, nguồn, giấy phép và checksum thích hợp để tái tạo artifact. Với file đã được Git theo dõi, thêm `.gitignore` không tự loại file khỏi lịch sử hay index.
- Khóa phiên bản thư viện sau khi kiểm tra import, đọc frame và chạy suy luận thành công. Không xem các lệnh cài đặt trong kế hoạch là một môi trường đã kiểm chứng.
- Test Python cần bao phủ lỗi camera/reconnect, chuỗi pose bị gián đoạn, chống cảnh báo lặp, ghép thiết bị và hợp đồng API. Dùng fake/mock cho các test không cần phần cứng thật.
- Push, âm thanh và vòng đời app cần kiểm tra trên điện thoại Android thật. Các chỉ tiêu hiệu năng trong kế hoạch là mục tiêu thử nghiệm, chưa phải kết quả đạt được.
- Ghi nhật ký sử dụng AI theo yêu cầu học phần: lưu prompt/phản hồi, đánh giá, quyết định sử dụng và cách kiểm chứng; không tạo lịch sử giả.

## Tài liệu

- [Kế hoạch phát triển hệ thống](docs/plan.md): kiến trúc, API, pipeline AI, phân công, kiểm thử và tiêu chí MVP.
- [Bàn giao SV1 tuần 1](#bàn-giao-sv1--tuần-1): lệnh smoke, tích hợp mock, kiểm thử và giới hạn hiện tại.
- [Đề bài học phần](docs/AI_Midterm_Project.md): sản phẩm cần nộp và yêu cầu AI Usage Log.

Các lệnh chạy phần SV1 tuần 1 và quy trình chuẩn bị dữ liệu ở bên dưới.

## Bàn giao SV1 — tuần 1

Phạm vi theo `docs/plan.md` mục 6.1.1. Code được bổ sung cho interface,
mock, buffer, factory, smoke và chuẩn bị dữ liệu. PoseEstimator đã có được
dùng lại, không load lại model theo từng frame.

### Chạy nhanh

Từ root repo, dùng môi trường có NumPy, OpenCV, Ultralytics, PyYAML:

```powershell
.\.venv\Scripts\python.exe scripts/ai_smoke.py --source <video.mp4> --mode pose
.\.venv\Scripts\python.exe scripts/ai_smoke.py --source <video.mp4> --mode mock --no-preview
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Phiên bản trực tiếp đã dùng smoke: NumPy 2.4.6, OpenCV 5.0.0.93,
Ultralytics 8.4.199, PyYAML 6.0.3, torch 2.15.0, torchvision 0.29.2,
lap 0.5.13. Đây chưa phải lockfile hoặc kiểm chứng cài mới Python 3.11.

`--no-preview` chạy không cửa sổ; `--output runtime/pose-preview.mp4` lưu
video vẽ box/khớp. Thư mục ảnh cần `--fps` đã xác minh hoặc `--timestamps`.
File video mặc định dùng frame index/FPS trong metadata (giả định CFR).
`--max-frames` giới hạn smoke, bỏ tham số này để chạy tới hết clip.
Các bộ đếm gồm frame, empty, thời gian inference trung bình và processing FPS.

### Tích hợp cho SV2

```python
from backend.ai.factory import create_detector, load_settings

settings = load_settings()
detector = create_detector({**settings, "mode": "mock"})
try:
    update = detector.process(packet)  # packet: backend.contracts.FramePacket
    payload = update.to_dict()         # JSON-safe, schema_version=1, is_test=True
finally:
    detector.close()
```

Mock mặc định luân phiên ba trường hợp: không người, một người đứng, pose
thiếu khớp. Gọi lại frame mới nhất trả nguyên update cũ; đổi camera/session
khởi động lại fixture. Có thể truyền fixture candidate tùy chỉnh khi cần
test trạng thái nghi ngờ. Mock không sinh event confirmed. Khi pipeline sau
này tạo event từ mock, phải giữ `is_test=True` tới event và kênh gửi.

`create_detector(mode=pretrained)` hiện báo lỗi có hướng dẫn: scorer luật và
state machine thuộc tuần 2. Giữ giá trị `pretrained` đang có trong YAML,
SV2 chủ động chọn mock ở cấu hình phát triển. Pose thật chạy độc lập qua
`create_pose_estimator()` hoặc smoke; không coi preview là phát hiện ngã.

`PoseBuffer.add(packet, poses)` trả true khi nhận tick mới; gọi
`window(track_id)` lấy lịch sử bounded, ready/valid_fraction. Timestamp
runtime là monotonic nhận frame; offline là thời gian nguồn. Không đếm lại
frame trùng, không nội suy khớp, không nối qua gap hợp lệ >0.3 giây, không
dùng track ID chưa được gán. Mỗi detector/buffer thuộc một inference worker.

### Dữ liệu và giới hạn bàn giao

Xem phần dữ liệu SV1 tuần 1 bên dưới để nhập metadata, khóa split,
gán nhãn và trích cache. CSV hiện là schema trống có chủ ý; split ở trạng
thái pending. Cần clip thật, nhãn đã soát, ít nhất hai group độc lập và smoke
clip có người 30–60 giây để nghiệm thu đầy đủ tuần 1. Model và cache không
commit vào Git.

Kế hoạch chọn Python 3.11; môi trường `.venv` hiện có là Python 3.12.10.
Không coi việc chạy tại môi trường này là xác minh tương thích Python 3.11.

### Kết quả kiểm chứng ngày 09/11/2026

- 16 test unittest đạt, gồm test PoseEstimator đã có, continuity/sampling,
  JSON mock, split chống leakage, timestamp nguồn, cache resume/invalidation
  và so sánh feature offline với cùng buffer/hàm dùng cho runtime.
- YOLO11n-pose thật chạy hết 12 frame clip đen: 0 detection; clip lặp ảnh
  bus.jpg có sẵn trong package: 36 detection qua 12 frame, 3 track.
  Clip lặp ảnh chỉ kiểm tra đường I/O và tracker, không đo chất lượng ngã.
- Đã kiểm tra pilot cache với model thật, shape `[36,54]`, timestamp 0–1.1
  giây, nhãn toàn `unknown`, feature hữu hạn; lượt chạy lại bỏ qua cache khớp.
  Các artifact smoke đã được xoá theo yêu cầu, không đưa vào tập đánh giá.
- Chưa nghiệm thu clip ngã thật 30–60 giây, RTSP/camera/Android hoặc scorer
  tuần 2; chưa có số liệu chất lượng nhận diện ngã.

## Dữ liệu SV1 tuần 1

Repo chưa có video/sequence hay nhãn đã xác minh. `data/manifests/clips.csv`,
`data/labels/intervals.csv` và `evaluation/cases.csv` hiện chỉ chứa schema để nhập
dữ liệu thật. `data/splits.json` mang trạng thái `pending_real_data`, chưa phải split
được nghiệm thu. Không có cache hoặc số liệu chất lượng AI được tạo giả.

### 1. Chuẩn bị nguồn và manifest

Đặt video hoặc thư mục RGB trong `data/raw/` (đã gitignore). Nguồn URFD:
https://fenix.ur.edu.pl/~mkepski/ds/uf.html . Trang nguồn cung cấp RGB, dữ liệu
đồng bộ và điều kiện CC BY-NC-SA 4.0 dành cho học thuật phi thương mại. Giữ
thông tin trích dẫn theo nguồn. Không suy đoán FPS từ tên dataset.

Tạo file JSON metadata cục bộ gồm một danh sách record theo schema sau;
các giá trị minh họa phải được thay bằng clip có thật:

```json
[
  {
    "clip_id": "recording01-cam0",
    "path": "data/raw/recording01-cam0",
    "group_id": "recording01",
    "recording_id": "recording01",
    "subject_id": "unknown",
    "camera_id": "cam0",
    "fps": null,
    "timestamps_path": "data/raw/recording01-cam0-timestamps.csv",
    "source": "URL nguồn hoặc mô tả clip tự quay có sự đồng ý",
    "license": "Điều kiện sử dụng đã xác minh"
  }
]
```

- Có ít nhất hai group để chia validation/test. Cùng recording/sự kiện ở hai
  góc camera phải cùng `recording_id` và `group_id`. Clip cắt từ cùng recording
  cũng giữ nguyên nhóm. Khi đã biết danh tính và muốn chia theo subject, dùng
  cùng group cho mọi recording của subject đó. `unknown` chỉ dùng cho subject
  chưa biết; không dùng làm group.
- Thư mục ảnh được đọc theo thứ tự số tự nhiên, không phải thứ tự từ điển.
  `timestamps_path` là CSV `frame_id,time_s`, index **0 đến N-1**, thời gian
  nguồn tính bằng giây, hữu hạn, không âm và tăng nghiêm ngặt. Chuẩn hóa dữ
  liệu đồng bộ của nguồn về CSV này, chọn đúng camera; không đưa trực tiếp
  CSV URFD chưa chuyển schema vào chương trình.
- Nếu nguồn là CFR đã xác minh, đặt `fps` dương và bỏ `timestamps_path`.
  Timestamp khi đó là `frame_index / fps`. Nguồn VFR hoặc ảnh có frame mất
  cần timestamp thật; không ép thành CFR để tính vận tốc.
- Mọi đường dẫn trong manifest tính từ root repo. ID clip chỉ gồm chữ ASCII,
  số, dấu chấm, gạch nối và gạch dưới, dùng làm tên cache an toàn.

```powershell
.\.venv\Scripts\python.exe -m evaluation.manifest --metadata local-clips.json
```

Lệnh kiểm tra đường dẫn/FPS khai báo, chống trùng ID/đường dẫn, tạo `clips.csv`
và split theo group với seed 42. Lần chạy sau giữ split đã có và từ chối dữ
liệu không khớp; không tự chia lại tập test. Khi cần bổ sung corpus, xem xét
thay đổi manifest/split có chủ ý trước khi tuning. Các nhóm không giao nhau
không tự bảo đảm cân bằng loại hoạt động; cần soát lại thành phần tập.

### 2. Gán nhãn sau khi xem video

Điền `data/labels/intervals.csv`: `clip_id,onset_s,impact_s,end_s,label`.
Khoảng thời gian theo quy ước `[onset_s,end_s)`:

- `fall`: onset bắt đầu diễn biến ngã, impact lúc chạm đất, end kết thúc
  đoạn sự kiện đã đánh dấu; cần `onset <= impact <= end`.
- `adl`, `hard_negative`, `lying`, `occlusion`: onset là đầu đoạn đã soát,
  end là cuối đoạn; impact để trống.
- Khoảng ngoài nhãn giữ `unknown`. Không gán toàn clip có ngã thành positive,
  và không mặc định phần chưa xem là negative. Các khoảng không chồng nhau.

Điền `evaluation/cases.csv` bằng clip thật, split từ `splits.json`, kỳ vọng và
khoảng thời gian tương ứng. Cần phủ ngã, ADL, nằm sẵn, che khuất; chỉ chọn
ngưỡng bằng validation. Chưa có clip thì giữ bảng chưa có dòng dữ liệu.

### 3. Trích xuất và đọc cache

```powershell
.\.venv\Scripts\python.exe -m evaluation.extract --clip-id recording01-cam0
```

Chạy không có `--clip-id` để trích tất cả. Model chỉ được load một lần cho
cả lượt chạy, tracker/buffer reset giữa clip. Cache trong `data/features/`
được bỏ qua nếu nội dung nguồn/model, config, nhãn và phiên bản feature còn
khớp. Đổi bất kỳ thành phần nào sẽ trích lại; `--overwrite` buộc trích lại.
File được ghi nguyên tử để lượt bị ngắt không tạo cache hoàn tất giả.

Schema `.npz` (đọc với `np.load(path, allow_pickle=False)`):

| Key | Shape / ý nghĩa |
| --- | --- |
| `features`, `validity` | `[T,54]` float32 / bool |
| `timestamps`, `frame_ids` | `[T]` thời gian nguồn / index nguồn |
| `track_ids`, `segment_ids` | `[T]` ID theo clip; segment mới sau gap dài |
| `labels` | `[T]` nhãn hoặc `unknown` |
| `keypoints`, `valid_keypoints` | `[T,17,3]` pixel COCO17 / `[T,17]` mask |
| `bboxes`, `image_heights` | `[T,4]` xyxy / `[T]` chiều cao ảnh |
| `window_ready`, `window_start` | `[T]` chất lượng đủ cửa sổ / đầu cửa sổ |
| `metadata_json` | Unicode JSON scalar: hash nguồn/model, config, provenance |

T là số quan sát `(tick,track)`, không phải số frame gốc. Nhiều track có thể
cùng timestamp; từng track/segment tăng theo thời gian. Frame không có track
có `track_id=-1` và mask false; không bỏ mất dấu vết khoảng trống.

Feature v1 gồm 51 số khớp, hip_y/chiều cao ảnh, góc thân/90°, và
min(tỉ lệ box,4)/4. Mỗi cửa sổ dùng chung gốc hông đầu tiên hợp lệ và scale
trung vị độ dài thân, giúp giữ chuyển động tương đối. Khớp thiếu có feature
0 và mask false; raw coordinates thiếu là NaN. `features[t]` là **hàng cuối
của cửa sổ nhân quả kết thúc tại t**, không ghép các hàng cache thành tensor
chuẩn hóa chung của cửa sổ mới. Khi cần toàn cửa sổ, dùng raw pose, buffer và
`normalize_window()` trong `evaluation/extract.py`. Khi làm tuần 2 mới tách
hàm dùng chung sang `backend/ai/features.py` theo kế hoạch. Tuần 1 chưa có
scorer hoặc xác nhận ngã.

Clip kiểm thử tổng hợp trong `runtime/` chỉ dùng kiểm tra I/O và timestamp,
không đưa vào manifest/split đánh giá AI.
