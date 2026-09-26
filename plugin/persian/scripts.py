# WriterAgent - AI Writing Assistant for LibreOffice
# Copyright (c) 2026 Mohammad Mostafa Yazdanpanah
# SPDX-License-Identifier: GPL-3.0-or-later
"""Built-in Persian helper scripts for WriterAgent's Run Python Script picker."""

from __future__ import annotations

from typing import Any

from plugin.doc.doc_type import is_writer
from plugin.persian.normalize import extract_hazm_changes
from plugin.persian.spelling import find_spelling_changes


PERSIAN_HELPER_NAMES = frozenset({"normalize_review"})
_SHIPPED_TEMPLATES = frozenset({"normalize_review"})


def supports_persian_manual(doc: Any) -> bool:
    """Expose Persian Helpers for Writer documents."""
    if doc is None:
        return False
    try:
        return is_writer(doc)
    except Exception:
        return False


def _normalize_review(text: str) -> dict[str, list[list[str]]]:
    """Return exact Persian normalization/spelling replacements for selected text."""
    mechanical = extract_hazm_changes(text)
    spelling = find_spelling_changes(text)

    changes: list[list[str]] = []
    seen: set[tuple[str, str]] = set()

    for source in (mechanical, spelling):
        for pair in source.get("changes", []):
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                continue
            old, new = str(pair[0]), str(pair[1])
            key = (old, new)
            if old and new and old != new and key not in seen:
                seen.add(key)
                changes.append([old, new])

    return {"changes": changes}


def run_persian(text: str) -> dict[str, list[list[str]]]:
    """Run the shipped Persian normalization/review helper."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return _normalize_review(text)


def get_persian_script_templates() -> dict[str, str]:
    """Return built-in Persian helper scripts for the Run Python Script picker."""
    return {
        "Normalize & Review": (
            "# Persian Normalize & Review\n"
            "# Select the Persian text you want to edit, then Run.\n"
            "from writeragent.persian.scripts import run_persian\n\n"
            "result = run_persian(text)\n"
        )
    }
