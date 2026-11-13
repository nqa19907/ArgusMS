# ArgusMS — SV3 tuần 1

App Flutter Android cho ghép thiết bị, status HTTP, sự kiện WebSocket và FCM smoke test.
Backend tương thích: `develop`/`backend` commit `e130c588225bdd954e9bf582c59ad3152461b167` (đối chiếu GitHub ngày 12/11/2026).

## Chức năng và giới hạn

- PairScreen: dán link, kiểm tra health, claim đúng một lần; thông báo rõ mã sai/đã dùng/hết hạn/timeout.
- Secure storage lưu server, installation, device ID và device secret trong một record; mở lại app vẫn ghép.
- Home: hiển thị backend, camera và AI riêng; nhãn MOCK khi dùng detector giả; dữ liệu cũ được đánh dấu khi backend offline.
- Status mỗi 5 giây khi foreground. WS có Bearer header, ping, backoff 1/2/4/8/15 giây, đóng khi background và mở lại khi resume.
- Nhận `fall.confirmed` dạng JSON gốc như SV2 đang phát; giới hạn dedup 100 ID trong bộ nhớ, lọc installation.
- Firebase lỗi không chặn pairing/status/WS. Nút xin quyền → lấy token → đăng ký vào API đúng device.
- Nhận FCM foreground và hiển thị nguồn riêng; chạm push background/terminated mở Home với thông tin event.
- Có demo offline được gắn nhãn DỮ LIỆU MẪU; không lưu pairing giả.
- Hủy ghép gọi DELETE để revoke. Nếu chỉ quên trên app khi offline, backend chưa được revoke; nhờ SV2 thu hồi bằng CLI.

Chưa thuộc bản tuần 1: cấu hình RTSP/camera preview, alarm foreground vòng lặp, nút ack, event replay bền qua restart, seen store bền, sound setting và raw sound tùy chỉnh. Không dùng bản này để tuyên bố pipeline AI end-to-end đã được nghiệm thu.

## File cần hiểu

| File | Công dụng |
| --- | --- |
| `lib/main.dart` | App và lifecycle |
| `lib/app_controller.dart` | Điều phối pairing/status/WS/FCM |
| `lib/config.dart` | Kiểm tra link/server, timeout |
| `lib/models.dart` | Parser REST/WS/FCM |
| `lib/fixtures.dart` | Dữ liệu demo gắn nhãn thử |
| `lib/services/api_client.dart` | Gọi đúng API SV2, auth và lỗi |
| `lib/services/device_store.dart` | Secure storage |
| `lib/services/ws_client.dart` | WS xác thực, ping và reconnect |
| `lib/services/notification_service.dart` | Firebase, quyền, channel, token adapter |
| `lib/screens/` | Pair và Home |
| `tool/ai_week1.yaml` | Cấu hình mock tùy chọn cho backend tuần 1 |
| `test/` | Parser, API, controller/lifecycle/dedup, WS cục bộ, giao diện |

## 1. Android trên máy SV3

Giữ `applicationId = com.student.mobile`. Bộ công cụ đang dùng: Flutter stable 3.47.9, Dart 3.13.7; compileSdk 37, AGP 9.1.1, Gradle 9.3.1, Java source/target 17, desugar_jdk_libs 2.1.4. JDK chạy Gradle trên Mac hiện là JDK 25 đi kèm Android Studio. Không cần đổi JDK nếu build đang thành công.

1. Android Studio → SDK Manager → SDK Platforms: cài Android SDK Platform 37.
2. SDK Tools: giữ Build-Tools, Platform-Tools, Command-line Tools và Emulator. NDK dùng phiên bản Gradle/Flutter yêu cầu.
3. Device Manager: máy ARM64 Google Play trên Mac Apple Silicon. Với API 37 dùng system image đã vá, revision 5 trở lên; image của bạn đã là revision 8.
4. Khởi động máy ảo, đợi vào màn hình chính. Kiểm tra Chrome/Play Store mở được.
5. Trong thư mục `mobile`, chạy:

```bash
flutter doctor -v
flutter devices
flutter pub get
flutter analyze
flutter test
flutter run -d emulator-5554
```

Thay device ID theo `flutter devices`. App không còn là màn đếm số: lần đầu mở PairScreen. Muốn xem ngay mà chưa có backend, bấm **Xem demo dữ liệu mẫu**.

Chỉ APK debug bật cleartext HTTP trong `android/app/src/debug/AndroidManifest.xml`. APK release cần HTTPS/WSS; parser từ chối pairing HTTP trong release. Không mở backend/camera ra Internet cho demo này.

## 2. Firebase của nhóm

