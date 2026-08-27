#!/usr/bin/env python3
"""Validate candidate word records, skip duplicates, and append new records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from word_utils import duplicate_key, load_collection, validate_entry, write_collection


HERE = Path(__file__).resolve().parent
WORDS_PATH = HERE / "words.json"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge a JSON array of complete word records into words.json."
    )
    parser.add_argument("candidates", type=Path, help="candidate JSON file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and report without changing words.json",
    )
    return parser.parse_args()


def load_candidates(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        candidates = json.load(handle)
    if not isinstance(candidates, list):
        raise ValueError(f"{path}: expected a JSON array")
    for position, entry in enumerate(candidates):
        validate_entry(entry, position, str(path))
    return candidates


def main() -> int:
    arguments = parse_arguments()
    existing = load_collection(WORDS_PATH)
    candidates = load_candidates(arguments.candidates)

    known = {duplicate_key(entry["word"]): entry["word"] for entry in existing}
    added: list[dict] = []
    skipped: list[tuple[str, str]] = []

    for entry in candidates:
        key = duplicate_key(entry["word"])
        if key in known:
            skipped.append((entry["word"], known[key]))
            continue
        known[key] = entry["word"]
        added.append(entry)

    if not arguments.dry_run and added:
        write_collection(WORDS_PATH, [*existing, *added])

    mode = "DRY RUN" if arguments.dry_run else "MERGED"
    print(
        f"{mode}: candidates={len(candidates)} added={len(added)} "
        f"skipped_duplicates={len(skipped)} total={len(existing) + len(added)}"
    )
    for candidate, existing_word in skipped:
        print(f"SKIP {candidate!r}: duplicate of {existing_word!r}")
    for entry in added:
        print(f"ADD  {entry['word']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"merge_words.py: {error}") from error
