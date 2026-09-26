# WriterAgent - AI Writing Assistant for LibreOffice
# Copyright (c) 2026 KeithCu
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persian Hazm normalization with exact-range change extraction — v0.2.

Experimental module that extracts mechanically safe Persian normalizations:
1. ZWNJ edits - insertions and removals of zero-width non-joiners
2. Arabic character normalization - ي -> ی, ك -> ک
3. Whitespace normalization - multiple spaces/tabs -> single space (preserve newlines)
4. Tatweel/Kashida removal - مـــوزه -> موزه
5. Ellipsis normalization - ... -> …

All transformations are applied with protection for URLs, emails, version numbers,
and code-like patterns to avoid damaging mixed content.

This is a minimal, reversible experiment. No external dependencies beyond
already-authorized modules (hazm, stdlib).
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

try:
    from hazm import Normalizer
except ImportError:
    Normalizer = None  # type: ignore[assignment]


# Unicode zero-width non-joiner (ZWNJ) used by Hazm for half-space
ZWNJ = "\u200c"

# Patterns for protecting content that must not be normalized
# URLs: http://..., https://..., ftp://...
URL_PATTERN = re.compile(r"\b(?:https?|ftp)://[^\s/$.?#].[^\s]*", re.IGNORECASE)

# Emails: user@domain.tld
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

# Version numbers: 1.0, 1.0.0, v1.2.3, version 2.0
VERSION_PATTERN = re.compile(r"\b(?:v|version\s+)?\d+(?:\.\d+)+(?:-[a-zA-Z0-9]+)?\b", re.IGNORECASE)

# Numbers with separators: 1,000, 1.000, 1 000
NUMBER_PATTERN = re.compile(r"\b\d{1,3}(?:[,. ]\d{3})+(?:\.\d+)?\b")