App giữ cấu hình client Firebase bạn đã tạo. `google-services.json` và `firebase_options.dart` là client config, không phải khóa Firebase Admin. Nếu nhóm chọn project khác, cấu hình lại từ thư mục `mobile`:

```bash
firebase login
firebase projects:list
flutterfire configure --platforms=android
```

Kiểm tra Project ID trong hai file client phải trùng project mà SV2 dùng để gửi FCM; package name phải là `com.student.mobile`. Rebuild hoàn toàn sau khi đổi file Android/Firebase.

Service account JSON chỉ nằm ở máy backend, bên ngoài Git và app. SV2 đặt `GOOGLE_APPLICATION_CREDENTIALS` trước khi chạy backend.

### Endpoint và channel tương thích SV2

Backend hiện gửi bằng `firebase_admin.messaging.Message(token=...)`; adapter app dùng `getToken()`/`onTokenRefresh` còn được hỗ trợ ở firebase_messaging 17.0.1. Các API này đã deprecated nhưng được giữ có chủ đích để tương thích sender hiện tại. Không thay bằng FID ở riêng app. Khi cả nhóm chuyển sang FID, phải đổi sender và adapter cùng lần rồi thử lại.

Backend hiện chọn `fall_alerts_v1`/`fall_silent_v1`, kể cả test event. App tạo sẵn hai ID này để nhận được, đồng thời giữ `fall_test_v0` làm default. Tuần 1 chỉ dùng sound mặc định. Vì sound channel đã tạo không thể tự đổi tùy ý, tuần 3 thêm âm raw riêng phải chốt ID version MỚI ở cả app và backend (ví dụ `fall_alerts_v2`), không giả định đổi sound v1 sẽ tác dụng trên máy đã cài.

Không dùng topic chung, không đặt device secret trong push, không in token/secret vào log.

## 3. Chuẩn bị backend với SV2

SV2 dùng môi trường Python/backend đã có trên nhánh `develop` hoặc `backend`, Python 3.11 và requirements của backend. Không cần AI hoàn chỉnh để thử pairing/status/push. Chạy từ GỐC ArgusMS, không từ mobile.

Có thể dùng file mock riêng để không sửa cấu hình AI dùng chung:

macOS/Linux:

```bash
AI_CONFIG_PATH=mobile/tool/ai_week1.yaml python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1
```

PowerShell trên máy Windows của SV2:

```powershell
$env:AI_CONFIG_PATH = "mobile/tool/ai_week1.yaml"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Nếu file `mobile/tool/ai_week1.yaml` chưa có trên máy SV2, gửi riêng file YAML này hoặc tích hợp nhánh app trước. Nội dung chỉ `mode: mock` và comment hướng dẫn. Giữ camera URL rỗng ở tuần 1 nếu chưa có camera.

Trước khi mở backend, nếu cần push, SV2 đặt credential cùng Firebase project:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/duong-dan-rieng/firebase-admin.json"
```

Đường dẫn trên là ví dụ, phải thay bằng file thực ở máy SV2. Không commit file hoặc dán private_key vào chat. Khởi động lại backend sau khi đặt biến vì sender đọc credential lúc startup.

## 4. Chọn địa chỉ backend ĐÚNG cho Android

| Thiết bị app | Backend ở đâu? | Server trong link ghép |
| --- | --- | --- |
| Emulator trên Mac bạn | Cùng Mac bạn | `http://10.0.2.2:8000` |
| Emulator trên Mac bạn | Laptop SV2 trong cùng LAN | `http://IP_LAN_MAY_SV2:8000` |
| Điện thoại Android thật | Laptop backend trong cùng LAN | `http://IP_LAN_BACKEND:8000` |

`localhost` trên Android là Android, không phải laptop. `10.0.2.2` chỉ trỏ về host của emulator, không trỏ tới máy SV2 khác.

SV2 chạy Uvicorn với `--host 0.0.0.0`; cho phép port 8000 qua firewall trên mạng lab. Cùng Wi-Fi vẫn có thể bị client isolation trên mạng guest/trường. Thử endpoint từ Chrome trong chính emulator trước.

Ví dụ backend cùng Mac: mở Chrome trên emulator, vào `http://10.0.2.2:8000/health`. Mong đợi `{"status":"alive","schema_version":1}`. Health chỉ xác nhận API sống, không chứng minh AI/camera/push.

## 5. Ghép thiết bị thật

1. SV2 giữ backend chạy trong terminal thứ nhất.
2. Mở terminal thứ hai, vào đúng gốc repository và cùng cấu hình storage/APP_CONFIG_PATH như server.
3. Tạo link mà Android truy cập được. Ví dụ backend cùng Mac:

