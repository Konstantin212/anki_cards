"""Shared validation and normalization for Anki word records."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path


ENTRY_FIELDS = ("word", "full", "translation", "forms", "examples")
FORMS_PATTERN = re.compile(
    r"^Perfekt: (er|sie|es) .+ · Präteritum: \1 .+$"
)


def clean_word(word: str) -> str:
    """Remove display markup used for split verbs and phrase blanks."""
    return " ".join(word.replace("*", "").replace("…", "").split())


def duplicate_key(word: str) -> str:
    """Return the canonical key used by merge and package generation."""
    return clean_word(word).lower()


def validate_entry(entry: object, position: int, source: str) -> None:
    """Validate one record and raise ValueError with source context."""
    label = f"{source}[{position}]"
    if not isinstance(entry, dict):
        raise ValueError(f"{label}: expected an object")
    if tuple(entry) != ENTRY_FIELDS:
        raise ValueError(
            f"{label}: expected fields in this order: {', '.join(ENTRY_FIELDS)}"
        )

    for field in ENTRY_FIELDS[:-1]:
        if not isinstance(entry[field], str):
            raise ValueError(f"{label}.{field}: expected a string")

    if not entry["word"].strip():
        raise ValueError(f"{label}.word: must not be empty")
    if entry["word"] != entry["word"].strip():
        raise ValueError(f"{label}.word: remove leading or trailing whitespace")
    if not duplicate_key(entry["word"]):
        raise ValueError(f"{label}.word: normalized duplicate key is empty")
    if entry["word"].count("*") > 1:
        raise ValueError(f"{label}.word: expected at most one '*' split marker")
    if not entry["translation"].strip():
        raise ValueError(f"{label}.translation: must not be empty")
    if entry["full"] and entry["forms"]:
        raise ValueError(f"{label}: full and forms cannot both be non-empty")
    if entry["forms"] and not FORMS_PATTERN.fullmatch(entry["forms"]):
        raise ValueError(
            f"{label}.forms: expected 'Perfekt: ... · Präteritum: ...' "
            "with the same subject"
        )

    examples = entry["examples"]
    if not isinstance(examples, list) or len(examples) > 2:
        raise ValueError(f"{label}.examples: expected a list with 0-2 pairs")
    for example_index, pair in enumerate(examples):
        if (
            not isinstance(pair, list)
            or len(pair) != 2
            or not all(isinstance(value, str) and value.strip() for value in pair)
        ):
            raise ValueError(
                f"{label}.examples[{example_index}]: expected two non-empty strings"
            )


def validate_collection(entries: object, source: str) -> list[dict]:
    """Validate a JSON collection, including canonical duplicate keys."""
    if not isinstance(entries, list):
        raise ValueError(f"{source}: expected a JSON array")

    seen: dict[str, str] = {}
    for position, entry in enumerate(entries):
        validate_entry(entry, position, source)
        key = duplicate_key(entry["word"])
        if key in seen:
            raise ValueError(
                f"{source}[{position}]: duplicate word {entry['word']!r}; "
                f"already saw {seen[key]!r}"
            )
        seen[key] = entry["word"]
    return entries


def load_collection(path: Path) -> list[dict]:
    """Load and validate a JSON collection from disk."""
    with path.open(encoding="utf-8") as handle:
        entries = json.load(handle)
    return validate_collection(entries, str(path))


def write_collection(path: Path, entries: list[dict]) -> None:
    """Atomically write a validated collection using project formatting."""
    validate_collection(entries, str(path))
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(entries, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temporary_path = Path(handle.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
