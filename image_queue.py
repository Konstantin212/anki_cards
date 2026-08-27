#!/usr/bin/env python3
"""List new image inputs and record them after a successful word import."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORDS_DIR = HERE / "Words"
STATE_PATH = HERE / "image_import_state.json"
IMAGE_SUFFIXES = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}


def image_files() -> list[Path]:
    return sorted(
        (
            path
            for path in WORDS_DIR.rglob("*")
            if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
        ),
        key=lambda path: path.relative_to(HERE).as_posix().casefold(),
    )


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"version": 1, "processed": {}}
    with STATE_PATH.open(encoding="utf-8") as handle:
        state = json.load(handle)
    if state.get("version") != 1 or not isinstance(state.get("processed"), dict):
        raise ValueError(f"invalid state file: {STATE_PATH}")
    return state


def write_state(state: dict) -> None:
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=HERE,
            prefix=".image_import_state.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            temporary_path = Path(handle.name)
        os.replace(temporary_path, STATE_PATH)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


def relative_name(path: Path) -> str:
    return path.resolve().relative_to(HERE.resolve()).as_posix()


def pending_images(state: dict) -> list[Path]:
    processed = state["processed"]
    return [
        path
        for path in image_files()
        if processed.get(relative_name(path), {}).get("sha256") != file_hash(path)
    ]


def resolve_image(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = HERE / path
    path = path.resolve()
    try:
        path.relative_to(WORDS_DIR.resolve())
    except ValueError as error:
        raise ValueError(f"image is outside {WORDS_DIR}: {value}") from error
    if not path.is_file() or path.suffix.casefold() not in IMAGE_SUFFIXES:
        raise ValueError(f"unsupported or missing image: {value}")
    return path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    pending_parser = subparsers.add_parser("pending", help="list new or changed images")
    pending_parser.add_argument("--json", action="store_true", help="print a JSON array")
    mark_parser = subparsers.add_parser("mark", help="mark images as processed")
    mark_parser.add_argument("images", nargs="+", help="image paths under Words/")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    state = load_state()

    if arguments.command == "pending":
        pending = [relative_name(path) for path in pending_images(state)]
        if arguments.json:
            print(json.dumps(pending, ensure_ascii=False, indent=2))
        else:
            print(f"Pending images: {len(pending)}")
            for name in pending:
                print(name)
        return 0

    timestamp = datetime.now(timezone.utc).isoformat()
    marked = []
    for value in arguments.images:
        path = resolve_image(value)
        name = relative_name(path)
        state["processed"][name] = {
            "sha256": file_hash(path),
            "processed_at": timestamp,
        }
        marked.append(name)
    write_state(state)
    print(f"Marked processed: {len(marked)}")
    for name in marked:
        print(name)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"image_queue.py: {error}") from error
