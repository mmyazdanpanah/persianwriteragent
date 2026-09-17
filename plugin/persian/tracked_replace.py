# WriterAgent - AI Writing Assistant for LibreOffice
# Copyright (c) 2026 KeithCu
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persian exact-range tracked replacements for Writer selections.

Provides a minimal, reversible proof-of-concept for Persian exact-range
replacements with native LibreOffice Track Changes. Each replacement is
applied as an exact UNO range replacement so LibreOffice Track Changes
can Accept/Reject it individually.
"""

from __future__ import annotations

import logging
from typing import Any

from plugin.doc.text_helpers import (
    get_selection_range,
    get_selection_text,
    get_text_cursor_at_range,
)
from plugin.framework.errors import ToolExecutionError, check_disposed
from plugin.framework.thread_guard import main_thread_only
from plugin.doc.doc_type import is_writer

log = logging.getLogger("writeragent.persian")


@main_thread_only
def apply_tracked_replacements(doc: Any, changes: list[list[str]]) -> dict[str, Any]:
    """Apply exact-range tracked replacements within the current Writer selection.

    Args:
        doc: Writer document model (must be a Writer document).
        changes: List of [source_text, target_text] pairs. Each pair is applied
            independently within the current selection. Multiple occurrences of
            the same source_text are replaced individually.

    Returns:
        Dict with keys:
            - "applied": int, number of individual replacements applied
            - "skipped": int, number of source texts not found in selection
            - "details": list of per-change results

    Requirements:
        - Operates ONLY inside the current Writer selection
        - Finds exact literal occurrences (no regex)
        - No global document replacement
        - Handles multiple occurrences individually
        - Processes matches from right to left so offsets remain valid
        - Skips an occurrence if the exact source text cannot be found
        - Replaces only the matched UNO range
        - Each replacement is an exact local UNO range replacement so
          LibreOffice Track Changes can Accept/Reject it individually
    """
    if not is_writer(doc):
        raise ToolExecutionError("apply_tracked_replacements requires a Writer document")

    try:
        check_disposed(doc, "Document Model")
    except Exception as e:
        raise ToolExecutionError(f"Document disposed: {e}")

    # Get the current selection text and its character offsets
    sel_text = get_selection_text(doc)
    if sel_text is None or sel_text == "":
        raise ToolExecutionError("No text selected. Select text in Writer before running.")

    sel_start, sel_end = get_selection_range(doc)
    if sel_start == sel_end:
        raise ToolExecutionError("Empty selection. Select text in Writer before running.")

    selection_text = normalize_linebreaks(sel_text)
    log.debug(
        "apply_tracked_replacements: selection [%d, %d), length=%d",
        sel_start, sel_end, len(selection_text)
    )

    # Find all matches for each change within the selection text
    # We'll collect all matches across all changes, then sort by position (right-to-left)
    all_matches: list[dict[str, Any]] = []

    for change_idx, change_pair in enumerate(changes):
        if not isinstance(change_pair, (list, tuple)) or len(change_pair) != 2:
            log.warning("Invalid change pair at index %d: %r (expected [source, target])", change_idx, change_pair)
            continue

        source_text, target_text = change_pair
        if not isinstance(source_text, str) or not isinstance(target_text, str):
            log.warning("Non-string change pair at index %d: %r", change_idx, change_pair)
            continue

        if source_text == "":
            log.warning("Empty source text at index %d, skipping", change_idx)
            continue

        if source_text == target_text:
            log.debug("Source equals target at index %d, skipping", change_idx)
            continue

        # Normalize the source text for matching (handle linebreaks consistently)
        source_norm = normalize_linebreaks(source_text)
        target_norm = normalize_linebreaks(target_text)

        # Find all occurrences of source_text in the selection
        # Use simple string find for exact literal matching
        start_idx = 0
        while True:
            found_idx = selection_text.find(source_norm, start_idx)
            if found_idx == -1:
                break

            # Convert selection-relative offset to document-relative offset
            doc_start = sel_start + found_idx
            doc_end = doc_start + len(source_norm)

            all_matches.append({
                "change_idx": change_idx,
                "source_text": source_norm,
                "target_text": target_norm,
                "doc_start": doc_start,
                "doc_end": doc_end,
                "sel_start": found_idx,
                "sel_end": found_idx + len(source_norm),
            })

            start_idx = found_idx + len(source_norm)

    if not all_matches:
        return {
            "applied": 0,
            "skipped": len(changes),
            "details": [{"source": c[0], "target": c[1], "status": "not_found"} for c in changes if isinstance(c, (list, tuple)) and len(c) == 2],
        }

    # Sort matches by document position DESCENDING (right-to-left)
    # This ensures that earlier replacements don't shift the offsets of later ones
    all_matches.sort(key=lambda m: m["doc_start"], reverse=True)

    # Apply each replacement using exact UNO range replacement
    applied_count = 0
    skipped_sources = set()
    details = []

    for match in all_matches:
        change_idx = match["change_idx"]
        source_text = match["source_text"]
        target_text = match["target_text"]
        doc_start = match["doc_start"]
        doc_end = match["doc_end"]

        # Create a cursor at the exact range
        cursor = get_text_cursor_at_range(doc, doc_start, doc_end)
        if cursor is None:
            log.warning("Failed to create cursor for range [%d, %d)", doc_start, doc_end)
            details.append({
                "change_idx": change_idx,
                "source": source_text,
                "target": target_text,
                "status": "cursor_failed",
                "doc_start": doc_start,
                "doc_end": doc_end,
            })
            continue

        # Verify the cursor text matches the source (defense against stale offsets)
        try:
            cursor_text = cursor.getString()
            cursor_text = normalize_linebreaks(cursor_text)
        except Exception as e:
            log.warning("Failed to read cursor text for range [%d, %d): %s", doc_start, doc_end, e)
            details.append({
                "change_idx": change_idx,
                "source": source_text,
                "target": target_text,
                "status": "read_failed",
                "doc_start": doc_start,
                "doc_end": doc_end,
            })
            continue

        if cursor_text != source_text:
            # Text doesn't match (may have been modified by a prior overlapping replacement)
            # This should be rare since we process right-to-left
            log.warning(
                "Cursor text mismatch at [%d, %d): expected %r, got %r",
                doc_start, doc_end, source_text, cursor_text
            )
            details.append({
                "change_idx": change_idx,
                "source": source_text,
                "target": target_text,
                "status": "text_mismatch",
                "doc_start": doc_start,
                "doc_end": doc_end,
                "expected": source_text,
                "actual": cursor_text,
            })
            continue

        # Perform the exact UNO range replacement
        # This creates a tracked Delete+Insert pair when Track Changes is ON
        try:
            cursor.setString(target_text)
            applied_count += 1
            details.append({
                "change_idx": change_idx,
                "source": source_text,
                "target": target_text,
                "status": "applied",
                "doc_start": doc_start,
                "doc_end": doc_end,
            })
            log.debug("Applied replacement %d: %r -> %r at [%d, %d)", change_idx, source_text, target_text, doc_start, doc_end)
        except Exception as e:
            log.exception("Failed to apply replacement at [%d, %d)", doc_start, doc_end)
            details.append({
                "change_idx": change_idx,
                "source": source_text,
                "target": target_text,
                "status": "apply_failed",
                "doc_start": doc_start,
                "doc_end": doc_end,
                "error": str(e),
            })

    # Count unique source texts that were not found
    found_sources = {m["source_text"] for m in all_matches if any(d.get("doc_start") == m["doc_start"] and d["status"] == "applied" for d in details)}
    all_sources = {c[0] for c in changes if isinstance(c, (list, tuple)) and len(c) == 2}
    skipped_sources = all_sources - found_sources

    return {
        "applied": applied_count,
        "skipped": len(skipped_sources),
        "details": details,
    }


def normalize_linebreaks(text: str) -> str:
    """Ensure all linebreaks use \n (LF)."""
    if text is None:
        return ""
    text = text.replace("\r\n", "\n")
    text = text.replace("\n\r", "\n")
    text = text.replace("\r", "\n")
    return text