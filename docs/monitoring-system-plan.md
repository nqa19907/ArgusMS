# KẾ HOẠCH PHÁT TRIỂN HỆ THỐNG GIÁM SÁT NGƯỜI CAO TUỔI BỊ NGÃ BẰNG COMPUTER VISION — NHÓM 3 SINH VIÊN — 4 TUẦN 

Kế hoạch triển khai kỹ thuật • 20 ngày làm việc • 3 vai trò • MVP Android và backend xử lý tại máy tính 

Phiên bản kế hoạch: 29/10/2026. Ngày 1–20 là ngày làm việc tương đối; nhóm tự gắn với lịch học thực tế. 

Đích đến: nhập RTSP, xem trạng thái và hình camera, phát hiện diễn biến nghi ngã, xác nhận bằng chuỗi bằng chứng, gửi cảnh báo đến đúng điện thoại đã ghép và phát âm thanh theo trạng thái ứng dụng. Không có đăng ký hoặc đăng nhập cho người dùng cuối. AI xử lý tại backend; điện thoại là thiết bị theo dõi và nhận cảnh báo. 

Cách dùng: đọc Chương 1–5 để hiểu thiết kế; mỗi thành viên làm theo Chương 6 và bảng ngày ở Chương 7; dùng Chương 8 khi chọn nhánh AI; dùng Chương 9 để tra hợp đồng từng file và Chương 11 để nghiệm thu. Các con số hiệu năng dưới đây là mục tiêu thử nghiệm hoặc ước lượng lập kế hoạch, chưa phải kết quả đạt được. 

## MỤC LỤC 

<u>1. Đối chiếu nguồn và chốt phạm vi</u> 

<u>2. Kiến trúc, công nghệ và môi trường chạy</u> 

<u>3. Hợp đồng dữ liệu, API và ghép thiết bị</u> 

<u>4. Pipeline RTSP và thuật toán nhận diện ngã</u> 

<u>5. Thông báo, âm thanh và giao diện ứng dụng</u> 

<u>6. Phân công chi tiết theo tuần và sinh viên</u> 

<u>7. Lịch 20 ngày: 60 mục phân công</u> 

<u>8. Hai lộ trình AI và mốc lựa chọn mô hình</u> 

<u>9. Cấu trúc source và quản lý file</u> 

<u>10. Hợp đồng bàn giao và kế hoạch tích hợp</u> 

<u>11. Kiểm thử, chỉ số và checklist MVP</u> 

<u>12. Ưu tiên, rủi ro và cách chạy bản demo</u> 

<u>13. Nguồn kỹ thuật và quy ước tra cứu</u> 

## 1. Đối chiếu nguồn và chốt phạm vi 

### 1.1. Nguồn nào quy định điều gì? 

Nguồn [S1] là AI_Midterm_Project.pdf, đã đọc đủ 7 trang. Hướng phù hợp là Application Track ở Mục I.1.1, trang 1–2: xây dựng phần mềm giải quyết nhu cầu thực tế, AI có vai trò rõ ràng, lựa chọn phương pháp, tích hợp, chạy demo và kiểm thử. Đề không bắt buộc tự huấn luyện từ đầu, không chọn sẵn đề tài ngã, không ấn định FastAPI, RTSP, Android, quy 

mô 3 người hoặc 4 tuần. Các điểm đó xuất phát từ yêu cầu xây dựng ứng dụng của bạn hoặc quyết định thiết kế trong kế hoạch này. 

Các sản phẩm học phần khác được liệt kê trong PDF vẫn thuộc yêu cầu môn học; tài liệu này chỉ phân công xây dựng ứng dụng theo phạm vi bạn yêu cầu. Không phân bổ thời gian cho các sản phẩm bên ngoài phần mềm. 

Nguồn [S2] là liên kết trong sample-github-project.txt. Đã đọc README, cấu hình, các module camera, pipeline, xử lý trạng thái, thông báo, API và đoạn giao diện liên quan tại commit 8256b6a042ef04907c31c53f5310028a10af79be. Phân tích dưới đây dựa trên mã nguồn; không coi các số liệu tác giả nêu là hiệu năng đã được nhóm kiểm chứng trên máy của mình. 

|**Yêu cầu**|**Nguồn**|**Quyết định triển khai**|
|---|---|---|
|AI phải tạo ra chức năng có<br>ích, tích hợp vào phần mềm|[S1], I.1.1|Pose và diễn biến theo thời gian quyết định sự kiện<br>nghi ngã; backend/app dùng kết quả đó.|
|Có mã nguồn và demo chạy<br>được, kiểm thử hiệu quả|[S1], trang 1–2|Một pipeline chạy trên máy thật; APK Android; lệnh<br>chạy và test kỹ thuật.|
|RTSP, không tài khoản, push<br>và âm thanh|Yêu cầu bổ sung của<br>người dùng|Nhập RTSP tại app; ghép thiết bị; FCM; xử lý<br>foreground/background riêng.|
|Hai hướng AI, 3 người, đúng 4<br>tuần|Yêu cầu bổ sung của<br>người dùng|B là baseline chính; A là TCN nhỏ được tự train;<br>quyết định cuối ngày 10.|
|Android trước, một camera và<br>một người mục tiêu|Đề xuất giảm phạm<br>vi|MVP kiểm chứng trong một phòng, góc camera cố<br>định, đủ toàn thân.|
|Không suy đoán tuổi từ hình<br>ảnh|Đề xuất kỹ thuật|Đối tượng sử dụng là hộ gia đình có người cao tuổi;<br>model phát hiện ngã của người trong vùng theo dõi.|
|Desktop/iOS và nhiều camera|Không bắt buộc<br>trong nguồn/yêu cầu<br>hiện tại|Ngoài đường găng; không chia thời gian P0 cho app<br>desktop hay phát hành iOS.|



### 1.2. Sample thực sự có những gì và nên dùng lại phần nào? 

|**Thành phần đã đọc**|**Nhận xét từ source**|**Cách áp dụng cho nhóm**|
|---|---|---|
|src/camera/stream.py;<br>src/camera/rtsp.py|Thread đọc camera; hàng đợi nhỏ<br>bỏ frame cũ; timeout mở/đọc; TCP<br>và backoff.|Tham khảo thuật toán, viết reader nhỏ<br>với cùng nguyên tắc; đo lại timeout,<br>tránh sao chép toàn bộ lớp phụ thuộc.|
|configs/model.yaml;<br>src/pipeline/decoupled_pipelin<br>e.py|Cấu hình pose hiện tại trỏ RTMO-s<br>ONNX; có nhánh YOLO, tracker,<br>chuỗi và nhiều tầng phân tích.|Không gọi sample chỉ là YOLO đơn<br>giản. MVP dùng YOLO11n-pose quen<br>thuộc, ít tầng hơn; giữ tách capture<br>khỏi inference.|
|src/temporal/<br>sequence_buffer.py;<br>sequence_features.py|Buffer theo track; chuẩn hóa chuỗi<br>bằng gốc và tỉ lệ dùng chung cho<br>cửa sổ.|Dùng ý tưởng giữ chuyển động tương<br>đối theo thời gian; bổ sung timestamp<br>và kiểm tra khoảng trống.|



|**Thành phần đã đọc**|**Nhận xét từ source**|**Cách áp dụng cho nhóm**|
|---|---|---|
|src/risk/state_machine.py;<br>configs/thresholds.yaml|Xác nhận theo thời gian, hysteresis,<br>phục hồi; có nhiều ngưỡng.|Viết máy trạng thái gọn cho bài toán<br>ngã; hiệu chỉnh trên validation, không<br>chép ngưỡng như chân lý.|
|src/alerts/alert_manager.py;<br>notification.py|Có cooldown theo track/loại sự kiện;<br>dispatch WebSocket, webhook,<br>Telegram.|Dùng ý tưởng event_id và chống lặp;<br>xây mới FCM và outbox nhỏ.<br>Telegram không thay cho thông báo<br>của app riêng.|
|src/api/server.py;<br>frontend/app.js|Có MJPEG, WebSocket và âm<br>thanh trong trình duyệt; frontend<br>dùng token đăng nhập.|Mượn định dạng stream và cách bắt<br>sự kiện; app Flutter mới; ghép thiết bị<br>thay hệ thống tài khoản.|
|configs/security.yaml; src/auth/|Cho phép localhost không đăng<br>nhập; thiết bị LAN mặc định phải<br>xác thực bằng tài khoản/JWT.|Không kết luận sample luôn mở link là<br>dùng được. Đổi cơ chế xác thực sang<br>khóa thiết bị, vẫn bảo vệ dữ liệu.|
|training/; models/; README|Sample có mô hình chuỗi,<br>autoencoder và checkpoint riêng;<br>phạm vi còn có dấu hiệu bất thường<br>khác.|Không đưa đột quỵ/co giật,<br>autoencoder hoặc toàn bộ bộ training<br>của sample vào MVP ngã. Checkpoint<br>sample chỉ là tham chiếu, không mặc<br>định dùng được với feature mới.|



Tái sử dụng cụ thể: đọc và chuyển ý tưởng về capture, buffer, xác nhận theo thời gian và MJPEG. Nếu chép một hàm ngắn, giữ thông tin nguồn và giấy phép phù hợp; source MIT không tự động thay thế giấy phép của model weights. Không dành tuần đầu để sửa toàn bộ sample thành app mới. Chọn một repository mới gọn để từng thành viên hiểu được phần mình bàn giao. 

### 1.3. Phạm vi MVP và giả định làm việc 

- Nhóm có 3 người, mỗi người 4 giờ/ngày × 5 ngày/tuần × 4 tuần = 80 giờ; tổng 240 giờ. Đã tính thời gian học ngay trong 80 giờ, không cộng học ngoài giờ như nguồn lực miễn phí. 

- Một laptop Windows hoặc Linux chạy Python 3.11, camera IP RTSP cùng mạng; một điện thoại Android có Google Play services và Internet. Máy backend có Internet khi gửi FCM. Không giả định GPU NVIDIA đã có sẵn. 

- Một camera, một vùng theo dõi, một người mục tiêu tại một thời điểm. Pose có thể trả nhiều người; MVP không hứa theo dõi chính xác danh tính của nhiều người giao nhau. 

- Demo P0 dùng LAN kiểm soát; app-debug.apk cài trực tiếp. Điện thoại không truy cập được localhost của laptop: dùng IP LAN thực của laptop trong liên kết ghép. 

- ● Mất Internet: AI và cảnh báo foreground qua LAN có thể tiếp tục; push qua FCM không hoạt động cho đến khi kết nối phù hợp phục hồi. Laptop tắt/ngủ thì không còn xử lý AI. 

- Không đưa nhận dạng tuổi, nhận dạng khuôn mặt, cấp cứu tự động, kho video đám mây, đa hộ gia đình, app iOS/desktop và phát hành cửa hàng vào P0. 

### 1.4. Quyền sở hữu và ngân sách thời gian 