```bash
python -m backend.pairing create --base-url http://10.0.2.2:8000
```

Nếu backend trên laptop SV2, thay base URL bằng IP LAN thực của laptop SV2. Link hết hạn sau 120 giây.

4. Sao chép TOÀN BỘ link `fallguard://pair?...` (không sao chép dòng `Pairing Link:`), dán vào PairScreen.
5. Bấm **Kiểm tra backend** để gọi health mà không tiêu thụ code.
6. Bấm **Ghép thiết bị** đúng một lần. Claim timeout có thể đã dùng code: tạo link mới, không retry tự động.
7. Home phải hiện Device ID, installation và status. STOPPED khi chưa bật camera là trạng thái hợp lệ. Camera có hình không đồng nghĩa AI READY.
8. Đóng rồi mở lại app thông thường: không cần ghép lại. Reinstall/xóa app data có thể mất khóa và phải ghép mới.

## 6. Kiểm tra HTTP/WS và mất kết nối

- Home: HTTP có status; WS hiển thị Đã kết nối.
- Source SV2 hiện chưa phát status định kỳ qua WS, nên app polling REST mỗi 5 giây. `fall.confirmed` đi WS như hiện có; khi SV2 bổ sung `camera.status`/`ai.status`, app yêu cầu snapshot mới.
- Dừng backend: HTTP báo lỗi/dữ liệu cũ; WS backoff, UI không treo.
- Mở lại cùng backend/storage: status và WS tự phục hồi khi app foreground.
- Nhấn Home trên Android: app ngừng polling/WS. Mở lại app: lấy status mới và chỉ một WS.
- Revoke khóa bằng backend CLI: lần REST tiếp theo trả 401, app xóa thông tin ghép và về Pair.
- Backend API hiện trả test event qua WS cho các client đang nối; nút gửi test nhận event qua WS KHÔNG chứng minh push FCM tới máy.

## 7. Kiểm tra FCM

1. Đảm bảo backend và Android có Internet, Firebase project trùng nhau, emulator có Google Play hoạt động.
2. Trên Home, bấm **Bật / đăng ký lại thông báo**; chọn Allow trên Android nếu có hộp xin quyền.
3. Đợi **Endpoint: backend đã xác nhận lưu**. Đây là PUT thành công, chưa phải push delivery.
4. Bấm **Yêu cầu backend gửi thử** khi app đang mở. Kiểm tra nguồn event: WS hoặc FCM foreground; cùng ID chỉ cập nhật một lần.
5. Để chứng minh đường FCM độc lập với WS, nhấn Home trên Android. Từ terminal SV2 ở gốc repo, dùng Device ID hiển thị trên Home:

```bash
python -m scripts.test_push --device-id MA_DEVICE_THUC
```

`MA_DEVICE_THUC` phải thay bằng `dev-...` của thiết bị vừa ghép. Đừng dùng `<...>` nguyên văn trong shell.

6. `Outcome: accepted` nghĩa FCM server nhận yêu cầu, chưa chứng minh thiết bị đã hiện thông báo. Quan sát system notification trên emulator.
7. Chạm notification: app mở Home và hiển thị đúng Event ID/camera/nhãn THÔNG BÁO THỬ. Script gửi test trực tiếp không lưu event vào event store; app đọc payload rút gọn nên vẫn hiển thị được.
8. Nếu script báo chưa có token/credential, xử lý đúng phía đó. Nếu app báo registration timeout, kiểm Google Play/network và dùng nút đăng ký lại sau khi sửa.

Foreground tuần 1 chỉ hiện thẻ trong app, không chạy alarm loop, không tạo thêm local notification có sound. Background dùng Android notification. Không có Dart background loop; không tạo thông báo trùng khi SDK đã hiển thị notification payload. Force-stop trong Android Settings có thể ngừng nhận đến khi mở lại app. Máy thật, DND, volume và tiết kiệm pin phải ghi kết quả riêng.

## 8. Contract khóa với SV2

| API | Dữ liệu app gửi/nhận |
| --- | --- |
| GET `/health` | `status=alive`, `schema_version=1` |
| POST `/api/v1/pairing/claim` | `pairing_code`, `expected_installation_id`, `client_label` → `device_id`, `device_secret`, `installation_id` |
| GET `/api/v1/status` | Bearer secret; camera.id/state, ai.state/mode/model_id/processed_fps, notifications |
| WS `/api/v1/ws` | Bearer header ở handshake; event gốc `type=fall.confirmed`; ping/pong |
| PUT `/api/v1/devices/{id}/push` | `push_kind: fcm`, `push_value: token`, `sound_enabled: true` |
| POST `/api/v1/notifications/test` | 202, `event_id`, `is_test: true`; không tự sinh kết quả AI |
| DELETE `/api/v1/devices/{id}` | Revoke chính thiết bị, rồi app xóa secure record |

