## Mô tả thay đổi
- **Vai trò thực hiện:** [ ] SV1 (AI/CV) | [ ] SV2 (Backend/RTSP/FCM) | [ ] SV3 (Flutter/Mobile)
- **Tuần / Ngày theo kế hoạch:** 
- **Các file chính đã thêm/sửa:** 

## Checklist bắt buộc trước khi Merge
- [ ] **Hợp đồng dữ liệu (`contracts.py` / `schema_version`):** Không tự ý đổi tên trường hoặc kiểu dữ liệu mà chưa thống nhất với 2 thành viên còn lại.
- [ ] **Kiểm thử độc lập:** Đã chạy `$env:PYTHONPATH="."; python -m pytest -v` (với SV1/SV2) hoặc `flutter test` (với SV3) và toàn bộ test đều PASS.
- [ ] **An toàn bảo mật:** Không chứa `.env`, RTSP URL có mật khẩu thật, file JSON Firebase Service Account, hoặc file `runtime/fallguard.db`.
- [ ] **Dữ liệu & Trọng số:** Không commit nhầm video nặng trong `data/raw/` hoặc cache `data/features/*.npz`.

## Cách thành viên khác kiểm tra (Smoke Test)
```powershell
# Ghi lệnh ngắn gọn để thành viên nhận bàn giao chạy thử:

```
