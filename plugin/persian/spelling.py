# WriterAgent - AI Writing Assistant for LibreOffice
# Copyright (c) 2026 KeithCu
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persian spelling/lexical correction layer — v0.3.

This module provides the spelling/lexical correction layer that consumes
the approved Persian dictionary and finds exact occurrences for replacement.

The spelling layer consumes the approved dictionary and produces the same
existing interface as the normalization layer:

```python
{
    "changes": [
        ["صرفا", "صرفاً"],
        ["بعنوان", "به‌عنوان"]
    ]
}
```

This module is separate from the mechanical normalization layer (v0.2) and
focuses on lexical/spelling corrections from the approved dictionary.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from plugin.persian.normalize import ProtectedText

# Unicode zero-width non-joiner (ZWNJ) used by Hazm for half-space
ZWNJ = "\u200c"


def get_dictionary_path() -> Path:
    """Get the path to the Persian dictionary directory."""
    return Path(__file__).parent / "dictionary"


def load_approved_dictionary() -> list[dict[str, Any]]:
    """Load the approved dictionary entries.
    
    Returns:
        List of approved dictionary entries. Each entry is a dict with keys:
        - wrong: the incorrect form
        - correct: the correct form
        - type: entry type (e.g., "spelling", "terminology")
        - status: must be "approved"
        - source: list of source identifiers
    """
    dict_path = get_dictionary_path() / "approved.json"
    if not dict_path.exists():
        return []
    
    try:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Only return approved entries
        return [entry for entry in data if entry.get("status") == "approved"]
    except (json.JSONDecodeError, OSError):
        return []


