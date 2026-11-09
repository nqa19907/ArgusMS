import numpy as np


def summarize_latency(samples: list[dict]) -> dict:
    stages = {
        "capture_to_infer_ms": ("t_capture", "t_infer_done"),
        "onset_to_confirmed_ms": ("t_onset", "t_confirmed"),
        "confirmed_to_fcm_accepted_ms": ("t_confirmed", "t_fcm_accepted"),
        "confirmed_to_app_received_ms": ("t_confirmed", "t_app_received"),
    }
    report: dict = {}
    for name, (start_k, end_k) in stages.items():
        diffs = [
            (float(s[end_k]) - float(s[start_k])) * 1000.0
            for s in samples
            if start_k in s and end_k in s and s[start_k] is not None and s[end_k] is not None
            and float(s[end_k]) >= float(s[start_k])
        ]
        if not diffs:
            report[name] = {"count": 0, "p50_ms": None, "p95_ms": None}
        else:
            arr = np.array(diffs, dtype=np.float64)
            report[name] = {
                "count": len(diffs),
                "p50_ms": round(float(np.percentile(arr, 50)), 2),
                "p95_ms": round(float(np.percentile(arr, 95)), 2),
            }
    return report