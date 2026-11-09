import argparse
from urllib.parse import quote
from backend.config import load_settings
from backend.storage import Storage


def build_pairing_uri(base_url: str, code: str, installation_id: str) -> str:
    encoded_server = quote(base_url.rstrip("/"), safe="")
    encoded_code = quote(code, safe="")
    encoded_inst = quote(installation_id, safe="")
    return f"fallguard://pair?server={encoded_server}&code={encoded_code}&installation={encoded_inst}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Quản lý ghép thiết bị FallGuard (không tài khoản)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create_p = sub.add_parser("create", help="Sinh liên kết ghép thiết bị dùng 1 lần (120 giây)")
    create_p.add_argument("--base-url", required=True, help="Ví dụ: http://192.168.1.20:8000")
    create_p.add_argument("--ttl", type=int, default=120, help="Thời gian hiệu lực (giây)")

    revoke_p = sub.add_parser("revoke", help="Thu hồi quyền truy cập của một thiết bị")
    revoke_p.add_argument("--device-id", required=True, help="Mã device_id cần thu hồi")

    args = parser.parse_args()
    app_settings, _ = load_settings()
    storage = Storage(app_settings.sqlite_path)

    if args.cmd == "create":
        code, expires_at, inst_id = storage.create_pairing_code(ttl_seconds=args.ttl)
        uri = build_pairing_uri(args.base_url, code, inst_id)
        print(f"Installation ID : {inst_id}")
        print(f"Expires At (UTC): {expires_at}")
        print(f"Pairing Link    :\n{uri}")
    elif args.cmd == "revoke":
        ok = storage.revoke_device(args.device_id)
        if ok:
            print(f"Đã thu hồi thiết bị: {args.device_id}")
        else:
            print(f"Không tìm thấy thiết bị: {args.device_id}")


if __name__ == "__main__":
    main()