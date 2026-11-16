"""Build verified clip metadata and lock validation/test splits by group.

Run: python -m evaluation.manifest --metadata local-clips.json
Metadata is a JSON list. See README.md for fields and annotation rules.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import random
import re
from collections.abc import Iterable, Mapping

from backend.ai.pose import PROJECT_ROOT


CLIP_FIELDS = ("clip_id", "path", "group_id", "recording_id", "subject_id", "camera_id",
               "fps", "timestamps_path", "source", "license")
LABEL_FIELDS = ("clip_id", "onset_s", "impact_s", "end_s", "label")
CASE_FIELDS = ("case_id", "clip_id", "split", "expected", "interval")


def project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def validate_records(records: Iterable[Mapping]) -> list[dict]:
    rows = [dict(row) for row in records]
    seen: set[str] = set()
    recordings: dict[str, str] = {}
    paths: set[Path] = set()
    for row in rows:
        for field in ("clip_id", "path", "group_id", "recording_id", "camera_id", "source", "license"):
            if not str(row.get(field, "")).strip():
                raise ValueError(f"Missing {field} in manifest record")
        clip_id = str(row["clip_id"])
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", clip_id) or clip_id in seen:
            raise ValueError(f"Duplicate or unsafe clip_id: {clip_id}")
        seen.add(clip_id)
        if str(row["group_id"]).lower() in {"unknown", "?"}:
            raise ValueError("group_id must identify a verified recording/event group")
        recording = str(row["recording_id"])
        if recording in recordings and recordings[recording] != row["group_id"]:
            raise ValueError(f"Recording {recording} spans multiple groups")
        recordings[recording] = row["group_id"]
        path = project_path(row["path"]).resolve()
        if path in paths:
            raise ValueError(f"Source path is listed more than once: {path}")
        paths.add(path)
        if not path.exists():
            raise FileNotFoundError(path)
        row["subject_id"] = row.get("subject_id") or "unknown"
        row["timestamps_path"] = row.get("timestamps_path") or ""
        fps = row.get("fps")
        row["fps"] = float(fps) if fps not in (None, "", "unknown") else ""
        if row["fps"] != "" and (not math.isfinite(row["fps"]) or row["fps"] <= 0):
            raise ValueError(f"Invalid FPS for {clip_id}")
        if row["timestamps_path"]:
            if not project_path(row["timestamps_path"]).is_file():
                raise FileNotFoundError(row["timestamps_path"])
        elif row["fps"] == "":
            raise ValueError(f"{clip_id}: supply verified fps or timestamps_path")
    return rows


def read_manifest(path: str | Path) -> list[dict]:
    with project_path(path).open(encoding="utf-8-sig", newline="") as stream:
        return validate_records(csv.DictReader(stream))


def validate_groups(records: Iterable[Mapping], splits: Mapping) -> None:
    rows = list(records)
    groups = {row["group_id"] for row in rows}
    val, test = list(splits["val_groups"]), list(splits["test_groups"])
    if len(set(val)) != len(val) or len(set(test)) != len(test):
        raise ValueError("Duplicate groups in split")
    if not val or not test or set(val) & set(test):
        raise ValueError("Validation/test groups must be nonempty and disjoint")
    if set(val) | set(test) != groups:
        raise ValueError("Splits must cover every manifest group exactly once")
    recordings: dict[str, str] = {}
    for row in rows:
        previous = recordings.setdefault(row["recording_id"], row["group_id"])
        if previous != row["group_id"]:
            raise ValueError("Camera views of one recording must share a group")


def split_groups(records: Iterable[Mapping], *, seed: int = 42, test_fraction: float = 0.3) -> dict:
    rows = list(records)
    groups = sorted({row["group_id"] for row in rows})
    if len(groups) < 2 or not 0 < test_fraction < 1:
        raise ValueError("Need >=2 groups and 0 < test_fraction < 1")
    random.Random(seed).shuffle(groups)
    count = max(1, min(len(groups) - 1, round(len(groups) * test_fraction)))
    splits = {"schema_version": 1, "seed": seed, "val_groups": sorted(groups[count:]),
              "test_groups": sorted(groups[:count])}
    validate_groups(rows, splits)
    return splits


def build_manifest(records: Iterable[Mapping], output: str | Path) -> list[dict]:
    rows = validate_records(records)
    if not rows:
        raise ValueError("Cannot build a manifest without real clips")
    output = project_path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CLIP_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output", default="data/manifests/clips.csv")
    parser.add_argument("--splits", default="data/splits.json")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-fraction", type=float, default=0.3)
    args = parser.parse_args()
    with args.metadata.open(encoding="utf-8") as stream:
        records = validate_records(json.load(stream))
    split_path = project_path(args.splits)
    if split_path.exists():
        with split_path.open(encoding="utf-8") as stream:
            splits = json.load(stream)
        if splits.get("status") == "pending_real_data":
            splits = split_groups(records, seed=args.seed, test_fraction=args.test_fraction)
        else:
            validate_groups(records, splits)  # Do not silently reshuffle a locked test set.
    else:
        splits = split_groups(records, seed=args.seed, test_fraction=args.test_fraction)
    build_manifest(records, args.output)
    split_path.parent.mkdir(parents=True, exist_ok=True)
    split_path.write_text(json.dumps(splits, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(records)} clips; splits saved to {split_path}")


if __name__ == "__main__":
    main()