|**Vai trò**|**Sở hữu đầu ra**|**Hỗ trợ bắt buộc**|**Giờ/**<br>**tuần**|
|---|---|---|---|
|SV1 — AI/CV|Pose, feature, hai scorer A/B, state<br>machine; dữ liệu, training và đánh giá<br>AI|Bàn giao contract ngay ngày 2; cùng<br>SV2 kiểm tra pipeline; cùng SV3 kiểm<br>tra ý nghĩa cảnh báo|20|
|SV2 —<br>backend/RTSP/tíc<br>h hợp|Camera reader, API, ghép thiết bị,<br>storage, event, FCM sender, vận hành<br>demo|Nhận AI stub từ ngày 2; cho app kết nối<br>từ ngày 3; chịu trách nhiệm đường đi<br>end-to-end|20|
|SV3 —<br>Flutter/UI/thông<br>báo|Ghép thiết bị, trạng thái, camera view,<br>cảnh báo, quyền, âm thanh và APK|Dùng dữ liệu giả khi API chưa xong;<br>phối hợp smoke test FCM từ tuần 1|20|



Nhịp một ngày 4 giờ: 45 phút học đúng chủ đề của task; 120 phút lập trình; 45 phút test và ghép với thành viên liên quan; 30 phút xử lý lỗi/đệm. Ngày khó có thể chuyển một phần code sang học, nhưng vẫn giữ ít nhất 30 phút test. Việc trích xuất dataset hoặc train có thể chạy tự động trong lúc làm task khác; thời gian theo dõi/chỉnh sửa vẫn tính vào ngân sách. Chốt cuối ngày 5, 10, 15 và 20 bằng thao tác trên phần mềm đang chạy, không bằng phát biểu “đã nghiên cứu xong”. 

## 2. Kiến trúc, công nghệ và môi trường chạy 

### 2.1. Stack chính và lý do chọn 

|**Lớp**|**Chọn cho MVP**|**Lý do và giới hạn**|
|---|---|---|
|Backend|Python 3.11; FastAPI; Uvicorn một<br>worker|Hợp với CV Python, API có schema,<br>WebSocket/stream. Một worker tránh nhân đôi camera<br>và model; không chạy inference chặn event loop.|
|Camera|OpenCV VideoCapture với FFmpeg<br>backend|Đọc RTSP/video/webcam cùng một adapter; timeout<br>phụ thuộc backend đã build. Không hứa<br>CAP_PROP_BUFFERSIZE luôn có tác dụng [S7].|
|Pose|Ultralytics YOLO11n-pose, ByteTrack<br>chỉ định rõ|Một lần suy luận lấy box và COCO-17 keypoints. Đây là<br>pose estimator, không phải bộ phân loại ngã [S3, S4].|
|AI B|Pose pretrained + luật theo thời gian|Không train pose; cần thêm đặc trưng, lịch sử, xác nhận<br>và chống lặp. Đây là baseline chính để hoàn thành<br>MVP.|
|AI A|Pose đóng băng + TCN nhỏ tự train<br>bằng PyTorch|Huấn luyện phần phân loại chuỗi từ đầu; không gọi đó là<br>train toàn bộ hệ thống thị giác từ đầu.|
|Storage|sqlite3 có sẵn trong Python, một file<br>cục bộ|Chỉ giữ thiết bị, cấu hình và sự kiện cần giao lại sau<br>reconnect; outbox notification. Không cần<br>PostgreSQL/Redis/Celery.|
|App|Flutter/Dart, Android trước|Một app có UI, WebSocket, HTTP, FCM. Dùng<br>StatefulWidget/ChangeNotifier nhẹ, không thêm<br>BLoC/Riverpod trong MVP.|



|**Lớp**|**Chọn cho MVP**|**Lý do và giới hạn**|
|---|---|---|
|Thông báo|Firebase Cloud Messaging; firebase-<br>admin tại backend|Push không phụ thuộc việc app giữ WebSocket. Người<br>phát triển cấu hình Firebase; người dùng cuối không tạo<br>tài khoản [S8–S11].|
|Video tới<br>app|MJPEG qua HTTP; flutter_mjpeg|Backend chuyển frame thành JPEG; widget nhận HTTP<br>cùng header thiết bị. Điện thoại không phải phát RTSP<br>trực tiếp [S14].|
|Thử RTSP|MediaMTX + FFmpeg, chỉ dùng công<br>cụ có sẵn|Nếu chưa có camera, phát MP4 qua RTSP thật; đọc<br>MP4 trực tiếp vẫn chỉ kiểm tra CV, chưa kiểm tra RTSP<br>[S15].|



Không chọn Django cho MVP này vì không cần admin site, ORM lớn hay hệ thống tài khoản. FastAPI không tự làm AI nhanh hơn: capture, model và gửi FCM đều phải chạy ngoài coroutine xử lý request [S17]. Không dùng Streamlit làm app cuối vì cần vòng đời mobile và push khi app không mở. Không thêm WebRTC/HLS ở tuần 1: MJPEG đủ cho xem một camera trong demo, đổi lại tốn băng thông và không có tiếng của camera. 

### 2.2. Sơ đồ kiến trúc 



<!-- Start of picture text -->
KIEN TRUC MVP: LAPTOP XU LY, ANDROID NHAN CANH BAO<br>BACKEND PYTHON * MOT WORKER<br>C»CAMERA IP. RTSP (...CAPTURE + BO DEM MOI NHAT Y MJPEG C.»<br>RTSP / TCP j ; APP ANDROID<br>L [ Thread riéng + frame cé timestamp. UL + ghép thiét bj<br>Frame mdi. 4m thanh foreground<br>Pose|___MOt ~model SCORERactive  A/B+ latch > XACtheo episodemt WS khi0S appnén mo/khéa<br>Confirmed<br>“ h<br>EVENT + SQLITE + OUTBOX FCM<br>M6t event_id + retry hiu han Notification + data<br>RTSP chi tdi backend. Dién thoai nhan HTTP/WS va push; khéng chay Al<br><!-- End of picture text -->

_Hình 1. Kiến trúc MVP: xử lý video tại laptop, app Android nhận hình và sự kiện, FCM là kênh push độc lập._ 

Trong một tiến trình backend có thread capture, thread inference và worker gửi notification; các request HTTP/WebSocket chạy trên vòng lặp Uvicorn. Capture đưa frame mới nhất vào bộ đệm dung lượng 1. Inference lấy frame và tạo DetectionUpdate. Máy trạng thái tạo sự kiện khi đủ bằng chứng. Event được lưu trước rồi phát WebSocket và đưa vào outbox FCM. JPEG mới nhất được dùng chung cho các client để không encode lại theo từng người xem. 

Không dùng chung một cv2.VideoCapture giữa các thread; thread capture sở hữu việc open/read/release. Không gọi phương thức YOLO cùng một model từ nhiều worker. Bảo vệ cấu trúc shared bằng lock ngắn; không giữ lock khi inference, encode JPEG hoặc gửi mạng. 

Nếu benchmark cho thấy CPU khiến API không phản hồi, bước cải tiến là tách inference sang một process với hàng đợi hữu hạn; không tăng số worker Uvicorn để chữa vấn đề đó. 

### 2.3. Hai môi trường demo cụ thể 

|**Chế độ**|**Cách nối**|**Điều kiện đạt**|
|---|---|---|
|A — RTSP giả lập<br>từ video|Laptop chạy MediaMTX; FFmpeg phát MP4 vào<br>rtsp://127.0.0.1:8554/fall_demo; backend đọc đúng<br>URL RTSP. Android ghép tới IP LAN của laptop.|Đủ kiểm tra toàn tuyến RTSP → AI<br>→ app. Ghi rõ hình vào là video đã<br>ghi; không gọi đây là thử camera IP<br>thật.|
|B — camera RTSP<br>thật|Camera và laptop cùng LAN; backend đọc<br>rtsp://<camera-host>/<path>; app vẫn chỉ nối<br>backend. Laptop và Android có Internet để FCM.|Ít nhất một phiên test RTSP thật,<br>rút mạng camera rồi cắm lại; kiểm<br>tra AI và nhận cảnh báo trên điện<br>thoại.|
|C — phát triển<br>nhanh|Video file hoặc webcam đọc trực tiếp, AI mock/real<br>tùy task; điện thoại dùng API/WS.|Chỉ là bước phát triển; không thay<br>thế nghiệm thu RTSP hoặc nghiệm<br>thu AI thật.|



### 2.4. Thiết lập môi trường ngày 1–2 

SV2 tạo môi trường Python riêng, SV1 dùng cùng Python và dependency lock; không cài cùng lúc opencv-python và opencv-python-headless vì cùng namespace cv2. Mặc định dùng opencv-python với ultralytics; nếu muốn bản headless phải kiểm tra phụ thuộc thực tế và khóa một bộ duy nhất. Cài PyTorch CPU trước nếu chưa xác minh CUDA; chỉ thêm CUDA đúng driver khi thật sự cần. Chọn phiên bản đã chạy smoke test rồi ghi chính xác vào requirements.lock.txt, không để một nhóm dùng ba phiên bản YOLO khác nhau. 

<mark>`python3.11 -m venv .venv # Linux/macOS: source .venv/bin/activate # Windows PowerShell: .\.venv\Scripts\Activate.ps1 python -m pip install --upgrade pip python -m pip install fastapi 'uvicorn[standard]' ultralytics opencv-python numpy pyyaml pydantic-settings firebase-admin pytest httpx scikit-learn python -m pip freeze > requirements.lock.txt python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1`</mark> Đây là nhóm package cần thiết, chưa phải bộ phiên bản đã được kiểm thử. SV1/SV2 kiểm tra import, đọc một frame và chạy một inference trước khi khóa phiên bản. Khi ultralytics đã kéo PyTorch/OpenCV thích hợp thì không cài lại một bản xung đột. Máy khác cài lại từ requirements.lock.txt. pyproject.toml quy định Python >=3.11,<3.12 và module của project; package init sinh theo cây mã nguồn. 

```
flutter doctor
flutter create --platforms=android --org com.student mobile
cd mobile
flutter pub add http web_socket_channel flutter_secure_storage
flutter pub add firebase_core firebase_messaging flutter_local_notifications
flutter pub add flutter_mjpeg audioplayers
flutterfire configure --platforms=android
flutter run
```

SV3 cài Android SDK và Flutter theo hướng dẫn chính thức, giải quyết flutter doctor trước khi làm UI. Thêm integration_test vào dev_dependencies theo đoạn YAML dưới. Chạy FlutterFire CLI sau khi cài Firebase CLI và đăng nhập tài khoản phát triển [S10]. Package 

name cố định từ đầu, ví dụ com.student.mobile; giữ đúng applicationId khi đăng ký Firebase. Nếu đổi tên hiển thị thì không đổi applicationId giữa tuần 2. 

```
# mobile/pubspec.yaml — bổ sung vào dev_dependencies đã có:
dev_dependencies:
  flutter_test:
    sdk: flutter
  integration_test:
    sdk: flutter
```

Lưu pubspec.lock để ba máy dùng cùng dependency. google-services.json và firebase_options.dart do công cụ tạo; service-account JSON chỉ nằm ở máy backend, được tham chiếu qua GOOGLE_APPLICATION_CREDENTIALS, không đóng gói vào APK. Tuần 1 dùng kênh thử fall_test_v0 với sound mặc định. Tuần 3, sau khi có raw sound, tạo mới hai kênh chính thức fall_alerts_v1/fall_silent_v1; không sửa sound của kênh cũ. Chốt minSdk/compileSdk theo bộ FlutterFire hiện hành đã cài, không hạ SDK để né lỗi build; bản thử nghiệm không đòi hỏi đưa lên Play Store. 

### 2.5. Cấu hình tối thiểu và biến có thể thay đổi 

```
# configs/app.yaml
camera_id: living_room
camera_source: rtsp
rtsp_transport: tcp
open_timeout_ms: 5000
read_timeout_ms: 3000
reconnect_seconds: [1, 2, 4, 8, 15]
stale_frame_seconds: 3
capture_queue_size: 1
preview_fps: 3
sqlite_path: runtime/fallguard.db
app_env: development
```

<mark>`# configs/ai.yaml mode: pretrained pose_weights: models/yolo11n-pose.pt image_size: 480 sample_hz: 10 window_samples: 30 max_pose_gap_seconds: 0.3 min_valid_window_fraction: 0.8 confirmation_seconds: 2.0 recovery_seconds: 3.0 cooldown_seconds: 60`</mark> Các giá trị này là điểm bắt đầu để chạy thử. Số 10 Hz, 30 mẫu và 2 giây phải được dùng nhất quán giữa trích xuất dữ liệu và runtime; thay đổi phải huấn luyện/đánh giá lại nhánh A hoặc xác nhận metadata khớp. RTSP URL có mật khẩu nằm trong cấu hình runtime do app gửi, không ghi vào YAML public. configs/app.yaml chỉ giữ URL ví dụ đã loại bí mật; .env.example chỉ giữ tên biến. Không trả RTSP URL nguyên vẹn về endpoint status. 

## 3. Hợp đồng dữ liệu, API và ghép thiết bị 

### 3.1. Hợp đồng giữa camera, AI, backend và app 

SV1 định nghĩa dataclass Python trong backend/contracts.py, SV2 định nghĩa schema HTTP tương ứng và cả hai cùng khóa nghĩa của trường trong ngày 2. Flutter không import Python: SV3 viết parser theo JSON mẫu trong mobile/lib/models.dart. Backend chỉ serialize bản DTO cho network; không đưa numpy.ndarray hoặc toàn bộ keypoints vào push. schema_version bắt đầu bằng 1; khi thay đổi ý nghĩa trường thì cả ba cùng cập nhật, không âm thầm đổi tên giữa tuần. 

```
from dataclasses import dataclass
from typing import Literal, Protocol
import numpy as np
```

<mark>`@dataclass(frozen=True) class FramePacket: camera_id: str stream_session_id: str frame_id: int captured_mono: float captured_at_utc: str image_bgr: np.ndarray @dataclass(frozen=True) class FallCandidate: track_id: int score: float score_kind: Literal["rule_score", "uncalibrated_model_score"] valid_pose: bool onset_observed: bool low_posture: bool reasons: tuple[str, ...] @dataclass(frozen=True) class DetectionUpdate: camera_id: str stream_session_id: str frame_id: int candidates: tuple[FallCandidate, ...] inference_ms: float model_id: str class FallDetector(Protocol): def process(self, packet: FramePacket) -> DetectionUpdate: ... def reset(self, stream_session_id: str) -> None: ... def close(self) -> None: ...`</mark> captured_mono dùng đo khoảng thời gian trong cùng tiến trình; captured_at_utc dùng hiển thị và đối chiếu thiết bị. captured_mono là lúc frame đã được backend nhận, không phải timestamp phơi sáng thật của camera. stream_session_id đổi sau reconnect/switch camera để không ghép lịch sử của hai luồng. frame_id tăng trong một phiên. score của luật chỉ là điểm quy tắc; score model chưa hiệu chuẩn không được hiển thị như xác suất y khoa hay “độ chính xác 84%”. 

FallDetector sở hữu pose, buffer và scorer A hoặc B; nó chỉ trả bằng chứng từng lần xử lý. FallStateMachine dùng chung nằm ngoài scorer để A/B có cùng điều kiện xác nhận. backend/pipeline.py gọi process(), đưa candidate vào state machine theo từng (stream_session_id, track_id), rồi gửi transition CONFIRMED sang EventService. Model không tự gửi notification, không giữ FCM token và không biết điện thoại nào đang xem. 

### 3.2. Schema status và sự kiện chuẩn 

```
{
  "schema_version": 1,
  "installation_id": "installation-lab-a",
  "camera": {
    "id": "living_room", "state": "CONNECTED",
    "last_frame_age_ms": 140, "reconnect_attempts": 0
  },
  "ai": {
    "state": "READY", "mode": "pretrained",
    "model_id": "pose-rules-v1", "processed_fps": 9.4,
    "last_inference_ms": 94, "warmup_remaining_samples": 0
  },
  "notifications": {"configured": true, "last_send_state": "accepted"}
}
```

Đây là dữ liệu minh họa hợp đồng, không phải số đo. camera.state thuộc STOPPED/CONNECTING/CONNECTED/RECONNECTING/ERROR; ai.state thuộc LOADING/WARMUP/READY/DEGRADED/ERROR. Camera CONNECTED nhưng AI ERROR vẫn phải hiện “camera có hình, nhận diện không hoạt động”. GET /health chỉ phản ánh tiến trình API sống; không dùng health=ok để kết luận camera hay push đã sẵn sàng. 

```
{
  "schema_version": 1,
  "type": "fall.confirmed",
  "event_id": "evt-550e8400-e29b-41d4-a716-446655440000",
  "episode_id": "ep-session7-track12-001",
  "installation_id": "installation-lab-a",
  "camera_id": "living_room",
  "stream_session_id": "session7",
  "track_id": 12,
  "occurred_at": "2026-10-29T08:10:00Z",
  "confirmed_at": "2026-10-29T08:10:02Z",
  "score": 0.84,
  "score_kind": "rule_score",
  "model_id": "pose-rules-v1",
  "message": "Phát hiện diễn biến nghi ngã. Vui lòng kiểm tra người được theo
dõi.",
  "reasons": ["rapid_descent", "low_posture_sustained"],
  "is_test": false
}
```

occurred_at là mốc onset suy ra từ khung hình, confirmed_at là khi đủ điều kiện xác nhận. Backend dùng một event_id cho REST, WS, FCM và thao tác xác nhận đã xem. episode_id biểu diễn một diễn biến ngã; mỗi frame sau ngã không tạo event mới. event_id được sinh và lưu đúng một lần sau transition, không tạo lại khi retry push. is_test=true phải hiện rõ “Thông báo thử”, không đưa vào TP/FP khi đánh giá. 

### 3.3. API tối thiểu được khóa cuối ngày 2 

|**Phương thức và route**|**Đầu vào/quyền**|**Đầu ra; lỗi cần xử lý**|
|---|---|---|
|GET /health|Công khai; không trả cấu hình|200: service alive, schema_version;<br>không có RTSP/token.|
|POST /api/v1/pairing/claim|Liên kết có code dùng một lần;<br>không tài khoản|201: device_id, device_secret,<br>installation_id; 400 sai dữ liệu; 409 đã<br>dùng; 410 hết hạn; 429 quá số lần.|
|GET /api/v1/status|Authorization: Bearer<br>device_secret|Status như ví dụ; 401/403 khóa không<br>hợp lệ hoặc đã thu hồi.|
|PUT /api/v1/camera|Khóa thiết bị đã ghép; URL<br>RTSP, nhãn camera|202: CONNECTING và request_id; kết<br>quả về status/WS. 422 scheme/host<br>thiếu; không block request chờ RTSP vô<br>hạn.|
|POST /api/v1/camera/stop|Khóa thiết bị|202; reader dừng, AI reset, không sinh<br>sự kiện vì mất frame.|
|GET /api/v1/stream.mjpeg|Khóa thiết bị qua header|multipart/x-mixed-replace;<br>boundary=frame. Không gửi RTSP cho<br>app; ngắt viewer không dừng AI.|



|**Phương thức và route**|**Đầu vào/quyền**|**Đầu ra; lỗi cần xử lý**|
|---|---|---|
|GET /api/v1/preview.jpg|Khóa thiết bị; route dự phòng<br>cùng cache|JPEG mới nhất hoặc 503 khi chưa có<br>frame; app có thể polling 1 FPS thay<br>MJPEG.|
|WS /api/v1/ws|Khóa qua header lúc handshake<br>trên Android|camera.status, ai.status, fall.confirmed;<br>ping/pong và reconnect; snapshot qua<br>REST sau resume.|
|GET /api/v1/events?<br>after=<cursor>|Khóa thiết bị; cursor event tăng<br>dần từ storage|Danh sách có giới hạn, next_cursor;<br>dùng khi WS bị ngắt. Không suy thứ tự<br>UUID theo thời gian.|
|POST /api/v1/events/{id}/ack|Khóa thiết bị; ack event thuộc<br>installation này|200 kể cả đã ack; 404 sự kiện không tồn<br>tại trong backend này. Ack không đồng<br>nghĩa người đã hồi phục.|
|PUT /api/v1/devices/{id}/push|Chỉ khóa của đúng device_id|Đăng ký/cập nhật endpoint FCM và<br>sound_enabled; 403 nếu đổi endpoint<br>của thiết bị khác.|
|DELETE /api/v1/devices/{id}|Chỉ khóa chính thiết bị hoặc CLI<br>cục bộ|204 và thu hồi khóa; loại thiết bị khỏi<br>fanout sau đó.|
|POST /api/v1/notifications/test|Khóa thiết bị; chỉ gửi về thiết bị<br>gọi|202: test event_id; không dùng để mô<br>phỏng kết quả AI thật.|



SV2 dùng Pydantic kiểm tra kích thước chuỗi, scheme, trường bắt buộc và enum; không nhận đường dẫn file tùy ý từ điện thoại. Chế độ video/webcam được bật bằng cấu hình phát triển hoặc CLI cục bộ, không mở endpoint đọc mọi file trên laptop. Với RTSP hợp lệ cú pháp nhưng không mở được, trả trạng thái lỗi có thể đọc được: URL sai, không có frame hoặc đang reconnect; tránh khẳng định sai mật khẩu nếu OpenCV chỉ báo không mở được. 

### 3.4. Ghép thiết bị không cần tài khoản 

“Không có tài khoản” vẫn cần cơ chế chứng minh thiết bị được phép xem camera. MVP dùng ghép cặp một lần (device pairing): người có quyền ở laptop chạy CLI cục bộ để sinh một liên kết bí mật sống 120 giây. App dán liên kết, đọc base URL và code, gọi claim qua backend; backend tiêu thụ code nguyên tử và cấp khóa thiết bị ngẫu nhiên 256 bit. Không có username, password, email, profile hoặc Firebase Authentication. 

```
python -m backend.pairing create --base-url http://192.168.1.20:8000
```

```
# Dạng liên kết để dán vào app, không phải giá trị thật:
fallguard://pair?server=http%3A%2F%2F192.168.1.20%3A8000&code=<one-time-
code>&installation=<installation-id>
```

```
POST /api/v1/pairing/claim
{
```

```
  "pairing_code": "<one-time-code>",
```

- <mark>`"expected_installation_id": "<installation-id>",`</mark> 

- <mark>`"client_label": "Dien thoai nguoi cham soc"`</mark> 

- `}` ● backend/pairing.py dùng secrets.token_urlsafe(32); chỉ lưu SHA-256 của code; hết hạn dựa UTC trong DB. BEGIN IMMEDIATE/transaction kiểm tra chưa dùng rồi đánh dấu đã dùng và tạo device trong cùng giao dịch; hai app claim đồng thời chỉ một app thành công. 

- Khóa thiết bị mới được gửi về đúng lần claim; backend chỉ lưu hash. device_secret là quyền API, khác FCM endpoint là địa chỉ nhận push. Cất khóa trong flutter_secure_storage; không lưu chung với UI settings dạng text. 

- installation_id bền qua restart nhưng khác giữa hai laptop. App so ID từ pairing và status; nhận event khác installation thì bỏ ở UI. Khi chuyển backend, xóa khóa/cursor cũ và làm ghép mới; không tự mang FCM endpoint sang backend khác. 

- ● Mỗi device gắn với đúng installation và camera P0. Backend chỉ gửi FCM về device còn active trong DB này; không dùng một topic công khai như all_users. Route push chỉ cập nhật endpoint của thiết bị đang xác thực. 

- Người ở laptop có thể thu hồi khóa qua CLI: python -m backend.pairing revoke -- device-id <id>. App nhận 401 thì dừng stream, WS và yêu cầu ghép lại; không tự tắt xác thực để “cho chạy được”. 

- Liên kết P0 được dán vào app; QR/deep link tự mở có thể làm P1. Không yêu cầu thêm thư viện quét camera và quyền camera trên điện thoại để hoàn tất MVP. 

Độ bảo vệ trong demo: khóa ngẫu nhiên và ràng buộc installation ngăn thiết bị không được ghép truy cập nhầm, nhưng HTTP trên LAN không chống được nghe lén. Vì vậy APK debug chỉ dùng mạng lab kiểm soát; không mở port backend/camera ra Internet. Nếu chuyển sang sử dụng ngoài lab, bật HTTPS có chứng chỉ được điện thoại tin cậy trước khi ghép và dùng wss://; giữ nguyên pairing và quyền route. Đây là giới hạn cụ thể của phương án demo, không được tuyên bố hệ thống đã an toàn cho triển khai công cộng. 

Endpoint tạo pairing không công khai trên LAN: CLI là cách tạo mã P0. GET /health không kèm bí mật. Status và thông báo lỗi che user/password trong URL camera. SQLite và service-account file nằm ở laptop với quyền file giới hạn. Push background dùng nội dung chung, không gửi frame, token truy cập hoặc URL có mật khẩu lên FCM; một message đã được FCM chấp nhận trước lúc revoke có thể còn xuất hiện muộn. 

### 3.5. Bảng dữ liệu đủ cho MVP 

|**Bảng**|**Trường chính**|**Ràng buộc cần có**|
|---|---|---|
|installation|id, created_at, schema_version|Một installation_id ổn định; không tạo mới ở<br>mỗi lần khởi động.|
|pairing_codes|code_hash, expires_at, consumed_at|Hash duy nhất; claim kiểm tra và tiêu thụ<br>trong một transaction.|
|devices|device_id, secret_hash, active, push_kind,<br>push_value, sound_enabled, updated_at|secret_hash duy nhất; không trả<br>secret_hash/push_value cho device khác.|
|camera_config|camera_id, source, protected_url, label|Chỉ một camera P0; không để protected_url<br>xuất hiện trong status.|
|events|cursor INTEGER, event_id, episode_id,<br>payload_json, ack_at|event_id và episode_id duy nhất; cursor tăng<br>dần; is_test nằm trong payload.|
|outbox|event_id, device_id, state, attempts,<br>next_attempt_at, expires_at|UNIQUE(event_id, device_id); state<br>pending/accepted/failed/expired; không dùng<br>accepted để suy đã nhận ở máy.|



schema.sql tạo bảng idempotent. Mở SQLite connection ngắn theo thread/giao dịch, đặt timeout, bật WAL nếu đã test trên máy; không share connection mặc định giữa thread capture/AI/API. Có lock cho các giao dịch ghi ngắn; tuyệt đối không giữ transaction khi gọi 

FCM. MVP giữ tối đa 100 sự kiện gần nhất hoặc 7 ngày; đó là dữ liệu tính năng để app đồng bộ, không xây kho video hay hệ thống phân tích vận hành lớn. 

## 4. Pipeline RTSP và thuật toán nhận diện ngã 

### 4.1. RTSP: từ URL đến frame mới nhất 

```
# Chạy hai terminal riêng khi chưa có camera IP:
# Terminal 1 — MediaMTX đã tải đúng bản cho hệ điều hành:
mediamtx deploy/mediamtx.yml
```

```
# Terminal 2 — MP4 dùng thử đặt tại data/raw/demo/fall.mp4:
ffmpeg -re -stream_loop -1 -i data/raw/demo/fall.mp4 -an -c:v libx264 -preset
veryfast -tune zerolatency -pix_fmt yuv420p -f rtsp -rtsp_transport tcp
rtsp://127.0.0.1:8554/fall_demo
```

```
# deploy/mediamtx.yml:
paths:
  fall_demo:
    source: publisher
```

FFmpeg và MediaMTX là chương trình ngoài Python cần cài trước. Nếu MP4 đã có video H.264 phù hợp có thể dùng -c:v copy thay encoder; giữ -re để mô phỏng thời gian thật. Dừng FFmpeg để thử mất nguồn; mở lại để thử reconnect. URL 127.0.0.1 ở đây là backend và RTSP server trên cùng laptop, không phải địa chỉ app dùng nối backend. 

- Bước 1 — kiểm tra đầu vào: trim URL, cho rtsp/rtsps theo khả năng camera, phải có hostname; không nhận http/file trong route cấu hình P0. Nếu nhập user/password riêng, dùng urllib.parse.quote để mã hóa các ký tự @, :, / trong credential trước khi ghép URL. 

- Bước 2 — mở luồng ở capture thread với cv2.CAP_FFMPEG và OPEN_TIMEOUT/READ_TIMEOUT truyền tại lúc mở. Chọn TCP để giảm lỗi packet trên Wi-Fi cho demo; đo lại độ trễ. Không gọi VideoCapture trong async route. 

- Bước 3 — kiểm tra isOpened(), rồi read() trả ret và frame không None/không rỗng. Lấy frame mới tạo FramePacket, cập nhật thời điểm last_frame và bộ đệm latest dung lượng 1. Không tích lũy hàng trăm frame khi AI chậm. 

- Bước 4 — read thất bại hoặc quá stale threshold: state RECONNECTING, ngừng đưa frame cũ vào AI; reset lịch sử theo phiên. Release ở thread đang sở hữu capture, chờ backoff 1,2,4,8,15 giây có thể dừng sớm bằng Event.wait(). 

- Bước 5 — reconnect thành công: sinh stream_session_id mới, reset tracker/pose buffer/state, chuyển WARMUP; không lấy tư thế trước mất mạng để kết luận ngã sau nối lại. 

- Bước 6 — stop/switch/shutdown: báo stop_event, để capture thread kết thúc theo read timeout rồi release; join có timeout và phản ánh lỗi nếu thread không dừng. Không tạo thêm reader khi reader cũ còn sống. 

CAP_PROP_BUFFERSIZE chỉ là một cấu hình hỗ trợ nếu backend triển khai; hàng đợi dung lượng 1 trong Python cũng không loại hết buffer trong camera/FFmpeg. Đo tuổi frame tại backend, thử xem đồng hồ/động tác trong preview và giảm buffer/chọn substream H.264 640×360 hoặc 640×480 khi cần. Không dùng số FPS từ camera làm FPS AI. Với file offline, timestamp dựa thứ tự frame và FPS/video timestamp đã xác minh, không lấy tốc độ vòng lặp chạy nhanh để tính vận tốc. 

```
# Pipeline trách nhiệm, không phải toàn bộ code chạy ngay:
capture_worker:
    open_with_timeouts()
    while not stop_event.is_set():
        ok, frame = capture.read()
        if not ok or frame is None:
            mark_reconnecting_and_reset_session()
```

```
            reconnect_with_bounded_backoff()
            continue
        latest_frame.replace(make_packet(frame))
```

```
inference_worker:
    packet = latest_frame.wait_newer_than(last_frame_id)
    update = detector.process(packet)
    for candidate in update.candidates:
        transition = fall_states.update(candidate, packet.captured_mono)
        if transition.just_confirmed:
            event_service.create_once(transition)
```

### 4.2. Pose và định danh người trong khung hình 

Khởi tạo YOLO("models/yolo11n-pose.pt") một lần. Với frame liên tiếp, model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False) cung cấp box/keypoints và ID nếu tracker đã tạo track [S3, S4]. Kiểm tra result.boxes, result.keypoints và boxes.id tồn tại; không ép int(None). Nếu chưa có track_id, hiển thị trạng thái đang theo dõi nhưng chưa tích lũy sự kiện cho người đó. Tách state theo track và stream session. Dùng model nano, imgsz 480 trước; giảm 320 khi CPU không đạt mục tiêu. 

Keypoint COCO-17 gồm mũi, mắt, tai, vai, khuỷu, cổ tay, hông, gối, cổ chân. Góc thân dùng trung điểm hai vai và trung điểm hai hông; cần đủ confidence. Không dùng tọa độ (0,0) của khớp không thấy làm tọa độ thật. Ảnh OpenCV mặc định BGR; adapter YOLO nhận numpy frame theo API của thư viện; nếu đổi sang MediaPipe phải chuyển RGB và ánh xạ schema một cách chủ động, không đổi màu hai lần. 

Đối với MVP một người, nếu có hơn một người trong vùng mục tiêu thì app hiện “nhiều người trong vùng; kết quả cần kiểm tra” và vẫn tách track, không gán danh tính “ông/bà” từ ID. Theo dõi xuyên che khuất dài, re-identification và phân quyền nhiều camera là nâng cao. Trên reconnect hoặc thay camera, gọi reset, không tái sử dụng ID cũ như cùng một người. 

### 4.3. Đặc trưng dùng chung: quan sát biến đổi thay vì chỉ một ảnh nằm 

|**Đặc trưng**|**Cách tính và ý nghĩa**|**Giới hạn cần xử lý**|
|---|---|---|
|Góc thân θ|u = midpoint(vai) − midpoint(hông); θ =<br>atan2(abs(u_x), abs(u_y)) đổi sang độ. Gần 0 là<br>thân đứng; gần 90 là thân ngang theo ảnh.|Thiếu vai/hông hoặc camera nhìn<br>cao làm góc méo<br>invalid, không<br>→<br>tự thay bằng 90.|
|Tỉ lệ khung r|r = width/(height+epsilon), chỉ tính khi box hợp lệ.<br>Hỗ trợ nhận biết hình người thấp, bè ra.|Ngồi/cúi cũng đổi box; r cao không<br>đủ kết luận ngã.|
|Vận tốc hông<br>theo ảnh|v = (y_hip(t) − y_hip(t−Δt)) / (H_ref × Δt). H_ref là<br>chiều cao đứng tin cậy trước đó. y tăng hướng<br>xuống.|Không phải m/s; không dùng scale<br>box đang co mạnh làm vận tốc tăng<br>giả. Chưa có H_ref thì giảm tin cậy.|
|Thay đổi góc|Δθ/Δt trên các mẫu có chất lượng, kết hợp tụt hông<br>trong thời gian ngắn.|Đạo hàm nhạy nhiễu; smoothing<br>nhẹ, khoảng cách thời gian thật;<br>không nối qua gap.|
|Tư thế thấp kéo<br>dài|Tổng thời gian bằng chứng low_posture hợp lệ sau<br>onset, trong cửa sổ xác nhận 2 s.|“Không thấy người” không đồng<br>nghĩa đang nằm bất động; gap dài<br>hủy xác nhận.|



|**Đặc trưng**|**Cách tính và ý nghĩa**|**Giới hạn cần xử lý**|
|---|---|---|
|Chuyển động sau<br>hạ người|Độ dịch khớp chuẩn hóa theo tỉ lệ cố định; dùng hỗ<br>trợ, không bắt buộc bất động tuyệt đối.|Một người ngã vẫn có thể cử động;<br>điều kiện bất động quá chặt gây bỏ<br>sót.|



Ngưỡng thử đầu tiên có thể là θ > 60°, r > 1.1, vận tốc hông > 0.7 chiều cao tham chiếu/giây và biến đổi nhanh trong < 1 giây. Chỉ coi đây là giả thuyết để sweep trên validation, không phải ngưỡng y khoa hay giá trị lấy từ kiểm thử. Rule candidate yêu cầu có ít nhất hai bằng chứng chuyển động/tư thế hợp lệ, tránh một tín hiệu nhiễu tự phát alarm. Ngưỡng cuối lưu trong configs/ai.yaml; giữ tập test tách biệt. 

### 4.4. Lấy mẫu theo thời gian và chuẩn hóa cho nhánh A 

Dùng một cửa sổ 30 mốc × 10 Hz = 3 giây. Buffer có timestamp chứ không coi 30 frame bất kỳ luôn là 3 giây. Không đếm cùng frame_id hai lần để tạo cảm giác đủ dữ liệu. Ở mỗi tick dùng quan sát mới gần tick; ghi confidence/mask khi thiếu, không bịa pose. Khoảng thiếu >0.3 giây làm mất tính liên tục, reset phần xác nhận và bắt đầu warmup; cửa sổ ít hơn 80% quan sát hợp lệ không được cho model phát candidate. 

Vector mỗi mẫu dài 54: 17 × (x,y,confidence) = 51 giá trị, thêm y_hip theo chiều cao ảnh, góc thân chuẩn hóa và tỉ lệ box đã giới hạn. TCN nhận [batch,54,30], dataset lưu [T,54] rồi transpose trước model. Dùng cùng hàm normalize_window() trong train và runtime. Gốc tọa độ và scale lấy chung cho cả cửa sổ: ví dụ gốc hông đầu cửa sổ có đủ tin cậy, scale trung vị chiều dài thân hợp lệ. Không trừ hông riêng mỗi frame rồi làm mất bằng chứng cơ thể đang tụt xuống. 

Khi có short gap, confidence tương ứng bằng 0 và coordinate lấy theo quy ước đã khóa, chỉ nội suy ngắn trong cửa sổ quan sát được nếu đã kiểm chứng giống runtime. Phương án P0 đơn giản hơn là không nội suy, loại cửa sổ không đủ chất lượng. Metadata model ghi feature_version, sample_hz, window_samples, input_dim=54 và pose_schema=COCO17. Khi khác metadata, backend báo model không tương thích và chuyển về B hoặc dừng AI rõ ràng; không load âm thầm rồi phát dự đoán sai. 

### 4.5. Máy trạng thái xác nhận và chặn cảnh báo lặp 



<!-- Start of picture text -->
MAY TRANG THAI: XAC NHAN MOT LAN CHO MOI DIEN BIEN<br>Khéng cén bang chting > hily nghi ng<br>> la .<br>WARMUP NORMAL SUSPECTED<br>DU lich sirhgp 16 Theo déi trudc onset Cé onset + score di<br>Re-arm sau héi phuc + codidown<br>Khéng ghp dai<br>RECOVERY Héi phuc LATCHED Event CONFIRMED<br>Binh thudng lién tuc ~3 s Mét event; khéng gif lai Low posture hgp Ié ~2 s<br>) \<br>Dé ligu tré lai<br>reset + WARMUP<br>Mat dif ligu 65 bat ky trang thai nao:<br>( ngimg xac nhan, khéng coi la bat dong<br>UNKNOWN<br>Thiéu frame / pose<br>Ack trén app ding canh bdo, khéng thay thé diéu kién héi phuc cia Al.<br><!-- End of picture text -->

_Hình 2. Máy trạng thái dùng chung cho A/B; mất dữ liệu làm gián đoạn xác nhận thay vì được tính như bất động._ 

|**Trạng thái**|**Điều kiện vào/ra**|**Hành động**|
|---|---|---|
|WARMUP|Bắt đầu stream, reconnect hoặc chưa có đủ lịch<br>sử hợp lệ.|Không phát fall.confirmed; ghi rõ đang lấy<br>mẫu. Người đã nằm sẵn được ghi là<br>chưa có diễn biến để kết luận.|
|NORMAL|Đủ dữ liệu, chưa có onset; scorer thấp hoặc<br>không có dấu chuyển tiếp.|Cập nhật lịch sử; nhớ chiều cao đứng<br>tham chiếu tin cậy.|
|SUSPECTED|Onset có bằng chứng hạ người/đổi tư thế nhanh<br>và scorer vượt ngưỡng vào.|Tạo episode tạm; tích lũy bằng chứng<br>thấp theo timestamp. Nếu trở lại bình<br>thường, hủy candidate.|
|CONFIRMED|Sau onset, low_posture hợp lệ duy trì khoảng 2<br>s; độ phủ đủ; không có gap > 0.3 s.|just_confirmed=True đúng một lần; tạo<br>event, chuyển LATCHED. Không chờ<br>thêm một cửa sổ xác nhận 2 s ở backend<br>nữa.|
|LATCHED|Đã tạo sự kiện cho episode và người vẫn<br>nằm/diễn biến chưa hồi phục.|Không tạo sự kiện mới dù hết 60 s<br>cooldown. Cooldown không phải bộ hẹn<br>giờ gửi lại vô hạn.|
|RECOVERY|Có đứng/dáng bình thường tin cậy liên tục 3 s.|Kết thúc episode; chỉ re-arm khi hồi phục<br>và cooldown tối thiểu đã qua. Ack chỉ<br>dừng UI/sound, không tự re-arm AI.|
|UNKNOWN|Thiếu pose hoặc frame stale, đổi session, ID<br>không tin cậy.|Dừng xác nhận đang dở; không tăng thời<br>gian nằm, không tự phát ngã. Sau dữ liệu<br>trở lại, warmup.|



Chống lặp có ba lớp khác nhau: state machine chỉ phát một lần mỗi episode; storage có UNIQUE(episode_id) và outbox UNIQUE(event_id,device_id); app deduplicate event_id giữa WS/FCM/REST. Nếu track ID mất rồi đổi trong khi người vẫn ở dưới sàn, không có lịch sử onset mới thì không phát lần nữa. Khi cùng camera vừa phát event, giữ một latch vùng không gian ngắn để giảm lặp do ID churn; quy tắc này phải test và không được chặn một ngã mới của người khác trong hệ nhiều người chưa hỗ trợ. 

Các ca dễ nhầm: ngồi ghế nhanh, cúi nhặt đồ, quỳ, nằm từ từ, ngả trên sofa, camera rung. Bắt buộc có chuỗi trước–trong–sau chuyển động, không suy ngã từ bbox nằm ngang. Các ca dễ bỏ sót: ngã chậm, ngã thẳng về phía camera, bị ghế che, ra khỏi vùng nhìn, ngã rồi đứng lên nhanh hoặc ngã trong warmup. Test riêng và ghi giới hạn của bản demo trong README; không “chữa” bằng cách tự báo ngã mỗi khi mất người. 

### 4.6. Ngân sách độ trễ và hiệu năng 

Đặt mục tiêu thử ở một camera: AI khoảng 8–10 lần xử lý/giây với ảnh 480 hoặc 320, preview 2–3 FPS. Với xác nhận tư thế thấp 2 giây, độ trễ từ onset đến event không thể là vài chục mili giây. Mốc lập kế hoạch: event sau khoảng 2–5 giây nếu thấy đủ onset; điện thoại nhận sau xác nhận dưới khoảng 3 giây trong LAN/Internet ổn định. Đây là mục tiêu cần đo; push ngoài mạng tốt có thể chậm hơn hoặc không đến. 

Đo t_capture→t_infer_done, t_onset→t_confirmed, t_confirmed→t_fcm_accepted và t_confirmed→t_app_received riêng. FPS AI = số frame_id mới đã xử lý/thời gian wall clock; FPS preview là số JPEG hiển thị, không dùng để chứng minh AI nhanh. Dùng p50/p95 trên ít nhất 20 lần cảnh báo thử và vài video thật; FCM accepted không phải app received. Nếu không có đồng bộ đồng hồ đáng tin, quay cả màn hình backend và điện thoại cùng một camera hoặc dùng mốc thời gian một thiết bị để đo end-to-end. 

## 5. Thông báo, âm thanh và giao diện ứng dụng 

### 5.1. Giao diện ít màn hình nhưng đủ chức năng 

|**Màn hình**|**Thao tác chính**|**Trạng thái bắt buộc**|
|---|---|---|
|Ghép thiết bị|Dán pairing link; xem server và nhãn; bấm<br>Kết nối.|Link sai/hết hạn, backend không tới được,<br>đã ghép, khóa bị thu hồi. Không có trang<br>đăng ký/đăng nhập.|
|Giám sát|Nhập/chỉnh RTSP; bắt đầu/dừng; xem ảnh;<br>trạng thái camera/AI; nút thử thông báo.|Connecting/reconnecting/error; AI<br>warmup/degraded; stream stale; quyền<br>notification bị từ chối.|
|Cảnh báo|Thông điệp nghi ngã, camera, giờ, nút Tắt<br>âm thanh và Đã xem.|Một event hiển thị một lần; nếu offline có<br>pending ack; không hiển thị “ngã chắc<br>chắn” hoặc độ chính xác giả.|
|Thiết lập gọn<br>trong trang giám<br>sát|Bật/tắt âm thanh thông báo, mở cài đặt hệ<br>điều hành, hủy ghép.|Thông báo rõ âm thanh foreground khác<br>kênh notification; không hứa vượt chế độ<br>im lặng/DND.|



Màn hình home dùng API lấy snapshot lúc mở và stream WS cho thay đổi; nếu WS rớt thì hiển thị mất kết nối và retry với backoff. Resume app: đọc status, đồng bộ events theo 

cursor, cập nhật token FCM mới nếu có. Không dựa WS luôn sống khi app ở nền. Bấm Đã xem chỉ xác nhận đã đọc event; không xác nhận người đã an toàn, không làm AI reset khi chưa có recovery. 

### 5.2. Luồng push từ AI tới Android 

- AI đủ bằng chứng → FallStateMachine just_confirmed → EventService ghi SQLite trong transaction → gửi event JSON cho WS và thêm outbox cho từng device active có push endpoint. 

- Outbox worker nạp device endpoint hiện hành, kiểm tra device chưa bị revoke và event chưa quá hạn; FcmSender gọi Firebase Admin SDK bằng credential tại backend. Gọi network ngoài event loop/inference thread; timeout hữu hạn. 

- MVP dùng notification + data. Notification title/body chung; data gồm chuỗi event_id, installation_id, camera_id, confirmed_at, is_test. Android priority high cho cảnh báo nhìn thấy được, TTL khoảng 60 giây, tag = event_id, channel_id theo lựa chọn âm thanh của thiết bị. 

- Foreground: FirebaseMessaging.onMessage đưa event qua AlertCoordinator giống WS. Cùng event_id chỉ hiện banner/phát audio một lần. Không tạo thêm local notification có âm thanh khi banner đã phát alarm. 

- Background/terminated thông thường: Android/FCM SDK hiển thị system notification và phát sound của channel; không cần Dart chạy vòng lặp audio. Khi chạm thông báo, dùng onMessageOpenedApp hoặc getInitialMessage để mở alert [S8, S9]. 

- Sau resume, GET events bù các sự kiện WS bỏ lỡ, nhưng sự kiện cũ chỉ hiện danh sách; không tự hú lại tất cả lịch sử. Chỉ replay sound nếu event còn trong khoảng tươi đã định, chưa seen và người dùng đang ở foreground. 

Đầu ngày 5 phải có một push thử tới điện thoại thật trước khi AI hoàn chỉnh. Điều này phát hiện sớm sai applicationId, thiếu Google Play services, quyền notification, dự án Firebase khác nhau hoặc credential backend không đúng. Không đợi tuần 3 mới biết môi trường FCM không hoạt động. Không dùng service-account JSON trong code Dart, không gọi FCM từ app để gửi sang điện thoại khác. 

```
# Hình dạng lời gọi SDK, cần kiểm tra với phiên bản đã khóa:
message = messaging.Message(
    token=device.push_value,
    notification=messaging.Notification(
        title="Cảnh báo giám sát",
        body="Có sự kiện cần kiểm tra. Mở ứng dụng để xem."
    ),
    data={
        "event_id": event.event_id,
        "installation_id": event.installation_id,
        "camera_id": event.camera_id,
        "schema_version": "1",
        "type": "fall.confirmed",
        "confirmed_at": event.confirmed_at,
        "is_test": str(event.is_test).lower(),
    },
    android=messaging.AndroidConfig(
        priority="high",
        ttl=timedelta(seconds=60),
        notification=messaging.AndroidNotification(
            channel_id="fall_alerts_v1" if device.sound_enabled else
"fall_silent_v1",
            tag=event.event_id,
        ),
    ),
)
message_id = messaging.send(message)
```

Payload FCM là dạng rút gọn và mọi giá trị data đều là chuỗi. FallEvent.fromPushData() chuyển schema_version/is_test từ chuỗi sang kiểu Dart, giữ score/episode/reasons là nullable nếu chưa có; không dùng nguyên parser REST với giả định bool/int đã đúng kiểu. Foreground hiển thị thông điệp chung và phát âm theo event_id ngay, sau đó có thể tìm chi tiết bằng GET /api/v1/events và event_id. Không đợi mạng tải chi tiết xong mới cảnh báo; không cần thêm route detail để MVP chạy. 

API message/token ở đoạn này là contract triển khai cần smoke test với dependency đã khóa. Tài liệu FCM hiện hành có thêm hướng nhận dạng installation/FID và đánh dấu token là đường chuyển tiếp ở một số SDK [S11]; không tự thay getToken() bằng một chuỗi FID chưa đăng ký. Giữ PushEndpoint(kind,value) trong contract; nếu phiên bản SDK chọn FID thì đổi ở adapter notification_service.dart/fcm.py và test cùng ngày, các module AI/event không thay đổi. Chỉ dùng một đường gửi đã xác minh hoạt động cho MVP. 

### 5.3. Chống lặp và retry đúng nghĩa 

Outbox có một bản ghi mỗi (event_id,device_id). Thành công nhận message ID thì state=accepted; không retry bản ghi này chỉ vì chưa thấy app ack. Lỗi endpoint không còn đăng ký thì vô hiệu hóa endpoint và yêu cầu app đăng ký lại khi mở; không xóa thiết bị/khóa ghép. Lỗi tạm thời retry tối đa 3 lần, ví dụ sau 5,15,30 giây nhưng không quá expires_at; lỗi cấu hình credential báo notification unavailable, không retry vô hạn. 

Không thể bảo đảm exactly-once giữa SQLite và FCM: tiến trình có thể mất sau khi FCM nhận nhưng trước khi DB cập nhật. Giữ event_id khi retry, dùng Android tag để thay cùng notification và seen-event store tại app. Không dùng cùng collapse_key cho mọi lần ngã khác nhau vì có thể làm mất sự kiện. Trong khoảng đua foreground→background có thể có OS notification cùng banner; test tình huống này và không hứa chặn được mọi lần âm thanh lặp do hệ điều hành. 

### 5.4. Âm thanh khi mở app và khi app ở nền 

|**Trạng thái**|**Cơ chế**|**Nút tắt và giới hạn**|
|---|---|---|
|App đang mở|AlertCoordinator gọi AlarmService phát<br>asset assets/audio/fall_alarm.wav, vòng<br>ngắn tối đa 10 s; hiển thị banner/alert<br>screen.|Nút Tắt âm thanh dừng player ngay; Đã<br>xem cũng dừng. Không tự tăng âm lượng<br>máy.|
|App chạy nền/khóa<br>màn hình|System notification dùng channel<br>fall_alerts_v1, sound từ<br>res/raw/fall_alarm.wav.|Âm báo ngắn do OS; chạm mở app hoặc<br>xóa notification. Không chạy vòng hú Dart<br>vô hạn ở nền.|
|Người dùng tắt âm<br>thông báo|Backend chọn channel fall_silent_v1 sau khi<br>app cập nhật sound_enabled; foreground<br>cũng không gọi player.|Tạo cả hai channel từ đầu; không sửa<br>sound của channel cũ vì Android không<br>cho đổi hành vi đó tùy ý [S12].|
|Quyền notification<br>bị từ chối|UI vẫn hiện trạng thái từ API/WS khi app<br>mở; hướng dẫn mở Settings.|Không coi WS là phương án nhận push<br>khi đã đóng app. Đánh dấu push chưa<br>sẵn sàng.|
|Force-stop trong<br>Settings|Không hứa nhận message cho tới khi mở<br>app lại [S9].|Đưa vào test giới hạn, không đánh đồng<br>với minimize hay process bị OS thu hồi.|



|**Trạng thái**|**Cơ chế**|**Nút tắt và giới hạn**|
|---|---|---|
|Máy im lặng/DND,<br>tiết kiệm pin, offline|Hệ điều hành/nhà sản xuất có thể chặn<br>hoặc trì hoãn sound/push.|Không xin quyền đặc biệt để ép vượt<br>DND trong P0; kiểm tra trạng thái và trình<br>bày giới hạn thật.|



Copy cùng một âm 2–3 giây do nhóm có quyền dùng vào hai đường dẫn: Flutter asset cho foreground và Android raw resource cho sound notification. Tên raw phải chữ thường/gạch dưới, không dấu. pubspec.yaml khai báo asset; notification_service.dart tạo channel dùng RawResourceAndroidNotificationSound("fall_alarm"). AndroidManifest.xml có POST_NOTIFICATIONS và metadata channel mặc định; xin quyền runtime trên Android 13+ [S8]. Giữ raw/icon trong cấu hình shrink resource khi build release; debug APK vẫn phải test âm thật. 

### 5.5. WebSocket và video được dùng đúng chỗ 

ws_client.dart dùng Authorization header trên kết nối Android, ping/timeout, exponential backoff có trần 15 giây; ngừng reconnect khi app unpair. Socket chỉ mang event nhỏ và status; JPEG qua stream.mjpeg riêng. Khi app chuyển nền, không cố giữ socket bằng foreground service. App mở lại lấy status/events rồi mới bật stream. camera_view.dart tắt đọc MJPEG khi màn hình không hiển thị để tiết kiệm mạng nhưng backend vẫn theo dõi. 

Mjpeg widget truyền header Bearer đã ghép, isLive=true khi app foreground. Nếu package hiện hành không hợp với Flutter SDK, P0 dùng snapshot JPEG 1 FPS từ cùng cache qua route GET /api/v1/preview.jpg có xác thực; đó là xem hình cập nhật chậm, không gọi là live 30 FPS. Backend bổ sung route này trong cùng api/stream.py, không đổi RTSP/AI. Chức năng cảnh báo phải chạy kể cả người dùng không mở khung xem video. 

## 6. Phân công chi tiết theo tuần và sinh viên 

Mỗi khối A–I là một gói công việc có thể kiểm chứng. E lấy trực tiếp từ danh mục chuẩn để đường dẫn, chủ sở hữu và tuần không bị lệch. Những file tồn tại từ trước chỉ được chỉnh để phục vụ mục tiêu tuần hiện tại; không viết lại toàn bộ module. Tên hàm là contract dự kiến để sinh viên bắt đầu code, có thể thêm helper nội bộ nhưng không tự đổi API đã bàn giao. 

### 6.0. Bốn mốc tăng chức năng của hệ thống 

|**Cuối tuần**|**Người dùng làm được gì?**|**Tích hợp bắt buộc**|**Điều kiện chuyển tuần**|
|---|---|---|---|
|1 — nền<br>tảng|Ghép điện thoại, xem trạng thái<br>backend/camera; thấy pose khi<br>chạy clip riêng; nhận push thử.|RTSP hoặc RTSP phát từ<br>video<br>backend; AI stub<br>→<br>→<br>WS<br>app; Firebase sender<br>→<br>máy thật.<br>→|Không chỉ có môi trường;<br>ngày 5 thao tác thật được.<br>Nếu camera chưa có, RTSP<br>giả lập phải chạy.|
|2 — nhận<br>diện|Xem hình camera; app hiện<br>trạng thái nghi ngã từ AI thật; B<br>chạy, A có train/validation tối<br>thiểu nếu dữ liệu đạt.|Pose/feature/state machine →<br>backend update → app; đổi<br>B/A qua cùng interface.|Ngày 10 chọn model MVP<br>theo validation/latency; giữ<br>B nếu A chưa đáng tin.|



|**Cuối tuần**|**Người dùng làm được gì?**|**Tích hợp bắt buộc**|**Điều kiện chuyển tuần**|
|---|---|---|---|
|3 — cảnh<br>báo|Nhận event có ID, push<br>nền/khóa màn hình, âm thanh<br>và nút tắt/ack; nằm lâu không<br>hú liên tục.|RTSP<br>AI<br>event store<br>→<br>→<br>→<br>WS+FCM→<br>coordinator/audio.|Ngày 15 có end-to-end thật<br>trên Android; gửi thử không<br>thay cho ngã trong video.|
|4 — ổn định|Cài APK, nhập RTSP thật, mất<br>mạng rồi tự hồi phục; nhận<br>cảnh báo theo phạm vi nền<br>tảng đã thử.|Sửa lỗi theo checklist; đo FPS,<br>latency và FP/FN; gói<br>model/config đã chọn.|Ngày 20 chạy lại từ startup<br>sạch và đạt P0; nêu rõ giới<br>hạn đo được.|



### 6.1.1. Tuần 1 — SV1: Pose chạy được và dữ liệu có cấu trúc 

#### A. Mục tiêu của tuần 

Trong 20 giờ tạo được detector interface, output mock, smoke script pose/video và manifest dữ liệu đầu tiên. Mục tiêu AI B là thấy được người/khớp trên clip; mục tiêu A là có mẫu dữ liệu trích xuất đúng và split theo nhóm, chưa bắt buộc có model ngã đã train. Dành khoảng 8 giờ cho pose/interface, 6 giờ dữ liệu/nhãn, 4 giờ extraction và 2 giờ bàn giao/test. 

#### B. Kiến thức cần học 

- Học trước: numpy array có shape H×W×3, dtype uint8; đọc video bằng cv2.VideoCapture, ret/frame/isOpened/release, resize giữ tỉ lệ; hiểu tọa độ ảnh x sang phải, y hướng xuống. Đạt mức tự đọc một clip và xử lý hết video không crash. 

- Học pose estimation và COCO-17: bounding box khác keypoint; confidence khác nhãn ngã; người bị che có thể thiếu khớp. Đạt mức lấy và vẽ vai/hông trên một frame, kiểm tra boxes.id trước khi dùng. 

- Học vòng lặp inference và track theo chuỗi: load model ngoài vòng for, persist=True cho các frame cùng video, reset khi đổi video. Không cần học sâu backbone YOLO hoặc tự cài ByteTrack trong tuần 1. 

- Học dataset ở mức clip/sequence, nhãn thời gian onset–impact, group split và leakage. Hiểu vì sao hai frame liền nhau không được rải ngẫu nhiên vào train và test. 

#### C. Áp dụng trực tiếp vào project 

Frame từ VideoCapture/RTSP của SV2 sẽ có cùng contract FramePacket. PoseEstimator nhận ảnh và trả khớp; PoseBuffer giữ lịch sử nhưng chưa kết luận ngã. MockDetector cho SV2 giả lập output để ghép API trước khi model xong. Manifest/nhãn/cached pose là đầu vào nhánh A ở tuần 2; SV3 chỉ nhận JSON minh họa, không phải nhận tensor. 

#### D. Công việc lập trình cụ thể 

- T1. Khóa dataclass và Protocol trước: viết 2–3 ví dụ DetectionUpdate, gồm không có người, một người và pose invalid. Nhờ SV2 chạy parser/import. Chỉ chuyển tiếp khi SV2 gọi được MockDetector.process(packet) mà không biết chi tiết model. 

- T2. Tải weights chính thức, tạo PoseEstimator với device CPU mặc định. Viết ai_smoke đọc 30–60 giây video, vẽ box/khớp, đếm frame_id và in thời gian trung bình. Chỉ chuyển tiếp khi một model được load một lần và clip chạy hết. 

- T3. Tải thử vài sequence RGB camera0 của URFD, mở xem tên file/thứ tự frame và nhãn nguồn. Tạo clips.csv với group/subject unknown nếu chưa xác minh; đặt 

train/val/test theo group trước khi trích hàng nghìn cửa sổ. Không chuyển sang full extraction khi chưa hiểu timestamp/FPS. 

- T4. Gán onset/impact/end cho ít nhất vài clip ngã và đánh dấu ADL/hard negative. Tạo extract.py trích một clip ra .npz, kiểm shape/timestamp/validity. Chạy nền phần còn lại nếu pilot tốt; không để việc tải dataset chặn việc giao baseline pose. 

- T5. Cuối ngày 5 bàn giao model path, contract, lệnh smoke và một cache mẫu cho SV2; cùng chạy backend với mock và pose độc lập. Các file checkpoint nhánh A chỉ tạo sau khi train thật, không tạo placeholder giả giống weights. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `configs/ai.yaml` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Model, cửa sổ và ngưỡng luật/xác nhận. Thành phần chính: mode; sample_hz; thresholds. I/O: YAML → detector/state machine config. Được dùng bởi/tại: backend/ai/factory.py; state_machine.py. Kiểm chứng: A/B đổi bằng config; không hardcode ngưỡng. 

**File:** `configs/train.yaml` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Seed, split, batch và siêu tham số train. Thành phần chính: seed; epochs; learning_rate. I/O: Cấu hình → dataset/train/evaluate. Được dùng bởi/tại: training/train.py. Kiểm chứng: Seed/split/feature_version được khóa cùng checkpoint. 

**File:** `backend/contracts.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: FramePacket, candidate/update và DTO event. Thành phần chính: FramePacket; FallCandidate; DetectionUpdate. I/O: Numpy nội bộ → DTO tách riêng cho network. Được dùng bởi/tại: AI, pipeline, API. Kiểm chứng: SV2 parse được output mock cùng schema_version. 

**File:** `backend/ai/interface.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Protocol detector và scorer thay thế được. Thành phần chính: FallDetector; SequenceScorer. I/O: Frame/window → DetectionUpdate/score. Được dùng bởi/tại: factory, mock, pretrained, trained. Kiểm chứng: Mock/B/A cùng interface; backend không import TCN trực tiếp. 

**File:** `backend/ai/mock.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Output giả có nhãn is_test ở nguồn phát triển. Thành phần chính: MockDetector.process/reset/close. I/O: Chuỗi fixture → candidate/status xác định. Được dùng bởi/tại: factory; test tích hợp T1. Kiểm chứng: Không bật mock trong nghiệm thu AI thật. 

**File:** `backend/ai/pose.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Load pose một lần, box/keypoint và track ID. Thành phần chính: PoseEstimator.estimate/reset/close. I/O: Frame BGR → tracked poses COCO17. Được dùng bởi/tại: pretrained và trained adapters. Kiểm chứng: Không có người/ID/khớp thiếu không crash. 

**File:** `backend/ai/buffer.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Cửa sổ theo track/session có timestamp. Thành phần chính: PoseBuffer.add/window/reset. I/O: Pose + time → 30 mốc/quality. Được dùng bởi/tại: Cả hai detector và feature extractor. Kiểm chứng: Không nối qua gap; không đếm trùng frame_id. 

**File:** `backend/ai/factory.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Tạo mock/B/A theo config. Thành phần chính: create_detector(settings). I/O: Config/model path → FallDetector. Được dùng bởi/tại: backend/main.py. Kiểm chứng: Không load model mỗi request; báo lỗi rõ. 

**File:** `training/manifest.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Lập danh sách clip, nguồn và group chống leakage. Thành phần chính: build_manifest; validate_groups. I/O: RGB sequences/clip metadata → clips.csv. Được dùng bởi/tại: extract; split generation. Kiểm chứng: Một clip/2 góc cùng sự kiện chung group. 

**File:** `data/manifests/clips.csv` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Manifest dữ liệu nguồn có provenance. Thành phần chính: 

clip_id,path,group_id,subject_id,camera_id,fps. I/O: Metadata clip → loader/split. Được dùng 

bởi/tại: manifest.py; extract.py. Kiểm chứng: FPS/nhóm có giá trị xác minh; unknown được ghi rõ. 

**File:** `data/labels/intervals.csv` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Nhãn onset/impact/end và hard negative. Thành phần chính: clip_id,onset_s,impact_s,end_s,label. I/O: Quan sát video → interval đã soát. Được dùng bởi/tại: training/extract; evaluate. Kiểm chứng: Không gắn mọi frame clip ngã là positive. 

**File:** `data/splits.json` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Train/val/test theo group và seed. Thành phần chính: train_groups; val_groups; test_groups. I/O: Manifest → split độc lập recording. Được dùng bởi/tại: dataset; train; evaluate. Kiểm chứng: Group giao nhau rỗng, khóa trước tuning. 

**File:** `training/extract.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Trích pose/features đúng timestamp. Thành phần chính: extract_clip; save_features. I/O: RGB/MP4 + labels → .npz có timestamps. Được dùng bởi/tại: PoseEstimator; normalize_window. Kiểm chứng: Có thể resume; không tải lại model mỗi clip. 

**File:** `data/features/*.npz` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Cache sinh tự động cho từng clip. Thành phần chính: features,timestamps,validity,labels. I/O: Clip + pose → numpy arrays. Được dùng bởi/tại: training/dataset.py. Kiểm chứng: Shape/thời gian khớp; không commit data lớn. 

**File:** `scripts/ai_smoke.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Chạy 1 clip độc lập để thấy pose/status. Thành phần chính: main --source --mode. I/O: Video/camera → preview/terminal counters. Được dùng bởi/tại: Detector interface. Kiểm chứng: Không cần backend/app để debug AI. 

**File:** `models/yolo11n-pose.pt` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Weights pose tải từ nguồn chính thức. Thành phần chính: Binary model, không tự viết code. I/O: Frame → pretrained pose. Được dùng bởi/tại: PoseEstimator. Kiểm chứng: Ghi nguồn/hash, load được offline sau tải. 

**File:** `evaluation/cases.csv` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Danh sách ca test có ground truth/tập dữ liệu. Thành phần chính: case_id,clip_id,split,expected,interval. I/O: Video kiểm chứng → test cases. Được dùng bởi/tại: training/evaluate; cả nhóm. Kiểm chứng: Có ngã, ADL, nằm sẵn, che khuất; không dùng test tuning. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 1 học ảnh và chạy pose; ngày 2 chốt interface/mock với SV2; ngày 3 xác minh dataset/nhãn/split; ngày 4 pilot extraction; ngày 5 test và bàn giao. Trong khi mạng tải dataset, tiếp tục T2/T1. Nếu downloader lỗi, dùng một clip nhóm tự quay an toàn để kiểm pipeline, đồng thời đánh dấu nhánh A chưa đủ dữ liệu; không gọi đó là validation độc lập. 

#### G. Kiểm thử sau khi hoàn thành 

- Chạy python scripts/ai_smoke.py --source <video> --mode pose: có box/khớp đúng người, hiển thị empty khi không có người, hết file giải phóng capture. Test một frame toàn đen và một người bị crop để xác nhận code không dùng khớp 0,0 như dữ liệu thật. 

- Dùng clip 10 giây: timestamp tăng theo thời gian nguồn, không theo tốc độ xử lý; reset video mới làm buffer rỗng. Kiểm tra clips.csv không có hai dòng trùng clip_id và group_id giao nhau giữa các split bằng assert. 

- Chạy mock với cùng packet hai lần: SV2 đọc đủ trường, schema_version=1, không có ndarray trong JSON. Mock phải được đánh dấu chế độ thử để không lẫn vào test cuối. 

#### H. Deliverables và thao tác demo 

Có file pose/interface/mock/buffer/factory cơ bản, ai_smoke chạy được, weights pose tải được, manifest/split/nhãn mẫu/cache pilot. Người dùng xem được người và khớp trong cửa sổ smoke; app qua backend nhận event/status giả có cấu trúc. Demo: mở clip có/không có người, đổi clip, rồi đưa mock vào pipeline của SV2. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi ba ví dụ contract đều chạy, pose đọc clip hết không crash, có ít nhất một cache đúng schema và split không trùng group. Nếu dataset chưa tải được cuối ngày 3, giữ nhánh B là P0 và giới hạn A ở pilot dữ liệu đến ngày 5; tiếp tục tìm nguồn hợp lệ trong giờ đã dành, không lấy tuần 3 làm tuần cài môi trường. Không tự nhận model phát hiện ngã chỉ vì skeleton đã vẽ được. 

### 6.1.2. Tuần 1 — SV2: Backend, RTSP và ghép thiết bị chạy từ điện thoại 

#### A. Mục tiêu của tuần 

Trong 20 giờ có FastAPI một worker, camera reader/last-frame, health/status/WS, SQLite tối thiểu và pairing không tài khoản; FCM sender smoke. Dành 6 giờ backend/contract, 6 giờ RTSP, 5 giờ pairing/storage và 3 giờ push/test. Endpoint event thật và outbox chưa là mục tiêu tuần này. 

#### B. Kiến thức cần học 

- Học HTTP method/status, JSON/Pydantic, FastAPI route và lifespan; phân biệt def với async def. Đạt mức viết GET status trả enum và khởi động/dừng worker qua lifespan. Không cần học ORM, Kubernetes hoặc microservices. 

- Học thread, threading.Event, Lock, queue dung lượng 1; không share VideoCapture và không chạy read trong event loop. Hiểu read/open có thể block và timeout cần truyền lúc mở với FFmpeg backend. 

- Học RTSP URL, TCP/UDP, IP LAN, port, localhost của từng máy. Đạt mức kiểm tra một RTSP stream bằng công cụ độc lập rồi đọc bằng OpenCV. 

- Học sqlite transaction, SHA-256 cho secret ngẫu nhiên, secrets.token_urlsafe và expiry; đây là xác thực thiết bị, không phải quản lý tài khoản. Học tối thiểu Firebase Admin để gửi test tới đúng endpoint do SV3 cung cấp. 

#### C. Áp dụng trực tiếp vào project 

reader.py cung cấp FramePacket cho interface SV1; latest.py cho cả AI và preview xem cùng ảnh mà không tranh lấy queue. routes/ws chuyển status hoặc mock event cho SV3. pairing/auth cấp và kiểm device context. fcm.py kiểm đường cloud độc lập từ script; chưa nối AI vào FCM nên lỗi mobile không làm chậm pose. 

#### D. Công việc lập trình cụ thể 

- T1. Tạo repository/cấu hình/runtime DB và backend/main.py; thêm /health và /api/v1/status. Lifespan dựng worker một lần và shutdown đúng. Đưa ví dụ JSON/schema cho SV3 ngay khi route trả được. 

- T2. Nhận FramePacket/MockDetector từ SV1, tạo Pipeline với nguồn video trước; thêm CameraReader RTSP và status. Chạy capture thread, latest buffer, stop_event, đọc lỗi rồi reconnect có backoff. Chỉ chuyển tiếp khi /health vẫn phản hồi lúc URL RTSP sai. 

- T3. Chưa có camera thì chạy MediaMTX, FFmpeg phát MP4 bằng -re; verify backend thật sự nhận rtsp://. Viết test fake capture để kiểm read thất bại và session reset mà không phải rút camera trong mọi lần chạy pytest. 

- T4. Tạo schema installation/pairing/devices; CLI sinh link; claim nguyên tử và auth cho status/WS. Để SV3 pair qua IP LAN, kiểm tra cùng code claim lại thất bại. Không dùng một secret cố định chung cho cả nhóm. 

- T5. Tạo WS hub phát status/mock schema; tạo FcmSender.send_test và test_push.py. Khi SV3 gửi endpoint từ đúng Firebase project, thử notification thật đến máy. Ghi bộ dependency đã chạy vào lock sau khi smoke thành công. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `pyproject.toml` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Khai báo package Python và dải Python 3.11. Thành phần chính: project; tool.pytest.ini_options. I/O: Không có hàm; đầu vào metadata, đầu ra môi trường cài được. Được dùng bởi/tại: pip và pytest. Kiểm chứng: Import backend/training từ root ổn định. 

**File:** `requirements.lock.txt` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Khóa dependency sau smoke test. Thành phần chính: pip freeze/pip install -r. I/O: Bộ package đã kiểm tra → phiên bản chính xác. Được dùng bởi/tại: Mọi laptop backend/AI. Kiểm chứng: Cài lại trên môi trường sạch, import được. 

**File:** `.env.example` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Tên biến cấu hình và placeholder không bí mật. Thành phần chính: GOOGLE_APPLICATION_CREDENTIALS; APP_ENV. I/O: Ví dụ env → config loader. Được dùng bởi/tại: backend/config.py. Kiểm chứng: Không có credential thật trong repo. 

**File:** `.gitignore` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Loại secret, runtime, data lớn và build khỏi git. Thành phần chính: Các pattern. I/O: Đường dẫn nhạy cảm → bỏ theo dõi git. Được dùng bởi/tại: Repository. Kiểm chứng: .env, credential JSON, runtime DB không được commit. 

**File:** `README.md` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Lệnh cài/chạy và thao tác vận hành MVP. Thành phần chính: Các lệnh backend/pairing/Flutter. I/O: Máy mới → chạy demo; không có báo cáo học phần. Được dùng bởi/tại: Cả nhóm và người chạy thử. Kiểm chứng: Có lệnh smoke và giới hạn bản chạy đúng thực tế. 

**File:** `configs/app.yaml` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Timeout, camera, rate preview, runtime DB. Thành phần chính: Config keys tại Chương 2. I/O: YAML/env → AppSettings. Được dùng bởi/tại: backend/config.py. Kiểm chứng: Giá trị lỗi bị báo lúc startup. 

**File:** `deploy/mediamtx.yml` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: RTSP server phục vụ video thử nội bộ. Thành phần chính: paths.fall_demo. I/O: Publisher FFmpeg → RTSP endpoint. Được dùng bởi/tại: MediaMTX độc lập. Kiểm chứng: Backend đọc được cùng stream bằng RTSP. 

**File:** `backend/main.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Tạo FastAPI app và lifecycle worker. Thành phần chính: create_app(); lifespan(). I/O: Settings → app; 

startup/shutdown worker. Được dùng bởi/tại: Uvicorn. Kiểm chứng: Một worker, start/stop không nhân đôi camera. 

**File:** `backend/config.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Nạp và kiểm tra config. Thành phần chính: AppSettings; load_settings(). I/O: YAML + env → settings typed. Được dùng bởi/tại: main, reader, pipeline. Kiểm chứng: Thiếu model/credential trả trạng thái rõ ràng. 

**File:** `backend/camera/reader.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Đọc RTSP/video/webcam, reconnect theo phiên. Thành phần chính: CameraReader.start/read_latest/stop; _capture_loop. I/O: Nguồn video → FramePacket/status. Được dùng bởi/tại: backend/pipeline.py. Kiểm chứng: Sai URL không treo API; tự nối lại; release đúng thread. 

**File:** `backend/camera/latest.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Bộ đệm frame/JPEG mới nhất dung lượng hữu hạn. Thành phần chính: LatestValue.replace/wait_newer/get. I/O: Frame mới → snapshot thread-safe. Được dùng bởi/tại: reader, pipeline, api/stream.py. Kiểm chứng: Không tích lũy frame; viewer không lấy mất frame AI. 

**File:** `backend/pipeline.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Ghép capture, detector, state machine và event service. Thành phần chính: Pipeline.start/stop; _infer_loop. I/O: FramePacket → status/transition/cache. Được dùng bởi/tại: main; routes; stream. Kiểm chứng: Inference không chặn API; reset khi đổi session. 

**File:** `backend/api/routes.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Health/status/camera/events/ack/test endpoint. Thành phần chính: health; get_status; set_camera; ack_event. I/O: HTTP DTO và device context → JSON. Được dùng bởi/tại: main; storage; pipeline. Kiểm chứng: Response/HTTP code khớp contract; có auth. 

**File:** `backend/api/ws.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Handshake có khóa và fanout event/status. Thành phần chính: ConnectionHub.connect/broadcast/disconnect. I/O: Event JSON → đúng kết nối installation. Được dùng bởi/tại: main; EventService. Kiểm chứng: Reconnect được; không lộ event cho khóa sai. 

**File:** `backend/storage.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: SQLite giao dịch cho device/config/events/outbox. Thành phần chính: open_db; claim_code; save_event_once; list_events. I/O: Record typed → SQLite → record. Được dùng bởi/tại: pairing, auth, routes, EventService. Kiểm chứng: Transaction ngắn; không dùng connection sai thread. 

**File:** `backend/schema.sql` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Bảng/unique index và phiên bản schema. Thành phần chính: CREATE TABLE/INDEX. I/O: DDL → installation/pairing/devices; thêm events/outbox T3. Được dùng bởi/tại: backend/storage.py. Kiểm chứng: Khởi động lại không mất pairing; event/episode unique. 

**File:** `backend/pairing.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: CLI sinh/thu hồi và claim code một lần. Thành phần chính: create_pairing; claim_pairing; revoke_device; main. I/O: Code 256 bit → device secret/installation. Được dùng bởi/tại: CLI; api/routes.py. Kiểm chứng: TTL và concurrent claim đúng; không cần tài khoản. 

**File:** `backend/auth.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Xác thực hash device secret và scope installation. Thành phần chính: require_device; verify_device_secret. I/O: Bearer secret → DeviceContext/401. Được dùng bởi/tại: Mọi route và WS/stream nhạy cảm. Kiểm chứng: Khóa sai/revoke không xem được ảnh/event. 

**File:** `backend/alerts/fcm.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Sender FCM: smoke T1, adapter đầy đủ T3. Thành phần chính: FcmSender.send_test/send_fall. I/O: PushEndpoint + event → provider message ID/error. Được dùng bởi/tại: scripts/test_push.py; outbox. Kiểm chứng: Accepted phân biệt delivered; secret chỉ backend. 

**File:** `scripts/publish_rtsp.sh` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Lệnh FFmpeg phát MP4 vào MediaMTX. Thành phần chính: ffmpeg -re -stream_loop -1. I/O: MP4 H.264 → RTSP server. Được dùng bởi/tại: Môi trường test RTSP. Kiểm chứng: Dùng realtime pacing, backend thực sự đọc rtsp://. 

**File:** `scripts/test_push.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Thử FCM riêng, không giả kết quả AI. Thành phần chính: main --device-id. I/O: Device DB/test payload → FCM accepted/error. Được dùng bởi/tại: FcmSender. Kiểm chứng: Điện thoại nhận test message, không cần pose. 

**File:** `tests/test_camera.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Test timeout/reconnect bằng fake capture. Thành phần chính: test_read_failure; test_new_session. I/O: Capture fake và clock → state/frame. Được dùng bởi/tại: pytest; CameraReader. Kiểm chứng: Không chờ camera thật trong unit test. 

**File:** `tests/test_pairing.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: TTL, claim hai lần và revoke. Thành phần chính: test_expired; test_concurrent_claim; test_revoke. I/O: Temp SQLite/code → HTTP/DB result. Được dùng bởi/tại: pytest; pairing/auth. Kiểm chứng: Code chỉ claim một lần, route ảnh/WS khóa sai bị chặn. 

**File:** `runtime/fallguard.db` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Dữ liệu runtime do schema/storage sinh. Thành phần chính: SQLite database, không viết tay. I/O: Installation/device/config/event/outbox → persistence. Được dùng bởi/tại: storage.py và pairing CLI. Kiểm chứng: Restart giữ pairing; file không commit, không chứa tài khoản. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

T1 chạy trước; T2 làm song song với SV1 bằng mock; T3 sau reader; T4 pair contract phải gửi SV3 ngày 2, có thể dùng claim stub trong vài giờ rồi thay SQLite trước nghiệm thu ngày 5; T5 phối hợp SV3 cuối tuần. Không yêu cầu AI A/B đã xong mới tạo API/WS. Việc tạo project Firebase và credentials do SV2/SV3 phối hợp từ ngày 3. 

#### G. Kiểm thử sau khi hoàn thành 

- GET /health luôn trả 200 khi camera không có; status cho biết camera ERROR/RECONNECTING thay vì backend “ok” chung chung. Thử rtsp://khong-tontai/stream và URL thiếu host; lỗi cú pháp 422, lỗi kết nối không treo server. 

- Chạy RTSP 5 phút, ngắt publisher 10 giây rồi mở lại: reader chuyển trạng thái và tự nối, stream_session_id đổi, frame_id không lặp trong một session. Ngắt server phải release tài nguyên, không để lần chạy sau báo camera đang bận. 

- Claim đúng link → có khóa; claim lại/expired → từ chối; khóa sai không truy cập status/WS. Điện thoại trong cùng Wi-Fi nhận WS mock; endpoint của máy khác không được dùng cho push test của device này. 

#### H. Deliverables và thao tác demo 

Backend thực sự chạy từ terminal; có RTSP stream hoặc RTSP giả lập đang đọc; app dùng được health/status, pairing, WS mock. Một push thử đã tới Android thật. Demo ngày 5: khởi động backend, sinh link, dán trên điện thoại, bật/tắt publisher và gửi thử thông báo. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi điện thoại pair được, khóa sai bị chặn, RTSP đọc ít nhất một phiên và push test có bằng chứng trên máy. Nếu camera thật chưa sẵn sàng, giữ MediaMTX; nếu FCM lỗi, dành tối đa phần đệm ngày 5 để xác định project/permission/Google services, ghi blocked rõ và sửa đầu ngày 6. Không hạ yêu cầu push thành WS, không bỏ auth để vượt lỗi kết nối. 

### 6.1.3. Tuần 1 — SV3: App Android kết nối thật, ghép và nhận push thử 

#### A. Mục tiêu của tuần 

Trong 20 giờ tạo app có màn hình ghép và home, kết nối health/status/WS, secure storage, Firebase setup và channel/quyền cơ bản. Dành khoảng 5 giờ Dart/Flutter/môi trường, 6 giờ UI+HTTP, 4 giờ pairing/storage, 3 giờ FCM và 2 giờ kiểm thử. Chưa làm UI phức tạp, animation hoặc nhiều màn hình. 

#### B. Kiến thức cần học 

- Học Dart nullable types, Future/async-await, Map JSON, class.fromJson; Flutter widget tree, State, setState, dispose. Đạt mức một form có loading/error/success và không setState sau dispose. 

- Học HTTP timeout/header/Bearer, URL parse và response code; IP LAN khác localhost; Android không tự cho cleartext HTTP ở mọi bản build. Chỉ mở HTTP tại debug manifest để demo LAN. 

- Học secure storage và vòng đời app resumed/paused; WS stream subscription phải hủy khi dispose để tránh nhân đôi listener. Chưa cần kiến trúc state management nhiều tầng. 

- Học FCM client initialization, permission Android 13+, token/endpoint, channel, foreground/background. Hiểu có Firebase project không có nghĩa app cần người dùng đăng nhập Firebase. 

#### C. Áp dụng trực tiếp vào project 

ApiClient ghép link do SV2 tạo; DeviceStore lưu device_secret/installation_id; WsClient nhận status/mock event. NotificationService khởi tạo Firebase và xin quyền để thử push, độc lập với AI của SV1. Home dùng snapshot status giả trong lúc SV2 làm route nhưng parser vẫn theo contract đã chốt. 

#### D. Công việc lập trình cụ thể 

- T1. Chạy Flutter counter app trên điện thoại thật trước, sau đó sửa main để route sang PairScreen khi chưa có pairing. Tạo config parser nhận server URL và reject link thiếu code. Chỉ làm UI khi build/deploy máy thật đã chạy. 

- T2. Viết models.fromJson và ApiClient có timeout, bắt lỗi SocketException/401/422. Dùng fixture cho trạng thái CONNECTING/READY/ERROR, tạo HomeScreen đơn giản hiển thị từng trạng thái riêng. 

- T3. Dán pairing link và gọi claim; chỉ lưu khóa sau response thành công, mở home; restart app vẫn kết nối bằng khóa đã lưu. Nếu claim timeout không biết server đã tiêu thụ code chưa, báo sinh link mới, không retry liên tục cùng code. 

- T4. Thêm WsClient có header và 1 subscription; show mock alert dạng text có nhãn thử. Ngắt Wi-Fi/đóng màn hình thì không crash, resume lấy status lại. Chưa cần camera view trong tuần 1. 

- T5. Đăng ký Firebase Android đúng applicationId, chạy FlutterFire configure; tạo channel và xin POST_NOTIFICATIONS; lấy endpoint bằng API SDK đã chọn rồi gửi SV2 qua cập nhật device hoặc lệnh thử. Nhận notification thử lúc app mở và thu nhỏ; chưa làm alarm loop. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `mobile/pubspec.yaml` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Dependency Flutter và asset audio. Thành phần chính: dependencies; flutter.assets. I/O: Package constraints → Flutter build. Được dùng bởi/tại: flutter pub get. Kiểm chứng: Một bộ package tương thích, asset tìm được. 

**File:** `mobile/pubspec.lock` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Khóa phiên bản package app. Thành phần chính: Generated lock. I/O: pubspec → resolved versions. Được dùng bởi/tại: Flutter SDK. Kiểm chứng: Máy thứ hai pub get ra cùng bộ dependency. 

**File:** `mobile/lib/main.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Khởi tạo app/Firebase/services và lifecycle. Thành phần chính: main; FallGuardApp. I/O: DeviceStore → pair/home; resume sync. Được dùng bởi/tại: Flutter entry point. Kiểm chứng: Mở app không cần tài khoản; không init FCM hai lần. 

**File:** `mobile/lib/config.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Quy ước timeout/schema/base URL đã parse. Thành phần chính: AppConfig; parseServerUri. I/O: Pairing URI → validated URL. Được dùng bởi/tại: ApiClient; WsClient. Kiểm chứng: Reject scheme/host thiếu; không hardcode localhost. 

**File:** `mobile/lib/models.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Parser status/event/pairing có kiểm trường. Thành phần chính: SystemStatus.fromJson; FallEvent.fromJson/fromPushData. I/O: JSON REST/WS/FCM → Dart models. Được dùng bởi/tại: Screens; coordinator. Kiểm chứng: Sai schema/optional field không crash UI. 

**File:** `mobile/lib/services/api_client.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: HTTP header, timeout và đồng bộ event. Thành phần chính: getStatus; pair; configureCamera; listEvents; ack. I/O: DTO/device secret → response typed. Được dùng bởi/tại: Home/Pair/Alert screens. Kiểm chứng: 401 chuyển trạng thái cần ghép; không tự retry claim bừa. 

**File:** `mobile/lib/services/device_store.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Lưu khóa và installation trong secure storage. Thành phần chính: savePairing; loadPairing; clearPairing. I/O: Claim result → storage an toàn. Được dùng bởi/tại: main; ApiClient; NotificationService. Kiểm chứng: Restart còn ghép; unpair xóa sạch khóa/cursor. 

**File:** `mobile/lib/services/ws_client.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: WS có auth và backoff theo lifecycle. Thành phần chính: connect; events; reconnect; dispose. I/O: Base URL/secret → event stream. Được dùng bởi/tại: Home; AlertCoordinator. Kiểm chứng: Không tạo socket trùng sau resume; retry có trần. 

**File:** `mobile/lib/services/notification_service.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: FCM setup, permission, channel và token refresh. Thành phần chính: initialize; registerEndpoint; onMessage; onOpen. I/O: RemoteMessage/token → coordinator/API. Được dùng bởi/tại: main; AlertCoordinator. Kiểm chứng: Foreground/background/terminated thường nhận đúng, không nhận nhầm installation. 

**File:** `mobile/lib/screens/pair_screen.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Dán link và claim không tài khoản. Thành phần chính: PairScreen; submitPairing. I/O: Pairing link → DeviceStore/home. Được dùng bởi/tại: main; ApiClient. Kiểm chứng: Hết hạn/sai server có lỗi dễ hiểu. 

**File:** `mobile/lib/screens/home_screen.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: RTSP form, status, camera, setting và thử push. Thành phần chính: HomeScreen; refresh; 

configureCamera. I/O: Status/camera config → UI. Được dùng bởi/tại: ApiClient; WsClient; CameraView. Kiểm chứng: Phân biệt camera connected và AI ready; password che mặc định. 

**File:** `mobile/lib/firebase_options.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Cấu hình Firebase sinh bởi FlutterFire. Thành phần chính: DefaultFirebaseOptions.currentPlatform. I/O: Firebase app config → initializeApp. Được dùng bởi/tại: main; notification service. Kiểm chứng: Đúng project/applicationId của APK. 

**File:** `mobile/android/app/google-services.json` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Config client Android do Firebase cung cấp. Thành phần chính: Generated config, không phải admin key. I/O: Android applicationId → SDK setup. Được dùng bởi/tại: Gradle Google services plugin. Kiểm chứng: Không nhầm file service account. 

**File:** `mobile/android/app/build.gradle.kts` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Android SDK/plugin/applicationId. Thành phần chính: android; plugins; buildTypes. I/O: Flutter/Android deps → APK. Được dùng bởi/tại: flutter build/run. Kiểm chứng: Không thay applicationId sau cấu hình FCM. 

**File:** `mobile/android/app/src/main/AndroidManifest.xml` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Internet, notification permission và metadata. Thành phần chính: INTERNET; POST_NOTIFICATIONS; default channel/icon. I/O: Manifest → Android runtime permissions. Được dùng bởi/tại: APK/FCM SDK. Kiểm chứng: Quyền runtime được xin; default channel tồn tại. 

**File:** `mobile/android/app/src/debug/AndroidManifest.xml` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Cho HTTP nội bộ chỉ trong APK debug. Thành phần chính: usesCleartextTraffic. I/O: Debug build config → HTTP LAN. Được dùng bởi/tại: Android debug build. Kiểm chứng: Release không vô tình mở cleartext toàn cục. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 1 build máy thật và Dart cơ bản; ngày 2 parser/API mock; ngày 3 parse link/storage bằng fixture và Firebase config; ngày 4 pair thật với SV2 rồi nối WS/lifecycle; ngày 5 push test. Nếu backend chưa mở cổng, tiếp tục UI bằng fixture nhưng phải ghép API thật ngày 5. Không đợi SV1 có model để bắt đầu màn hình alert. 

#### G. Kiểm thử sau khi hoàn thành 

- Mở app lần đầu không có màn login; link đúng kết nối; link sai/hết hạn báo lỗi; kill rồi mở lại giữ pairing. Thử backend URL localhost từ điện thoại để hiểu lỗi và đổi IP LAN đúng. 

- Lần lượt cấp/từ chối quyền notification; UI phản ánh trạng thái, không crash. Nhận push thử cùng project khi foreground và background; thử chạm notification mở app. Force-stop là ca giới hạn riêng, không dùng làm bằng chứng push hỏng khi thu nhỏ. 

- ● Ngắt Wi-Fi khi WS đang nối, mở lại: chỉ một socket active, không có hai alert giống nhau do subscribe hai lần. Khóa bị revoke thì quay về trạng thái cần ghép, không tiếp tục hiện hình cũ như đang live. 

#### H. Deliverables và thao tác demo 

App chạy trên Android thật, có các file parser/API/storage/pair/home/WS, Firebase config và quyền/channel cơ bản. Demo: dán link mới, xem status thay đổi khi SV2 ngắt RTSP, nhận 

một push có nhãn thử. APK debug có thể cài lại trên đúng thiết bị; chưa coi đó là bản MVP cuối. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi luồng mở app → pair → status/WS → push test chạy trên máy. Nếu UI thiếu thời gian, giữ hai màn hình và text status, bỏ trang settings riêng. Nếu điện thoại không có Google Play services, dùng máy khác/emulator có Google Play để xác minh, nhưng tuần 3 vẫn phải thử một điện thoại thật phù hợp. Không đổi sang web app chỉ để tránh cấu hình Android. 

### 6.2.1. Tuần 2 — SV1: Hai scorer ngã, xác nhận theo thời gian và model A đầu tiên 

#### A. Mục tiêu của tuần 

Có baseline B phát hiện diễn biến nghi ngã trên video; nhánh A có dataset loader, TCN nhỏ, training/validation và adapter nếu pilot dữ liệu đạt. Hai hướng trả cùng candidate cho state machine. Dành 6 giờ B/features/state, 8 giờ A/train, 4 giờ đánh giá và 2 giờ bàn giao. Không train hai pose model và hai hệ thống riêng. 

#### B. Kiến thức cần học 

- Học sliding window có timestamp, tính góc thân, tỉ lệ box, vận tốc chuẩn hóa và xử lý confidence thấp. Đạt mức tự tính được từng feature trên một chuỗi ngắn bằng tay rồi so với hàm Python. 

- Học finite state machine, hysteresis và latch: điểm vượt ngưỡng trong một frame khác với bằng chứng duy trì 2 giây. Hiểu vì sao cooldown riêng không chặn được báo lại mỗi phút cho cùng người đang nằm. 

- Nhánh A: tensor [N,C,T], Dataset/DataLoader, Conv1d, logits, BCEWithLogitsLoss, optimizer, backward/step, train/eval, no_grad và early stopping. Cần hiểu forward/loss/gradient ở mức sửa script; không cần chứng minh toàn bộ convolution hay tự viết autograd. 

- Học precision, recall, F1, confusion matrix và event matching; accuracy của frame không thay cho số lần báo nhầm/giờ. Học group split, class imbalance và dùng validation chọn threshold, test chỉ đánh giá cuối. 

#### C. Áp dụng trực tiếp vào project 

features.py chuẩn hóa cùng cách cho extraction/runtime; pretrained.py biến feature thành rule_score; trained.py gọi FallTCN rồi chuyển logits thành score chưa hiệu chuẩn. state_machine.py dùng chung để output của hai nhánh đều qua xác nhận/latch. SV2 nhận DetectionUpdate từ detector đã chọn mà không phải biết Conv1d hay dataset. 

#### D. Công việc lập trình cụ thể 

- T1. Viết extract_kinematics/normalize_window; test vai/hông thiếu, Δt=0, người đứng/ngang và frame gap. So feature cùng clip ở offline và realtime replay; chỉ chuyển sang train khi feature_version đã ổn. 

- T2. Cài RuleScorer theo bằng chứng onset + tư thế thấp; đặt ngưỡng trong config. Viết state machine và test nằm sẵn/cúi nhanh/ngồi nhanh/gap/latch. Cho SV2 import B trong ngày 8, không chờ training. 

- T3. Hoàn tất cache, dataset window 30×54, chia theo data/splits.json; augment chỉ train. Viết FallTCN 2–3 block Conv1d nhỏ, train 2 epoch để kiểm loss và shape, sau đó tối đa khoảng 30 epoch có early stopping patience 5. 

- T4. Lưu best state_dict và meta; load lại trên CPU trong process mới, output gần bằng lần trước trong sai số số thực. Thêm TrainedDetector theo cùng interface; nếu metadata lệch, reject hoặc fallback B có thông báo. 

- T5. Sweep ngưỡng B/A trên validation và chạy episode replay cùng state machine. So false alarms, recall và thời gian inference trên cùng clip/máy. Lưu validation.json với số mẫu, không điền “độ chính xác kỳ vọng” thành kết quả thật. 

- T6. Cổng ngày 10: chọn B mặc định; A chỉ được lên MVP nếu dữ liệu/split hợp lệ, load được, không tăng FP đáng kể, recall không kém trên validation và đáp ứng độ trễ. Không dùng test để chọn. Nếu mẫu ít hoặc kết quả không rõ, giữ B và tiếp tục A như nhánh đã có đường triển khai. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `configs/ai.yaml` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Model, cửa sổ và ngưỡng luật/xác nhận. Thành phần chính: mode; sample_hz; thresholds. I/O: YAML → detector/state machine config. Được dùng bởi/tại: backend/ai/factory.py; state_machine.py. Kiểm chứng: A/B đổi bằng config; không hardcode ngưỡng. 

**File:** `configs/train.yaml` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Seed, split, batch và siêu tham số train. Thành phần chính: seed; epochs; learning_rate. I/O: Cấu hình → dataset/train/evaluate. Được dùng bởi/tại: training/train.py. Kiểm chứng: Seed/split/feature_version được khóa cùng checkpoint. 

**File:** `backend/contracts.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: FramePacket, candidate/update và DTO event. Thành phần chính: FramePacket; FallCandidate; DetectionUpdate. I/O: Numpy nội bộ → DTO tách riêng cho network. Được dùng bởi/tại: AI, pipeline, API. Kiểm chứng: SV2 parse được output mock cùng schema_version. 

**File:** `backend/ai/interface.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Protocol detector và scorer thay thế được. Thành phần chính: FallDetector; SequenceScorer. I/O: Frame/window → DetectionUpdate/score. Được dùng bởi/tại: factory, mock, pretrained, trained. Kiểm chứng: Mock/B/A cùng interface; backend không import TCN trực tiếp. 

**File:** `backend/ai/mock.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Output giả có nhãn is_test ở nguồn phát triển. Thành phần chính: MockDetector.process/reset/close. I/O: Chuỗi fixture → candidate/status xác định. Được dùng bởi/tại: factory; test tích hợp T1. Kiểm chứng: Không bật mock trong nghiệm thu AI thật. 

**File:** `backend/ai/pose.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Load pose một lần, box/keypoint và track ID. Thành phần chính: PoseEstimator.estimate/reset/close. I/O: Frame BGR → tracked poses COCO17. Được dùng bởi/tại: pretrained và trained adapters. Kiểm chứng: Không có người/ID/khớp thiếu không crash. 

**File:** `backend/ai/buffer.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Cửa sổ theo track/session có timestamp. Thành phần chính: PoseBuffer.add/window/reset. I/O: Pose + time → 30 mốc/quality. Được dùng bởi/tại: Cả hai detector và feature extractor. Kiểm chứng: Không nối qua gap; không đếm trùng frame_id. 

**File:** `backend/ai/features.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Feature/chuẩn hóa dùng chung train và runtime. Thành phần chính: extract_kinematics; normalize_window. 

I/O: Pose window → kinematics + [30,54]. Được dùng bởi/tại: training/extract, dataset; scorer A/B. Kiểm chứng: Cùng clip tạo feature giống offline/online. 

**File:** `backend/ai/pretrained.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Scorer luật dùng pose pretrained. Thành phần chính: RuleScorer.score; PretrainedDetector.process. I/O: Feature/history → candidate rule_score. Được dùng bởi/tại: factory; pipeline qua interface. Kiểm chứng: Không kết luận ngã từ một pose nằm. 

**File:** `backend/ai/trained.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Adapter load TCN và kiểm metadata. Thành phần chính: TrainedDetector.process; load_checkpoint. I/O: Window [30,54] → uncalibrated_model_score. Được dùng bởi/tại: factory; pipeline qua interface. Kiểm chứng: A/B đổi config; checkpoint thiếu quay B rõ ràng. 

**File:** `backend/ai/state_machine.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Xác nhận, latch episode, recovery. Thành phần chính: FallStateMachine.update/reset. I/O: Candidate + monotonic timestamp → transition. Được dùng bởi/tại: pipeline; tests/test_ai_sequence.py. Kiểm chứng: Giữ nằm không báo lặp; gap không tăng confirmation. 

**File:** `backend/ai/factory.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Tạo mock/B/A theo config. Thành phần chính: create_detector(settings). I/O: Config/model path → FallDetector. Được dùng bởi/tại: backend/main.py. Kiểm chứng: Không load model mỗi request; báo lỗi rõ. 

**File:** `backend/ai/tcn.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Kiến trúc phân loại chuỗi nhỏ dùng chung. Thành phần chính: FallTCN.forward. I/O: Tensor [N,54,30] → logits [N,1]. Được dùng bởi/tại: training/train; trained.py. Kiểm chứng: Forward CPU chạy được; shape có kiểm tra. 

**File:** `training/manifest.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Lập danh sách clip, nguồn và group chống leakage. Thành phần chính: build_manifest; validate_groups. I/O: RGB sequences/clip metadata → clips.csv. Được dùng bởi/tại: extract; split generation. Kiểm chứng: Một clip/2 góc cùng sự kiện chung group. 

**File:** `data/manifests/clips.csv` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Manifest dữ liệu nguồn có provenance. Thành phần chính: clip_id,path,group_id,subject_id,camera_id,fps. I/O: Metadata clip → loader/split. Được dùng bởi/tại: manifest.py; extract.py. Kiểm chứng: FPS/nhóm có giá trị xác minh; unknown được ghi rõ. 

**File:** `data/labels/intervals.csv` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Nhãn onset/impact/end và hard negative. Thành phần chính: clip_id,onset_s,impact_s,end_s,label. I/O: Quan sát video → interval đã soát. Được dùng bởi/tại: training/extract; evaluate. Kiểm chứng: Không gắn mọi frame clip ngã là positive. 

**File:** `data/splits.json` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Train/val/test theo group và seed. Thành phần chính: train_groups; val_groups; test_groups. I/O: Manifest → split độc lập recording. Được dùng bởi/tại: dataset; train; evaluate. Kiểm chứng: Group giao nhau rỗng, khóa trước tuning. 

**File:** `training/extract.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Trích pose/features đúng timestamp. Thành phần chính: extract_clip; save_features. I/O: RGB/MP4 + labels → .npz có timestamps. Được dùng bởi/tại: PoseEstimator; normalize_window. Kiểm chứng: Có thể resume; không tải lại model mỗi clip. 

**File:** `data/features/*.npz` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Cache sinh tự động cho từng clip. Thành phần chính: features,timestamps,validity,labels. I/O: Clip + pose → numpy arrays. Được dùng bởi/tại: training/dataset.py. Kiểm chứng: Shape/thời gian khớp; không commit data lớn. 

**File:** `training/dataset.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Loader cửa sổ, nhãn, augment chỉ train. Thành phần chính: FallWindowDataset.__getitem__. I/O: Cache + split → X [54,30], y, sample weight. Được dùng bởi/tại: DataLoader trong train/evaluate. Kiểm chứng: Val/test không augment; scaler chỉ fit train nếu dùng. 

**File:** `training/train.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Train TCN nhỏ, early stopping và lưu best. Thành phần chính: train_epoch; validate_epoch; main. I/O: Dataset/config → state_dict + meta. Được dùng bởi/tại: FallTCN; DataLoader. Kiểm chứng: Loss hữu hạn; best theo val, không chọn theo test. 

**File:** `training/evaluate.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Đánh giá window và episode theo cùng logic runtime. Thành phần chính: evaluate_windows; replay_events; summarize. I/O: Model/B + clips → precision/recall/FP/latency. Được dùng bởi/tại: Cả hai nhánh; configs/ai.yaml. Kiểm chứng: One-to-one matching event; bỏ is_test. 

**File:** `scripts/ai_smoke.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Chạy 1 clip độc lập để thấy pose/status. Thành phần chính: main --source --mode. I/O: Video/camera → preview/terminal counters. Được dùng bởi/tại: Detector interface. Kiểm chứng: Không cần backend/app để debug AI. 

**File:** `models/fall_tcn.pt` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Checkpoint nhánh A sinh từ training. Thành phần chính: state_dict do torch.save. I/O: Model đã train → adapter CPU/GPU. Được dùng bởi/tại: TrainedDetector. Kiểm chứng: Load lại cho output gần như tương đương; không giả file khi train chưa xong. 

**File:** `models/fall_tcn.meta.json` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Hợp đồng weights/feature và threshold validation. Thành phần chính: feature_version; sample_hz; class_map; seed. I/O: Training/validation → metadata. Được dùng bởi/tại: TrainedDetector.load_checkpoint. Kiểm chứng: Từ chối shape/version không khớp. 

**File:** `evaluation/cases.csv` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Danh sách ca test có ground truth/tập dữ liệu. Thành phần chính: case_id,clip_id,split,expected,interval. I/O: Video kiểm chứng → test cases. Được dùng bởi/tại: training/evaluate; cả nhóm. Kiểm chứng: Có ngã, ADL, nằm sẵn, che khuất; không dùng test tuning. 

**File:** `evaluation/validation.json` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Kết quả chọn ngưỡng/model trên val. Thành phần chính: Metrics, counts, model_id, config hash. I/O: Val predictions → kết quả đo. Được dùng bởi/tại: Cổng quyết định ngày 10/15. Kiểm chứng: Kèm denominator và thời gian; không chứa số bịa. 

**File:** `tests/test_ai_sequence.py` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Test lỗi temporal và xác nhận meaningful. Thành phần chính: test_gap_resets; test_no_repeat; test_sit_vs_fall. I/O: Chuỗi timestamp/pose giả → transitions. Được dùng bởi/tại: pytest; state machine/features. Kiểm chứng: Không test từng getter; kiểm ca rớt mạng/lặp/góc thiếu. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 6–7 features/rules; ngày 8 bàn giao B và khởi tạo training A; ngày 9 train/evaluate/load; ngày 10 so sánh và chọn. B và state machine là đường găng; extraction có thể chạy nền trong khi viết B. Nếu SV2 chưa có RTSP ổn, chạy replay file với timestamp nguồn; nếu A chưa train được, TrainedDetector phải trả MODEL_UNAVAILABLE thay vì dự đoán giả. 

#### G. Kiểm thử sau khi hoàn thành 

- Video ngã rõ có onset và nằm sau đó → SUSPECTED rồi CONFIRMED một lần. Video cúi nhặt đồ/ngồi nhanh/chủ động nằm → không phát fall.confirmed với cấu hình hiện tại; nếu có FP thì lưu case và sửa trên validation. 

- Đang SUSPECTED rồi mất frame >0.3 giây → UNKNOWN/WARMUP, không confirmed nhờ đồng hồ chạy tiếp. Giữ người nằm 90 giây → một event episode. Đứng phục hồi đủ 3 giây, ngã mới sau cooldown → event mới. 

- A: batch dummy [2,54,30] forward ra [2,1]; 2 epoch loss hữu hạn; train và val không chung group; load CPU chạy; missing weights/version mismatch có lỗi rõ. Không dùng cùng clip đã tuning làm test độc lập. 

#### H. Deliverables và thao tác demo 

B chạy từ ai_smoke và backend; feature/state/test module hoàn chỉnh; dataset loader/train/evaluate chạy tối thiểu pilot. Nếu dữ liệu đạt: có fall_tcn.pt/meta và kết quả validation thật. App nhận trạng thái ngã từ video AI thật; sự kiện push đầy đủ sẽ nối ở tuần 3. Demo đổi ai.mode trong config và restart, backend giữ nguyên API. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS P0 khi B + state machine tích hợp và không báo lặp ở các ca đã nêu; nhánh A PASS thử nghiệm khi có train/load/validation thật, không đòi A thắng B. Nếu train vướng sau ngày 9, dừng mở rộng kiến trúc/dataset, hoàn thiện pilot rồi giữ B. Không cắt xác nhận theo thời gian hoặc bỏ hard negative để có con số đẹp. 

### 6.2.2. Tuần 2 — SV2: RTSP → AI thật → status và preview cho app 

#### A. Mục tiêu của tuần 

Thay MockDetector bằng B qua factory, giữ API không đổi; app thấy camera preview, trạng thái AI và candidate thật. Hoàn tất route camera config và contract tests; chuẩn bị điểm nối event service tuần 3. Phân bổ 6 giờ pipeline/threading, 4 giờ MJPEG, 4 giờ API/quyền, 4 giờ test/tối ưu và 2 giờ bàn giao. 

#### B. Kiến thức cần học 

- Học ranh giới event loop/thread và thread-safe handoff: dùng loop.call_soon_threadsafe hoặc asyncio.run_coroutine_threadsafe để đưa thông báo từ inference thread vào hub; không asyncio.run() lồng trong loop API. 

- Học MIME multipart/x-mixed-replace, JPEG bytes, boundary và stream generator; biết cache JPEG dùng chung khác queue bị consume. Không cần học H.264 encoder, WebRTC signaling hoặc media server production. 

- Học dependency injection mức nhỏ để test FastAPI với fake reader/detector và temp SQLite. Hiểu auth phải áp dụng cả stream/WS, không chỉ REST. 

- Học cập nhật camera hai pha: route validate trả 202, worker đổi nguồn; status CONNECTING→CONNECTED/ERROR. Đạt mức app không bị treo khi camera URL sai. 

#### C. Áp dụng trực tiếp vào project 

Pipeline gọi detector.process(packet), cập nhật AI state và truyền candidate cho máy trạng thái do SV1 cung cấp. stream.py đọc JPEG cache để Flutter hiển thị. routes.py nhận URL từ SV3 rồi ra lệnh cho reader; auth bảo vệ camera/event/preview. Sau reconnect pipeline.reset(session) gọi cùng detector/state thay vì tái dùng buffer cũ. 

#### D. Công việc lập trình cụ thể 

- T1. Thêm detector factory B vào startup, warmup và xử lý load lỗi; mock chỉ bật khi development. Nếu model thiếu, status AI ERROR rõ, camera vẫn có thể hiển thị. Không tạo event fall giả khi exception. 

- T2. Nối candidate/state machine; phát ai.status qua WS có schema, tạm hiện confirmed dạng update phát triển nhưng chưa dựng outbox. Giữ một API/event sample để SV3 viết coordinator trước. 

- T3. Encode JPEG ở nhịp 2–3 FPS, cache latest; tạo stream.mjpeg xác thực header. Thử hai client đọc không ảnh hưởng tốc độ AI. Nếu flutter_mjpeg không tương thích, thêm preview.jpg từ cùng cache. 

- T4. Hoàn thiện PUT camera, stop và status stale; masked URL ở mọi response. Giới hạn URL length, không cho route video file arbitrary. Kiểm tra điện thoại đang dùng khóa đúng installation. 

- T5. Viết test_api cho status/preview/auth; test reader stop/reconnect; đo FPS và thời gian GET status trong khi inference chạy. Nếu API chậm, giảm preview trước, giảm imgsz với SV1; không tăng worker Uvicorn. 

- T6. Chốt demo tích hợp ngày 10 bằng một clip phát qua RTSP: app thấy ảnh, AI state/candidate và trạng thái reconnect. Chuyển contract event và điểm gọi EventService cho tuần 3. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `README.md` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Lệnh cài/chạy và thao tác vận hành MVP. Thành phần chính: Các lệnh backend/pairing/Flutter. I/O: Máy mới → chạy demo; không có báo cáo học phần. Được dùng bởi/tại: Cả nhóm và người chạy thử. Kiểm chứng: Có lệnh smoke và giới hạn bản chạy đúng thực tế. 

**File:** `configs/app.yaml` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Timeout, camera, rate preview, runtime DB. Thành phần chính: Config keys tại Chương 2. I/O: YAML/env → AppSettings. Được dùng bởi/tại: backend/config.py. Kiểm chứng: Giá trị lỗi bị báo lúc startup. 

**File:** `backend/main.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Tạo FastAPI app và lifecycle worker. Thành phần chính: create_app(); lifespan(). I/O: Settings → app; startup/shutdown worker. Được dùng bởi/tại: Uvicorn. Kiểm chứng: Một worker, start/stop không nhân đôi camera. 

**File:** `backend/config.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Nạp và kiểm tra config. Thành phần chính: AppSettings; load_settings(). I/O: YAML + env → settings typed. Được dùng bởi/tại: main, reader, pipeline. Kiểm chứng: Thiếu model/credential trả trạng thái rõ ràng. 

**File:** `backend/camera/reader.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Đọc RTSP/video/webcam, reconnect theo phiên. Thành phần chính: CameraReader.start/read_latest/stop; _capture_loop. I/O: Nguồn video → FramePacket/status. Được dùng bởi/tại: backend/pipeline.py. Kiểm chứng: Sai URL không treo API; tự nối lại; release đúng thread. 

**File:** `backend/camera/latest.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Bộ đệm frame/JPEG mới nhất dung lượng hữu hạn. Thành phần chính: LatestValue.replace/wait_newer/get. I/O: Frame mới → snapshot thread-safe. Được dùng bởi/tại: reader, pipeline, api/stream.py. Kiểm chứng: Không tích lũy frame; viewer không lấy mất frame AI. 

**File:** `backend/pipeline.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Ghép capture, detector, state machine và event service. Thành phần chính: Pipeline.start/stop; _infer_loop. I/O: FramePacket → status/transition/cache. Được dùng bởi/tại: main; routes; stream. Kiểm chứng: Inference không chặn API; reset khi đổi session. 

**File:** `backend/api/routes.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Health/status/camera/events/ack/test endpoint. Thành phần chính: health; get_status; set_camera; ack_event. I/O: HTTP DTO và device context → JSON. Được dùng bởi/tại: main; storage; pipeline. Kiểm chứng: Response/HTTP code khớp contract; có auth. 

**File:** `backend/api/ws.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Handshake có khóa và fanout event/status. Thành phần chính: ConnectionHub.connect/broadcast/disconnect. I/O: Event JSON → đúng kết nối installation. Được dùng bởi/tại: main; EventService. Kiểm chứng: Reconnect được; không lộ event cho khóa sai. 

**File:** `backend/api/stream.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: MJPEG và snapshot có xác thực. Thành phần chính: mjpeg_generator; get_preview. I/O: Cache JPEG → HTTP stream/ảnh. Được dùng bởi/tại: FastAPI; Flutter camera_view. Kiểm chứng: Ngắt viewer không dừng AI; frame stale có trạng thái. 

**File:** `backend/auth.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Xác thực hash device secret và scope installation. Thành phần chính: require_device; verify_device_secret. I/O: Bearer secret → DeviceContext/401. Được dùng bởi/tại: Mọi route và WS/stream nhạy cảm. Kiểm chứng: Khóa sai/revoke không xem được ảnh/event. 

**File:** `tests/test_camera.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Test timeout/reconnect bằng fake capture. Thành phần chính: test_read_failure; test_new_session. I/O: Capture fake và clock → state/frame. Được dùng bởi/tại: pytest; CameraReader. Kiểm chứng: Không chờ camera thật trong unit test. 

**File:** `tests/test_api.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Contract/API với mock AI. Thành phần chính: test_status; test_protected_preview; test_ack. I/O: TestClient + mock pipeline → JSON/HTTP. Được dùng bởi/tại: pytest; routes. Kiểm chứng: Không đòi camera/GPU để chạy contract tests. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 6 ổn reader/factory, ngày 7 preview, ngày 8 nhận B thật, ngày 9 config/status/test và ngày 10 tích hợp. Nếu B chậm, tiếp tục với MockDetector trong test hợp đồng nhưng demo phải phân biệt rõ; dành cửa sổ ngày 8 với SV1 để nối B. A có thể được nạp sau bằng config, không là điều kiện để MJPEG/app chạy. 

#### G. Kiểm thử sau khi hoàn thành 

- Khởi động B, chạy RTSP có người và không người: status/WS không chứa numpy hay NaN. Không có frame mới thì ai không xử lý lại frame cũ để tích đủ xác nhận. 

- Hai máy xem preview, đóng một viewer: backend/AI còn chạy và viewer kia vẫn cập nhật. URL stream không khóa hoặc khóa sai trả 401/403; không trả ảnh dù /health công khai. 

- PUT URL hợp lệ cú pháp nhưng camera tắt trả 202 rồi status lỗi/retry; /health không treo. Đổi camera khi đang SUSPECTED không được sinh confirmed từ session cũ. 

#### H. Deliverables và thao tác demo 

Có preview MJPEG hoặc snapshot đã xác minh, reader/AI/reset tích hợp, API config và contract tests. Người dùng pair, nhập RTSP, xem hình và trạng thái nhận diện từ app. Demo ngày 10 có thể cho camera mất nguồn hoặc dừng FFmpeg rồi mở lại để thấy tự phục hồi. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi AI thật chạy cùng camera và app, preview không đánh đổi mất cảnh báo, route nhạy cảm có auth. Nếu trễ, bỏ overlay skeleton trong preview, dùng raw frame, giảm preview xuống 1 FPS; vẫn giữ RTSP, AI state và camera reconnect. Không dành thời gian multi-camera, camera discovery hay clip recording. 

### 6.2.3. Tuần 2 — SV3: Hiển thị camera và xử lý cảnh báo từ AI thật 

#### A. Mục tiêu của tuần 

Home nhập RTSP và hiển thị preview/status đúng; AlertScreen và AlertCoordinator đầu tiên xử lý sự kiện WS; lifecycle/reconnect ổn. Tiếp tục giữ FCM smoke có thể chạy để tuần 3 mở rộng. Phân bổ 6 giờ camera/status, 5 giờ coordinator/alert UI, 4 giờ reconnect/lifecycle, 3 giờ parser test và 2 giờ tích hợp. 

#### B. Kiến thức cần học 

- Học Form/TextEditingController, che mật khẩu và submit async; Loading/Error widget cho camera. Hiểu kết nối tới backend và kết nối backend tới camera là hai tầng lỗi khác nhau. 

- Học MJPEG qua HTTP và Authorization header; isLive theo lifecycle; khi app nền chỉ ngắt viewer, không gọi stop camera backend. Không cần học giải mã RTSP trực tiếp trong Flutter. 

- Học event stream, Set/LRU event_id để dedup, model immutability và trạng thái foreground/background. Hiểu WS là realtime trong phiên đang mở, không thay push. 

- ● Học unit test parser và fake ApiClient/AlarmService để xác minh hành vi; chưa viết test widget mọi màu sắc hay từng getter. 

#### C. Áp dụng trực tiếp vào project 

Home gọi PUT camera và chờ status thay vì giả định request 202 là connected. CameraView dùng stream của SV2. Models parse schema từ SV1/SV2; coordinator là điểm nhận chung để tuần 3 gắn FCM/audio mà không sửa mỗi màn hình. SV3 cung cấp cho SV2 danh sách code/status UI đang xử lý để khóa contract. 

#### D. Công việc lập trình cụ thể 

- T1. Thêm form RTSP gồm nhãn, URL hoặc user/password theo thiết kế; không đưa URL vào log/debug UI. Submit và hiển thị CONNECTING, đọc status tới CONNECTED/ERROR. 

- T2. Thêm CameraView có auth, loading/error và stale notice; dùng raw image trước, không vẽ lại skeleton trên Flutter. Pause/resume chỉ quản lý stream/widget, để backend vẫn inference. 

- T3. Viết FallEvent parser và AlertCoordinator.handleEvent; event chưa đủ trường bị reject có thông báo kỹ thuật gọn, không crash. Dùng event_id cho seen store và installation_id để chống sự kiện nhầm backend. 

- T4. AlertScreen hiển thị message/camera/time/is_test và nút Đã xem/Tắt âm thanh (âm sẽ nối T3). Candidate chỉ là “đang xác minh”, chưa hiện như alarm confirmed. 

- T5. Nối WS update từ AI B, test reconnect và resume lấy status; cập nhật parser test với field thiếu/null/sai schema. Chốt fixture event cuối ngày 10 cho push mapping tuần 3. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `mobile/pubspec.yaml` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Dependency Flutter và asset audio. Thành phần chính: dependencies; flutter.assets. I/O: Package constraints → Flutter build. Được dùng bởi/tại: flutter pub get. Kiểm chứng: Một bộ package tương thích, asset tìm được. 

**File:** `mobile/pubspec.lock` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Khóa phiên bản package app. Thành phần chính: Generated lock. I/O: pubspec → resolved versions. Được dùng bởi/tại: Flutter SDK. Kiểm chứng: Máy thứ hai pub get ra cùng bộ dependency. 

**File:** `mobile/lib/main.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Khởi tạo app/Firebase/services và lifecycle. Thành phần chính: main; FallGuardApp. I/O: DeviceStore → pair/home; resume sync. Được dùng bởi/tại: Flutter entry point. Kiểm chứng: Mở app không cần tài khoản; không init FCM hai lần. 

**File:** `mobile/lib/models.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Parser status/event/pairing có kiểm trường. Thành phần chính: SystemStatus.fromJson; FallEvent.fromJson/fromPushData. I/O: JSON REST/WS/FCM → Dart models. Được dùng bởi/tại: Screens; coordinator. Kiểm chứng: Sai schema/optional field không crash UI. 

**File:** `mobile/lib/services/api_client.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: HTTP header, timeout và đồng bộ event. Thành phần chính: getStatus; pair; configureCamera; listEvents; ack. I/O: DTO/device secret → response typed. Được dùng bởi/tại: Home/Pair/Alert screens. Kiểm chứng: 401 chuyển trạng thái cần ghép; không tự retry claim bừa. 

**File:** `mobile/lib/services/ws_client.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: WS có auth và backoff theo lifecycle. Thành phần chính: connect; events; reconnect; dispose. I/O: Base URL/secret → event stream. Được dùng bởi/tại: Home; AlertCoordinator. Kiểm chứng: Không tạo socket trùng sau resume; retry có trần. 

**File:** `mobile/lib/services/notification_service.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: FCM setup, permission, channel và token refresh. Thành phần chính: initialize; registerEndpoint; onMessage; onOpen. I/O: RemoteMessage/token → coordinator/API. Được dùng bởi/tại: main; AlertCoordinator. Kiểm chứng: Foreground/background/terminated thường nhận đúng, không nhận nhầm installation. 

**File:** `mobile/lib/services/alert_coordinator.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Một điểm nhận event từ WS/FCM/REST. Thành phần chính: handleEvent; 

acknowledge; markSeen. I/O: FallEvent + app state → UI/audio một lần. Được dùng bởi/tại: WsClient; NotificationService; screens. Kiểm chứng: Cùng event từ hai kênh chỉ báo một lần ở foreground. 

**File:** `mobile/lib/screens/home_screen.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: RTSP form, status, camera, setting và thử push. Thành phần chính: HomeScreen; refresh; configureCamera. I/O: Status/camera config → UI. Được dùng bởi/tại: ApiClient; WsClient; CameraView. Kiểm chứng: Phân biệt camera connected và AI ready; password che mặc định. 

**File:** `mobile/lib/screens/alert_screen.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Thông tin sự kiện, tắt âm và ack. Thành phần chính: AlertScreen; onSilence; onAcknowledge. I/O: FallEvent → UI/action. Được dùng bởi/tại: AlertCoordinator; ApiClient. Kiểm chứng: Nút tắt âm/đã xem hoạt động kể cả API tạm lỗi. 

**File:** `mobile/lib/widgets/camera_view.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Hiển thị MJPEG qua HTTP có header. Thành phần chính: CameraView; onLifecycleChanged. I/O: URL stream + secret → widget ảnh. Được dùng bởi/tại: HomeScreen; flutter_mjpeg. Kiểm chứng: Nền app ngắt view; AI backend vẫn chạy. 

**File:** `mobile/test/models_test.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Parser schema và dữ liệu thiếu. Thành phần chính: FallEvent/status parsing tests. I/O: JSON fixtures → Dart models/error. Được dùng bởi/tại: flutter test. Kiểm chứng: Schema cũ/sai không làm app crash. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Làm UI/parse bằng fixture ngày 6, CameraView khi SV2 có stream ngày 7, nhận B thật ngày 8, coordinator/lifecycle ngày 9, ghép ngày 10. Khi backend chưa tạo event store, coordinator nhận fixture WS có is_test=true; không tự đổi candidate thành event thật ở điện thoại. Logic xác nhận thuộc backend. 

#### G. Kiểm thử sau khi hoàn thành 

- Nhập RTSP đúng/sai, camera tắt, backend tắt: UI có ba thông báo khác nhau. 202 không tự chuyển xanh trước khi status CONNECTED. Key sai không được xem stream. 

- Một event WS gửi lại ba lần → một banner; event khác installation → bỏ; candidate không hú. Home→background→resume không mở ba stream camera hay ba socket. 

- Clip AI B thật qua RTSP → thấy trạng thái đổi trên app; không người vẫn xem được camera và status NO_PERSON/không candidate. Test parser với JSON thiếu reasons hoặc version không hỗ trợ. 

#### H. Deliverables và thao tác demo 

App xem được hình camera qua HTTP, nhập RTSP, phản ánh camera/AI state, có AlertScreen/coordinator cơ bản và parser tests. Demo ngày 10: nhập RTSP, xem video ngã thử do backend xử lý, thấy SUSPECTED/CONFIRMED update; âm/push toàn tuyến hoàn thiện ở tuần sau. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi UI không giả “AI chạy tốt” từ camera connected, event/candidate phân biệt được, stream/WS reconnect không nhân đôi. Nếu camera widget lỗi khó sửa, chuyển snapshot polling 1 FPS theo route của SV2, giữ auth và stale state; không bỏ màn cảnh báo để tối ưu giao diện. 

### 6.3.1. Tuần 3 — SV1: Giảm báo nhầm và khóa hành vi confirmed/recovery 

#### A. Mục tiêu của tuần 

Ổn định model đã chọn, bàn giao transition tạo event thật; kiểm tra các ca ngồi/nằm/cúi, che khuất và thay ID. Nhánh A có tối đa 4 giờ cải tiến nếu pilot đã chạy; không mở thêm kiến trúc mới. Dành 8 giờ hard negatives, 6 giờ tích hợp, 4 giờ A và 2 giờ cập nhật đánh giá. 

#### B. Kiến thức cần học 

- Học phân tích lỗi theo clip: false positive xảy ra ở onset, feature, scorer hay state machine; sửa đúng tầng thay vì nâng mọi threshold. Đọc lại feature và status trên chuỗi gần thời điểm sai. 

- Học precision/recall tradeoff và threshold sweep. Đạt mức so cùng validation với cùng event tolerance trước/sau một thay đổi, không chỉ xem một video thuận lợi. 

- ● Học track loss/ID churn, warmup sau reconnect và chất lượng pose. Hiểu invalid pose không được tính là immobility và ack app không phải tín hiệu người đã đứng lên. 

- Nếu A tiếp tục: xem overfit, weighted loss/sampler một phương án, early stopping; không cần học Transformer/ST-GCN/3D-CNN ở tuần này. 

#### C. Áp dụng trực tiếp vào project 

Scorer/state machine phải trả just_confirmed và episode_id đủ cho EventService của SV2. Features/cases giữ các hard negative dùng giảm FP; AlertScreen của SV3 chỉ hiện message không chẩn đoán và lý do thân thiện. Mọi thay đổi threshold được phản ánh qua config/model_id để khi so sánh không nhầm hai phiên bản. 

#### D. Công việc lập trình cụ thể 

- T1. Chạy baseline trên danh sách validation gồm ngồi nhanh, cúi, nằm có chủ ý, nằm sẵn khi mở camera, đi ra khỏi khung và ngã thật trong video. Phân loại lỗi theo nguyên nhân, ưu tiên hai lỗi làm alarm giả nhiều nhất. 

- T2. Chỉnh logic onset/low posture/hysteresis trong phạm vi đã thiết kế; thêm test tái hiện lỗi quan trọng. Không dùng một vùng “giường” chặn tất cả nếu chưa test ngã từ giường xuống sàn; vùng nghỉ chỉ là hỗ trợ P1. 

- T3. Giao transition contract cho SV2: same episode lặp process không just_confirmed lại; recovery đủ 3 giây mới kết thúc latch. Cùng SV2 cố tình retry/create_once để kiểm chặn lặp cả AI và DB. 

- T4. Nếu A có dữ liệu tốt, thử một điều chỉnh nhỏ như class weighting hoặc LR; so trên cùng val. Nếu A chưa vượt B rõ, giữ B, không dùng tuần 3 để thu thập dataset mới lớn. Điểm đóng băng A muộn nhất ngày 15. 

- T5. Kiểm tra timestamp thực khi RTSP tốc độ biến thiên; nếu thiếu mẫu/gap, UI AI degraded và không fake tiếp tục inference. Hạ imgsz và preview với SV2 khi CPU quá tải rồi chạy lại validation. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `configs/ai.yaml` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Model, cửa sổ và ngưỡng luật/xác nhận. Thành phần chính: mode; sample_hz; thresholds. I/O: YAML → detector/state machine config. Được dùng bởi/tại: backend/ai/factory.py; state_machine.py. Kiểm chứng: A/B đổi bằng config; không hardcode ngưỡng. 

**File:** `backend/contracts.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: FramePacket, candidate/update và DTO event. Thành phần chính: FramePacket; FallCandidate; DetectionUpdate. I/O: Numpy nội bộ → DTO tách riêng cho network. Được dùng bởi/tại: AI, pipeline, API. Kiểm chứng: SV2 parse được output mock cùng schema_version. 

**File:** `backend/ai/features.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Feature/chuẩn hóa dùng chung train và runtime. Thành phần chính: extract_kinematics; normalize_window. I/O: Pose window → kinematics + [30,54]. Được dùng bởi/tại: training/extract, dataset; scorer A/B. Kiểm chứng: Cùng clip tạo feature giống offline/online. 

**File:** `backend/ai/pretrained.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Scorer luật dùng pose pretrained. Thành phần chính: RuleScorer.score; PretrainedDetector.process. I/O: Feature/history → candidate rule_score. Được dùng bởi/tại: factory; pipeline qua interface. Kiểm chứng: Không kết luận ngã từ một pose nằm. 

**File:** `backend/ai/trained.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Adapter load TCN và kiểm metadata. Thành phần chính: TrainedDetector.process; load_checkpoint. I/O: Window [30,54] → uncalibrated_model_score. Được dùng bởi/tại: factory; pipeline qua interface. Kiểm chứng: A/B đổi config; checkpoint thiếu quay B rõ ràng. 

**File:** `backend/ai/state_machine.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Xác nhận, latch episode, recovery. Thành phần chính: FallStateMachine.update/reset. I/O: Candidate + monotonic timestamp → transition. Được dùng bởi/tại: pipeline; tests/test_ai_sequence.py. Kiểm chứng: Giữ nằm không báo lặp; gap không tăng confirmation. 

**File:** `backend/ai/factory.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Tạo mock/B/A theo config. Thành phần chính: create_detector(settings). I/O: Config/model path → FallDetector. Được dùng bởi/tại: backend/main.py. Kiểm chứng: Không load model mỗi request; báo lỗi rõ. 

**File:** `training/train.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Train TCN nhỏ, early stopping và lưu best. Thành phần chính: train_epoch; validate_epoch; main. I/O: Dataset/config → state_dict + meta. Được dùng bởi/tại: FallTCN; DataLoader. Kiểm chứng: Loss hữu hạn; best theo val, không chọn theo test. 

**File:** `training/evaluate.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Đánh giá window và episode theo cùng logic runtime. Thành phần chính: evaluate_windows; replay_events; summarize. I/O: Model/B + clips → precision/recall/FP/latency. Được dùng bởi/tại: Cả hai nhánh; configs/ai.yaml. Kiểm chứng: One-to-one matching event; bỏ is_test. 

**File:** `models/fall_tcn.pt` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Checkpoint nhánh A sinh từ training. Thành phần chính: state_dict do torch.save. I/O: Model đã train → adapter CPU/GPU. Được dùng bởi/tại: TrainedDetector. Kiểm chứng: Load lại cho output gần như tương đương; không giả file khi train chưa xong. 

**File:** `models/fall_tcn.meta.json` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Hợp đồng weights/feature và threshold validation. Thành phần chính: feature_version; sample_hz; class_map; seed. I/O: Training/validation → metadata. Được dùng bởi/tại: TrainedDetector.load_checkpoint. Kiểm chứng: Từ chối shape/version không khớp. 

**File:** `evaluation/cases.csv` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Danh sách ca test có ground truth/tập dữ liệu. Thành phần chính: case_id,clip_id,split,expected,interval. I/O: Video kiểm chứng → test cases. Được dùng bởi/tại: training/evaluate; cả nhóm. Kiểm chứng: Có ngã, ADL, nằm sẵn, che khuất; không dùng test tuning. 

**File:** `evaluation/validation.json` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Kết quả chọn ngưỡng/model trên val. Thành phần chính: Metrics, counts, model_id, config hash. I/O: Val predictions → kết quả đo. Được dùng bởi/tại: Cổng quyết định ngày 10/15. Kiểm chứng: Kèm denominator và thời gian; không chứa số bịa. 

**File:** `tests/test_ai_sequence.py` — Chỉnh sửa file đã có; SV1 chịu trách nhiệm. Chức năng: Test lỗi temporal và xác nhận meaningful. Thành phần chính: test_gap_resets; test_no_repeat; test_sit_vs_fall. I/O: Chuỗi timestamp/pose giả → transitions. Được dùng bởi/tại: pytest; state machine/features. Kiểm chứng: Không test từng getter; kiểm ca rớt mạng/lặp/góc thiếu. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Đầu ngày 11 khóa transition, ngày 12–13 hard negatives/tuning, ngày 14 tích hợp cảnh báo thật và thử phần cứng, ngày 15 khóa cấu hình MVP. Có thể làm A tối đa 4 giờ song song khi video test chạy; không chặn tích hợp FCM. Nếu SV2 chưa có EventService, trả danh sách transition trong test harness để người khác dùng fixture. 

#### G. Kiểm thử sau khi hoàn thành 

- Replay cùng clip ở tốc độ đọc khác nhau nhưng timestamp nguồn giống nhau: số event không đổi. Gap giữa candidate và nằm → không được confirmed nhờ sleep. Camera rung/khớp nhảy không được tự coi là drop hợp lệ. 

- Giữ một episode 2 phút với ID ổn định; ép mất ID ngắn rồi nhận lại gần chỗ cũ: không phát lặp nếu không thấy onset mới. Nếu không giữ được identity tin cậy, chuyển warmup rõ thay vì hứa tracking xuyên che khuất. 

- Ngã mới sau hồi phục/cooldown có event mới. Validation metrics và số case của bản trước/sau được lưu thật; test giữ nguyên không dùng sửa threshold. 

#### H. Deliverables và thao tác demo 

AI module đã khóa đầu ra/episode, validation cập nhật, các test false alarm/gap/recovery; model MVP path + config + metadata bàn giao. Demo với SV2/SV3: một video qua RTSP tạo một cảnh báo trên điện thoại, nằm tiếp không hú lại, video ngồi/cúi không tạo alarm ở các ca đã thử. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi event creation không lặp và các hard negative đã kiểm chứng; có giới hạn rõ cho che khuất/ngã chậm. Nếu chưa giảm FP đủ, thu hẹp góc camera/vùng demo và công bố kết quả trên phạm vi đó; không sửa nhãn test để hợp model. Giữ nguyên giao thức nên backend/app không phải đổi theo mỗi thử nghiệm. 

### 6.3.2. Tuần 3 — SV2: Event thật, outbox và FCM không làm chậm AI 

#### A. Mục tiêu của tuần 

Có đường RTSP → AI → SQLite event → WS/outbox FCM → Android. Mỗi episode một event, retry hữu hạn, ack và đồng bộ events hoạt động. Dành 5 giờ event/storage, 5 giờ FCM/outbox, 4 giờ WS/REST/ack, 4 giờ test lỗi và 2 giờ tích hợp. 

#### B. Kiến thức cần học 

- Học idempotency, unique constraint và transaction: event phải lưu một lần trước fanout; không phát alarm mới từ mỗi frame CONFIRMED. Phân biệt event creation, notification accepted và app received. 

- Học outbox mức nhỏ: pending/accepted/failed/expired, attempt và next_attempt_at; tách network khỏi DB transaction. Không cần message broker hoặc distributed transaction. 

- Học FCM notification+data, channel_id, TTL, tag, priority và lỗi endpoint/credential/network. Đạt mức sender trả kết quả typed để worker xử lý, không print lỗi rồi coi như gửi thành công. 

- Học WS fanout có auth và event replay theo cursor sau ngắt mạng. Ack là thao tác idempotent, không tác động state machine AI. 

#### C. Áp dụng trực tiếp vào project 

EventService nhận transition từ SV1, tạo event_id/episode_id trong storage; ConnectionHub chuyển JSON cho app mở; Outbox gọi FcmSender cho điện thoại chạy nền. Routes cung cấp events/ack/push registration cho SV3. DeviceStore của app và devices table của backend dùng cùng device_id nên chỉ đúng endpoint được cập nhật. 

#### D. Công việc lập trình cụ thể 

- T1. Mở rộng schema events/outbox; save_event_once có UNIQUE episode_id. Tạo cursor để GET events lấy lại theo thứ tự; seed dữ liệu chỉ ở môi trường test. 

- T2. Nối just_confirmed vào EventService, serialize FallEvent theo schema. Gửi WS sau khi commit; nếu WS không có client vẫn event/outbox tồn tại, AI không đợi app. 

- ● T3. Mở rộng FcmSender từ smoke tuần 1 thành send_fall. Nhận cập nhật push endpoint/sound_enabled của đúng device, không nhận device_id tùy ý ở body mà không kiểm ownership. 

- T4. Outbox worker gửi ngoài inference/API loop, tối đa 3 lần retry, bỏ job quá TTL, không retry accepted. Trước mỗi lần gửi kiểm device còn active. Không xóa event khi FCM lỗi. 

- T5. Thêm events list/ack/test notification; test notification chỉ gửi device gọi và is_test=true. Chạy lại pairing/auth trên WS/stream để route mới không bị quên bảo vệ. 

- T6. Test sender fake cho lỗi timeout/invalid endpoint/crash trước mark accepted; sau đó test FCM thật cùng SV3 ở foreground/background/khóa màn hình. Một vòng với AI thật ngày 14–15 là mốc bắt buộc. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `.env.example` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Tên biến cấu hình và placeholder không bí mật. Thành phần chính: 

GOOGLE_APPLICATION_CREDENTIALS; APP_ENV. I/O: Ví dụ env → config loader. Được dùng bởi/tại: backend/config.py. Kiểm chứng: Không có credential thật trong repo. 

**File:** `README.md` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Lệnh cài/chạy và thao tác vận hành MVP. Thành phần chính: Các lệnh backend/pairing/Flutter. I/O: Máy mới → chạy demo; không có báo cáo học phần. Được dùng bởi/tại: Cả nhóm và người chạy thử. Kiểm chứng: Có lệnh smoke và giới hạn bản chạy đúng thực tế. 

**File:** `configs/app.yaml` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Timeout, camera, rate preview, runtime DB. Thành phần chính: Config keys tại Chương 2. I/O: YAML/env → AppSettings. Được dùng bởi/tại: backend/config.py. Kiểm chứng: Giá trị lỗi bị báo lúc startup. 

**File:** `backend/main.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Tạo FastAPI app và lifecycle worker. Thành phần chính: create_app(); lifespan(). I/O: Settings → app; startup/shutdown worker. Được dùng bởi/tại: Uvicorn. Kiểm chứng: Một worker, start/stop không nhân đôi camera. 

**File:** `backend/config.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Nạp và kiểm tra config. Thành phần chính: AppSettings; load_settings(). I/O: YAML + env → settings typed. Được dùng bởi/tại: main, reader, pipeline. Kiểm chứng: Thiếu model/credential trả trạng thái rõ ràng. 

**File:** `backend/pipeline.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Ghép capture, detector, state machine và event service. Thành phần chính: Pipeline.start/stop; _infer_loop. I/O: FramePacket → status/transition/cache. Được dùng bởi/tại: main; routes; stream. Kiểm chứng: Inference không chặn API; reset khi đổi session. 

**File:** `backend/api/routes.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Health/status/camera/events/ack/test endpoint. Thành phần chính: health; get_status; set_camera; ack_event. I/O: HTTP DTO và device context → JSON. Được dùng bởi/tại: main; storage; pipeline. Kiểm chứng: Response/HTTP code khớp contract; có auth. 

**File:** `backend/api/ws.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Handshake có khóa và fanout event/status. Thành phần chính: ConnectionHub.connect/broadcast/disconnect. I/O: Event JSON → đúng kết nối installation. Được dùng bởi/tại: main; EventService. Kiểm chứng: Reconnect được; không lộ event cho khóa sai. 

**File:** `backend/storage.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: SQLite giao dịch cho device/config/events/outbox. Thành phần chính: open_db; claim_code; save_event_once; list_events. I/O: Record typed → SQLite → record. Được dùng bởi/tại: pairing, auth, routes, EventService. Kiểm chứng: Transaction ngắn; không dùng connection sai thread. 

**File:** `backend/schema.sql` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Bảng/unique index và phiên bản schema. Thành phần chính: CREATE TABLE/INDEX. I/O: DDL → installation/pairing/devices; thêm events/outbox T3. Được dùng bởi/tại: backend/storage.py. Kiểm chứng: Khởi động lại không mất pairing; event/episode unique. 

**File:** `backend/auth.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Xác thực hash device secret và scope installation. Thành phần chính: require_device; verify_device_secret. I/O: Bearer secret → DeviceContext/401. Được dùng bởi/tại: Mọi route và WS/stream nhạy cảm. Kiểm chứng: Khóa sai/revoke không xem được ảnh/event. 

**File:** `backend/alerts/events.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Tạo event một lần sau confirmed. Thành phần chính: EventService.create_once; acknowledge. I/O: State transition → event_id/record. Được dùng bởi/tại: pipeline; routes; outbox; ws. Kiểm chứng: Một episode chỉ một event; ack idempotent. 

**File:** `backend/alerts/outbox.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Worker gửi có retry và hết hạn. Thành phần chính: enqueue; run_due; mark_result. I/O: Event + device active → dispatch status. Được dùng bởi/tại: EventService; FcmSender. Kiểm chứng: Unique event/device; tối đa 3 retry; không block AI. 

**File:** `backend/alerts/fcm.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Sender FCM: smoke T1, adapter đầy đủ T3. Thành phần chính: FcmSender.send_test/send_fall. I/O: PushEndpoint + event → provider message ID/error. Được dùng bởi/tại: scripts/test_push.py; outbox. Kiểm chứng: Accepted phân biệt delivered; secret chỉ backend. 

**File:** `scripts/test_push.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Thử FCM riêng, không giả kết quả AI. Thành phần chính: main --device-id. I/O: Device DB/test payload → FCM accepted/error. Được dùng bởi/tại: FcmSender. Kiểm chứng: Điện thoại nhận test message, không cần pose. 

**File:** `tests/test_api.py` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Contract/API với mock AI. Thành phần chính: test_status; test_protected_preview; test_ack. I/O: TestClient + mock pipeline → JSON/HTTP. Được dùng bởi/tại: pytest; routes. Kiểm chứng: Không đòi camera/GPU để chạy contract tests. 

**File:** `tests/test_alerts.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Event uniqueness và lỗi gửi có retry. Thành phần chính: test_same_episode_once; test_retry_ttl. I/O: Fake sender/clock → event/outbox. Được dùng bởi/tại: pytest; EventService/Outbox. Kiểm chứng: Crash/retry không sinh event_id mới; accepted không retry. 

**File:** `runtime/fallguard.db` — Chỉnh sửa file đã có; SV2 chịu trách nhiệm. Chức năng: Dữ liệu runtime do schema/storage sinh. Thành phần chính: SQLite database, không viết tay. I/O: Installation/device/config/event/outbox → persistence. Được dùng bởi/tại: storage.py và pairing CLI. Kiểm chứng: Restart giữ pairing; file không commit, không chứa tài khoản. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 11 schema/EventService, ngày 12 FCM registration/sender, ngày 13 outbox/ack, ngày 14 test thật và ngày 15 tích hợp. Khi SV1 đang tuning, tạo transition fixture có nhãn thử để SV3 nhận UI nhưng không đưa vào metric. Không chờ video stream hoạt động hoàn hảo mới gửi push: event không phụ thuộc viewer. 

#### G. Kiểm thử sau khi hoàn thành 

- → 

- Gọi create_once hai lần cùng episode_id một event_id/một outbox per device. Nếu DB lỗi, không phát một event “mồ côi” chỉ qua WS. Ack hai lần trả cùng trạng thái. 

- Fake sender timeout, mạng tắt, sai credentials, endpoint unregistered: worker xử lý đúng trạng thái, API và FPS AI vẫn phản hồi. Pending hết TTL không gửi alarm cũ khi Internet quay lại rất muộn. 

- App mở: WS+FCM cùng event không tạo hai foreground alarm nhờ coordinator. App nền/khóa: có system notification; app tắt thông thường có thông báo theo khả năng OS. Force-stop được ghi là giới hạn, không tăng retry vô hạn. 

#### H. Deliverables và thao tác demo 

EventService/outbox/FCM hoàn chỉnh, schema/API events/ack/push đăng ký, test_alerts và contract tests. Người dùng nhận cảnh báo thật và xem lại event sau WS reconnect. Demo: đóng viewer, phát video ngã, điện thoại vẫn nhận push; ngắt Internet để thấy FCM unavailable nhưng event vẫn có thể đồng bộ khi mở app. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi ít nhất một ngã từ RTSP tạo push trên điện thoại thật; event không lặp theo frame, retry không chặn AI. Nếu thiếu giờ, chỉ gửi text notification, bỏ ảnh/clip và delivery receipt; không bỏ outbox uniqueness/TTL hoặc thay push bằng Telegram. Giữ một device P0 nếu chưa thử fanout nhiều máy. 

### 6.3.3. Tuần 3 — SV3: FCM các trạng thái app, âm thanh và tắt cảnh báo 

#### A. Mục tiêu của tuần 

Nối WS/FCM/REST vào một coordinator, có âm thanh foreground, system sound background, nút tắt/ack và setting âm thanh. Dành 6 giờ FCM/lifecycle, 4 giờ âm thanh/resource, 4 giờ coordinator/dedup, 4 giờ test máy thật và 2 giờ tích hợp. 

#### B. Kiến thức cần học 

- Học FirebaseMessaging.onMessage, onMessageOpenedApp, getInitialMessage, token refresh; hiểu notification+data khi nền do OS hiển thị. Background handler không được tạo UI và không tự tạo notification thứ hai khi notification payload đã có. 

- Học Android notification channels và POST_NOTIFICATIONS; channel sound không tùy ý sửa sau khi tạo, người dùng kiểm soát cuối cùng. Học raw resource/icon/keep rules để build không làm mất sound. 

- Học audioplayers asset, stop/dispose và timer tối đa 10 giây; không phát bằng thread UI vòng lặp. Tách nút tắt âm cục bộ khỏi ack gửi backend. 

- Học race giữa WS/FCM, seen-event store theo installation và xử lý resume. Không cần học foreground service, full-screen intent hoặc bypass DND cho MVP. 

#### C. Áp dụng trực tiếp vào project 

NotificationService đăng ký endpoint sau pairing, refresh cập nhật đúng device qua ApiClient; coordinator nhận FallEvent mọi nguồn và kiểm installation/event_id. AlarmService chỉ phát khi foreground và người dùng bật âm. Background dùng hai channel alert/silent mà FcmSender của SV2 chọn; Android resource file là phần không thể chỉ viết trong Dart. 

#### D. Công việc lập trình cụ thể 

- T1. Hoàn thiện tạo hai channel ngay lúc mở app và xin permission. Cập nhật manifest metadata/icon, bảo đảm default channel đúng. Nếu user từ chối quyền, home hiện trạng thái và đường mở Settings, không khóa toàn bộ app. 

- T2. Nối onMessage→coordinator; chạm notification qua onMessageOpenedApp/getInitialMessage mở đúng event. Khi payload thiếu thông tin chi tiết, gọi GET /api/v1/events để tìm event_id bằng device secret, không đưa secret vào push. 

- T3. Thêm audio asset ở Flutter/raw, AlarmService play/stop/timer/dispose. Foreground chỉ một banner và một audio player; không bật thêm local notification sound cùng lúc. Nút Tắt âm dừng ngay cả khi backend đang offline. 

- T4. Dedup theo event_id và installation_id; seen store bền qua restart có giới hạn số lượng; REST replay không hú toàn bộ lịch sử. App pause ngừng nhận WS cho alarm UI; FCM vẫn do OS theo cơ chế chuẩn. 

- T5. Khi sound_enabled đổi, cập nhật local setting và backend device; backend chọn silent channel cho thông báo tương lai. Nếu update API lỗi, báo pending và không hứa background đã tắt âm trên server. 

- T6. Viết test coordinator bằng fake services cho duplicate/wrong installation/mute; sau đó thử máy thật 6 trạng thái ở Chương 11. Nhận một event AI thật qua RTSP cùng SV1/SV2. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `mobile/pubspec.yaml` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Dependency Flutter và asset audio. Thành phần chính: dependencies; flutter.assets. I/O: Package constraints → Flutter build. Được dùng bởi/tại: flutter pub get. Kiểm chứng: Một bộ package tương thích, asset tìm được. 

**File:** `mobile/pubspec.lock` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Khóa phiên bản package app. Thành phần chính: Generated lock. I/O: pubspec → resolved versions. Được dùng bởi/tại: Flutter SDK. Kiểm chứng: Máy thứ hai pub get ra cùng bộ dependency. 

**File:** `mobile/lib/main.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Khởi tạo app/Firebase/services và lifecycle. Thành phần chính: main; FallGuardApp. I/O: DeviceStore → pair/home; resume sync. Được dùng bởi/tại: Flutter entry point. Kiểm chứng: Mở app không cần tài khoản; không init FCM hai lần. 

**File:** `mobile/lib/models.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Parser status/event/pairing có kiểm trường. Thành phần chính: SystemStatus.fromJson; FallEvent.fromJson/fromPushData. I/O: JSON REST/WS/FCM → Dart models. Được dùng bởi/tại: Screens; coordinator. Kiểm chứng: Sai schema/optional field không crash UI. 

**File:** `mobile/lib/services/api_client.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: HTTP header, timeout và đồng bộ event. Thành phần chính: getStatus; pair; configureCamera; listEvents; ack. I/O: DTO/device secret → response typed. Được dùng bởi/tại: Home/Pair/Alert screens. Kiểm chứng: 401 chuyển trạng thái cần ghép; không tự retry claim bừa. 

**File:** `mobile/lib/services/device_store.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Lưu khóa và installation trong secure storage. Thành phần chính: savePairing; loadPairing; clearPairing. I/O: Claim result → storage an toàn. Được dùng bởi/tại: main; ApiClient; NotificationService. Kiểm chứng: Restart còn ghép; unpair xóa sạch khóa/cursor. 

**File:** `mobile/lib/services/ws_client.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: WS có auth và backoff theo lifecycle. Thành phần chính: connect; events; reconnect; dispose. I/O: Base URL/secret → event stream. Được dùng bởi/tại: Home; AlertCoordinator. Kiểm chứng: Không tạo socket trùng sau resume; retry có trần. 

**File:** `mobile/lib/services/notification_service.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: FCM setup, permission, channel và token refresh. Thành phần chính: initialize; registerEndpoint; onMessage; onOpen. I/O: RemoteMessage/token → coordinator/API. Được dùng bởi/tại: main; AlertCoordinator. Kiểm chứng: Foreground/background/terminated thường nhận đúng, không nhận nhầm installation. 

**File:** `mobile/lib/services/alert_coordinator.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Một điểm nhận event từ WS/FCM/REST. Thành phần chính: handleEvent; acknowledge; markSeen. I/O: FallEvent + app state → UI/audio một lần. Được dùng bởi/tại: WsClient; NotificationService; screens. Kiểm chứng: Cùng event từ hai kênh chỉ báo một lần ở foreground. 

**File:** `mobile/lib/services/alarm_service.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Audio foreground có dừng và timeout. Thành phần chính: playForEvent; stop; dispose. I/O: Asset và event_id → audio player. Được dùng bởi/tại: AlertCoordinator; AlertScreen. Kiểm chứng: Stop ngay; tối đa 10 s; không phát khi sound off. 

**File:** `mobile/lib/screens/home_screen.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: RTSP form, status, camera, setting và thử push. Thành phần chính: HomeScreen; refresh; configureCamera. I/O: Status/camera config → UI. Được dùng bởi/tại: ApiClient; WsClient; CameraView. Kiểm chứng: Phân biệt camera connected và AI ready; password che mặc định. 

**File:** `mobile/lib/screens/alert_screen.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Thông tin sự kiện, tắt âm và ack. Thành phần chính: AlertScreen; onSilence; onAcknowledge. I/O: FallEvent → UI/action. Được dùng bởi/tại: AlertCoordinator; ApiClient. Kiểm chứng: Nút tắt âm/đã xem hoạt động kể cả API tạm lỗi. 

**File:** `mobile/lib/firebase_options.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Cấu hình Firebase sinh bởi FlutterFire. Thành phần chính: DefaultFirebaseOptions.currentPlatform. I/O: Firebase app config → initializeApp. Được dùng bởi/tại: main; notification service. Kiểm chứng: Đúng project/applicationId của APK. 

**File:** `mobile/android/app/google-services.json` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Config client Android do Firebase cung cấp. Thành phần chính: Generated config, không phải admin key. I/O: Android applicationId → SDK setup. Được dùng bởi/tại: Gradle Google services plugin. Kiểm chứng: Không nhầm file service account. 

**File:** `mobile/android/app/build.gradle.kts` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Android SDK/plugin/applicationId. Thành phần chính: android; plugins; buildTypes. I/O: Flutter/Android deps → APK. Được dùng bởi/tại: flutter build/run. Kiểm chứng: Không thay applicationId sau cấu hình FCM. 

**File:** `mobile/android/app/src/main/AndroidManifest.xml` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Internet, notification permission và metadata. Thành phần chính: INTERNET; POST_NOTIFICATIONS; default channel/icon. I/O: Manifest → Android runtime permissions. Được dùng bởi/tại: APK/FCM SDK. Kiểm chứng: Quyền runtime được xin; default channel tồn tại. 

**File:** `mobile/assets/audio/fall_alarm.wav` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Âm ngắn cho foreground có quyền sử dụng. Thành phần chính: WAV asset; không có hàm. I/O: Bytes audio → AlarmService. Được dùng bởi/tại: pubspec.yaml; audioplayers. Kiểm chứng: Nghe rõ trên điện thoại; cùng nội dung raw sound. 

**File:** `mobile/android/app/src/main/res/raw/fall_alarm.wav` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Âm của Android notification channel. Thành phần chính: Raw resource name fall_alarm. I/O: Bytes audio → Android channel. Được dùng bởi/tại: notification_service.dart; FCM. Kiểm chứng: Channel sound hoạt động lúc khóa màn hình. 

**File:** `mobile/android/app/src/main/res/drawable/ic_stat_fall.xml` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Icon notification đơn sắc đúng resource. Thành phần chính: Vector drawable. I/O: Resource → notification icon. Được dùng bởi/tại: Manifest; notification service. Kiểm chứng: Notification không mất icon trên máy thật. 

**File:** `mobile/android/app/src/main/res/raw/keep.xml` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Giữ raw sound/icon nếu shrink resource. Thành phần chính: tools:keep. I/O: 

Resource list → build retention. Được dùng bởi/tại: Android resource shrinker. Kiểm chứng: Release test không bị loại sound/icon; debug vẫn build. 

**File:** `mobile/test/models_test.dart` — Chỉnh sửa file đã có; SV3 chịu trách nhiệm. Chức năng: Parser schema và dữ liệu thiếu. Thành phần chính: FallEvent/status parsing tests. I/O: JSON fixtures → Dart models/error. Được dùng bởi/tại: flutter test. Kiểm chứng: Schema cũ/sai không làm app crash. 

**File:** `mobile/test/alert_coordinator_test.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Dedup và lifecycle/audio bằng fake service. Thành phần chính: testDuplicateSources; testWrongInstallation; testMute. I/O: Event/app state → số lần UI/audio. Được dùng bởi/tại: flutter test. Kiểm chứng: WS+FCM cùng event chỉ 1 foreground alarm; không nhận sai backend. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 11 channels/permission, ngày 12 coordinator/FCM mapping, ngày 13 audio, ngày 14 background/terminated test, ngày 15 toàn tuyến. Dùng notifications/test của SV2 để test mobile nhanh trước; vòng nghiệm thu tuần phải có AI thật. Nếu sender chưa xong, giữ test_push tuần 1, nhưng hoàn tất device registration trước ngày 14. 

#### G. Kiểm thử sau khi hoàn thành 

- Foreground WS và FCM cùng event theo hai thứ tự → một audio lần; event mới có ID khác → cảnh báo mới. Wrong installation bị bỏ. Hủy ghép xong không tiếp tục xem ảnh, đăng ký push hay replay event cũ. 

- Thu nhỏ, khóa màn hình, process tắt thông thường: notification xuất hiện theo OS, sound đúng channel. Chạm thông báo mở đúng AlertScreen; không có audio vòng vô hạn tự chạy khi app nền. 

- Tắt âm foreground dừng ngay; sound off tạo thông báo silent sau khi server xác nhận cập nhật; thử notification denied, volume=0 và DND để thấy giới hạn. Không coi không nghe tiếng trong DND là lý do ép quyền đặc biệt. 

#### H. Deliverables và thao tác demo 

App có push thật, alarm foreground, sound background, tắt/ack, settings và coordinator tests. Hai resource audio/icon có trong APK; permission được xin đúng. Demo: app mở nhận một alarm; thu nhỏ nhận system notification; mở event và bấm tắt/đã xem; giữ người nằm không báo lại liên tục. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi push và sound đã thử trên điện thoại thật ít nhất foreground/background/khóa màn hình, cùng event không lặp foreground. Nếu thiếu giờ, dùng màn home+modal alert, bỏ animation/history phức tạp; giữ permission, channels, endpoint update, dedup và stop audio. Không đưa iOS vào tuần 3. 

### 6.4.1. Tuần 4 — SV1: Đánh giá khóa, kiểm tra ngã thật trong video và hiệu năng 

#### A. Mục tiêu của tuần 

Đóng băng AI được chọn, chạy held-out test và kiểm tra camera thật; đo event-level metrics/AI FPS, sửa lỗi tái hiện được. Không thay mô hình lớn ở cuối dự án. Dành 6 giờ test khóa, 5 giờ giảm lỗi P0, 4 giờ tốc độ/chất lượng pose, 3 giờ bàn giao và 2 giờ dự phòng. 

#### B. Kiến thức cần học 

- Ôn one-to-one event matching, FA/hour và latency denominator. Hiểu 0 FP trên một video vài phút không chứng minh tin cậy nhiều ngày; mẫu nhỏ phải hiện số tuyệt đối bên cạnh tỷ lệ. 

- Học domain shift: góc camera, ánh sáng, trang phục, đồ che khác dataset. Đạt mức chỉ ra được điều kiện gây hỏng và test lại trên môi trường demo, không suy hiệu quả cho mọi người cao tuổi. 

- Học profiling cơ bản bằng perf_counter, tách thời gian pose/feature/scorer/state; giảm imgsz/rate preview trước khi làm ONNX/TensorRT. Không cần học quantization production nếu CPU đã đạt mục tiêu. 

#### C. Áp dụng trực tiếp vào project 

evaluation/final.json chứa số đo thật từ evaluate.py/clip replay, không phải một tính năng mới. Config/model/meta cuối được bàn giao cho pipeline; SV2 đóng gói lệnh chạy và SV3 kiểm message/độ trễ cùng cấu hình đã khóa. E tuần 4 là phạm vi kiểm tra/sửa khi lỗi, không có nghĩa phải viết lại mọi file được liệt kê. 

#### D. Công việc lập trình cụ thể 

- T1. Khóa config/model_id và danh sách test; chạy đúng một vòng held-out trước khi sửa từ test. Nếu phát hiện lỗi P0 buộc sửa, dùng tập sửa lỗi riêng và ghi lần đánh giá tiếp theo không còn hoàn toàn unseen, không lặp tuning mà gọi là test mới. 

- T2. Chạy ngã/ADL, báo TP/FP/FN, recall/precision/F1, số phút ADL và FA/hour. Kiểm tra model A/B đã chọn thật đang load, không phải mock; labels/video phải khớp. 

- T3. Test RTSP thật cùng SV2; kiểm camera nhìn đủ toàn thân và độ tin cậy khớp ở tư thế thấp. Chỉ dùng clip đã có hoặc tình huống mô phỏng an toàn trên đệm bởi người khỏe; không yêu cầu người cao tuổi ngã thử. 

- T4. Profile trên máy demo; hạ input/preview nếu cần và đo lại các ca bắt buộc. Nếu tốc độ chưa đạt đủ 10 Hz cho nhánh A, ưu tiên B hoặc cấu hình sampling đã kiểm chứng, không nhân bản frame để làm đủ cửa sổ. 

- T5. Bàn giao weights/hash/meta/config cuối; load trên CPU khi GPU không sẵn sàng. Cùng nhóm chạy startup sạch và demo đầy đủ, không sửa threshold sát giờ chỉ để một clip báo đẹp. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `configs/ai.yaml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Model, cửa sổ và ngưỡng luật/xác nhận. Thành phần chính: mode; sample_hz; thresholds. I/O: YAML → detector/state machine config. Được dùng bởi/tại: backend/ai/factory.py; state_machine.py. Kiểm chứng: A/B đổi bằng config; không hardcode ngưỡng. 

**File:** `configs/train.yaml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Seed, split, batch và siêu tham số train. Thành phần chính: seed; epochs; learning_rate. I/O: Cấu hình → dataset/train/evaluate. Được dùng bởi/tại: training/train.py. Kiểm chứng: Seed/split/feature_version được khóa cùng checkpoint. 

**File:** `backend/ai/pose.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Load pose một lần, box/keypoint và track ID. Thành phần chính: PoseEstimator.estimate/reset/close. I/O: Frame BGR → tracked poses COCO17. Được dùng bởi/tại: pretrained và trained adapters. Kiểm chứng: Không có người/ID/khớp thiếu không crash. 

**File:** `backend/ai/buffer.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Cửa sổ theo track/session có timestamp. Thành phần chính: PoseBuffer.add/window/reset. I/O: Pose + time → 30 mốc/quality. Được dùng bởi/tại: Cả hai detector và feature extractor. Kiểm chứng: Không nối qua gap; không đếm trùng frame_id. 

**File:** `backend/ai/features.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Feature/chuẩn hóa dùng chung train và runtime. Thành phần chính: extract_kinematics; normalize_window. I/O: Pose window → kinematics + [30,54]. Được dùng bởi/tại: training/extract, dataset; scorer A/B. Kiểm chứng: Cùng clip tạo feature giống offline/online. 

**File:** `backend/ai/pretrained.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Scorer luật dùng pose pretrained. Thành phần chính: RuleScorer.score; PretrainedDetector.process. I/O: Feature/history → candidate rule_score. Được dùng bởi/tại: factory; pipeline qua interface. Kiểm chứng: Không kết luận ngã từ một pose nằm. 

**File:** `backend/ai/trained.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Adapter load TCN và kiểm metadata. Thành phần chính: TrainedDetector.process; load_checkpoint. I/O: Window [30,54] → uncalibrated_model_score. Được dùng bởi/tại: factory; pipeline qua interface. Kiểm chứng: A/B đổi config; checkpoint thiếu quay B rõ ràng. 

**File:** `backend/ai/state_machine.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Xác nhận, latch episode, recovery. Thành phần chính: FallStateMachine.update/reset. I/O: Candidate + monotonic timestamp → transition. Được dùng bởi/tại: pipeline; tests/test_ai_sequence.py. Kiểm chứng: Giữ nằm không báo lặp; gap không tăng confirmation. 

**File:** `backend/ai/factory.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Tạo mock/B/A theo config. Thành phần chính: create_detector(settings). I/O: Config/model path → FallDetector. Được dùng bởi/tại: backend/main.py. Kiểm chứng: Không load model mỗi request; báo lỗi rõ. 

**File:** `backend/ai/tcn.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Kiến trúc phân loại chuỗi nhỏ dùng chung. Thành phần chính: FallTCN.forward. I/O: Tensor [N,54,30] → logits [N,1]. Được dùng bởi/tại: training/train; trained.py. Kiểm chứng: Forward CPU chạy được; shape có kiểm tra. 

**File:** `data/manifests/clips.csv` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Manifest dữ liệu nguồn có provenance. Thành phần chính: clip_id,path,group_id,subject_id,camera_id,fps. I/O: Metadata clip → loader/split. Được dùng bởi/tại: manifest.py; extract.py. Kiểm chứng: FPS/nhóm có giá trị xác minh; unknown được ghi rõ. 

**File:** `data/labels/intervals.csv` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Nhãn onset/impact/end và hard negative. Thành phần chính: clip_id,onset_s,impact_s,end_s,label. I/O: Quan sát video → interval đã soát. Được dùng bởi/tại: training/extract; evaluate. Kiểm chứng: Không gắn mọi frame clip ngã là positive. 

**File:** `training/extract.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Trích pose/features đúng timestamp. Thành phần chính: extract_clip; save_features. I/O: RGB/MP4 + labels → .npz có timestamps. Được dùng bởi/tại: PoseEstimator; normalize_window. Kiểm chứng: Có thể resume; không tải lại model mỗi clip. 

**File:** `data/features/*.npz` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Cache sinh tự động cho từng clip. Thành phần chính: features,timestamps,validity,labels. I/O: Clip + pose → numpy arrays. Được dùng bởi/tại: training/dataset.py. Kiểm chứng: Shape/thời gian khớp; không commit data lớn. 

**File:** `training/dataset.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Loader cửa sổ, nhãn, augment chỉ train. Thành phần chính: FallWindowDataset.__getitem__. I/O: Cache + split → X [54,30], y, sample weight. Được dùng bởi/tại: DataLoader trong train/evaluate. Kiểm chứng: Val/test không augment; scaler chỉ fit train nếu dùng. 

**File:** `training/evaluate.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Đánh giá window và episode theo cùng logic runtime. Thành phần chính: evaluate_windows; replay_events; summarize. I/O: Model/B + clips → precision/recall/FP/latency. Được dùng bởi/tại: Cả hai nhánh; configs/ai.yaml. Kiểm chứng: One-to-one matching event; bỏ is_test. 

**File:** `scripts/ai_smoke.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Chạy 1 clip độc lập để thấy pose/status. Thành phần chính: main -- source --mode. I/O: Video/camera → preview/terminal counters. Được dùng bởi/tại: Detector interface. Kiểm chứng: Không cần backend/app để debug AI. 

**File:** `models/yolo11n-pose.pt` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Weights pose tải từ nguồn chính thức. Thành phần chính: Binary model, không tự viết code. I/O: Frame → pretrained pose. Được dùng bởi/tại: PoseEstimator. Kiểm chứng: Ghi nguồn/hash, load được offline sau tải. 

**File:** `models/fall_tcn.pt` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Checkpoint nhánh A sinh từ training. Thành phần chính: state_dict do torch.save. I/O: Model đã train → adapter CPU/GPU. Được dùng bởi/tại: TrainedDetector. Kiểm chứng: Load lại cho output gần như tương đương; không giả file khi train chưa xong. 

**File:** `models/fall_tcn.meta.json` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Hợp đồng weights/feature và threshold validation. Thành phần chính: feature_version; sample_hz; class_map; seed. I/O: Training/validation → metadata. Được dùng bởi/tại: TrainedDetector.load_checkpoint. Kiểm chứng: Từ chối shape/version không khớp. 

**File:** `evaluation/cases.csv` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Danh sách ca test có ground truth/tập dữ liệu. Thành phần chính: case_id,clip_id,split,expected,interval. I/O: Video kiểm chứng → test cases. Được dùng bởi/tại: training/evaluate; cả nhóm. Kiểm chứng: Có ngã, ADL, nằm sẵn, che khuất; không dùng test tuning. 

**File:** `evaluation/final.json` — Tạo mới; SV1 chịu trách nhiệm. Chức năng: Kết quả kỹ thuật test khóa cuối cùng. Thành phần chính: TP,FP,FN,FA/hour,latency,FPS,limitations. I/O: Held-out test và demo → chỉ số đo. Được dùng bởi/tại: Nghiệm thu MVP. Kiểm chứng: Ghi rõ chưa đo nếu thiếu mẫu, không điền ước lượng thành kết quả. 

**File:** `tests/test_ai_sequence.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV1 chịu trách nhiệm. Chức năng: Test lỗi temporal và xác nhận meaningful. Thành phần chính: test_gap_resets; test_no_repeat; test_sit_vs_fall. I/O: Chuỗi timestamp/pose giả → transitions. Được dùng bởi/tại: pytest; state machine/features. Kiểm chứng: Không test từng getter; kiểm ca rớt mạng/lặp/góc thiếu. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 16 khóa và test; ngày 17 sửa lỗi quan trọng; ngày 18 thử camera thật; ngày 19 profile/regression; ngày 20 chạy sạch/bàn giao. Chỉ train lại A nếu model đó đã là MVP và một lỗi có nguyên nhân/dữ liệu sửa rõ; nếu không, giữ B. SV1 hỗ trợ SV2 nếu status DEGRADED không tương ứng chất lượng mẫu. 

#### G. Kiểm thử sau khi hoàn thành 

- Đo metric có số lượng sự kiện/ADL phút và cửa sổ matching đã định ở Chương 11. Test nằm sẵn, ngồi, cúi, mất frame/khớp, slow fall và ngã ngoài vùng; ca ngoài phạm vi phải được mô tả đúng. 

- Chạy 20–30 phút ở cấu hình demo; FPS không suy từ preview, latency không gồm warmup tùy ý bị giấu. Không crash/NaN khi không có người. 

- Restart backend/model, config mode khớp model_id; checksum/meta và input_dim đúng. Model file bị thiếu/không tương thích → fallback B rõ ràng hoặc AI ERROR, không alarm giả. 

#### H. Deliverables và thao tác demo 

evaluation/final.json có kết quả thật, model/config cuối đã khóa, test regressions, lệnh ai_smoke và adapter chạy được. Demo ngày 20: một clip ngã qua RTSP tạo một event, hard negative không alarm trong bộ đã thử, AI hồi phục đúng sau reconnect. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi pipeline AI hoạt động thực, số liệu có mẫu và không đánh tráo độ chính xác pose thành ngã. Nếu không đạt chỉ số mong muốn, nêu kết quả thực và thu hẹp điều kiện demo; không tự ghi 95% khi chưa đo. Giữ đủ công việc P0 để toàn tuyến chạy, bỏ ONNX/TensorRT/multi-person nâng cao. 

### 6.4.2. Tuần 4 — SV2: Ổn định RTSP, restart, độ trễ và gói backend chạy lại được 

#### A. Mục tiêu của tuần 

Backend chạy bền cho phiên demo, mất kết nối tự phục hồi, quyền thiết bị đúng, outbox không gửi alarm cũ vô hạn và có lệnh khởi động sạch. Dành 5 giờ RTSP/network, 5 giờ event/notification lỗi, 4 giờ latency/CPU, 4 giờ gói và test hồi quy, 2 giờ dự phòng. 

#### B. Kiến thức cần học 

- Ôn shutdown/thread ownership/timeouts và trạng thái stale; học phân biệt lỗi camera, AI, API và cloud để sửa đúng lớp. 

- Học retry race/idempotency khi restart: đọc pending chưa hết hạn; accepted không gửi lại; DB transaction bảo toàn event. Không cần thiết kế high availability. 

- Học đo latency nhiều mốc và đồng bộ clock; bảo vệ secret khi chia lệnh chạy. README chỉ cần giúp cài/chạy/debug phần mềm, không chuyển thành báo cáo hành chính. 

#### C. Áp dụng trực tiếp vào project 

Các sửa đổi tập trung reader/pipeline/outbox/routes và config; measure_e2e tính từ mốc kiểm thử. README/lock/config là bộ để người khác chạy lại backend. Phối hợp SV3 xác minh app chỉ ra lỗi đúng và pairing vẫn bền sau restart. 

#### D. Công việc lập trình cụ thể 

- T1. Test camera RTSP thật: URL sai, mất mạng 10/60 giây, nguồn camera bật lại; kiểm reset session và warmup. Chặn reader cũ còn sống khi bấm đổi nguồn liên tục; debounce hoặc khóa lệnh camera. 

- T2. Test restart backend khi event pending/accepted, hết TTL, khi device revoke và khi FCM endpoint thay. Event không tạo lại từ trạng thái nằm sau restart; pending cũ hết hạn không gửi. 

- T3. Đo GET status/WS trong khi AI và MJPEG hoạt động; tách preview, giảm encode/rate trước. Nếu pure Python làm loop nghẽn, chuyển tính toán cần thiết ra process chỉ khi lỗi đo được và đủ giờ; không mở nhiều Uvicorn worker. 

- T4. Chạy pytest cần thiết và các ca toàn tuyến của Chương 11; kiểm auth trên mọi route/WS/preview, code dùng lại/expired và revoke. Test không có Internet vẫn AI + foreground LAN theo thiết kế. 

- T5. Khóa requirement versions, chuẩn bị runtime DB tự tạo mới, credentials ngoài repo, lệnh startup/pairing/test. Thử trong venv mới hoặc máy khác; giữ installer Windows/auto update ngoài P0. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `pyproject.toml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Khai báo package Python và dải Python 3.11. Thành phần chính: project; tool.pytest.ini_options. I/O: Không có hàm; đầu vào metadata, đầu ra môi trường cài được. Được dùng bởi/tại: pip và pytest. Kiểm chứng: Import backend/training từ root ổn định. 

**File:** `requirements.lock.txt` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Khóa dependency sau smoke test. Thành phần chính: pip freeze/pip install -r. I/O: Bộ package đã kiểm tra → phiên bản chính xác. Được dùng bởi/tại: Mọi laptop backend/AI. Kiểm chứng: Cài lại trên môi trường sạch, import được. 

**File:** `.gitignore` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Loại secret, runtime, data lớn và build khỏi git. Thành phần chính: Các pattern. I/O: Đường dẫn nhạy cảm → bỏ theo dõi git. Được dùng bởi/tại: Repository. Kiểm chứng: .env, credential JSON, runtime DB không được commit. 

**File:** `README.md` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Lệnh cài/chạy và thao tác vận hành MVP. Thành phần chính: Các lệnh backend/pairing/Flutter. I/O: Máy mới → chạy demo; không có báo cáo học phần. Được dùng bởi/tại: Cả nhóm và người chạy thử. Kiểm chứng: Có lệnh smoke và giới hạn bản chạy đúng thực tế. 

**File:** `configs/app.yaml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Timeout, camera, rate preview, runtime DB. Thành phần chính: Config keys tại Chương 2. I/O: YAML/env → AppSettings. Được dùng bởi/tại: backend/config.py. Kiểm chứng: Giá trị lỗi bị báo lúc startup. 

**File:** `deploy/mediamtx.yml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: RTSP server phục vụ video thử nội bộ. Thành phần chính: paths.fall_demo. I/O: Publisher FFmpeg → RTSP endpoint. Được dùng bởi/tại: MediaMTX độc lập. Kiểm chứng: Backend đọc được cùng stream bằng RTSP. 

**File:** `backend/main.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Tạo FastAPI app và lifecycle worker. Thành phần chính: create_app(); lifespan(). I/O: Settings → app; startup/shutdown worker. Được dùng bởi/tại: Uvicorn. Kiểm chứng: Một worker, start/stop không nhân đôi camera. 

**File:** `backend/camera/reader.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Đọc RTSP/video/webcam, reconnect theo phiên. Thành phần chính: CameraReader.start/read_latest/stop; _capture_loop. I/O: Nguồn video → FramePacket/status. Được dùng bởi/tại: backend/pipeline.py. Kiểm chứng: Sai URL không treo API; tự nối lại; release đúng thread. 

**File:** `backend/camera/latest.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Bộ đệm frame/JPEG mới nhất dung lượng hữu hạn. Thành phần chính: LatestValue.replace/wait_newer/get. I/O: Frame mới → snapshot thread-safe. Được dùng bởi/tại: reader, pipeline, api/stream.py. Kiểm chứng: Không tích lũy frame; viewer không lấy mất frame AI. 

**File:** `backend/pipeline.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Ghép capture, detector, state machine và event service. Thành phần chính: Pipeline.start/stop; _infer_loop. I/O: FramePacket → status/transition/cache. Được dùng bởi/tại: main; routes; stream. Kiểm chứng: Inference không chặn API; reset khi đổi session. 

**File:** `backend/api/routes.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Health/status/camera/events/ack/test endpoint. Thành phần chính: health; get_status; set_camera; ack_event. I/O: HTTP DTO và device context → JSON. Được dùng bởi/tại: main; storage; pipeline. Kiểm chứng: Response/HTTP code khớp contract; có auth. 

**File:** `backend/api/ws.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Handshake có khóa và fanout event/status. Thành phần chính: ConnectionHub.connect/broadcast/disconnect. I/O: Event JSON → đúng kết nối installation. Được dùng bởi/tại: main; EventService. Kiểm chứng: Reconnect được; không lộ event cho khóa sai. 

**File:** `backend/api/stream.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: MJPEG và snapshot có xác thực. Thành phần chính: mjpeg_generator; get_preview. I/O: Cache JPEG → HTTP stream/ảnh. Được dùng bởi/tại: FastAPI; Flutter camera_view. Kiểm chứng: Ngắt viewer không dừng AI; frame stale có trạng thái. 

**File:** `backend/storage.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: SQLite giao dịch cho device/config/events/outbox. Thành phần chính: open_db; claim_code; save_event_once; list_events. I/O: Record typed → SQLite → record. Được dùng bởi/tại: pairing, auth, routes, EventService. Kiểm chứng: Transaction ngắn; không dùng connection sai thread. 

**File:** `backend/pairing.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: CLI sinh/thu hồi và claim code một lần. Thành phần chính: create_pairing; claim_pairing; revoke_device; main. I/O: Code 256 bit → device secret/installation. Được dùng bởi/tại: CLI; api/routes.py. Kiểm chứng: TTL và concurrent claim đúng; không cần tài khoản. 

**File:** `backend/auth.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Xác thực hash device secret và scope installation. Thành phần chính: 

require_device; verify_device_secret. I/O: Bearer secret → DeviceContext/401. Được dùng bởi/tại: Mọi route và WS/stream nhạy cảm. Kiểm chứng: Khóa sai/revoke không xem được ảnh/event. 

**File:** `backend/alerts/events.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Tạo event một lần sau confirmed. Thành phần chính: EventService.create_once; acknowledge. I/O: State transition → event_id/record. Được dùng bởi/tại: pipeline; routes; outbox; ws. Kiểm chứng: Một episode chỉ một event; ack idempotent. 

**File:** `backend/alerts/outbox.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Worker gửi có retry và hết hạn. Thành phần chính: enqueue; run_due; mark_result. I/O: Event + device active → dispatch status. Được dùng bởi/tại: EventService; FcmSender. Kiểm chứng: Unique event/device; tối đa 3 retry; không block AI. 

**File:** `backend/alerts/fcm.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Sender FCM: smoke T1, adapter đầy đủ T3. Thành phần chính: FcmSender.send_test/send_fall. I/O: PushEndpoint + event → provider message ID/error. Được dùng bởi/tại: scripts/test_push.py; outbox. Kiểm chứng: Accepted phân biệt delivered; secret chỉ backend. 

**File:** `scripts/publish_rtsp.sh` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Lệnh FFmpeg phát MP4 vào MediaMTX. Thành phần chính: ffmpeg -re -stream_loop -1. I/O: MP4 H.264 → RTSP server. Được dùng bởi/tại: Môi trường test RTSP. Kiểm chứng: Dùng real-time pacing, backend thực sự đọc rtsp://. 

**File:** `scripts/measure_e2e.py` — Tạo mới; SV2 chịu trách nhiệm. Chức năng: Tính độ trễ từ mốc kiểm thử. Thành phần chính: summarize_latency(samples). I/O: Timestamp đồng bộ → p50/p95 và sample count. Được dùng bởi/tại: Test kỹ thuật; evaluation/final.json. Kiểm chứng: Không trộn accepted với received; clock lệch bị loại. 

**File:** `tests/test_camera.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Test timeout/reconnect bằng fake capture. Thành phần chính: test_read_failure; test_new_session. I/O: Capture fake và clock → state/frame. Được dùng bởi/tại: pytest; CameraReader. Kiểm chứng: Không chờ camera thật trong unit test. 

**File:** `tests/test_pairing.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: TTL, claim hai lần và revoke. Thành phần chính: test_expired; test_concurrent_claim; test_revoke. I/O: Temp SQLite/code → HTTP/DB result. Được dùng bởi/tại: pytest; pairing/auth. Kiểm chứng: Code chỉ claim một lần, route ảnh/WS khóa sai bị chặn. 

**File:** `tests/test_api.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Contract/API với mock AI. Thành phần chính: test_status; test_protected_preview; test_ack. I/O: TestClient + mock pipeline → JSON/HTTP. Được dùng bởi/tại: pytest; routes. Kiểm chứng: Không đòi camera/GPU để chạy contract tests. 

**File:** `tests/test_alerts.py` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Event uniqueness và lỗi gửi có retry. Thành phần chính: test_same_episode_once; test_retry_ttl. I/O: Fake sender/clock → event/outbox. Được dùng bởi/tại: pytest; EventService/Outbox. Kiểm chứng: Crash/retry không sinh event_id mới; accepted không retry. 

**File:** `runtime/fallguard.db` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV2 chịu trách nhiệm. Chức năng: Dữ liệu runtime do schema/storage sinh. Thành phần chính: SQLite database, không viết tay. I/O: Installation/device/config/event/outbox → persistence. Được dùng bởi/tại: storage.py và pairing CLI. Kiểm chứng: Restart giữ pairing; file không commit, không chứa tài khoản. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các __init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 16 đọc lỗi tích hợp và đo, ngày 17 sửa RTSP/outbox, ngày 18 camera thật với SV1/SV3, ngày 19 môi trường sạch, ngày 20 chạy demo. Không thêm endpoint mới nếu không đóng một lỗi P0. Khi máy thật không sẵn sàng tạm dùng RTSP giả lập, nhưng phải ghi rõ phần camera thật chưa PASS thay vì đổi tên test. 

#### G. Kiểm thử sau khi hoàn thành 

- 20–30 phút chạy: API không chết, queue không tăng, RAM không tăng liên tục sau nhiều lần viewer reconnect. Reconnect camera theo backoff có trần, không busy loop. 

- Khóa sai/revoke không xem hình/event; device khác không sửa endpoint của nhau. Claim đồng thời/hết hạn test lại sau thay đổi storage. 

- Chạy CLI từ root repo với config/weights đã khóa, app ghép mới và nhận một alert thật; sau backend restart giữ pairing/installation. Tổng latency thực có p50/p95 hoặc ghi chưa đủ mẫu. 

#### H. Deliverables và thao tác demo 

Backend/config/lock/README chạy lại được, các test trọng yếu xanh, số đo latency và camera failure recovery. Người dùng cài app, nhập RTSP, nhận alarm và khôi phục sau mạng lỗi. Demo ngày 20 từ server chưa chạy, không dựa trạng thái process đã giữ từ nhiều ngày. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi tất cả đường P0 chạy và không có lỗi gây mất event do duplicate worker/session. Nếu trễ, giữ một camera/device, không ảnh/clip/history nâng cao, preview thấp; không bỏ push, pairing, temporal confirmation hoặc reconnect. Các ca chưa đạt được đánh dấu đúng trong checklist. 

### 6.4.3. Tuần 4 — SV3: APK có thể cài, kiểm vòng đời app và trải nghiệm lỗi 

#### A. Mục tiêu của tuần 

Có app-debug.apk cài được lên Android thử nghiệm, thao tác ghép/RTSP/cảnh báo/sound/ack rõ ràng, thử đủ vòng đời và giới hạn OS. Dành 6 giờ device matrix, 4 giờ sửa P0, 4 giờ APK/cài mới, 4 giờ toàn tuyến và 2 giờ dự phòng. 

#### B. Kiến thức cần học 

- Ôn Android foreground/background/terminated/force-stop; quyền notification và channel setting. Học vì sao swipe khỏi recent apps trên một số hãng có thể khác máy Android chuẩn. 

- Học build APK debug, cài mới/upgrade và ảnh hưởng secure storage/token refresh; không cần ký/phát hành cửa hàng trong 4 tuần. 

- Học kiểm tra trải nghiệm lỗi: trạng thái backend offline, camera offline và AI degraded phải khác nhau; pending ack/sound setting hiển thị trung thực. 

#### C. Áp dụng trực tiếp vào project 

Sửa main/lifecycle/WS/coordinator/screens theo lỗi đã tái hiện; test tự động tập trung parser/dedup, integration flow cơ bản. Push/sound thực phải kiểm trên thiết bị, không dùng test Flutter unit làm bằng chứng Android đã phát âm thanh. 

#### D. Công việc lập trình cụ thể 

- T1. Chạy ma trận foreground, Home/background, khóa màn hình, process bị tắt thông thường, force-stop, notification denied, sound off/DND. Ghi kết quả kỹ thuật vào checklist đang dùng, không tạo chức năng mới để vượt OS. 

- T2. Sửa duplicate listeners, audio không stop, event cũ hú lại, request timeout làm treo UI. Test unpair/re-pair khác backend; installation cũ không được lẫn event mới. 

- ● T3. Chạy flutter test và luồng pair/status/ack với backend thử; build APK debug, cài mới và mở lần đầu. Quyền notification/channel tạo trước khi nhận push. 

- T4. Kiểm debug manifest chỉ dành LAN HTTP; README của SV2 ghi đúng bản debug và điều kiện mạng. Không gắn credential vào dart-define; base URL lấy từ link ghép. 

- T5. Cùng SV1/SV2 đo video ngã → alarm mở app và push nền, thử RTSP thật, nút tắt và recovery. Build lại sau lần sửa cuối và xác minh APK đúng build, không gửi nhầm artifact cũ. 

#### E. File, thành phần và hợp đồng I/O 

**File:** `mobile/pubspec.yaml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Dependency Flutter và asset audio. Thành phần chính: dependencies; flutter.assets. I/O: Package constraints → Flutter build. Được dùng bởi/tại: flutter pub get. Kiểm chứng: Một bộ package tương thích, asset tìm được. 

**File:** `mobile/pubspec.lock` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Khóa phiên bản package app. Thành phần chính: Generated lock. I/O: pubspec → resolved versions. Được dùng bởi/tại: Flutter SDK. Kiểm chứng: Máy thứ hai pub get ra cùng bộ dependency. 

**File:** `mobile/lib/main.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Khởi tạo app/Firebase/services và lifecycle. Thành phần chính: main; FallGuardApp. I/O: DeviceStore → pair/home; resume sync. Được dùng bởi/tại: Flutter entry point. Kiểm chứng: Mở app không cần tài khoản; không init FCM hai lần. 

**File:** `mobile/lib/config.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Quy ước timeout/schema/base URL đã parse. Thành phần chính: AppConfig; parseServerUri. I/O: Pairing URI → validated URL. Được dùng bởi/tại: ApiClient; WsClient. Kiểm chứng: Reject scheme/host thiếu; không hardcode localhost. 

**File:** `mobile/lib/models.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Parser status/event/pairing có kiểm trường. Thành phần chính: SystemStatus.fromJson; FallEvent.fromJson/fromPushData. I/O: JSON REST/WS/FCM → Dart models. Được dùng bởi/tại: Screens; coordinator. Kiểm chứng: Sai schema/optional field không crash UI. 

**File:** `mobile/lib/services/api_client.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: HTTP header, timeout và đồng bộ event. Thành phần chính: getStatus; pair; configureCamera; listEvents; ack. I/O: DTO/device secret → 

response typed. Được dùng bởi/tại: Home/Pair/Alert screens. Kiểm chứng: 401 chuyển trạng thái cần ghép; không tự retry claim bừa. 

**File:** `mobile/lib/services/device_store.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Lưu khóa và installation trong secure storage. Thành phần chính: savePairing; loadPairing; clearPairing. I/O: Claim result → storage an toàn. Được dùng bởi/tại: main; ApiClient; NotificationService. Kiểm chứng: Restart còn ghép; unpair xóa sạch khóa/cursor. 

**File:** `mobile/lib/services/ws_client.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: WS có auth và backoff theo lifecycle. Thành phần chính: connect; events; reconnect; dispose. I/O: Base URL/secret → event stream. Được dùng bởi/tại: Home; AlertCoordinator. Kiểm chứng: Không tạo socket trùng sau resume; retry có trần. 

**File:** `mobile/lib/services/notification_service.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: FCM setup, permission, channel và token refresh. Thành phần chính: initialize; registerEndpoint; onMessage; onOpen. I/O: RemoteMessage/token → coordinator/API. Được dùng bởi/tại: main; AlertCoordinator. Kiểm chứng: Foreground/background/terminated thường nhận đúng, không nhận nhầm installation. 

**File:** `mobile/lib/services/alert_coordinator.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Một điểm nhận event từ WS/FCM/REST. Thành phần chính: handleEvent; acknowledge; markSeen. I/O: FallEvent + app state → UI/audio một lần. Được dùng bởi/tại: WsClient; NotificationService; screens. Kiểm chứng: Cùng event từ hai kênh chỉ báo một lần ở foreground. 

**File:** `mobile/lib/services/alarm_service.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Audio foreground có dừng và timeout. Thành phần chính: playForEvent; stop; dispose. I/O: Asset và event_id → audio player. Được dùng bởi/tại: AlertCoordinator; AlertScreen. Kiểm chứng: Stop ngay; tối đa 10 s; không phát khi sound off. 

**File:** `mobile/lib/screens/pair_screen.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Dán link và claim không tài khoản. Thành phần chính: PairScreen; submitPairing. I/O: Pairing link → DeviceStore/home. Được dùng bởi/tại: main; ApiClient. Kiểm chứng: Hết hạn/sai server có lỗi dễ hiểu. 

**File:** `mobile/lib/screens/home_screen.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: RTSP form, status, camera, setting và thử push. Thành phần chính: HomeScreen; refresh; configureCamera. I/O: Status/camera config → UI. Được dùng bởi/tại: ApiClient; WsClient; CameraView. Kiểm chứng: Phân biệt camera connected và AI ready; password che mặc định. 

**File:** `mobile/lib/screens/alert_screen.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Thông tin sự kiện, tắt âm và ack. Thành phần chính: AlertScreen; onSilence; onAcknowledge. I/O: FallEvent → UI/action. Được dùng bởi/tại: AlertCoordinator; ApiClient. Kiểm chứng: Nút tắt âm/đã xem hoạt động kể cả API tạm lỗi. 

**File:** `mobile/lib/widgets/camera_view.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Hiển thị MJPEG qua HTTP có header. Thành phần chính: CameraView; onLifecycleChanged. I/O: URL stream + secret → widget ảnh. Được dùng bởi/tại: HomeScreen; flutter_mjpeg. Kiểm chứng: Nền app ngắt view; AI backend vẫn chạy. 

**File:** `mobile/android/app/build.gradle.kts` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Android SDK/plugin/applicationId. Thành phần chính: android; plugins; buildTypes. I/O: Flutter/Android deps → APK. Được dùng bởi/tại: flutter build/run. Kiểm chứng: Không thay applicationId sau cấu hình FCM. 

**File:** `mobile/android/app/src/main/AndroidManifest.xml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Internet, notification permission và metadata. Thành phần chính: INTERNET; POST_NOTIFICATIONS; default channel/icon. I/O: Manifest → Android runtime permissions. Được dùng bởi/tại: APK/FCM SDK. Kiểm chứng: Quyền runtime được xin; default channel tồn tại. 

**File:** `mobile/android/app/src/debug/AndroidManifest.xml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Cho HTTP nội bộ chỉ trong APK debug. Thành phần chính: usesCleartextTraffic. I/O: Debug build config → HTTP LAN. Được dùng bởi/tại: Android debug build. Kiểm chứng: Release không vô tình mở cleartext toàn cục. 

**File:** `mobile/assets/audio/fall_alarm.wav` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Âm ngắn cho foreground có quyền sử dụng. Thành phần chính: WAV asset; không có hàm. I/O: Bytes audio → AlarmService. Được dùng bởi/tại: pubspec.yaml; audioplayers. Kiểm chứng: Nghe rõ trên điện thoại; cùng nội dung raw sound. 

**File:** `mobile/android/app/src/main/res/raw/fall_alarm.wav` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Âm của Android notification channel. Thành phần chính: Raw resource name fall_alarm. I/O: Bytes audio → Android channel. Được dùng bởi/tại: notification_service.dart; FCM. Kiểm chứng: Channel sound hoạt động lúc khóa màn hình. 

**File:** `mobile/android/app/src/main/res/drawable/ic_stat_fall.xml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Icon notification đơn sắc đúng resource. Thành phần chính: Vector drawable. I/O: Resource → notification icon. Được dùng bởi/tại: Manifest; notification service. Kiểm chứng: Notification không mất icon trên máy thật. 

**File:** `mobile/android/app/src/main/res/raw/keep.xml` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Giữ raw sound/icon nếu shrink resource. Thành phần chính: tools:keep. I/O: Resource list → build retention. Được dùng bởi/tại: Android resource shrinker. Kiểm chứng: Release test không bị loại sound/icon; debug vẫn build. 

**File:** `mobile/test/models_test.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Parser schema và dữ liệu thiếu. Thành phần chính: FallEvent/status parsing tests. I/O: JSON fixtures → Dart models/error. Được dùng bởi/tại: flutter test. Kiểm chứng: Schema cũ/sai không làm app crash. 

**File:** `mobile/test/alert_coordinator_test.dart` — Rà soát/chỉnh khi có lỗi, giữ nguyên nếu đã đạt; SV3 chịu trách nhiệm. Chức năng: Dedup và lifecycle/audio bằng fake service. Thành phần chính: testDuplicateSources; testWrongInstallation; testMute. I/O: Event/app state → số lần UI/audio. Được dùng bởi/tại: flutter test. Kiểm chứng: WS+FCM cùng event chỉ 1 foreground alarm; không nhận sai backend. 

**File:** `mobile/integration_test/flow_test.dart` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Luồng pair/status/ack cơ bản với backend thử. Thành phần chính: main flow_test. I/O: Test backend + app → thao tác end-to-end. Được dùng bởi/tại: flutter test integration_test. Kiểm chứng: Test tự động cho UI chính; push thật vẫn test trên máy bằng checklist. 

**File:** `mobile/build/app/outputs/flutter-apk/app-debug.apk` — Tạo mới; SV3 chịu trách nhiệm. Chức năng: Bản app debug sinh bằng Flutter build. Thành phần chính: Binary APK, không viết tay. I/O: Source/resources/config → app cài được. Được dùng bởi/tại: Điện thoại Android thử nghiệm. Kiểm chứng: Cài mới, pairing/RTSP/push/sound/ack chạy thật. 

Các file sinh tự động hoặc file dữ liệu trong danh sách là đầu ra của lệnh/script tương ứng; không yêu cầu viết tay nhị phân weights, lockfile, cache hoặc cấu hình Firebase. Các 

__init__.py rỗng và skeleton Android do Flutter tạo được tạo theo cấu trúc chuẩn, không có nghiệp vụ riêng. 

#### F. Thứ tự, phụ thuộc và stub 

Ngày 16 ma trận thiết bị, ngày 17 sửa vòng đời/sound, ngày 18 RTSP thật/toàn tuyến, ngày 19 cài mới APK, ngày 20 chạy sạch. Nếu UI chưa đẹp, giữ typography/form/banner đơn giản; hoàn thành chức năng quan trọng trước. Không thêm responsive web/desktop hay iOS ở tuần cuối. 

#### G. Kiểm thử sau khi hoàn thành 

- Cài APK trên máy đã chọn, xóa dữ liệu/mở lần đầu, pair link mới, nhập RTSP và thấy đúng status. Cấp/từ chối notification rồi đổi qua Settings; app phản ánh thay đổi sau resume. 

- Cùng event đi theo WS rồi FCM/FCM rồi WS → một foreground alarm; nền dùng một tag event. Tắt âm local dừng ngay; API ack lỗi không làm audio tiếp tục vô hạn. 

- Mất Wi-Fi/có Internet di động: push có thể tới nhưng preview LAN không truy cập được; UI giải thích backend ngoài tầm, không hứa xem camera qua 4G khi chưa có remote access. Mở lại LAN sync events và status. 

#### H. Deliverables và thao tác demo 

APK debug cuối tại mobile/build/app/outputs/flutter-apk/app-debug.apk, source Flutter, audio/resources và các test trọng yếu. Người dùng thực hiện được toàn tuyến không cần account. Đây là file build sinh tự động, không phải module viết tay; chỉ build sau khi config và permissions đã kiểm. 

#### I. Điều kiện hoàn thành, rủi ro và dự phòng 

PASS khi app cài mới và chạy toàn tuyến, foreground/background có kết quả thiết bị thật, tắt sound hoạt động, không lẫn event sau re-pair. Nếu nền trên một hãng bị hạn chế, ghi thiết bị/OS và điều kiện đã thử; không tuyên bố hỗ trợ mọi Android. Không dùng screenshot notification giả làm bằng chứng. 

## 7. Lịch 20 ngày: 60 mục phân công 

Mỗi dòng là một người trong một ngày: đúng 4 tuần × 5 ngày × 3 người = 60 mục. Ngày 1–5 thuộc tuần 1; 6–10 thuộc tuần 2; 11–15 thuộc tuần 3; 16–20 thuộc tuần 4. Một ngày dự kiến 45 phút học, 120 phút code, 45 phút test/tích hợp và 30 phút đệm. Tên file ngắn trong bảng được ánh xạ duy nhất sang đường dẫn đầy đủ ở Chương 9; khi có tên trùng, bảng ghi đường dẫn. Kết quả cuối ngày là sản phẩm chạy được, không chỉ đọc xong tài liệu. 

### 7.1. Tuần 1: ngày 1–5 

|**Ngày**|**SV**|**Học**|**Lập trình**|**File/module**|**Đầu ra + thử**|**Phụ**<br>**thuộc**|
|---|---|---|---|---|---|---|
|1|SV1|Ảnh numpy,<br>BGR,<br>box/keypoint|Cài pose, chạy clip một<br>người|ai/pose.py;<br>ai_smoke.py|Vẽ được pose; clip<br>hết không crash|Môi<br>trường<br>Python|



|**Ngày**|**SV**|**Học**|**Lập trình**|**File/module**|**Đầu ra + thử**|**Phụ**<br>**thuộc**|
|---|---|---|---|---|---|---|
|1|SV2|FastAPI,<br>lifespan, config|Tạo app, health/status<br>và repo|main.py; config.py;<br>app.yaml|Server 200; lỗi<br>config rõ|Không|
|1|SV3|Dart async,<br>Flutter State|Chạy Android thật; tạo<br>pair/home|main.dart;<br>pair_screen.dart|App mở hai màn<br>hình|Flutter<br>doctor|
|2|SV1|Protocol,<br>dataclass,<br>timestamp|Khóa contract; viết<br>mock/buffer|contracts.py;<br>interface.py;<br>mock.py|SV2 gọi process()<br>được|SV2<br>thống<br>nhất<br>DTO|
|2|SV2|Thread, queue<br>một phần tử|Reader video; WS<br>mock; chốt API|reader.py;<br>latest.py; ws.py|Frame + WS mock<br>tới client|SV1<br>contract|
|2|SV3|JSON, header,<br>timeout|Parser/API client bằng<br>fixture|models.dart;<br>api_client.dart|Loading/error/<br>status hiển thị|JSON từ<br>SV2|
|3|SV1|Sequence,<br>nhóm, nhãn<br>thời gian|Xem URFD; manifest<br>và split|manifest.py;<br>clips.csv;<br>splits.json|Group không giao<br>giữa split|Nguồn<br>dữ liệu|
|3|SV2|RTSP/TCP,<br>open/read<br>timeout|MediaMTX/FFmpeg;<br>reader RTSP|mediamtx.yml;<br>publish_rtsp.sh|Backend đọc<br>RTSP thật giao<br>thức|MP4 thử|
|3|SV3|Secure<br>storage, URI<br>parse|Link/storage fixture;<br>Firebase config|device_store.dart;<br>pair_screen.dart|Parse link, lưu<br>fixture; Firebase<br>sẵn|Contract<br>SV2|
|4|SV1|FPS nguồn,<br>confidence<br>thiếu|Gán interval; extraction<br>pilot|intervals.csv;<br>extract.py; *.npz|Một cache đúng<br>timestamp/shape|Manifest/<br>split|
|4|SV2|Transaction,<br>hash/expiry|Pairing/auth; test<br>TTL/revoke|pairing.py;<br>auth.py;<br>storage.py|Khóa sai không<br>xem status/WS|Claim<br>contract|
|4|SV3|WS lifecycle,<br>device pairing|Pair thật; nối WS và<br>permission|ws_client.dart;<br>notification_servic<br>e.dart|Pair/WS tới app;<br>có endpoint|Claim<br>SV2<br>ngày 4|
|5|SV1|Kiểm cache,<br>empty pose|Chạy smoke nhiều ca,<br>bàn giao|factory.py;<br>ai_smoke.py;<br>cases.csv|Pose/mock import<br>từ backend|SV2<br>pipeline|
|5|SV2|Admin SDK,<br>message<br>accepted|Gửi push thử, test<br>camera lỗi|fcm.py;<br>test_push.py;<br>test_camera.py|RTSP + push test<br>chạy|Endpoint<br>SV3|
|5|SV3|Channel/<br>permission,<br>app state|Nhận push thử và chạm<br>mở app|notification_servic<br>e.dart; manifest|Push máy thật<br>mở/nền|Sender<br>SV2|



30 phút đệm mỗi người/ngày dành cho lỗi cài đặt, review interface và ghép module ngay trong ngày. Nếu một task vượt ngân sách, cắt P1/P2 trước; không dồn toàn bộ test/tích hợp sang tuần cuối. 

### 7.2. Tuần 2: ngày 6–10 

|**Ngày**|**SV**|**Học**|**Lập trình**|**File/module**|**Đầu ra + thử**|**Phụ**<br>**thuộc**|
|---|---|---|---|---|---|---|
|6|SV1|Góc, vận tốc,<br>chuẩn hóa cửa<br>sổ|Feature chung và tests<br>gap|features.py;<br>buffer.py|Vector 30×54,<br>invalid đúng|Cache<br>T1|
|6|SV2|Factory/<br>lifecycle AI|Nối detector và reset<br>session|pipeline.py;<br>factory.py|Load model một<br>lần; AI status|SV1<br>interface|
|6|SV3|Form async,<br>camera states|RTSP form; trạng thái<br>kết nối|home_screen.dart;<br>api_client.dart|202 rồi chờ<br>camera state|PUT<br>camera<br>SV2|
|7|SV1|State machine,<br>latch/hysteresi<br>s|RuleScorer và xác nhận<br>ngã|pretrained.py;<br>state_machine.py|Ngã 1 event; cúi<br>không alarm|Features<br>ngày 6|
|7|SV2|MJPEG, cache<br>dùng chung|Stream và preview có<br>auth|api/stream.py;<br>latest.py|Hai viewer không<br>chặn AI|JPEG<br>cache|
|7|SV3|HTTP MJPEG,<br>lifecycle view|Thêm camera view có<br>header|camera_view.dart|Hiện hình; nền<br>dừng viewer|Stream<br>SV2|
|8|SV1|Dataset,<br>Conv1d, BCE<br>logits|TCN/DataLoader, train<br>2 epoch|dataset.py; tcn.py;<br>train.py|Loss hữu hạn; B<br>bàn giao|Split/<br>features|
|8|SV2|Thread→<br>event loop|Nối B thật và status<br>realtime|pipeline.py; ws.py;<br>routes.py|RTSP qua AI tới<br>WS|B từ SV1|
|8|SV3|Event ID,<br>candidate/confi<br>rmed|Coordinator/AlertScreen<br>fixture|alert_coordinator.d<br>art;<br>alert_screen.dart|Một banner cho<br>event lặp|Event<br>schema|
|9|SV1|Early stopping,<br>val threshold|Train best; load CPU;<br>val A/B|trained.py;<br>evaluate.py;<br>meta.json|Checkpoint load,<br>metrics thật|Pilot train|
|9|SV2|API contract,<br>camera<br>switching|Test auth/stream/reset;<br>sửa lag|test_api.py;<br>reader.py;<br>pipeline.py|Switch không<br>ghép session cũ|AI + app|
|9|SV3|Parser errors,<br>resume sync|Nối trạng thái thật; test<br>models|models_test.dart;<br>ws_client.dart|Sai schema không<br>crash|B/WS<br>SV2|
|10|SV1|Precision/recall<br>tradeoff|So A/B, khóa hướng<br>MVP|validation.json;<br>ai.yaml|Có lựa chọn dựa<br>val/latency|Cùng dữ<br>liệu/máy|



|**Ngày**|**SV**|**Học**|**Lập trình**|**File/module**|**Đầu ra + thử**|**Phụ**<br>**thuộc**|
|---|---|---|---|---|---|---|
|10|SV2|Debug end-to-<br>end|Tích hợp<br>RTSP/AI/preview/app|pipeline.py; api/*|App xem ảnh và<br>AI thật|SV1 +<br>SV3|
|10|SV3|Lifecycle<br>camera/socket|Test UI thật, chuẩn<br>event push|home_screen.dart;<br>coordinator|Một socket; xem<br>AI thật|Backend<br>ngày 10|



30 phút đệm mỗi người/ngày dành cho lỗi cài đặt, review interface và ghép module ngay trong ngày. Nếu một task vượt ngân sách, cắt P1/P2 trước; không dồn toàn bộ test/tích hợp sang tuần cuối. 

### 7.3. Tuần 3: ngày 11–15 

|**Ngày**|**SV**|**Học**|**Lập trình**|**File/module**|**Đầu ra + thử**|**Phụ**<br>**thuộc**|
|---|---|---|---|---|---|---|
|11|SV1|Transition/<br>episode ID|Khóa<br>confirmed/recovery<br>contract|state_machine.py;<br>contracts.py|SV2 tạo event từ<br>transition|B/A đã<br>chọn|
|11|SV2|Idempotency,<br>unique index|EventService +<br>events/outbox schema|events.py;<br>schema.sql;<br>storage.py|Cùng episode một<br>event|Transitio<br>n SV1|
|11|SV3|Channels,<br>permission<br>state|Hoàn thiện 2 channel<br>và Settings|notification_servic<br>e.dart; manifest|Sound/silent<br>channels tồn tại|FCM T1|
|12|SV1|Phân tích false<br>positives|Hard negatives và chỉnh<br>onset|pretrained.py;<br>cases.csv|Giảm lỗi đã tái<br>hiện trên val|Video<br>ADL|
|12|SV2|FCM<br>data/notificatio<br>n, endpoint|Đăng ký push; send_fall|fcm.py; routes.py|Test message<br>đúng device|SV3<br>endpoint|
|12|SV3|onMessage/<br>open/<br>initialMessage|Nối FCM vào<br>coordinator|notification_servic<br>e.dart; models.dart|Chạm push mở<br>đúng event|Sender<br>SV2|
|13|SV1|Gap/<br>occlusion/ID<br>churn|Test thiếu pose và latch|buffer.py;<br>test_ai_sequence.<br>py|Gap không bị tính<br>là bất động|State<br>contract|
|13|SV2|Retry/TTL,<br>không block AI|Outbox worker +<br>events/ack API|outbox.py;<br>test_alerts.py|Timeout không<br>chặn inference|Event<br>storage|
|13|SV3|Audio<br>asset/stop/disp<br>ose|AlarmService, raw<br>sound/icon|alarm_service.dart<br>; audio; res/raw|Foreground âm 10<br>s tối đa|Coordina<br>tor|



|**Ngày**|**SV**|**Học**|**Lập trình**|**File/module**|**Đầu ra + thử**|**Phụ**<br>**thuộc**|
|---|---|---|---|---|---|---|
|14|SV1|Imbalance/LR<br>nếu A đã chạy|Một thử A nhỏ; hỗ trợ<br>toàn tuyến|train.py;<br>evaluate.py;<br>ai.yaml|So val; không mở<br>kiến trúc mới|Ngân<br>sách A<br>4h<br>≤|
|14|SV2|Lỗi<br>cloud/device,<br>retry race|Test FCM thật và<br>duplicate|outbox.py;<br>tests/test_alerts.py|AI<br>event<br>push<br>→<br>→<br>nền|SV1 +<br>SV3|
|14|SV3|Dedup/pause/<br>resume|Test nền/khóa và<br>WS+FCM|alert_coordinator_t<br>est.dart|Một alarm<br>foreground/event|FCM thật|
|15|SV1|Regression/<br>khóa version|Chốt model/config, test<br>hard negatives|validation.json;<br>model meta|Weights/config<br>cuối tuần|Toàn<br>tuyến|
|15|SV2|Khôi phục sau<br>WS/network lỗi|Tích hợp, thử event<br>replay|routes.py; ws.py;<br>README.md|App sync event bỏ<br>lỡ|SV3<br>resume|
|15|SV3|Mute/ack/<br>offline UX|Hoàn thiện sound<br>setting và ack|alert_screen.dart;<br>api_client.dart|Tắt âm ngay; ack<br>idempotent|API<br>ack/soun<br>d|



30 phút đệm mỗi người/ngày dành cho lỗi cài đặt, review interface và ghép module ngay trong ngày. Nếu một task vượt ngân sách, cắt P1/P2 trước; không dồn toàn bộ test/tích hợp sang tuần cuối. 

### 7.4. Tuần 4: ngày 16–20 

|**Ngày**|**SV**|**Học**|**Lập trình**|**File/module**|**Đầu ra + thử**|**Phụ**<br>**thuộc**|
|---|---|---|---|---|---|---|
|16|SV1|Event<br>matching,<br>unseen test|Khóa test, chạy metric<br>cuối|evaluate.py;<br>final.json|TP/FP/FN có mẫu<br>số|Model<br>ngày 15|
|16|SV2|Latency nhiều<br>mốc|Đo API/camera/FCM,<br>đọc lỗi P0|measure_e2e.py;<br>pipeline.py|Có số đo và lỗi tái<br>hiện|Toàn<br>tuyến|
|16|SV3|App state/OS<br>restrictions|Ma trận<br>foreground/nền/force-<br>stop|notification_servic<br>e.dart; checklist|Kết quả máy/OS<br>thật|Push<br>backend|
|17|SV1|Phân tích lỗi<br>theo tầng|Sửa lỗi P0; giữ test<br>khóa rõ|features.py;<br>state_machine.py|Regression<br>gap/FP qua|Lỗi ngày<br>16|
|17|SV2|Shutdown/retry<br>idempotent|Sửa<br>reader/outbox/restart|reader.py;<br>outbox.py; tests|Reconnect không<br>nhân worker|Lỗi ngày<br>16|
|17|SV3|Listener/audio<br>race|Sửa trùng<br>alarm/stop/resume|coordinator;<br>alarm_service.dart|Tắt âm không phụ<br>thuộc API|Ca lỗi<br>ngày 16|



|**Ngày**|**SV**|**Học**|**Lập trình**|**File/module**|**Đầu ra + thử**|**Phụ**<br>**thuộc**|
|---|---|---|---|---|---|---|
|18|SV1|Domain shift<br>góc/ánh sáng|Test camera RTSP thật<br>an toàn|pose.py;<br>cases.csv;<br>final.json|Nêu điều<br>kiện/case bỏ sót|Camera<br>thật|
|18|SV2|RTSP outage<br>thật|Rút mạng, bật lại; toàn<br>tuyến|reader.py;<br>pipeline.py|Session mới, app<br>có status|Camera<br>+ SV1|
|18|SV3|Thiết bị/mạng<br>LAN–Internet|Test nhận push khi<br>khóa/đổi mạng|home_screen.dart;<br>notification|Push và preview<br>phân biệt|SV2<br>sender|
|19|SV1|Profile<br>pose/feature/s<br>corer|Tối ưu nhỏ và chạy hồi<br>quy|ai.yaml;<br>ai_smoke.py;<br>final.json|FPS đo trên máy<br>demo|Config<br>đã chọn|
|19|SV2|Cài sạch,<br>secret/config|Venv sạch; khóa<br>dependency/lệnh|requirements.lock.<br>txt; README.md|Người khác chạy<br>được|Model/<br>config<br>SV1|
|19|SV3|Build/cài mới<br>APK|Build debug, cài<br>mới/pair lại|build.gradle.kts;<br>app-debug.apk|APK mới chạy đầy<br>đủ|Backend<br>sạch|
|20|SV1|Kiểm<br>model/schema<br>cuối|Load CPU,<br>ngã/ADL/regression|model/meta;<br>final.json|AI thật; không<br>mock/NaN|Cấu hình<br>cuối|
|20|SV2|Startup sạch,<br>P0 acceptance|Chạy<br>backend/camera/alert<br>từ đầu|main.py;<br>README.md;<br>tests|MVP end-to-end<br>được lặp lại|SV1 +<br>SV3|
|20|SV3|Luồng sử dụng<br>hoàn chỉnh|Pair<br>RTSP<br>alarm<br>tắ<br>→<br>→<br>→<br>t/ack|APK; app<br>screens/services|App dùng không<br>tài khoản|Backend/<br>AI thật|



30 phút đệm mỗi người/ngày dành cho lỗi cài đặt, review interface và ghép module ngay trong ngày. Nếu một task vượt ngân sách, cắt P1/P2 trước; không dồn toàn bộ test/tích hợp sang tuần cuối. 

## 8. Hai lộ trình AI và mốc lựa chọn mô hình 

### 8.1. Phân biệt ba nghĩa của “tự train” 

|**Cách làm**|**Nhóm tự học tham số nào?**|**Chọn trong 4 tuần?**|
|---|---|---|
|Train toàn bộ vision<br>model từ đầu|Khởi tạo ngẫu nhiên detector/pose và mạng<br>hành vi, cần dữ liệu box/keypoint/hành vi đủ<br>lớn.|Không chọn: thời gian/dữ liệu/hạ<br>tầng vượt phạm vi. Đây không<br>phải điều kiện Application Track.|



|**Cách làm**|**Nhóm tự học tham số nào?**|**Chọn trong 4 tuần?**|
|---|---|---|
|Fine-tune model đã<br>pretrained|Tiếp tục cập nhật weights đã có bằng dữ liệu<br>phù hợp cùng kiểu nhãn. Ví dụ pose cần nhãn<br>khớp, action model cần chuỗi/nhãn hành vi<br>tương thích.|Là lựa chọn thay thế có điều<br>kiện, không cộng thêm hệ thống<br>thứ ba. URFD RGB có nhãn ngã<br>không tự trở thành pose<br>annotations.|
|Train classifier nhỏ từ<br>đầu trên feature<br>pretrained|Pose giữ nguyên weights; TCN mới khởi tạo<br>ngẫu nhiên và học phân loại chuỗi ngã/không<br>ngã.|Chọn làm hướng A thực tế. Phải<br>nói rõ phần pose dùng<br>pretrained, phần ngã do nhóm tự<br>train.|



Nếu giảng viên yêu cầu cụ thể tự huấn luyện, nhóm trình bày chính xác phạm vi TCN đã train; không nhận đã train YOLO từ đầu. Fine-tuning một model hành vi có sẵn chỉ xem xét nếu có weights, giấy phép, label map và loader sẵn, chạy được trong buổi thử tối đa 2 giờ. Nếu phải học thêm framework video lớn, giữ TCN. Không fine-tune pose bằng hai nhãn fall/non-fall vì sai bài toán. 

### 8.2. Dataset và gán nhãn dùng cho hướng A 

Nguồn chính được kiểm tra là UR Fall Detection Dataset [S6]: 70 sequence gồm 30 ngã và 40 hoạt động thường ngày; dữ liệu RGB/depth được phân phối dạng chuỗi PNG nén, không chỉ là các MP4 sẵn. Ngã có hai camera; ADL dùng camera0. MVP chỉ dùng RGB camera0 để cấu trúc đồng nhất. Nguồn công bố giới hạn học thuật phi thương mại; nhóm kiểm điều kiện tải và lưu provenance khi lấy dữ liệu. Không cần xử lý accelerometer/depth cho ứng dụng một camera RGB. 

- Bước A1 — kiểm nguồn: tải 2 clip ngã và 2 ADL trước; giải nén, sort tên frame theo số tự nhiên, mở xem. Xác minh FPS/timestamp bằng metadata/tài liệu đi kèm; nếu buộc giả định FPS, ghi assumption ở clips.csv và không suy vận tốc chính xác từ dữ liệu đó. 

- Bước A2 — manifest: mỗi clip có clip_id, source, path, camera_id, group_id, subject_id nếu xác minh được, source_fps/timestamps. Nếu hai góc cùng một hành động được dùng sau này, chúng phải cùng group. Không đoán subject_id từ tên file nếu dataset không cung cấp. 

- Bước A3 — annotation: với clip ngã, đánh onset_s (bắt đầu mất thăng bằng/đi xuống), impact_s (chạm nền/đến tư thế ngã), end_s (cuối sự kiện) bằng xem chậm. ADL có nhãn negative; không gán mọi frame của clip ngã là positive vì đoạn đầu còn đứng. 

- Bước A4 — split: ưu tiên subject-independent nếu nhận diện được người và mỗi tập đủ class; nếu không, group theo recording, khoảng 60/20/20. Một phân bổ camera0 theo clip có thể là train 18 fall+24 ADL, val 6+8, test 6+8 nếu group cho phép; số thật thay đổi khi group ràng buộc. Công bố rõ khi chỉ độc lập recording, chưa độc lập người. 

- Bước A5 — giữ cả clip/phiên thuộc một split trước rồi mới cắt window; hai window overlap không lọt khác split. Test địa điểm/camera demo là tập ngoài miền bổ sung, không hòa lại vào train sau khi đã xem kết quả rồi gọi là unseen. 

- Bước A6 — hard negatives: thêm video ngồi nhanh/cúi/quỳ/nằm có chủ ý/đã nằm khi bật camera/camera rung. Tự quay ở điều kiện được phép bằng người khỏe hoặc dùng nguồn có quyền; không yêu cầu người cao tuổi diễn ngã. Các clip này có group theo người và buổi quay. 

- Bước A7 — quality: trích COCO17 bằng cùng pose weights/input, lấy mẫu 10 Hz, lưu timestamps/validity. Clip thiếu toàn thân nhiều thì gắn quality flag; không bịa tọa độ hoặc âm thầm xóa ca khó khỏi test. 

Nhãn cửa sổ: positive khi cửa sổ nhân quả 3 giây đã chứa chuyển tiếp ngã và mốc quyết định nằm trong đoạn sau impact đến impact+2 giây; negative cho ADL hoặc đoạn trước onset đủ cách biệt. Window đang chuyển tiếp chưa rõ nhãn có thể loại khỏi training ban đầu nhưng vẫn chạy trong replay để đo cảnh báo. Sau positive label, state machine vẫn phải xác nhận thời gian bằng dữ liệu mới. Nhãn phân loại window không được dùng làm ground truth event cuối nếu không có interval gốc. 

Augmentation chỉ trên train: jitter tọa độ nhỏ theo scale thân, bỏ một số keypoint ngắn với confidence=0, thay scale/translation nhẹ và mirror có đổi trái–phải đúng mapping. Nếu thay tốc độ thời gian, phải thay cả timestamp/nhãn vận tốc nhất quán; P0 có thể bỏ augmentation tốc độ để giảm lỗi. Không xoay một người đang đứng 90° rồi gán nhãn ngã vì không có diễn biến ngã. Val/test không augment; mọi scaler/hyperparameter chỉ fit/chọn từ train/val. 

### 8.3. Pipeline training, model và bàn giao nhánh A 

FallTCN nhận [N,54,30], gồm 2–3 tầng Conv1d hidden khoảng 32, kernel 3 và dilation 1/2/4, activation ReLU, dropout nhỏ và linear binary head. Nếu dùng causal padding thì crop phần phải để không nhìn vượt mốc quyết định; cũng có thể dùng toàn bộ 30 mẫu quá khứ với pooling vì mọi mẫu đều đã quan sát. Script huấn luyện từ đầu weights của TCN, pose luôn frozen. Không thêm Transformer, autoencoder hoặc 10 lớp hành vi như sample. 

```
# Thực thi từ root sau khi manifest/nhãn/split đã được kiểm:
python -m training.manifest --source data/raw/urfd --output
data/manifests/clips.csv
python -m training.extract --manifest data/manifests/clips.csv --labels
data/labels/intervals.csv --output data/features
python -m training.train --config configs/train.yaml --splits data/splits.json --
features data/features --epochs 2
python -m training.train --config configs/train.yaml --splits data/splits.json --
features data/features
python -m training.evaluate --split val --mode trained --weights models/fall_tcn.pt
--output evaluation/validation.json
python scripts/ai_smoke.py --source <video> --mode trained
```

Các CLI flags là hợp đồng cần triển khai trong script, không phải lệnh của một package bên ngoài đã có sẵn. Train loop: model.train(), zero_grad(), logits=model(X), 

BCEWithLogitsLoss(logits,y), backward(), optimizer.step(); validation dùng model.eval() và inference_mode/no_grad. Bắt đầu batch 16/32, Adam learning rate khoảng 1e-3, tối đa 30 epoch và early stopping patience 5; tất cả là cấu hình thử, điều chỉnh theo pilot chứ không đảm bảo tối ưu. Dùng class weight hoặc sampler khi lệch lớp, không cùng lúc tăng mọi trọng số mà không kiểm hiệu ứng. 

Lưu state_dict tốt nhất theo validation; meta ghi input_dim, window, sample_hz, feature_version, label map, seed, split hash, pose weights hash và threshold được chọn trên val. Load bằng FallTCN đúng kiến trúc, torch.load(...,map_location="cpu",weights_only=True), load_state_dict và eval trước inference [S13]. Không tải checkpoint không rõ nguồn. Bàn giao trọn bộ weights+meta+config+1 clip kiểm chứng+output shape, không chỉ gửi một file .pt không biết dùng. 

|**Tuần**|**Học và lập trình**|**File/đầu ra kiểm chứng**|**Bàn giao và dự phòng**|
|---|---|---|---|
|1|Dataset/group split/label, pose<br>extraction pilot, cố định<br>timestamp/COCO17.|manifest.py; clips.csv;<br>intervals.csv; splits.json;<br>extract.py; cache .npz mẫu.|Ngày 5: SV2 nhận<br>interface/pose; nếu dữ liệu<br>chưa có, giữ B P0, A chỉ<br>pilot chưa đánh giá.|
|2|Dataset windows, TCN/logits/loss,<br>train 2 epoch rồi early stop, val<br>threshold, load adapter.|dataset.py; tcn.py; train.py;<br>evaluate.py; trained.py;<br>fall_tcn.pt/meta khi train thật.|Ngày 10: so A/B trên val<br>cùng hardware; A không đạt<br>thì không lên MVP, backend<br>không đổi API.|
|3|Phân tích FP/FN; một thử nghiệm<br>nhỏ về imbalance/LR nếu còn giờ,<br>replay event chung state machine.|validation.json cập nhật;<br>checkpoint/meta có version;<br>test_ai_sequence.py.|Tối đa 4 giờ cho A; ngày 15<br>đóng băng. Nếu không có<br>cải thiện, giữ checkpoint thử<br>nghiệm và B làm demo.|
|4|Test khóa, camera ngoài miền,<br>CPU load và benchmark, kiểm<br>metadata.|final.json có số đo;<br>model/config/hash cuối; không<br>xuất model giả khi A chưa train<br>xong.|Nếu A là MVP nhưng lỗi<br>deploy chưa sửa trong ngân<br>sách, quay B đã test; không<br>train gấp từ đầu.|



Tài nguyên và thời gian là ước lượng lập kế hoạch: với TCN nhỏ trên cache pose, RAM khoảng vài GB thường đủ; GPU không phải điều kiện để code/train pilot, nhưng trích pose có thể là phần chậm nhất. Dự trù 1–4 giờ trích xuất unattended trên CPU cho bộ thử nhỏ đến trung bình và 0.5–3 giờ một lượt train CPU; GPU phù hợp có thể giảm. Không dùng các khoảng này như benchmark: ngày 4 đo 2–4 clip và 100 batch rồi ngoại suy; nếu vượt cửa sổ làm việc thì giảm subset có nhãn, không lấy thời gian ngoài kế hoạch để mặc nhiên cứu tiến độ. Không đưa huấn luyện pose từ đầu vào 240 giờ. 

### 8.4. Pretrained B: so lựa chọn và lộ trình riêng 

|**Giải pháp**|**Đầu ra có sẵn**|**Cần bổ sung và quyết định**|
|---|---|---|
|YOLO11n-pose +<br>ByteTrack|Box, COCO-17 keypoint; tracker qua<br>track() [S3, S4].|Chọn chính: feature + onset + máy trạng<br>thái. Không có nhãn fall tự động chỉ từ<br>weights pose.|
|MediaPipe Pose<br>Landmarker|Landmarks cơ thể theo ảnh/video, có<br>tọa độ ảnh và world coordinates [S5].|Dự phòng khi YOLO không đáp ứng máy:<br>cần adapter mapping; world coordinates<br>không tự thành khoảng cách người tới<br>sàn. Không đổi giữa tuần nếu không<br>benchmark.|
|Action model/checkpoint<br>của sample|Sample có model chuỗi và<br>feature/label contract riêng [S2].|Chỉ tham khảo: không load vào input 54<br>chiều mới; cần cùng<br>normalization/window/classes. Không làm<br>đường găng vì phụ thuộc nặng.|



B không cần train pose nhưng vẫn cần video ngã/không ngã để tune và đánh giá. Nhánh này gọi PoseEstimator → PoseBuffer → feature → RuleScorer → máy trạng thái. Lưu rules/config có version tương đương model artifact; không gọi điều chỉnh ngưỡng là “huấn luyện YOLO”. CPU inference có thể dùng; nếu chậm thử input 320, 1 người, 1 camera, 

preview thấp. Đổi MediaPipe sẽ cần mapping/feature_version mới và làm lại kiểm chứng, nên chỉ quyết định đầu tuần 1 nếu không chạy được YOLO. 

|**Tuần**|**Kiến thức và công việc**|**File/đầu ra**|**Đo và tích hợp**|
|---|---|---|---|
|1|VideoCapture, BGR/shape, pretrained<br>weights, confidence/track ID; smoke<br>pose và mock contract.|pose.py; interface.py; mock.py;<br>buffer.py; ai_smoke.py; yolo11n-<br>pose.pt.|Ngày 5 chạy clip không<br>người/có người, reset;<br>SV2 dùng cùng interface.|
|2|Góc/vận tốc/box; lịch sử onset; low<br>posture 2 s; latch/recovery; tune val.|features.py; pretrained.py;<br>state_machine.py; ai.yaml;<br>test_ai_sequence.py.|Ngày 8 B vào RTSP; ngày<br>10 có validation và tốc độ,<br>là fallback cho A.|
|3|Hard negatives, thiếu khớp/gap/ID<br>churn, event one-shot, đồng bộ<br>model_id.|Sửa features/rules/state;<br>validation.json; contract<br>transition hoàn chỉnh.|Ngày 14–15 B hoặc A tạo<br>event push thật, không<br>phải pose demo độc lập.|
|4|Domain shift/camera thật, profile và<br>held-out event metrics.|Config/weights pose cuối;<br>final.json; smoke/regression.|Một camera thật và RTSP<br>giả lập; đo<br>FPS/FN/FA/latency; giữ<br>giới hạn thực.|



### 8.5. So sánh hai hướng trên cùng hệ thống 

|**Tiêu chí**|**A — TCN tự train trên pose**|**B — pose pretrained + luật thời gian**|
|---|---|---|
|Độ khó|Cao hơn: dữ<br>liệu/nhãn/split/train/load/evaluate thêm.|Vừa: hình học, thời gian, chất lượng pose,<br>máy trạng thái vẫn cần làm đúng.|
|Kiến thức|PyTorch tensors, Conv1d,<br>loss/optimizer/overfit + toàn bộ nền CV<br>chung.|CV, keypoint, kinematics, validation và<br>state machine; không cần train loop.|
|Giờ thực hiện|Khoảng 20–24 giờ riêng cho A, dùng lại<br>pose/features/đánh giá.|Khoảng 20–24 giờ baseline B, chưa tính<br>phần chung; phù hợp giữ đường găng.|
|Dataset|Cần nhãn/đa dạng/split tốt; URFD nhỏ,<br>không đủ chứng minh cho mọi người cao<br>tuổi.|Không cần nhãn train pose; vẫn cần<br>validation/test và hard negatives.|
|GPU|Không bắt buộc cho TCN nhỏ; pose<br>extraction/huấn luyện lớn sẽ hưởng lợi nếu<br>có.|Không bắt buộc; CPU cần benchmark tại<br>input/máy cụ thể.|
|Inference|Pose + TCN nhỏ; chi phí pose thường<br>chính, phải đo thực.|Pose + phép tính luật; có thể nhẹ hơn<br>nhưng không hứa FPS.|
|Độ chính xác kỳ<br>vọng|Có thể học mẫu tốt hơn nhưng dễ overfit;<br>không đưa tỷ lệ trước đo.|Dễ giải thích, có thể nhạy góc camera;<br>không bảo đảm ít FP hơn A.|
|Cách kiểm chứng|Cùng held-out group, cùng event<br>matching/FP-hour/latency; test không<br>tuning.|Dùng chính protocol đó; threshold chỉ chọn<br>trên val.|



|**Tiêu chí**|**A — TCN tự train trên pose**|**B — pose pretrained + luật thời gian**|
|---|---|---|
|Realtime|Được nếu cache online, nhịp<br>mẫu/metadata đúng và đo đạt.|Được nếu pose đủ nhanh và confirmation<br>có timestamp.|
|Khả năng 4 tuần|Khả thi ở phạm vi classifier nhỏ, không<br>train toàn vision từ đầu.|Khả thi hơn để có MVP ổn định, vẫn phải<br>test phần cứng và push.|
|Rủi ro|Thiếu nhãn, leakage, overfit,<br>shape/normalization lệch runtime.|Threshold nhạy camera, ngồi/nằm nhanh<br>gây nhầm, ngã chậm bỏ sót.|
|Mức phù hợp|Nhánh học thêm có giới hạn giờ, không bắt<br>buộc thắng baseline.|Hướng chính khuyến nghị cho nhóm năm<br>2; cùng interface hỗ trợ đổi sau.|



### 8.6. Cổng quyết định và interface thay model 

Ngày 5: pose/RTSP/app và push smoke phải chạy; nếu môi trường/dataset chưa đạt thì ưu tiên B và sửa tích hợp. Ngày 10: A chỉ được chọn nếu train/load thật, split không leakage, validation ít nhất không kém B về recall/FP trong cùng protocol, tốc độ phù hợp và không còn lỗi shape/version. Với số mẫu ít hoặc bằng chứng không rõ, giữ B. Ngày 15: đóng băng model/config để tuần 4 test và sửa lỗi; không đổi sang kiến trúc lớn. 

```
# Backend không thay API khi chuyển nhánh:
detector = create_detector(settings.ai_mode)  # pretrained hoặc trained
detector.reset(stream_session_id)
update = detector.process(frame_packet)
for candidate in update.candidates:
    transition = states.update(candidate, frame_packet.captured_mono)
    if transition.just_confirmed:
        events.create_once(transition)
```

Không chạy A và B đồng thời trong mọi frame production để “vừa test vừa dùng” nếu chưa kiểm tài nguyên. Offline evaluation có thể chạy lần lượt trên cùng cache; online MVP chỉ một scorer active. Nếu checkpoint A lỗi lúc startup, factory ghi rõ fallback_to=pretrained trong status và model_id mới. Không fallback âm thầm rồi báo kết quả của A. 

## 9. Cấu trúc source và quản lý file 

### 9.1. Cây thư mục nhất quán 

```
fallguard/
  pyproject.toml
  requirements.lock.txt
  .env.example
  .gitignore
  README.md
  configs/
    app.yaml
    ai.yaml
    train.yaml
  deploy/
    mediamtx.yml
  backend/
    main.py
    config.py
    contracts.py
    camera/
      reader.py
      latest.py
```

```
    pipeline.py
    api/
      routes.py
      ws.py
      stream.py
    storage.py
    schema.sql
    pairing.py
    auth.py
    alerts/
      events.py
      outbox.py
      fcm.py
    ai/
      interface.py
      mock.py
      pose.py
      buffer.py
      features.py
      pretrained.py
      trained.py
      state_machine.py
      factory.py
      tcn.py
  training/
    manifest.py
    extract.py
    dataset.py
    train.py
    evaluate.py
  data/
    manifests/
      clips.csv
    labels/
      intervals.csv
    splits.json
    features/
      *.npz
  scripts/
    ai_smoke.py
    publish_rtsp.sh
    test_push.py
    measure_e2e.py
  models/
    yolo11n-pose.pt
    fall_tcn.pt
    fall_tcn.meta.json
  evaluation/
    cases.csv
    validation.json
    final.json
  tests/
    test_ai_sequence.py
    test_camera.py
    test_pairing.py
    test_api.py
    test_alerts.py
  mobile/
    pubspec.yaml
    pubspec.lock
    lib/
      main.dart
      config.dart
      models.dart
      services/
        api_client.dart
        device_store.dart
        ws_client.dart
```

```
        notification_service.dart
        alert_coordinator.dart
        alarm_service.dart
      screens/
        pair_screen.dart
        home_screen.dart
        alert_screen.dart
      widgets/
        camera_view.dart
      firebase_options.dart
    android/
      app/
        google-services.json
        build.gradle.kts
        src/
          main/
            AndroidManifest.xml
            res/
              raw/
                fall_alarm.wav
                keep.xml
              drawable/
                ic_stat_fall.xml
          debug/
            AndroidManifest.xml
    assets/
      audio/
        fall_alarm.wav
    test/
      models_test.dart
      alert_coordinator_test.dart
    integration_test/
      flow_test.dart
    build/
      app/
        outputs/
          flutter-apk/
            app-debug.apk
  runtime/
    fallguard.db
  data/raw/                        # dữ liệu nguồn, không commit
```

Thêm __init__.py rỗng ở backend, camera, api, alerts, ai và training khi cần package import; file này không có logic nghiệp vụ. Flutter/Android còn có skeleton Gradle, MainActivity và icon launcher do flutter create sinh; giữ mặc định và chỉ chỉnh các file Android được liệt kê khi nhiệm vụ yêu cầu. Không coi hàng trăm file build/cache sinh tự động là nhiệm vụ thủ công. runtime/ và data/raw không đưa vào git; dùng URL nguồn/checksum và script để tái tạo dữ liệu được phép. 

### 9.2. Chủ sở hữu theo module 

|**Thư mục**|**Sở**<br>**hữu**|**Trách nhiệm và hướng phụ thuộc**|
|---|---|---|
|backend/ai/; training/; models/; data/;<br>evaluation/|SV1|Tạo khớp/feature/score/state machine; training và đánh giá.<br>Không import Firebase, Flutter hoặc route API trong AI.|
|backend/camera/; backend/pipeline.py|SV2|Đọc frame, schedule, reset, gọi detector interface; không<br>viết trực tiếp thuật toán phân loại ngã ở routes.|
|backend/api/; auth.py; pairing.py;<br>storage.py|SV2|Quyền thiết bị, API/WS/video, DB. Không xuất secret trong<br>JSON/status.|



|**Thư mục**|**Sở**<br>**hữu**|**Trách nhiệm và hướng phụ thuộc**|
|---|---|---|
|backend/alerts/|SV2|Event uniqueness, outbox, sender FCM. Chỉ nhận transition,<br>không đọc camera lần thứ hai.|
|mobile/lib/; mobile/android/; assets/;<br>tests app|SV3|UI/lifecycle/notification/audio; AI quyết định ở backend.<br>Không hardcode model hay khóa backend vào APK.|
|configs/; deploy/; scripts/; tests/|Theo<br>file ở<br>bảng<br>9.3|Config AI thuộc SV1, config runtime SV2; app config SV3.<br>Người sửa interface báo hai thành viên trước tích hợp.|



### 9.3. Bảng quản lý file theo tiến độ 

“Tuần tạo” là lần đầu có file có ích; “tuần tích hợp” là mốc được dùng trong phần mềm lần đầu. Một số file như FCM/notification chỉ có smoke tuần 1 và được hoàn thiện tuần 3; cột điều kiện hoàn thành nói tới phiên bản đầy đủ. File dữ liệu/weights/cache có đầu ra thực thì mới có mặt; không tạo file rỗng để đánh dấu xong. E ở từng tuần đã ghi chức năng, hàm/class, I/O và nơi sử dụng cho từng file quan trọng. 

#### 9.3.1. Cấu hình và backend 

|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F001 · pyproject.toml`|Khai báo package<br>Python và dải Python<br>3.11|SV2|1|1|Import backend/training từ<br>root ổn định|
|`F002 ·`<br>`requirements.lock.txt`|Khóa dependency sau<br>smoke test|SV2|1|1|Cài lại trên môi trường sạch,<br>import được|
|`F003 · .env.example`|Tên biến cấu hình và<br>placeholder không bí<br>mật|SV2|1|1|Không có credential thật<br>trong repo|
|`F004 · .gitignore`|Loại secret, runtime,<br>data lớn và build khỏi<br>git|SV2|1|1|.env, credential JSON,<br>runtime DB không được<br>commit|
|`F005 · README.md`|Lệnh cài/chạy và thao<br>tác vận hành MVP|SV2|1|1|Có lệnh smoke và giới hạn<br>bản chạy đúng thực tế|
|`F006 · configs/app.yaml`|Timeout, camera, rate<br>preview, runtime DB|SV2|1|1|Giá trị lỗi bị báo lúc startup|
|`F007 · configs/ai.yaml`|Model, cửa sổ và<br>ngưỡng luật/xác nhận|SV1|1|2|A/B đổi bằng config; không<br>hardcode ngưỡng|
|`F008 · configs/train.yaml`|Seed, split, batch và<br>siêu tham số train|SV1|1|2|Seed/split/feature_version<br>được khóa cùng checkpoint|



|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F009 ·`<br>`deploy/mediamtx.yml`|RTSP server phục vụ<br>video thử nội bộ|SV2|1|1|Backend đọc được cùng<br>stream bằng RTSP|
|`F010 · backend/main.py`|Tạo FastAPI app và<br>lifecycle worker|SV2|1|1|Một worker, start/stop không<br>nhân đôi camera|
|`F011 · backend/config.py`|Nạp và kiểm tra config|SV2|1|1|Thiếu model/credential trả<br>trạng thái rõ ràng|
|`F012 ·`<br>`backend/contracts.py`|FramePacket,<br>candidate/update và<br>DTO event|SV1|1|1|SV2 parse được output mock<br>cùng schema_version|
|`F013 ·`<br>`backend/camera/reader.py`|Đọc<br>RTSP/video/webcam,<br>reconnect theo phiên|SV2|1|1|Sai URL không treo API; tự<br>nối lại; release đúng thread|
|`F014 ·`<br>`backend/camera/latest.py`|Bộ đệm frame/JPEG<br>mới nhất dung lượng<br>hữu hạn|SV2|1|1|Không tích lũy frame; viewer<br>không lấy mất frame AI|
|`F015 ·`<br>`backend/pipeline.py`|Ghép capture,<br>detector, state<br>machine và event<br>service|SV2|1|1|Inference không chặn API;<br>reset khi đổi session|
|`F016 ·`<br>`backend/api/routes.py`|Health/status/camera/<br>events/ack/test<br>endpoint|SV2|1|1|Response/HTTP code khớp<br>contract; có auth|
|`F017 · backend/api/ws.py`|Handshake có khóa và<br>fanout event/status|SV2|1|1|Reconnect được; không lộ<br>event cho khóa sai|
|`F018 ·`<br>`backend/api/stream.py`|MJPEG và snapshot<br>có xác thực|SV2|2|2|Ngắt viewer không dừng AI;<br>frame stale có trạng thái|
|`F019 · backend/storage.py`|SQLite giao dịch cho<br>device/config/events/o<br>utbox|SV2|1|1|Transaction ngắn; không<br>dùng connection sai thread|
|`F020 · backend/schema.sql`|Bảng/unique index và<br>phiên bản schema|SV2|1|1|Khởi động lại không mất<br>pairing; event/episode unique|
|`F021 · backend/pairing.py`|CLI sinh/thu hồi và<br>claim code một lần|SV2|1|1|TTL và concurrent claim<br>đúng; không cần tài khoản|
|`F022 · backend/auth.py`|Xác thực hash device<br>secret và scope<br>installation|SV2|1|1|Khóa sai/revoke không xem<br>được ảnh/event|
|`F023 ·`<br>`backend/alerts/events.py`|Tạo event một lần sau<br>confirmed|SV2|3|3|Một episode chỉ một event;<br>ack idempotent|
|`F024 ·`<br>`backend/alerts/outbox.py`|Worker gửi có retry và<br>hết hạn|SV2|3|3|Unique event/device; tối đa 3<br>retry; không block AI|



|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F025 ·`<br>`backend/alerts/fcm.py`|Sender FCM: smoke<br>T1, adapter đầy đủ T3|SV2|1|1|Accepted phân biệt delivered;<br>secret chỉ backend|
|`F026 ·`<br>`backend/ai/interface.py`|Protocol detector và<br>scorer thay thế được|SV1|1|1|Mock/B/A cùng interface;<br>backend không import TCN<br>trực tiếp|
|`F027 · backend/ai/mock.py`|Output giả có nhãn<br>is_test ở nguồn phát<br>triển|SV1|1|1|Không bật mock trong<br>nghiệm thu AI thật|
|`F028 · backend/ai/pose.py`|Load pose một lần,<br>box/keypoint và track<br>ID|SV1|1|1|Không có người/ID/khớp<br>thiếu không crash|
|`F029 ·`<br>`backend/ai/buffer.py`|Cửa sổ theo<br>track/session có<br>timestamp|SV1|1|2|Không nối qua gap; không<br>đếm trùng frame_id|
|`F030 ·`<br>`backend/ai/features.py`|Feature/chuẩn hóa<br>dùng chung train và<br>runtime|SV1|2|2|Cùng clip tạo feature giống<br>offline/online|
|`F031 ·`<br>`backend/ai/pretrained.py`|Scorer luật dùng pose<br>pretrained|SV1|2|2|Không kết luận ngã từ một<br>pose nằm|
|`F032 ·`<br>`backend/ai/trained.py`|Adapter load TCN và<br>kiểm metadata|SV1|2|2|A/B đổi config; checkpoint<br>thiếu quay B rõ ràng|
|`F033 ·`<br>`backend/ai/state_machine.`<br>`py`|Xác nhận, latch<br>episode, recovery|SV1|2|2|Giữ nằm không báo lặp; gap<br>không tăng confirmation|
|`F034 ·`<br>`backend/ai/factory.py`|Tạo mock/B/A theo<br>config|SV1|1|1|Không load model mỗi<br>request; báo lỗi rõ|
|`F035 · backend/ai/tcn.py`|Kiến trúc phân loại<br>chuỗi nhỏ dùng chung|SV1|2|2|Forward CPU chạy được;<br>shape có kiểm tra|
|`F087 ·`<br>`runtime/fallguard.db`|Dữ liệu runtime do<br>schema/storage sinh|SV2|1|1|Restart giữ pairing; file không<br>commit, không chứa tài<br>khoản|



#### 9.3.2. AI training, dữ liệu và test Python 

|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F036 ·`<br>`training/manifest.py`|Lập danh sách clip,<br>nguồn và group chống<br>leakage|SV1|1|1|Một clip/2 góc cùng sự kiện<br>chung group|



|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F037 ·`<br>`data/manifests/clips.csv`|Manifest dữ liệu nguồn<br>có provenance|SV1|1|2|FPS/nhóm có giá trị xác<br>minh; unknown được ghi rõ|
|`F038 ·`<br>`data/labels/intervals.csv`|Nhãn onset/impact/end<br>và hard negative|SV1|1|2|Không gắn mọi frame clip<br>ngã là positive|
|`F039 · data/splits.json`|Train/val/test theo<br>group và seed|SV1|1|2|Group giao nhau rỗng, khóa<br>trước tuning|
|`F040 ·`<br>`training/extract.py`|Trích pose/features<br>đúng timestamp|SV1|1|2|Có thể resume; không tải lại<br>model mỗi clip|
|`F041 ·`<br>`data/features/*.npz`|Cache sinh tự động<br>cho từng clip|SV1|1|2|Shape/thời gian khớp; không<br>commit data lớn|
|`F042 ·`<br>`training/dataset.py`|Loader cửa sổ, nhãn,<br>augment chỉ train|SV1|2|2|Val/test không augment;<br>scaler chỉ fit train nếu dùng|
|`F043 · training/train.py`|Train TCN nhỏ, early<br>stopping và lưu best|SV1|2|2|Loss hữu hạn; best theo val,<br>không chọn theo test|
|`F044 ·`<br>`training/evaluate.py`|Đánh giá window và<br>episode theo cùng<br>logic runtime|SV1|2|2|One-to-one matching event;<br>bỏ is_test|
|`F045 ·`<br>`scripts/ai_smoke.py`|Chạy 1 clip độc lập để<br>thấy pose/status|SV1|1|1|Không cần backend/app để<br>debug AI|
|`F046 ·`<br>`scripts/publish_rtsp.sh`|Lệnh FFmpeg phát<br>MP4 vào MediaMTX|SV2|1|1|Dùng real-time pacing,<br>backend thực sự đọc rtsp://|
|`F047 ·`<br>`scripts/test_push.py`|Thử FCM riêng, không<br>giả kết quả AI|SV2|1|1|Điện thoại nhận test<br>message, không cần pose|
|`F048 ·`<br>`scripts/measure_e2e.py`|Tính độ trễ từ mốc<br>kiểm thử|SV2|4|4|Không trộn accepted với<br>received; clock lệch bị loại|
|`F049 · models/yolo11n-`<br>`pose.pt`|Weights pose tải từ<br>nguồn chính thức|SV1|1|1|Ghi nguồn/hash, load được<br>offline sau tải|
|`F050 · models/fall_tcn.pt`|Checkpoint nhánh A<br>sinh từ training|SV1|2|2|Load lại cho output gần như<br>tương đương; không giả file<br>khi train chưa xong|
|`F051 ·`<br>`models/fall_tcn.meta.json`|Hợp đồng<br>weights/feature và<br>threshold validation|SV1|2|2|Từ chối shape/version không<br>khớp|
|`F052 ·`<br>`evaluation/cases.csv`|Danh sách ca test có<br>ground truth/tập dữ<br>liệu|SV1|1|2|Có ngã, ADL, nằm sẵn, che<br>khuất; không dùng test tuning|
|`F053 ·`<br>`evaluation/validation.jso`<br>`n`|Kết quả chọn<br>ngưỡng/model trên val|SV1|2|2|Kèm denominator và thời<br>gian; không chứa số bịa|



|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F054 ·`<br>`evaluation/final.json`|Kết quả kỹ thuật test<br>khóa cuối cùng|SV1|4|4|Ghi rõ chưa đo nếu thiếu<br>mẫu, không điền ước lượng<br>thành kết quả|
|`F055 ·`<br>`tests/test_ai_sequence.py`|Test lỗi temporal và<br>xác nhận meaningful|SV1|2|2|Không test từng getter; kiểm<br>ca rớt mạng/lặp/góc thiếu|
|`F056 ·`<br>`tests/test_camera.py`|Test timeout/reconnect<br>bằng fake capture|SV2|1|1|Không chờ camera thật trong<br>unit test|
|`F057 ·`<br>`tests/test_pairing.py`|TTL, claim hai lần và<br>revoke|SV2|1|1|Code chỉ claim một lần, route<br>ảnh/WS khóa sai bị chặn|
|`F058 · tests/test_api.py`|Contract/API với mock<br>AI|SV2|2|2|Không đòi camera/GPU để<br>chạy contract tests|
|`F059 ·`<br>`tests/test_alerts.py`|Event uniqueness và<br>lỗi gửi có retry|SV2|3|3|Crash/retry không sinh<br>event_id mới; accepted<br>không retry|



#### 9.3.3. Flutter, Android và tài nguyên 

|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F060 ·`<br>`mobile/pubspec.yaml`|Dependency Flutter và<br>asset audio|SV3|1|1|Một bộ package tương thích,<br>asset tìm được|
|`F061 ·`<br>`mobile/pubspec.lock`|Khóa phiên bản<br>package app|SV3|1|1|Máy thứ hai pub get ra cùng<br>bộ dependency|
|`F062 ·`<br>`mobile/lib/main.dart`|Khởi tạo<br>app/Firebase/services<br>và lifecycle|SV3|1|1|Mở app không cần tài khoản;<br>không init FCM hai lần|
|`F063 ·`<br>`mobile/lib/config.dart`|Quy ước<br>timeout/schema/base<br>URL đã parse|SV3|1|1|Reject scheme/host thiếu;<br>không hardcode localhost|
|`F064 ·`<br>`mobile/lib/models.dart`|Parser<br>status/event/pairing có<br>kiểm trường|SV3|1|1|Sai schema/optional field<br>không crash UI|
|`F065 ·`<br>`mobile/lib/services/api_c`<br>`lient.dart`|HTTP header, timeout<br>và đồng bộ event|SV3|1|1|401 chuyển trạng thái cần<br>ghép; không tự retry claim<br>bừa|
|`F066 ·`<br>`mobile/lib/services/devic`<br>`e_store.dart`|Lưu khóa và<br>installation trong<br>secure storage|SV3|1|1|Restart còn ghép; unpair xóa<br>sạch khóa/cursor|



|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F067 ·`<br>`mobile/lib/services/ws_cl`<br>`ient.dart`|WS có auth và backoff<br>theo lifecycle|SV3|1|1|Không tạo socket trùng sau<br>resume; retry có trần|
|`F068 ·`<br>`mobile/lib/services/notif`<br>`ication_service.dart`|FCM setup,<br>permission, channel và<br>token refresh|SV3|1|1|Foreground/background/<br>terminated thường nhận<br>đúng, không nhận nhầm<br>installation|
|`F069 ·`<br>`mobile/lib/services/alert`<br>`_coordinator.dart`|Một điểm nhận event<br>từ WS/FCM/REST|SV3|2|2|Cùng event từ hai kênh chỉ<br>báo một lần ở foreground|
|`F070 ·`<br>`mobile/lib/services/alarm`<br>`_service.dart`|Audio foreground có<br>dừng và timeout|SV3|3|3|Stop ngay; tối đa 10 s; không<br>phát khi sound off|
|`F071 ·`<br>`mobile/lib/screens/pair_s`<br>`creen.dart`|Dán link và claim<br>không tài khoản|SV3|1|1|Hết hạn/sai server có lỗi dễ<br>hiểu|
|`F072 ·`<br>`mobile/lib/screens/home_s`<br>`creen.dart`|RTSP form, status,<br>camera, setting và thử<br>push|SV3|1|1|Phân biệt camera connected<br>và AI ready; password che<br>mặc định|
|`F073 ·`<br>`mobile/lib/screens/alert_`<br>`screen.dart`|Thông tin sự kiện, tắt<br>âm và ack|SV3|2|2|Nút tắt âm/đã xem hoạt động<br>kể cả API tạm lỗi|
|`F074 ·`<br>`mobile/lib/widgets/camera`<br>`_view.dart`|Hiển thị MJPEG qua<br>HTTP có header|SV3|2|2|Nền app ngắt view; AI<br>backend vẫn chạy|
|`F075 ·`<br>`mobile/lib/firebase_optio`<br>`ns.dart`|Cấu hình Firebase<br>sinh bởi FlutterFire|SV3|1|1|Đúng project/applicationId<br>của APK|
|`F076 ·`<br>`mobile/android/app/google`<br>`-services.json`|Config client Android<br>do Firebase cung cấp|SV3|1|1|Không nhầm file service<br>account|
|`F077 ·`<br>`mobile/android/app/build.`<br>`gradle.kts`|Android<br>SDK/plugin/application<br>Id|SV3|1|1|Không thay applicationId sau<br>cấu hình FCM|
|`F078 ·`<br>`mobile/android/app/src/ma`<br>`in/AndroidManifest.xml`|Internet, notification<br>permission và<br>metadata|SV3|1|1|Quyền runtime được xin;<br>default channel tồn tại|
|`F079 ·`<br>`mobile/android/app/src/de`<br>`bug/AndroidManifest.xml`|Cho HTTP nội bộ chỉ<br>trong APK debug|SV3|1|1|Release không vô tình mở<br>cleartext toàn cục|
|`F080 ·`<br>`mobile/assets/audio/fall_`<br>`alarm.wav`|Âm ngắn cho<br>foreground có quyền<br>sử dụng|SV3|3|3|Nghe rõ trên điện thoại; cùng<br>nội dung raw sound|



|**File**|**Chức năng**|**Chủ**|**Tạo**|**Ghé**<br>**p**|**Điều kiện hoàn thành**|
|---|---|---|---|---|---|
|`F081 ·`<br>`mobile/android/app/src/ma`<br>`in/res/raw/fall_alarm.wav`|Âm của Android<br>notification channel|SV3|3|3|Channel sound hoạt động lúc<br>khóa màn hình|
|`F082 ·`<br>`mobile/android/app/src/ma`<br>`in/res/drawable/ic_stat_f`<br>`all.xml`|Icon notification đơn<br>sắc đúng resource|SV3|3|3|Notification không mất icon<br>trên máy thật|
|`F083 ·`<br>`mobile/android/app/src/ma`<br>`in/res/raw/keep.xml`|Giữ raw sound/icon<br>nếu shrink resource|SV3|3|3|Release test không bị loại<br>sound/icon; debug vẫn build|
|`F084 ·`<br>`mobile/test/models_test.d`<br>`art`|Parser schema và dữ<br>liệu thiếu|SV3|2|2|Schema cũ/sai không làm<br>app crash|
|`F085 ·`<br>`mobile/test/alert_coordin`<br>`ator_test.dart`|Dedup và<br>lifecycle/audio bằng<br>fake service|SV3|3|3|WS+FCM cùng event chỉ 1<br>foreground alarm; không<br>nhận sai backend|
|`F086 ·`<br>`mobile/integration_test/f`<br>`low_test.dart`|Luồng pair/status/ack<br>cơ bản với backend<br>thử|SV3|4|4|Test tự động cho UI chính;<br>push thật vẫn test trên máy<br>bằng checklist|
|`F088 ·`<br>`mobile/build/app/outputs/`<br>`flutter-apk/app-debug.apk`|Bản app debug sinh<br>bằng Flutter build|SV3|4|4|Cài mới,<br>pairing/RTSP/push/sound/ac<br>k chạy thật|



Ngoài bảng: runtime/fallguard.db do storage khởi tạo, APK do Flutter build, dữ liệu raw và secrets được đưa vào máy chạy theo hướng dẫn. Chúng không được tạo bằng cách viết tay trong source. scripts/publish_rtsp.sh là lệnh mẫu cho Bash; Windows có thể chạy cùng FFmpeg command trong PowerShell với đường dẫn đã đổi, không bắt buộc tạo thêm một framework triển khai. 

### 9.4. Quy tắc sửa file và ghép code 

- Mỗi người giữ nhánh theo vai trò và commit nhỏ khi một hành vi chạy được; không để ba tuần code trong máy riêng. Ngày 2 đã merge contract/mock/API parser, ngày 5 có baseline cùng chạy. 

- Ai sở hữu file chịu trách nhiệm cuối, người khác có thể pair sửa lỗi tích hợp. contracts.py do SV1 khởi tạo nhưng SV2/SV3 cùng chốt nghĩa dữ liệu; không tự đổi event_id thành id ở riêng app. 

- Config runtime/AI có schema; đổi sample_hz/window/input_dim cần cập nhật meta và test tương thích. Không sửa các giá trị này trên máy demo mà quên commit cấu hình phù hợp. 

- Chỉ viết test cho hành vi dễ lỗi: gap/latch, pairing TTL/claim race, event uniqueness/retry, parser/dedup. Không dùng thời gian tạo test lặp lại mọi dòng code hoặc giao diện thuần hình thức. 

- Các mốc đã PASS không chạy lại toàn bộ vô cớ; sau sửa phần nào chạy ca liên quan và ca toàn tuyến trọng yếu. Giai đoạn cuối chạy checklist P0 một lần từ môi trường sạch. 

## 10. Hợp đồng bàn giao và kế hoạch tích hợp 

### 10.1. Bàn giao SV1 → SV2 

|**Mốc**|**Gói bàn giao**|**Contract/kiểm tra riêng**|**Kiểm tra ghép và stub**|
|---|---|---|---|
|Ngày 2|contracts.py + interface.py +<br>MockDetector; JSON mẫu không<br>người/pose invalid/một người.|SV2 import và gọi<br>process(FramePacket); output<br>đủ<br>camera/session/frame_id/candi<br>date.|Pipeline chạy bằng mock với<br>file video; không cần weights<br>để API/WS phát triển.|
|Ngày 5|PoseEstimator, model path/hash,<br>ai_smoke và cache pilot.|AI đọc clip độc lập; reset không<br>giữ ID/buffer từ clip khác.|Backend load factory; nếu B<br>chưa có giữ mock ghi rõ<br>development.|
|Ngày 8|B + features + buffer + state<br>machine, ai.yaml.|Replay ngã/ADL/gap/latch có<br>kết quả; output cùng interface.|RTSP thật giao thức<br>B<br>→<br>→<br>status/WS; A chưa xong<br>không chặn.|
|Ngày<br>10|Adapter A nếu train/load đã chạy,<br>checkpoint/meta và validation A/B.|Shape [N,54,30],<br>feature_version/hash; CPU load<br>đúng.|Chỉ đổi config ai.mode và<br>restart; REST/WS/mobile<br>không đổi.|
|Ngày<br>11–15|Transition just_confirmed,<br>episode_id; cấu hình khóa.|Cùng episode không<br>just_confirmed nhiều lần;<br>invalid/gap không confirmed.|EventService create_once;<br>nếu sender chậm vẫn AI tiếp<br>tục.|
|Ngày<br>19|Weights/meta/config/hash cuối,<br>lệnh smoke.|Process sạch import/load/test<br>xong.|Backend demo dùng đúng<br>model_id; không mock.|



### 10.2. Bàn giao SV2 → SV3 

|**Mốc**|**Gói bàn giao**|**Cách SV3 test riêng**|**Cách test tích hợp**|
|---|---|---|---|
|Ngày 2|Base URL, health/status fixture,<br>schema/pairing/WS contract.|ApiClient dùng fixture và<br>timeout, Models.fromJson.|Điện thoại GET health qua IP<br>LAN; không dùng localhost.|
|Ngày 3–<br>5|Pair link/claim thực, khóa device,<br>WS mock, endpoint push test.|Link sai/hết hạn/401 và trạng<br>thái UI.|Pair thật<br>status/WS<br>→<br>→<br>push thử trên Android.|
|Ngày 7|MJPEG có header và PUT camera<br>async.|CameraView loading/error,<br>fixture status.|App nhập RTSP và xem<br>stream; đóng viewer backend<br>không stop.|
|Ngày 10|Event schema chuẩn (Chương 3),<br>candidate/status phân biệt<br>confirmed.|Coordinator dedup bằng<br>event_id và installation.|AI thật làm UI đổi trạng thái,<br>chưa tự tạo alarm từ<br>candidate.|



|**Mốc**|**Gói bàn giao**|**Cách SV3 test riêng**|**Cách test tích hợp**|
|---|---|---|---|
|Ngày 12<br>–15|Push registration, events<br>cursor/ack/test, notification<br>payload/channel.|FCM console/script thử nhận<br>và navigation trước AI.|WS+FCM event thật;<br>foreground và<br>background/lock screen.|
|Ngày 19<br>–20|Backend/config chạy sạch;<br>credential ngoài repo.|APK cài mới, pair lại.|Toàn tuyến RTSP thật/giả lập,<br>sound/ack/reconnect.|



### 10.3. SV3 cần chuẩn bị sớm để không chờ backend 

Ngày 2 tạo ApiClient interface và fixture các JSON trong Chương 3; dựng UI state loading/connected/reconnecting/error/AI warmup. Khi SV2 đưa endpoint thật chỉ đổi implementation/base URL, không viết lại màn hình. Ngày 4 có NotificationService lấy endpoint và permission state; ngày 8 có AlertCoordinator nhận event từ fixture. Nút tắt âm xử lý cục bộ trước khi gọi ack qua mạng. Các stub đều mang is_test hoặc chế độ mock rõ; ngày 15 không được còn stub trong đường nghiệm thu. 

### 10.4. Luồng dữ liệu khi phát hiện một lần ngã 



<!-- Start of picture text -->
LUONG SU KIEN: WEBSOCKET VA PUSH DUOC TACH RIENG<br>—,_ — —O_o<br>CAMERA+ Al | BACKEND | FCM l ANDROID |<br>1. Transition confirmed<br>ls<br>2. Luu event + outbox<br>3. WS: app dang mé<br>ee<br>4, Giti déc lap UL<br>|<br>5. OS notification<br>————<br>6. Mé app<br>a<br>a / déng bé / ack idempotent<br>ung event _id trén REST, WS va FCM. FCM accepted khéng cé nghia app da nhan.<br><!-- End of picture text -->

- _Hình 3. Trình tự tạo và phân phối sự kiện; push không phụ thuộc app đang giữ WebSocket._ 

- ● 1. Camera gửi RTSP; capture thread nhận frame mới và gắn camera/session/frame/timestamp. 

- 2. Pose → buffer theo track → scorer A/B → candidate; state machine xác nhận đúng một lần cho episode. 

- 3. EventService lưu event và outbox sau cùng một giao dịch có ràng buộc unique; transaction kết thúc trước gọi network. 

- 4. ConnectionHub đưa JSON tới app đang mở; outbox độc lập gửi notification+data qua FCM tới device active. 

- 5. App foreground gom WS/FCM qua coordinator để hiện một banner/audio; background dùng system notification/channel. 

- 6. App mở lại đồng bộ events bằng cursor; bấm đã xem gửi ack idempotent, AI vẫn latch đến recovery thật. 

### 10.5. Điều kiện của mỗi lần merge tích hợp 

Trước khi ghép, người giao chạy lệnh smoke độc lập và gửi một input/output mẫu đúng schema; người nhận chạy contract test không GPU/camera bằng mock. Sau ghép, chạy một ca thật ở ranh giới vừa thay: camera→frame, frame→candidate, transition→event, event→app. Nếu contract đổi, cập nhật parser/test phía nhận trong cùng mốc. Không giải quyết lỗi bằng cách bỏ kiểm trường hoặc đổi tất cả response thành “success”. 

## 11. Kiểm thử, chỉ số và checklist MVP 

### 11.1. Bộ ca test tối thiểu có ý nghĩa 

|**Mã/ca**|**Đầu vào và thao tác**|**Kết quả mong đợi**|**Phụ trách**|
|---|---|---|---|
|T01 — RTSP đúng|Camera thật hoặc MediaMTX phát<br>MP4; nhập URL qua app.|CONNECTED, frame mới, AI<br>warmup rồi ready, preview cập nhật.|SV2+SV3|
|T02 — URL sai|Scheme/host thiếu; tiếp theo URL<br>hợp lệ nhưng camera không tồn<br>tại.|422 cho cú pháp; lỗi<br>runtime/reconnect rõ, API không<br>treo.|SV2|
|T03 — mất camera|Đang chạy rút mạng 10 s/60 s rồi<br>cắm lại.|RECONNECTING; không dùng<br>frame cũ; session mới, AI reset.|SV2+SV1|
|T04 — không có<br>người|Khung phòng trống 2 phút.|Không confirmed; status hoạt động,<br>không NaN/crash.|SV1|
|T05 — ngã có onset|Video ngã rõ trước–trong–sau,<br>nằm đủ sau impact.|Một episode/event sau xác nhận;<br>app cảnh báo.|Cả ba|
|T06 — ADL dễ nhầm|Ngồi nhanh, cúi, quỳ, đứng<br>lên/ngồi xuống, chủ động nằm.|Không alarm ở các ca đã xác minh;<br>FP nếu xảy ra được tính thật.|SV1|
|T07 — nằm sẵn|Mở camera khi người đã nằm.|Warmup/thiếu diễn biến; không tự<br>kết luận ngã từ ảnh nằm.|SV1|
|T08 — che khuất/gap|SUSPECTED rồi thiếu frame/pose<br>>0.3 s.|UNKNOWN/WARMUP; không cộng<br>gap thành nằm bất động.|SV1+SV2|
|T09 — nằm kéo dài|Sau event giữ low posture 90–120<br>s.|Một event episode; hết cooldown<br>không tự gửi lại.|SV1+SV2|
|T10 — hồi phục/ngã<br>mới|Đứng tin cậy 3 s; qua cooldown;<br>lần ngã khác.|Episode/event mới; không dùng ack<br>để re-arm giả.|SV1|
|T11 — duplicate<br>event|Cùng event qua WS, FCM và<br>REST theo các thứ tự.|Một foreground banner/audio; event<br>khác vẫn nhận.|SV3|



|**Mã/ca**|**Đầu vào và thao tác**|**Kết quả mong đợi**|**Phụ trách**|
|---|---|---|---|
|T12 — nền và khóa|Home/minimize, lock screen; phát<br>event thật/test.|System notification đúng channel;<br>chạm mở event.|SV2+SV3|
|T13 —<br>terminated/force-stop|Tắt process thông thường; riêng<br>force-stop trong Settings rồi thử.|Đo terminated theo OS; force-stop<br>ghi giới hạn tới khi mở lại.|SV3|
|T14 — notification<br>denied/DND|Từ chối quyền, sound off,<br>volume=0 hoặc DND.|UI phản ánh; không hứa sound khi<br>OS chặn; silent channel đúng.|SV3|
|T15 — mất Internet|LAN còn, Internet backend hoặc<br>điện thoại mất.|AI/WS LAN có thể chạy; FCM<br>unavailable/retry hữu hạn, TTL.|SV2+SV3|
|T16 — quyền thiết bị|Code hết hạn/claim hai lần; key<br>sai/revoke; device khác sửa push.|Từ chối đúng; không lộ<br>camera/event/endpoint của nhau.|SV2|
|T17 —<br>restart/endpoint đổi|Restart backend; refresh FCM<br>endpoint; reinstall app.|Giữ installation; đăng ký mới;<br>accepted không retry; re-pair sau<br>mất key.|SV2+SV3|
|T18 — máy mới/load<br>model|Venv sạch/CPU, thiếu<br>weights/metadata lệch.|Load đúng hoặc fallback B/AI<br>ERROR rõ; không event giả.|SV1+SV2|



Dùng fake clock/capture/sender cho các ca lỗi để không mất nhiều phút chờ timeout trong unit tests. Video thật và RTSP thật dành cho integration/manual acceptance. Không thêm hàng chục bài test chỉ để kiểm tra getter/setter; tập trung vào lỗi mất cảnh báo, lặp cảnh báo, sai thiết bị và thời gian. 

### 11.2. Chỉ số AI theo sự kiện và cách đo 

Trước vòng test, khóa interval ground truth [onset,impact/end] và cửa sổ matching: một cảnh báo từ onset đến impact+5 giây có thể ghép với sự kiện ngã đó nếu chưa có cảnh báo khác đã ghép. Ghép một-một: một ngã chỉ có một TP; không có cảnh báo trong cửa sổ là FN; cảnh báo ngoài mọi cửa sổ là FP. Cảnh báo trùng cho cùng episode ghi duplicate riêng và tính là lỗi gây phiền, không cộng nhiều TP. Với bộ clip ADL, đo số phút/giờ thực chạy để tính cảnh báo nhầm theo giờ. 

```
precision = TP / (TP + FP)
recall = TP / (TP + FN)
F1 = 2 * precision * recall / (precision + recall)
false_alarms_per_hour = FP_on_ADL / ADL_duration_hours
miss_rate = FN / (TP + FN)
AI_FPS = processed_unique_frames / elapsed_seconds
fall_to_event = confirmed_at - annotated_onset_at
event_to_app = app_received_at - confirmed_at
```

Mẫu số bằng 0 thì kết quả “không xác định/chưa đủ dữ liệu”, không tự điền 0 hoặc 100%. Báo số TP/FP/FN bên cạnh precision/recall. Đo thêm rate keypoint invalid và camera uptime trong phiên thử vì AI không có frame thì không thể phát hiện. Không dùng mAP pose của YOLO hoặc accuracy window để tuyên bố recall ngã của hệ thống. Bộ dữ liệu chủ yếu diễn ngã không chứng minh hiệu quả lâm sàng ở người cao tuổi thật. 

|**Chỉ số**|**Mục tiêu thử ban đầu**|**Nghiệm thu và cách xử lý khi không đạt**|
|---|---|---|
|AI FPS|Khoảng 8–10 unique frame/s, một<br>camera; sampling thiết kế 10 Hz.|Đo trên máy/demo thực. Nếu thiếu, giảm<br>input/preview; A chỉ chạy khi chất lượng<br>mẫu đúng metadata.|
|Preview FPS|2–3 FPS đủ quan sát; dự phòng<br>snapshot 1 FPS.|Mất preview không được dừng AI; không<br>dùng preview FPS thay AI FPS.|
|Onset<br>confirmed<br>→|Khoảng 2–5 s trên ca ngã rõ có đủ<br>bằng chứng.|Có confirmation 2 s nên không hứa tức thì;<br>đo p50/p95 và các ca thiếu onset.|
|Confirmed<br>app<br>→|Mục tiêu khoảng ≤3 s trong điều kiện<br>mạng thử tốt.|Tách foreground WS và background FCM;<br>FCM best effort, không bảo đảm giới hạn<br>OS/mạng.|
|Recall/false alarms|Gợi ý mục tiêu nội bộ: recall<br>80%<br>≥<br>trên ít nhất 10 event thử; ADL<br>60<br>≥<br>phút, mong<br>1 alarm nhầm/giờ.<br>≤|Chỉ là mục tiêu để đánh giá, không kết quả<br>hiện có. Nếu chưa đủ mẫu hoặc không đạt,<br>báo số thật và giới hạn; không kết luận triển<br>khai thực tế an toàn.|
|Độ ổn định|Một phiên 20–30 phút; mất mạng và<br>restart phục hồi đúng.|Không crash, queue không tăng vô hạn,<br>không sinh event do frame stale. Không<br>tương đương bảo đảm 24/7.|



Chỉ số mong muốn không thay thế điều kiện chức năng P0. Một bản demo có thể chạy được toàn tuyến nhưng chưa đạt ngưỡng chất lượng mong muốn; phải tách hai kết luận đó. Nếu không đủ 60 phút ADL trước ngày 20, ghi thời lượng đã thử và FA/hour quy đổi với độ bất định cao, không tự tạo dữ liệu. Nên dùng clip ADL dài có nguồn hợp lệ hoặc một phiên phòng thật được đồng ý để chạy unattended trong thời gian nhóm đang làm task khác. 

### 11.3. Checklist nghiệm thu gắn module, người, ngày và PASS 

|**Checkbox chức năng**|**Chủ/mốc**|**Module và cách kiểm tra**<br>**PASS**<br>**→**|**Giới hạn**|
|---|---|---|---|
|C01<br>Backend khởi<br>☐<br>động|SV2 · D5|main.py/config.py: khởi động sạch, /health phản<br>hồi ngay khi camera lỗi.|Một worker P0.|
|C02<br>Kết nối RTSP<br>☐|SV2 · D5,<br>thật D18|reader.py: đọc ít nhất 5 phút nguồn rtsp://; trạng<br>thái connected và frame mới.|MP4 đọc thẳng<br>không đủ.|
|C03<br>Đọc liên tục,<br>☐<br>queue hữu hạn|SV2 · D10|latest.py/pipeline.py: AI và hai viewer; không tăng<br>backlog, không xử lý lại frame_id.|Buffer camera có<br>thể còn trễ.|
|C04<br>Mất kết<br>☐<br>nối/reconnect|SV2+1 ·<br>D18|reader/state machine: T03/T08 PASS; session<br>đổi, warmup, không false fall.|Timeout tùy<br>FFmpeg build.|
|C05<br>Phát hiện<br>☐<br>người/pose|SV1 · D5|pose.py: có box/keypoint khi thấy người;<br>empty/missing pose không crash.|Không xác định<br>tuổi.|
|C06<br>Nhận diện diễn<br>☐<br>biến ngã|SV1 · D10|pretrained hoặc trained + state: T05 tạo<br>confirmed từ video có onset.|Chất lượng phải<br>đo, không khẳng<br>định mọi ngã.|



|**Checkbox chức năng**|**Chủ/mốc**|**Module và cách kiểm tra**<br>**PASS**<br>**→**|**Giới hạn**|
|---|---|---|---|
|C07<br>Giảm nhầm ADL<br>☐|SV1 · D15|features/state/cases: T06/T07; đếm FP thật trên<br>val/test.|Ngã chậm/che<br>khuất có thể bỏ sót.|
|C08<br>AI vào backend<br>☐|SV1+2 ·<br>D10|pipeline/interface: update có<br>camera/session/frame/model_id; không numpy<br>trong JSON.|Không dùng mock<br>ở test cuối.|
|C09<br>Event một<br>☐<br>lần/episode|SV2+1 ·<br>D15|events.py/storage: cùng episode một event_id;<br>T09/T10 đúng recovery.|Không exactly-once<br>cloud.|
|C10<br>App nối backend<br>☐|SV3+2 ·<br>D5|ApiClient/Pair/Home: điện thoại LAN pair,<br>status/WS thật; timeout có lỗi rõ.|Remote preview<br>ngoài LAN chưa<br>P0.|
|C11<br>Không tài khoản,<br>☐<br>đúng thiết bị|SV2+3 ·<br>D5, lại<br>D19|Pairing/auth/DeviceStore: không login; T16 và re-<br>pair khác installation không lẫn event.|HTTP lab không<br>chống nghe lén.|
|C12<br>Trạng thái<br>☐<br>camera/AI|SV3+2 ·<br>D10|Home/status: camera offline khác AI error;<br>warmup/degraded hiện đúng.|Health không thay<br>readiness.|
|C13<br>Xem hình<br>☐<br>camera|SV2+3 ·<br>D10|stream.py/CameraView: MJPEG có auth hoặc<br>snapshot dự phòng; viewer dừng AI vẫn chạy.|Không audio<br>camera.|
|C14<br>Alert khi app mở<br>☐|SV3 · D15|Coordinator/WS/FCM: T11 một banner/audio cho<br>event cùng ID.|Đua state có thể có<br>OS notification.|
|C15<br>Push nền/khóa<br>☐|SV2+3 ·<br>D15, lại<br>D19|FcmSender/NotificationService: T12 trên điện<br>thoại thật; chạm mở đúng event.|Internet/<br>permission/OS cần<br>phù hợp.|
|C16<br>Terminated và<br>☐<br>giới hạn|SV3 · D19|T13 có kết quả theo máy/OS; force-stop không<br>được nhận là bảo đảm hoạt động.|Mở lại để khôi phục<br>sau force-stop.|
|C17<br>Âm thanh và tắt<br>☐|SV3 · D15|AlarmService/assets/raw/channels: foreground<br>stop ngay, nền sound/silent đúng setting.|OS volume/DND do<br>người dùng.|
|C18<br>Giới hạn gửi<br>☐<br>lặp/retry|SV2+3 ·<br>D15|Outbox/Coordinator: event-device unique,<br>accepted không retry, TTL, dedup.|FCM accepted<br>không là delivered.|
|C19<br>Đồng bộ sau<br>☐<br>ngắt|SV2+3 ·<br>D15|Events cursor/resume: event bỏ lỡ hiện lại, không<br>hú toàn bộ lịch sử.|Chỉ giữ dữ liệu gần<br>theo retention.|
|C20<br>Hai hướng AI có<br>☐<br>đường chạy|SV1 · D10<br>–15|B smoke thật; A manifest→train→load→val pilot<br>nếu dữ liệu đủ; không weights giả.|A không bắt buộc<br>được chọn MVP.|
|C21<br>End-to-end và đo<br>☐|Cả ba ·<br>D20|T01→T05→T12→T17; final.json có mẫu thật,<br>FPS/latency và TP/FP/FN hoặc chưa đủ dữ liệu.|Phạm vi demo,<br>chưa chứng minh<br>24/7.|
|C22<br>APK và backend<br>☐<br>chạy lại|SV3+2 ·<br>D20|Cài app-debug.apk mới; env sạch,<br>pairing/RTSP/alarm/ack được lặp từ đầu.|Không phát hành<br>cửa hàng/iOS.|



Tất cả checkbox để trống trong kế hoạch vì nhóm chưa thực hiện kiểm thử. Chỉ đánh dấu sau khi thao tác tương ứng chạy thực. Một push gửi tay chỉ kiểm sender/app; không đủ 

đánh dấu AI end-to-end. Một skeleton trên webcam chỉ kiểm pose; không đủ đánh dấu phát hiện ngã. Nếu nhánh A thiếu dữ liệu thật, ghi đúng blocked/partial và hoàn thiện phần pipeline huấn luyện pilot; không gọi đó là model đã được kiểm chứng. 

## 12. Ưu tiên, rủi ro và cách chạy bản demo 

### 12.1. P0/P1/P2 và thứ tự cắt phạm vi 

|**Mức**|**Giữ/làm chức năng gì?**|**Điều kiện ưu tiên**|
|---|---|---|
|P0 — đường<br>chạy MVP|Một RTSP; reconnect; AI pose+temporal; confirm/latch;<br>event ID; ghép không account có key; Android<br>status/preview; push nền; sound/stop; test toàn tuyến;<br>APK debug.|Mọi yêu cầu cốt lõi của bạn nằm ở<br>đây. Hai hướng AI phải có lộ<br>trình/thử tối thiểu; chỉ một hướng<br>được dùng online cho MVP.|
|P1 — khi P0<br>ổn|QR/deep link tự mở, HTTPS có chứng chỉ cho dùng<br>ngoài lab, thêm hard negatives/threshold per camera,<br>history UI gọn, CPU optimization đã đo.|Nếu chuyển ra mạng công cộng thì<br>HTTPS trở thành điều kiện bắt buộc<br>trước sử dụng, không coi HTTP lab<br>là đủ.|
|P2 — có thể<br>bỏ|iOS/desktop app, nhiều camera/nhiều người xuyên che<br>khuất, camera discovery, lưu clip/ảnh push,<br>WebRTC/HLS, auto-update, TensorRT/quantization,<br>dashboard lớn.|Không phân bổ trước khi ngày 15<br>P0 PASS. Bỏ P2 trước, không bỏ<br>push/âm/pairing để thêm giao diện.|



Thứ tự giảm tải: bỏ ảnh/clip push → bỏ overlay skeleton trên preview → preview snapshot 1 FPS → chỉ một device/camera → giữ B thay A nếu A chưa đạt. Luôn giữ đọc RTSP thật giao thức, state machine xác nhận, one-event episode, push nền và âm thanh theo OS. Không giảm bằng cách coi một message WS là push, coi “nằm” là “ngã”, hoặc bỏ khóa truy cập để khỏi sửa pairing. 

### 12.2. Rủi ro và hành động kiểm chứng cụ thể 

|**Rủi ro**|**Phát hiện sớm**|**Giảm rủi ro và mốc quyết định**|
|---|---|---|
|Dataset không tải/thiếu<br>nhãn|Ngày 3–4 tải 4 sequence, xem<br>metadata và cache pilot.|A giữ pilot/TCN nhỏ, B là đường chính; không<br>chuyển sang train pose từ đầu.|
|Leakage/overfit|Assert split groups; so train/val;<br>subject_id unknown không tự bịa.|Khóa split trước windowing; ghi giới hạn<br>recording-independent; không test-tune lặp.|
|Báo nhầm ngồi/nằm/cúi|Bộ hard negative từ tuần 2;<br>T06/T07.|Onset + nhiều tín hiệu + thời gian; tune val; giữ<br>số FP thật.|
|Bỏ sót ngã chậm/che<br>khuất|T08 và clip ngã hướng camera;<br>kiểm thiếu pose.|Không giả dữ liệu; camera đủ toàn thân; công<br>bố điều kiện chưa hỗ trợ và recall đo được.|
|RTSP block/độ trễ|Ngày 3 camera tắt/sai URL; đo last-<br>frame age.|Timeout tại open, TCP, capture riêng, buffer<br>nhỏ; giảm substream/preview, test actual<br>backend.|



|**Rủi ro**|**Phát hiện sớm**|**Giảm rủi ro và mốc quyết định**|
|---|---|---|
|CPU/GPU không đủ|Benchmark pose ngay ngày 1 và<br>ngày 4 extraction pilot.|CPU first, nano/320, một camera; không thêm<br>model nặng. A chỉ chạy khi sampling thật đủ.|
|Push không tới|Smoke điện thoại ngày 5, kiểm<br>project/applicationId/permission/ser<br>vices.|FCM đúng SDK, foreground/background tách;<br>message accepted khác nhận; TTL/retry hữu<br>hạn.|
|Âm thanh nền không<br>như mong|Channel/sound test máy thật trước<br>ngày 15.|Hai channel alert/silent; raw resource; không<br>hứa vượt DND hoặc force-stop.|
|Lẫn thiết bị/camera|T16 pairing/revoke/mismatch<br>installation và endpoint ownership.|Key riêng, backend installation ID, FCM device<br>list scoped, không topic global; HTTPS khi<br>ngoài lab.|
|Chờ nhau đến tuần 4|Ngày 2 contract/mock, ngày 5 ghép<br>thật.|Bàn giao từng ranh giới; stub có nhãn; ngày 10<br>AI thật, ngày 15 toàn tuyến.|



### 12.3. Kịch bản chạy demo cuối từ đầu 

- 1. Laptop mở đúng venv/config/weights, credential backend đã đặt ngoài repo; Uvicorn một worker. Kiểm /health và AI mode/model_id, không mock. 

- 2. Khởi động camera RTSP thật. Nếu buổi thử chưa có camera, mở MediaMTX và FFmpeg -re phát MP4 qua RTSP, nói rõ nguồn giả lập. Không đổi sang đọc file trực tiếp rồi gọi là RTSP. 

- 3. Cài APK debug cuối lên Android, mở app, cấp quyền thông báo, CLI tạo link ghép mới, dán vào app. Nhập RTSP; xem CONNECTING→CONNECTED và AI WARMUP→READY. 

- 4. Bấm thử thông báo để kiểm đường FCM/sound trước; message có nhãn thử. Tắt âm, xác nhận đã xem; sau đó bắt đầu thử AI thật. 

- 5. Phát clip ngã hoặc dùng video hợp lệ qua camera/publisher; chờ confirmation, kiểm một event ID hiện ở app. Giữ tư thế nằm trong clip, không có cảnh báo lặp theo frame. 

- 6. Thu nhỏ/khóa điện thoại và cho lần ngã tiếp theo sau recovery/cooldown hoặc dùng episode mới; system notification có sound theo channel. Chạm mở đúng event, bấm tắt/đã xem. 

- 7. Dừng nguồn RTSP rồi mở lại: app thấy reconnect, AI warmup và phục hồi; không tự báo ngã từ khoảng mất frame. Thử một hard negative để kiểm báo nhầm. 

- 8. Restart backend và mở lại app; installation/pairing bền, status/events được đồng bộ. Đối chiếu C01–C22 và số đo thật; phần chưa kiểm được giữ chưa PASS. 

### 12.4. Hoàn thành 4 tuần nghĩa là gì? 

Sản phẩm hoàn thành khi nhóm có thể cài APK, khởi động backend, ghép không tài khoản, cấu hình RTSP và lặp được pipeline AI thật → xác nhận → sự kiện → push/app → âm thanh/tắt cảnh báo, kèm test các lỗi quan trọng. Nhóm hiểu module mình viết và hợp đồng mình dùng. Mức hoàn thiện không được suy từ số file hoặc giao diện đẹp. A là nhánh tự train có quy trình thử nghiệm rõ; B bảo vệ khả năng hoàn thành. Tính năng chạy được và chất lượng phát hiện là hai kết quả phải kiểm tra riêng bằng bằng chứng thật. 

## 13. Nguồn kỹ thuật và quy ước tra cứu 

### 13.1. Nguồn đã đối chiếu 

[S1] Đề bài chính thức — AI_Midterm_Project.pdf, 7 trang; Application Track trang 1–2; các phần còn lại xác định phạm vi toàn học phần. 

[S2] Sample project — Commit 8256b6a042ef04907c31c53f5310028a10af79be; README, camera, pipeline, risk/state_machine, alerts, API, frontend và configs. 

<u>https://github.com/QuocCuong66/Project-monitoring-model/tree/ 8256b6a042ef04907c31c53f5310028a10af79be</u> 

[S3] Ultralytics YOLO11 — Danh sách model filenames và hỗ trợ pose; lựa chọn yolo11npose được dùng làm baseline, không yêu cầu phiên bản mới nhất. 

<u>https://docs.ultralytics.com/models/yolo11/</u> 

[S4] Ultralytics tracking — Track mode, tracker và persist qua frame; kế hoạch chỉ định ByteTrack rõ ràng. 

<u>https://docs.ultralytics.com/modes/track/</u> 

[S5] MediaPipe Pose Landmarker — Đầu ra landmarks và setup Python; dùng khi so phương án pose dự phòng. 

<u>https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python</u> 

[S6] UR Fall Detection Dataset — Nguồn dataset gốc: sequence RGB/depth, camera và điều kiện sử dụng. 

<u>https://fenix.ur.edu.pl/~mkepski/ds/uf.html</u> 

[S7] OpenCV Video I/O flags — OPEN_TIMEOUT/READ_TIMEOUT là cấu hình lúc mở và phụ thuộc backend. 

<u>https://docs.opencv.org/4.10.0/d4/d15/group__videoio__flags__base.html</u> 

[S8] FCM Android setup — POST_NOTIFICATIONS, service/config và notification channel. <u>https://firebase.google.com/docs/cloud-messaging/android/get-started</u> 

[S9] FCM Flutter receive — Foreground/background/terminated, onMessage/open/initial message và giới hạn force-stop. 

<u>https://firebase.google.com/docs/cloud-messaging/flutter/receive-messages</u> 

[S10] Firebase Flutter setup — Firebase CLI/FlutterFire, firebase_options.dart và nền tảng Android. 

##### <u>https://firebase.google.com/docs/flutter/setup</u> 

[S11] Firebase Admin send — Server SDK, credential và gửi theo endpoint đã đăng ký; kiểm API SDK hiện hành khi smoke. 

<u>https://firebase.google.com/docs/cloud-messaging/send/admin-sdk</u> 

[S12] Android notification channels — Hành vi channel và quyền kiểm soát của người dùng. <u>https://developer.android.com/develop/ui/compose/notifications/channels</u> 

[S13] PyTorch save/load — state_dict, eval, map_location và load weights cho inference. 

<u>https://docs.pytorch.org/tutorials/beginner/saving_loading_models</u> 

[S14] flutter_mjpeg — Widget HTTP MJPEG, header, timeout và lifecycle isLive. 

<u>https://pub.dev/documentation/flutter_mjpeg/latest/</u> 

[S15] MediaMTX + FFmpeg — Phát MP4 qua RTSP bằng FFmpeg, dùng cho môi trường thử giao thức. 

##### <u>https://mediamtx.org/docs/publish/ffmpeg</u> 

[S16] flutter_local_notifications — Raw resource sound, Android channels, icon và resource giữ khi build. 

##### <u>https://pub.dev/documentation/flutter_local_notifications/latest/</u> 

[S17] FastAPI async/concurrency — I/O và tác vụ CPU; cơ sở tách inference khỏi event loop. 

##### <u>https://fastapi.tiangolo.com/async/</u> 

Tài liệu kỹ thuật được đối chiếu ngày 29/10/2026. API/thư viện có thể thay đổi; ngày 1 nhóm chọn bộ phiên bản thực sự chạy smoke, ghi lockfile rồi giữ bộ đó trong 4 tuần. Các thuật toán, cấu trúc project, ngưỡng thử, phân chia giờ và chỉ tiêu trong kế hoạch là đề xuất kỹ thuật của kế hoạch này; không phải các kết quả đo hoặc yêu cầu nguyên văn từ tài liệu framework. 

### 13.2. Từ điển ngắn cho thành viên mới 

|**Thuật ngữ**|**Hiểu và áp dụng trong project**|
|---|---|
|Suy luận (inference)|Chạy model đã có weights trên frame/chuỗi để lấy output; khác huấn luyện<br>cập nhật weights.|
|Ước lượng tư thế (pose<br>estimation)|Tìm khớp cơ thể; chưa phải xác định sự kiện ngã.|
|Cửa sổ trượt (sliding window)|Giữ một đoạn quá khứ gần nhất; phải có thời gian thật để biết 30 mẫu dài<br>bao lâu.|
|Máy trạng thái (finite state<br>machine)|Quyết định khi nào nghi ngờ/xác nhận/latch/hồi phục; giúp một frame<br>nhiễu không thành alarm.|
|Chống lặp<br>(deduplication/idempotency)|Cùng sự kiện/episode được xử lý nhiều lần nhưng chỉ tạo một kết quả<br>cảnh báo có ích.|
|Tập xác thực (validation)|Dùng chọn threshold/siêu tham số; khác tập test khóa để đánh giá sau lựa<br>chọn.|
|Rò rỉ dữ liệu (data leakage)|Thông tin/recording của test xuất hiện ở train/tuning, làm điểm đánh giá<br>cao giả.|
|Thông báo đẩy (push notification)|Message được nền tảng chuyển tới app/OS dù không giữ WS, có điều<br>kiện mạng/quyền/vòng đời.|
|Ghép thiết bị (device pairing)|Cấp khóa cho điện thoại được phép dùng backend, không tạo tài khoản<br>người dùng.|
|MVP|Phiên bản tối thiểu chạy được trọn quy trình cốt lõi và đã kiểm tra các lỗi<br>quan trọng.|



