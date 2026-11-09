#!/usr/bin/env bash
set -euo pipefail
VIDEO_PATH="${1:-data/raw/demo/fall.mp4}"
RTSP_URL="${2:-rtsp://127.0.0.1:8554/fall_demo}"

ffmpeg -re -stream_loop -1 -i "$VIDEO_PATH" \
  -an -c:v libx264 -preset veryfast -tune zerolatency -pix_fmt yuv420p \
  -f rtsp -rtsp_transport tcp "$RTSP_URL"