# Code-like patterns: function(), variable_name, ClassName, /path/to/file
CODE_PATTERN = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\(\)|\b[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*|/[^\s]+")

# File paths and URLs with dots: example.com, /path/to/file
DOT_PATH_PATTERN = re.compile(r"(?:^|[\s\(\[<])(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?(?=[\s\)\]>.,;:!?]|$)")

# Combined protection pattern - all things that should not be normalized
PROTECT_PATTERNS = [
    URL_PATTERN,
    EMAIL_PATTERN,
    VERSION_PATTERN,
    NUMBER_PATTERN,
    CODE_PATTERN,
    DOT_PATH_PATTERN,
]


class ProtectedText:
    """Manages protection of sensitive text regions during normalization."""

    def __init__(self, text: str):
        self.original = text
        self.protected_regions: list[tuple[int, int, str]] = []  # (start, end, placeholder)
        self.placeholder_map: dict[str, str] = {}  # placeholder -> original text
        self._placeholder_counter = 0

    def protect(self) -> str:
        """Replace protected regions with placeholders and return modified text."""
        if not self.protected_regions:
            self._find_protected_regions()

        if not self.protected_regions:
            return self.original

        # Build result by replacing protected regions with placeholders
        result_parts = []
        last_end = 0

        for start, end, placeholder in self.protected_regions:
            result_parts.append(self.original[last_end:start])
            result_parts.append(placeholder)
            last_end = end

        result_parts.append(self.original[last_end:])
        return "".join(result_parts)

    def restore(self, text: str) -> str:
        """Restore protected regions from placeholders."""
        result = text
        for placeholder, original in self.placeholder_map.items():
            result = result.replace(placeholder, original)
        return result

    def _find_protected_regions(self) -> None:
        """Find all protected regions in the original text."""
        matches = []

        for pattern in PROTECT_PATTERNS:
            for match in pattern.finditer(self.original):
                start, end = match.span()
                matched_text = match.group(0)
                # Only protect if it looks like it should be protected
                if self._should_protect(matched_text):
                    matches.append((start, end, matched_text))

        # Sort by start position, then by length (longer first for overlapping)
        matches.sort(key=lambda x: (x[0], -(x[1] - x[0])))

        # Remove overlapping matches (keep longest)
        filtered = []
        for start, end, text in matches:
            overlaps = False
            for f_start, f_end, _ in filtered:
                if start < f_end and end > f_start:
                    overlaps = True
                    break
            if not overlaps:
                filtered.append((start, end, text))

        # Create placeholders
        for start, end, matched_text in filtered:
            # Use base36 (letters only) to avoid Hazm digit normalization
            import string
            chars = string.ascii_lowercase
            n = self._placeholder_counter
            # Convert to base26 using only letters
            placeholder_chars = []
            if n == 0:
                placeholder_chars = ['a', 'a', 'a', 'a']
            else:
                temp = n
                while temp > 0:
                    placeholder_chars.insert(0, chars[temp % 26])
                    temp //= 26
                while len(placeholder_chars) < 4:
                    placeholder_chars.insert(0, 'a')
            placeholder = "\u0000PROT_" + "".join(placeholder_chars) + "\u0000"
            self._placeholder_counter += 1
            self.protected_regions.append((start, end, placeholder))
            self.placeholder_map[placeholder] = matched_text

    def _should_protect(self, text: str) -> bool:
        """Determine if a matched text should be protected."""
        # Always protect URLs and emails
        if URL_PATTERN.fullmatch(text) or EMAIL_PATTERN.fullmatch(text):
            return True
        # Protect version numbers
        if VERSION_PATTERN.fullmatch(text):
            return True
        # Protect numbers with separators
        if NUMBER_PATTERN.fullmatch(text):
            return True
        # Protect code-like patterns
        if CODE_PATTERN.search(text):
            return True
        # Protect dot-paths (domains, file paths)
        if DOT_PATH_PATTERN.search(text):
            return True
        return False


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


def apply_safe_normalizations(text: str) -> str:
    """Apply mechanically safe normalizations directly (without Hazm's aggressive normalizer).

    Safe transformations:
    1. Arabic character normalization: ي -> ی, ك -> ک
    2. Whitespace: multiple spaces/tabs -> single space (preserve newlines)
    3. Tatweel/Kashida removal
    4. Ellipsis: ... -> …
    5. ZWNJ joins (handled separately via Hazm)

    Args:
        text: Input text (with protected regions already replaced)

    Returns:
        Normalized text
    """
    # 1. Arabic character normalization (ي -> ی, ك -> ک)
    text = text.replace("ي", "ی").replace("ك", "ک")

    # 2. Whitespace normalization: multiple spaces/tabs -> single space, preserve newlines
    lines = text.split("\n")
    normalized_lines = []
    for line in lines:
        # Replace tabs with spaces, then collapse multiple spaces
        line = line.replace("\t", " ")
        line = re.sub(r" {2,}", " ", line)
        normalized_lines.append(line)
    text = "\n".join(normalized_lines)

    # 3. Tatweel/Kashida removal (U+0640)
    text = text.replace("\u0640", "")

    # 4. Ellipsis normalization: ... -> … (U+2026)
    text = re.sub(r"\.{3,}", "…", text)

    return text


def find_joined_word_changes(original: str, normalized: str) -> list[tuple[str, str]]:
    """Find conservative ZWNJ joins from Hazm normalization.

    Hazm can insert ZWNJ into many Persian word combinations. Some are
    mechanically safe, while others are lexical or context-dependent.
    PersianWriterAgent therefore accepts only an explicit conservative
    set here. Broader lexical joins belong in the reviewed spelling
    dictionary rather than the mechanical normalization layer.

    Args:
        original: Original text
        normalized: Hazm-normalized text

    Returns:
        List of (old_text, new_text) pairs
    """
    changes = []

    # Conservative mechanical joins validated for automatic normalization.
    # Do not expand this list casually: context-dependent compounds belong
    # in the reviewed Persian spelling/terminology dictionary.
    SAFE_ZWNJ_JOINS = {
        "شکل گیری": "شکل‌گیری",
        "سازمان دهی": "سازمان‌دهی",
        "همکاری های": "همکاری‌های",
        "نه تنها": "نه‌تنها",
    }

    for old_text, new_text in SAFE_ZWNJ_JOINS.items():
        if old_text in original and new_text in normalized:
            changes.append((old_text, new_text))

    return changes


def find_arabic_char_changes(original: str, normalized: str) -> list[tuple[str, str]]:
    """Find Arabic character normalization changes (ي -> ی, ك -> ک).

    Returns individual character changes, not whole words, to avoid
    including surrounding punctuation in the replacement.

    Args:
        original: Original text
        normalized: Normalized text (after safe normalizations)

    Returns:
        List of (old_text, new_text) pairs
    """
    changes = []

    # Find positions where Arabic chars were normalized
    i = 0
    while i < len(original) and i < len(normalized):
        if original[i] != normalized[i]:
            o, n = original[i], normalized[i]
            if (o == "ي" and n == "ی") or (o == "ك" and n == "ک"):
                # Record the individual character change only
                changes.append((o, n))
        i += 1

    # Deduplicate consecutive identical changes at the same position
    # (can happen if same change detected multiple times)
    deduped = []
    for old, new in changes:
        if not deduped or deduped[-1] != (old, new):
            deduped.append((old, new))

    return deduped


def find_whitespace_changes(original: str, normalized: str) -> list[tuple[str, str]]:
    """Find whitespace normalization changes (multiple spaces -> single space).

    Args:
        original: Original text
        normalized: Normalized text

    Returns:
        List of (old_text, new_text) pairs
    """
    changes = []

    # Find runs of multiple spaces or tabs
    ws_pattern = re.compile(r"[ \t]{2,}")

    matches = list(ws_pattern.finditer(original))
    if not matches:
        return changes

    # Merge adjacent/overlapping matches
    merged = []
    current_start, current_end = matches[0].span()

    for match in matches[1:]:
        start, end = match.span()
        if start <= current_end + 1:  # Adjacent or overlapping
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end

    merged.append((current_start, current_end))

    for start, end in merged:
        old_text = original[start:end]
        new_text = " "
        if old_text != new_text:
            changes.append((old_text, new_text))

    return changes


def find_tatweel_changes(original: str, normalized: str) -> list[tuple[str, str]]:
    """Find tatweel/kashida removal changes.

    Args:
        original: Original text
        normalized: Normalized text

    Returns:
        List of (old_text, new_text) pairs
    """
    changes = []

    # Find tatweel characters (U+0640)
    tatweel_pattern = re.compile(r"[^\s]*\u0640[^\s]*")

    for match in tatweel_pattern.finditer(original):
        old_text = match.group(0)
        # Remove tatweel from the matched word
        new_text = old_text.replace("\u0640", "")
        if old_text != new_text:
            changes.append((old_text, new_text))

    return changes


def find_ellipsis_changes(original: str, normalized: str) -> list[tuple[str, str]]:
    """Find ellipsis normalization changes (... -> …).

    Args:
        original: Original text
        normalized: Normalized text

    Returns:
        List of (old_text, new_text) pairs
    """
    changes = []

    # Find 3+ dots
    ellipsis_pattern = re.compile(r"\.{3,}")

    for match in ellipsis_pattern.finditer(original):
        old_text = match.group(0)
        new_text = "…"  # U+2026
        if old_text != new_text:
            changes.append((old_text, new_text))

    return changes


def find_hazm_zwnj_changes(
    original: str, normalized: str
) -> list[tuple[str, str]]:
    """Extract exact word-level replacements caused by Hazm ZWNJ edits.

    Hazm may insert or remove a zero-width non-joiner (ZWNJ). Character-level
    replacements are unsafe for the current tracked-replacement contract,
    because each [old, new] pair is applied to every matching occurrence.
    We therefore expand each ZWNJ-related diff to its surrounding Persian
    word span before returning it.

    Handles both directions:
    - ``می کردند`` -> ``می‌کردند`` (ZWNJ insertion)
    - ``جنگ‌ جهانی`` -> ``جنگ جهانی`` (ZWNJ removal)
    """
    changes: list[tuple[str, str]] = []
    word_char = re.compile(r"[^\W\d_]|" + re.escape(ZWNJ), re.UNICODE)

    def expand(text: str, start: int, end: int) -> tuple[int, int]:
        """Expand a changed range to the surrounding Persian word span."""
        while start > 0 and word_char.fullmatch(text[start - 1]):
            start -= 1
        while end < len(text) and word_char.fullmatch(text[end]):
            end += 1
        return start, end

    matcher = SequenceMatcher(None, original, normalized, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        old_fragment = original[i1:i2]
        new_fragment = normalized[j1:j2]
        if ZWNJ not in old_fragment and ZWNJ not in new_fragment:
            continue

        old_start, old_end = expand(original, i1, i2)
        new_start, new_end = expand(normalized, j1, j2)
        old_text = original[old_start:old_end]
        new_text = normalized[new_start:new_end]
        if old_text and new_text and old_text != new_text:
            changes.append((old_text, new_text))

    unique: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for change in changes:
        if change not in seen:
            seen.add(change)
            unique.append(change)
    return unique

def extract_hazm_changes(text: str) -> dict[str, list[list[str]]]:
    """Extract exact replacements from full Hazm normalization plus mechanical cleanup."""
    if not text or not text.strip():
        return {"changes": []}

    protector = ProtectedText(text)
    protected_text = protector.protect()

    # Hazm is the full Persian linguistic normalization engine.
    hazm_normalized = normalize_with_hazm(protected_text)

    # Mechanical normalization is deliberately separate and deterministic.
    mechanical_normalized = apply_safe_normalizations(hazm_normalized)

    final_normalized = protector.restore(mechanical_normalized)

    if final_normalized == text:
        return {"changes": []}

    all_changes: list[tuple[str, str]] = []

    # Hazm linguistic changes: extract ZWNJ insertions and removals.
    all_changes.extend(
        find_hazm_zwnj_changes(protected_text, hazm_normalized)
    )

    # Mechanical changes use the existing exact extractors.
    all_changes.extend(find_arabic_char_changes(text, final_normalized))
    all_changes.extend(find_whitespace_changes(text, final_normalized))
    all_changes.extend(find_tatweel_changes(text, final_normalized))
    all_changes.extend(find_ellipsis_changes(text, final_normalized))

    # Deduplicate while preserving order.
    seen: set[tuple[str, str]] = set()
    unique_changes: list[list[str]] = []

    for old, new in all_changes:
        key = (old, new)
        if old and new and old != new and key not in seen:
            seen.add(key)
            unique_changes.append([old, new])

    return {"changes": unique_changes}


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
