# WriterAgent - AI Writing Assistant for LibreOffice
# Copyright (c) 2026 KeithCu
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persian Hazm normalization with exact-range change extraction — v0.1.

Experimental module that extracts ONLY ZWNJ (half-space) word joins produced
by Hazm Normalizer. No other normalization rules.

This is a minimal, reversible experiment. No external dependencies beyond
already-authorized modules (hazm, stdlib).
"""

from __future__ import annotations

import re

try:
    from hazm import Normalizer
except ImportError:
    Normalizer = None  # type: ignore[assignment]


# Unicode zero-width non-joiner (ZWNJ) used by Hazm for half-space
ZWNJ = "\u200c"


def normalize_with_hazm(text: str) -> str:
    """Normalize Persian text using Hazm Normalizer.

    Args:
        text: Input Persian text

    Returns:
        Normalized text, or original text if Hazm is unavailable
    """
    if Normalizer is None:
        return text

    try:
        normalizer = Normalizer()
        return normalizer.normalize(text)
    except Exception:
        return text


def find_joined_word_changes(original: str, normalized: str) -> list[tuple[str, str]]:
    """Find Hazm changes where words are joined with ZWNJ.

    Hazm's primary normalization is inserting ZWNJ between word parts:
    - "شکل گیری" -> "شکل\u200cگیری"
    - "سازمان دهی" -> "سازمان\u200cدهی"
    - etc.

    This function finds such patterns by looking for:
    1. In normalized: words containing ZWNJ
    2. In original: the corresponding space-separated parts

    Args:
        original: Original text
        normalized: Hazm-normalized text

    Returns:
        List of (old_text, new_text) pairs
    """
    changes = []

    # Find all ZWNJ-containing words in normalized text
    # Pattern: word\u200cword (Persian letters around ZWNJ)
    zwnj_pattern = re.compile(r"([\u0600-\u06FF]+)" + ZWNJ + r"([\u0600-\u06FF]+)")

    for match in zwnj_pattern.finditer(normalized):
        full_word = match.group(0)  # e.g., "شکل\u200cگیری"
        part1 = match.group(1)      # e.g., "شکل"
        part2 = match.group(2)      # e.g., "گیری"

        # Look for "part1 part2" in original (space separated)
        space_separated = part1 + " " + part2

        # Find this pattern in original text
        if space_separated in original:
            changes.append((space_separated, full_word))

    return changes


def extract_hazm_changes(text: str) -> dict[str, list[list[str]]]:
    """Main entry point: extract Hazm ZWNJ join changes from text.

    v0.1: ONLY extracts word joins with ZWNJ (half-space).
    No Arabic char normalization, no punctuation space changes.

    Args:
        text: Input Persian text (typically the Writer selection)

    Returns:
        Dict with "changes" key containing list of [old_text, new_text] pairs
    """
    if not text or not text.strip():
        return {"changes": []}

    normalized = normalize_with_hazm(text)

    if normalized == text:
        return {"changes": []}

    # v0.1: ONLY ZWNJ joins
    changes = find_joined_word_changes(text, normalized)

    # Deduplicate while preserving order
    seen = set()
    unique_changes = []
    for old, new in changes:
        key = (old, new)
        if key not in seen:
            seen.add(key)
            unique_changes.append((old, new))

    return {"changes": [[old, new] for old, new in unique_changes]}


# For direct execution as a Python Script
if __name__ == "__main__":
    # This block runs when executed via Tools → Run Python Script
    # The 'text' variable is injected by the host
    try:
        # 'text' is injected by python_runner when script uses the text binding
        text_var = globals().get("text")
        if text_var is not None:
            result = extract_hazm_changes(text_var)
        else:
            result = {"changes": [], "error": "text binding not available"}
    except NameError:
        # Fallback for direct testing
        result = {"changes": [], "error": "text binding not available"}