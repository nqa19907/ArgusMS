"""Preview real pose or deterministic mock independently of the backend/app."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
import uuid

# Support both `python scripts/ai_smoke.py` and `python -m scripts.ai_smoke`.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2

from backend.ai.factory import create_detector, create_pose_estimator, load_settings
from backend.contracts import FramePacket
from evaluation.extract import FrameSource


SKELETON = ((5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12),
            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16))


def draw_poses(image, poses) -> None:
    for pose in poses:
        x1, y1, x2, y2 = map(int, pose.bbox_xyxy)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 220, 0), 2)
        cv2.putText(image, f"track={pose.track_id}", (x1, max(15, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 220, 0), 1)
        for a, b in SKELETON:
            if pose.valid_keypoints[a] and pose.valid_keypoints[b]:
                cv2.line(image, tuple(map(int, pose.keypoints[a, :2])),
                         tuple(map(int, pose.keypoints[b, :2])), (0, 180, 255), 2)
        for point, valid in zip(pose.keypoints, pose.valid_keypoints):
            if valid:
                cv2.circle(image, tuple(map(int, point[:2])), 3, (255, 100, 0), -1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Video, RGB folder, RTSP URL, or webcam index")
    parser.add_argument("--mode", choices=("pose", "mock"), default="pose")
    parser.add_argument("--config", default="configs/ai.yaml")
    parser.add_argument("--fps", type=float, help="Verified source FPS override")
    parser.add_argument("--timestamps", type=Path, help="CSV frame_id,time_s for image sequences/VFR")
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--max-frames", type=int, help="Omit to process the entire clip")
    parser.add_argument("--output", type=Path, help="Optional annotated MP4")
    args = parser.parse_args()
    if args.max_frames is not None and args.max_frames < 1:
        parser.error("--max-frames must be positive")
    settings = load_settings(args.config)
    engine = create_pose_estimator(settings) if args.mode == "pose" else create_detector({**settings, "mode": "mock"})
    source = int(args.source) if args.source.isdecimal() else args.source
    session = uuid.uuid4().hex
    count = detections = empty = 0
    elapsed_ms = 0.0
    writer = None
    started = perf_counter()
    try:
        with FrameSource(source, fps=args.fps, timestamps_path=args.timestamps) as frames:
            for frame_id, timestamp, image in frames:
                before = perf_counter()
                if args.mode == "pose":
                    poses = engine.estimate(image)
                    amount = len(poses)
                else:
                    packet = FramePacket("smoke", session, frame_id, timestamp,
                                         datetime.now(timezone.utc).isoformat(), image)
                    update = engine.process(packet)
                    if count < 3:
                        print(json.dumps(update.to_dict(), ensure_ascii=False))
                    amount = len(update.candidates)
                    poses = []
                elapsed_ms += (perf_counter() - before) * 1000
                count += 1
                detections += amount
                empty += amount == 0
                if not args.no_preview or args.output:
                    canvas = image.copy()
                    draw_poses(canvas, poses)
                    text = f"{args.mode} frame={frame_id} t={timestamp:.2f} " + (f"people={amount}" if amount else "empty")
                    cv2.putText(canvas, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
                    if args.output:
                        if writer is None:
                            args.output.parent.mkdir(parents=True, exist_ok=True)
                            writer = cv2.VideoWriter(str(args.output), cv2.VideoWriter_fourcc(*"mp4v"),
                                                     frames.fps or 10, (image.shape[1], image.shape[0]))
                            if not writer.isOpened():
                                raise OSError("Unable to open annotated video output")
                        writer.write(canvas)
                    if not args.no_preview:
                        cv2.imshow("ArgusMS SV1 week 1 (q to stop)", canvas)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                if args.max_frames is not None and count >= args.max_frames:
                    break
    finally:
        engine.close()
        if writer is not None:
            writer.release()
        if not args.no_preview:
            cv2.destroyAllWindows()
    seconds = perf_counter() - started
    print(json.dumps({"mode": args.mode, "is_test": args.mode == "mock", "frames": count,
                      "detections": detections, "empty_frames": empty,
                      "mean_inference_ms": elapsed_ms / count if count else 0,
                      "processing_fps": count / seconds if seconds else 0,
                      "fall_scoring_available": False}, indent=2))


if __name__ == "__main__":
    main()