FCM data dùng chuỗi cho `schema_version` và `is_test`. Parser app có đường riêng. Event khác installation bị bỏ qua; không hiển thị rule_score như xác suất chính xác/y khoa.

## 9. Push nhánh và mở PR với SV2

Nhánh SV3 đề xuất: `sv3/flutter-app`, tạo từ `origin/develop` vì backend SV2 đã nằm ở develop. Không merge nguyên backend vào main để thử app.

Từ gốc ArgusMS, nếu đã có nhánh SV3 thì không tạo lại:

```bash
git status
git branch --show-current
git diff --check
```

Kiểm thử trong thư mục mobile:

```bash
flutter analyze
flutter test
flutter build apk --debug
```

Sau đó về gốc repo, xem file trước khi stage/commit:

```bash
cd ..
git add mobile
git diff --cached --stat
git diff --cached --check
git commit -m "feat(mobile): implement SV3 week-one pairing status and push setup"
git push -u origin sv3/flutter-app
```

Trên GitHub: Compare & pull request → base `develop`, compare `sv3/flutter-app`; nhờ SV2 review schema và cùng chạy checklist. Không tự merge PR trước khi đã test ranh giới app/backend.

Để cập nhật code SV2 sau này, commit công việc đang làm trước rồi:

```bash
git fetch origin
git switch sv3/flutter-app
git merge origin/develop
```

Nếu nhóm chốt nhánh tích hợp khác develop, thay nhánh theo quyết định chung. Không dùng force push để giải quyết conflict.

## 10. Checklist bàn giao — chỉ đánh dấu khi đã thao tác

- [ ] APK debug cài và mở Pair/Home trên emulator/Android đã chọn.
- [ ] Health thực từ emulator truy cập được.
- [ ] Pair một lần; claim lại 409/hết hạn 410 hiển thị rõ; khóa sai 401 về Pair.
- [ ] Restart app thông thường vẫn giữ pairing.
- [ ] Camera STOPPED/CONNECTED/ERROR khác AI WARMUP/READY/ERROR.
- [ ] WS nối thật; pause/resume không nhân socket; backend restart tự nối lại.
- [ ] Quyền notification được xin; từ chối vẫn dùng HTTP/WS.
- [ ] Endpoint được đăng ký đúng device_id ở backend.
- [ ] Push foreground và chạm push đúng event.
- [ ] System notification đến khi Home/khóa màn hình, kiểm bằng script SV2, không nhầm WS thành push.
- [ ] Không có secret, URL camera có mật khẩu, local.properties, build/cache trong Git.
- [ ] Ghi máy/OS và kết quả máy thật riêng; emulator chưa thay thế nghiệm thu máy thật.

Kiểm thử tự động trong báo cáo bàn giao chỉ chứng minh các phạm vi đã chạy. Firebase delivery, sound và lifecycle trên máy thật vẫn là checklist tích hợp chưa được tự động suy thành PASS.

## 11. Test contract tự động với source SV2 (tùy chọn)

`tool/contract_server.py` là harness chỉ dùng để test trên localhost: import route/auth/SQLite/WS thật của backend, thay pipeline và FCM sender bằng đối tượng kiểm thử. Không chạy AI, không có outbox worker gửi mạng, không đọc service account. Không dùng harness này làm backend demo/production.

Từ gốc repo, với môi trường backend đã có FastAPI/Uvicorn/OpenCV/numpy và WebSocket transport:

```bash
python -m mobile.tool.contract_server
```

Mở terminal khác ở `mobile`:

```bash
flutter test test/backend_contract_test.dart --dart-define=ARGUS_CONTRACT_TEST=true
```

Test thực hiện health → claim → claim lại 409 → status → WS Bearer → PUT endpoint → test event qua WS → revoke → status 401. Server chỉ lắng nghe `127.0.0.1:18761`, dùng SQLite tạm và xóa sau khi dừng. Dừng server bằng Control+C.

`flutter test` thông thường bỏ qua test contract này để không phụ thuộc backend đang chạy; các test còn lại dùng fake/local WS và chạy độc lập.

Home có bộ đếm **FCM đã nhận khi app mở** và **Lần mở từ notification** để không nhầm một event được dedup từ WS thành bằng chứng FCM. Các bộ đếm là chẩn đoán trong phiên, không phải metric nghiệm thu hay lịch sử bền.