def load_candidates_dictionary() -> list[dict[str, Any]]:
    """Load the candidates dictionary entries."""
    dict_path = get_dictionary_path() / "candidates.json"
    if not dict_path.exists():
        return []
    
    try:
        with open(dict_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_candidates_dictionary(candidates: list[dict[str, Any]]) -> bool:
    """Save the candidates dictionary entries."""
    dict_path = get_dictionary_path() / "candidates.json"
    try:
        with open(dict_path, "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def add_candidate_entry(
    candidate: str,
    frequency: int = 1,
    sources: list[str] | None = None,
    context: str | None = None
) -> bool:
    """Add or update a candidate entry in the candidates dictionary.
    
    Args:
        candidate: The candidate form
        frequency: Frequency count
        sources: List of source documents
        context: Optional surrounding context
    
    Returns:
        True if saved successfully
    """
    candidates = load_candidates_dictionary()
    
    # Check if candidate already exists
    for entry in candidates:
        if entry.get("candidate") == candidate:
            entry["frequency"] = entry.get("frequency", 0) + frequency
            if sources:
                entry.setdefault("sources", []).extend(sources)
            if context:
                entry.setdefault("context", []).append(context)
            return save_candidates_dictionary(candidates)
    
    # Add new candidate
    new_entry = {
        "candidate": candidate,
        "frequency": frequency,
        "sources": sources or [],
    }
    if context:
        new_entry["context"] = [context]
    
    candidates.append(new_entry)
    return save_candidates_dictionary(candidates)


def promote_candidate_to_approved(
    candidate: str,
    correct: str,
    entry_type: str = "spelling",
    source: list[str] | None = None
) -> bool:
    """Promote a candidate to approved status.
    
    Args:
        candidate: The candidate form (wrong form)
        correct: The correct form
        entry_type: Type of entry (spelling, terminology, etc.)
        source: Source of the approval
    
    Returns:
        True if promoted successfully
    """
    candidates = load_candidates_dictionary()
    approved = load_approved_dictionary()
    
    # Find and remove from candidates
    candidates = [c for c in candidates if c.get("candidate") != candidate]
    
    # Add to approved
    new_entry = {
        "wrong": candidate,
        "correct": correct,
        "type": entry_type,
        "status": "approved",
        "source": source or ["manual"]
    }
    approved.append(new_entry)
    
    # Save both
    dict_path = get_dictionary_path()
    try:
        with open(dict_path / "candidates.json", "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        with open(dict_path / "approved.json", "w", encoding="utf-8") as f:
            json.dump(approved, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def find_spelling_changes(text: str) -> dict[str, list[list[str]]]:
    """Find spelling/lexical changes from the approved dictionary.

    This function:
    1. Loads the approved dictionary
    2. Finds exact occurrences of wrong forms in the text
    3. Skips matches that fall inside protected regions (URLs, emails, versions, etc.)
    5. Returns structured changes for the tracked replacement bridge

    Args:
        text: Input Persian text (typically the Writer selection)

    Returns:
        Dict with "changes" key containing list of [old_text, new_text] pairs
    """
    if not text or not text.strip():
        return {"changes": []}

    # Load approved dictionary
    approved_entries = load_approved_dictionary()
    if not approved_entries:
        return {"changes": []}

    # Filter for spelling/lexical entries
    spelling_entries = [e for e in approved_entries if e.get("type") in ("spelling", "terminology")]
    if not spelling_entries:
        return {"changes": []}

    # Build list of protected regions in the original text
    protector = ProtectedText(text)
    protector.protect()  # This populates protected_regions
    protected_regions = protector.protected_regions  # List of (start, end, placeholder)

    # Find all matches in original text that are NOT in protected regions
    all_changes = []

    for entry in spelling_entries:
        wrong = entry.get("wrong", "")
        correct = entry.get("correct", "")

        if not wrong or not correct or wrong == correct:
            continue

        # Find all occurrences in the original text
        start_idx = 0
        while True:
            found_idx = text.find(wrong, start_idx)
            if found_idx == -1:
                break

            match_start = found_idx
            match_end = found_idx + len(wrong)

            # Check if this match falls inside a protected region
            is_protected = False
            for p_start, p_end, _ in protected_regions:
                if match_start >= p_start and match_end <= p_end:
                    is_protected = True
                    break

            if not is_protected:
                all_changes.append((wrong, correct, found_idx))

            start_idx = found_idx + len(wrong)

    if not all_changes:
        return {"changes": []}

    # Sort by position descending (right-to-left) for safe replacement
    all_changes.sort(key=lambda x: x[2], reverse=True)

    # Deduplicate while preserving order (right-to-left order)
    seen = set()
    unique_changes = []
    for wrong, correct, _ in all_changes:
        key = (wrong, correct)
        if key not in seen:
            seen.add(key)
            unique_changes.append([wrong, correct])

    return {"changes": unique_changes}


def extract_candidates_from_text(text: str, source_doc: str) -> list[dict[str, Any]]:
    """Extract potential Persian lexical candidates from approved academic text.
    
    This function identifies potentially useful Persian lexical forms
    from approved academic documents. It does NOT auto-approve anything.
    
    Args:
        text: The document text
        source_doc: Source document identifier
    
    Returns:
        List of candidate entries for review
    """
    if not text or not text.strip():
        return []
    
    candidates = []
    
    # Simple extraction: find Persian words with ZWNJ, Arabic chars, etc.
    # This is a basic extractor - more sophisticated extraction can be added
    
    # Pattern for Persian words (including ZWNJ)
    persian_word_pattern = re.compile(r"[\u0600-\u06FF]+(?:\u200c[\u0600-\u06FF]+)*")
    
    words = persian_word_pattern.findall(text)
    
    # Count frequencies
    freq = {}
    for word in words:
        if len(word) > 1:  # Ignore single characters
            freq[word] = freq.get(word, 0) + 1
    
    # Create candidates for words that appear multiple times
    # and contain ZWNJ or Arabic chars (potential normalization targets)
    for word, count in freq.items():
        if count >= 2:
            # Check if it has ZWNJ (half-space) or Arabic characters
            has_zwnj = "\u200c" in word
            has_arabic = any(c in word for c in "ي ك")
            
            if has_zwnj or has_arabic:
                candidates.append({
                    "candidate": word,
                    "frequency": count,
                    "sources": [source_doc],
                })
    
    return candidates


def extract_candidates_from_file(file_path: str) -> list[dict[str, Any]]:
    """Extract candidates from a Markdown or plain text file.
    
    Args:
        file_path: Path to the document file
    
    Returns:
        List of candidate entries
    """
    path = Path(file_path)
    if not path.exists():
        return []
    
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    
    return extract_candidates_from_text(text, path.name)


# For direct execution as a Python Script
if __name__ == "__main__":
    # This block runs when executed via Tools → Run Python Script
    # The 'text' variable is injected by the host
    try:
        text_var = globals().get("text")
        if text_var is not None:
            result = find_spelling_changes(text_var)
        else:
            result = {"changes": [], "error": "text binding not available"}
    except NameError:
        result = {"changes": [], "error": "text binding not available"}