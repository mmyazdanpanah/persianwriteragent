#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal test script for Persian exact-range tracked replacements.

This script can be executed through WriterAgent's existing Python Script
interface (Tools → Run Python Script) in a Writer document with Persian text
selected.

It returns a structured result with "changes" that the python_runner will
recognize and process via apply_tracked_replacements.

Do not import UNO or WriterAgent internals from this script.
"""

# This is the exact structure that python_runner.py recognizes for Persian
# tracked replacements. Each inner list is [source_text, target_text].
# The replacement operates ONLY inside the current Writer selection,
# finds exact literal occurrences, and replaces each match individually
# with native LibreOffice Track Changes (Accept/Reject per replacement).

result = {
    "changes": [
        ["موزه شناسی", "موزه‌شناسی"],
        ["کتاب خانه", "کتابخانه"],
        ["رایانه", "کامپیوتر"],
    ]
}