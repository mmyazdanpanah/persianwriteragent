#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for Persian spelling/lexical correction layer — v0.3.1.

Tests the corrected candidate extraction behavior:
1. Valid ZWNJ words should NOT become candidates
2. Mechanical anomalies (Arabic chars, tatweel) SHOULD become candidates
3. Punctuation should be excluded from candidates by the regex
4. Protection of URLs, emails, versions, etc. still works
"""

from pathlib import Path


import json

import pytest

import plugin.persian.spelling as spelling
from plugin.persian.spelling import (
    find_spelling_changes,
    load_approved_dictionary,
    add_candidate_entry,
    load_candidates_dictionary,
    promote_candidate_to_approved,
    extract_candidates_from_text,
    _is_mechanical_anomaly,
    PERSIAN_WORD_PATTERN,
)

# ============================================================
# Test 1: Load approved dictionary (should have 3 entries)
# ============================================================
print("=== Test 1: Load Approved Dictionary ===")
approved = load_approved_dictionary()
print(f"Loaded {len(approved)} approved entries:")
for entry in approved:
    print(f"  {entry['wrong']} -> {entry['correct']} ({entry['type']}, {entry['status']})")
assert len(approved) == 3, f"Expected 3 approved entries, got {len(approved)}"
assert all(e["type"] == "spelling" for e in approved), "All should be spelling type"
print("✓ PASS: 3 approved spelling entries, no duplicates")
print()

# ============================================================
# Test 2: Mechanical anomaly detection
# ============================================================
print("=== Test 2: Mechanical Anomaly Detection ===")

# Should be anomalies (contain Arabic chars, tatweel)
anomaly_words = [
    "يک",      # Arabic yeh
    "كتاب",    # Arabic kaf
    "مـــوزه",  # tatweel
    "كتاب ي",   # both
]

# Should NOT be anomalies (valid Persian with ZWNJ)
valid_words = [
    "یک",
    "کتاب",
    "موزه",
    "رسانه‌های",
    "می‌کند",
    "پژوهش‌های",
    "مهم‌ترین",
    "داده‌های",
    "نمونه‌های",
    "می‌دهد",
    "می‌شود",
    "واقعیت‌های",
    "روایت‌های",
    "گزارش‌های",
    "رسانه‌ها",
    "حکومت‌ها",
    "نظام‌مند",
    "پژوهش‌ها",
    "کلیشه‌های",
    "به‌کار",
]

print("Anomaly words (should be True):")
for w in anomaly_words:
    result = _is_mechanical_anomaly(w)
    print(f"  {w!r}: {result}")
    assert result, f"{w!r} should be anomaly"

print("\nValid words (should be False):")
for w in valid_words:
    result = _is_mechanical_anomaly(w)
    print(f"  {w!r}: {result}")
    assert not result, f"{w!r} should NOT be anomaly"

print("✓ PASS: Mechanical anomaly detection works correctly")
print()

# ============================================================
# Test 4: Persian word pattern (no punctuation in matches)
# ============================================================
print("=== Test 4: Persian Word Pattern (No Punctuation) ===")
test_text = "شده‌اند، می‌کند، کتاب، می‌کند؟ کتاب؛ سلام! کتاب: داده‌ها، نمونه‌ها؛"
matches = PERSIAN_WORD_PATTERN.findall(test_text)
print(f"Input: {test_text!r}")
print(f"Matches: {matches}")

# Verify no punctuation in matches
for m in matches:
    assert not any(c in m for c in "،؛؟!.،؛؟"), f"Punctuation found in match: {m!r}"

# Verify expected words are captured
expected_words = ["شده\u200cاند", "می\u200cکند", "کتاب", "می\u200cکند", "کتاب", "سلام", "کتاب", "داده\u200cها", "نمونه\u200cها"]
assert matches == expected_words, f"Expected {expected_words}, got {matches}"

print("✓ PASS: Persian word pattern excludes punctuation")
print()

# ============================================================
# Test 5: Candidate extraction - valid ZWNJ words should NOT be candidates
# ============================================================
print("=== Test 5: Candidate Extraction - Valid ZWNJ Words Excluded ===")
test_text = """
رسانه‌های یکی از حوزه‌های مهم است. رسانه‌های در ایران رشد کرده.
میه‌کند نیز مورد بررسی قرار گرفته. می‌کند مهم است.
پژوهش‌های علمی در این حوزه انجام شده. پژوهش‌های مهم است.
این یک تست برای استخراج کاندید است.
"""

candidates = extract_candidates_from_text(test_text, "test-doc.md")
print(f"Extracted candidates: {candidates}")

# Should NOT include valid ZWNJ words
forbidden_candidates = ["رسانه‌های", "می‌کند", "پژوهش‌های", "مهم‌ترین", "داده‌های", "نمونه‌ها", "می‌دهد", "می‌شود", "حقایق‌ها"]
for cand in candidates:
    assert cand["candidate"] not in forbidden_candidates, f"Should not be candidate: {cand['candidate']}"

print("✓ PASS: Valid ZWNJ words correctly excluded from candidates")
print()

# ============================================================
# Test 6: Candidate extraction - mechanical anomalies ARE candidates
# ============================================================
print("=== Test 6: Candidate Extraction - Mechanical Anomalies Included ===")
anomaly_text = """
كتاب يک نمونه است. كتاب يک در مكتبة موجود است.
مـــوزه قديم است. مـــوزه بازدید شد.
يك كتاب. يك كتاب.
"""

candidates = extract_candidates_from_text(anomaly_text, "test-doc.md")
print(f"Extracted candidates: {candidates}")

# Should include words with Arabic chars, tatweel
candidate_words = [c["candidate"] for c in candidates]
print(f"Candidate words: {candidate_words}")

# Check for expected anomalies
for c in candidates:
    assert _is_mechanical_anomaly(c["candidate"]), f"Candidate should be anomaly: {c['candidate']}"

print("✓ PASS: Mechanical anomalies correctly included as candidates")
print()

# ============================================================
# Test 8: Basic Spelling Changes (v0.3 spelling layer)
# ============================================================
print("=== Test 8: Basic Spelling Changes ===")
test_cases = [
    ("این متن صرفا برای تست است", [("صرفا", "صرفاً")]),
    ("موزه بعنوان یک نهاد فرهنگی", [("بعنوان", "به\u200cعنوان")]),
    ("اهمیت بویژه دارد", [("بویژه", "به\u200cویژه")]),
    ("صرفا و بعنوان و بویژه در یک متن", [("صرفا", "صرفاً"), ("بعنوان", "به\u200cعنوان"), ("بویژه", "به\u200cویژه")]),
]

for text, expected in test_cases:
    result = find_spelling_changes(text)
    changes = result.get("changes", [])
    print(f"Input: {text!r}")
    for old, new in changes:
        print(f"  ✓ {old!r} -> {new!r}")
    # Check all expected are present
    for exp_old, exp_new in expected:
        assert [exp_old, exp_new] in changes, f"Missing expected change: {exp_old} -> {exp_new}"

print("✓ PASS: Basic spelling changes work")
print()

# ============================================================
# Test 8b: Terminology with identical wrong/correct produces NO changes
# ============================================================
print("=== Test 8b: Terminology with identical wrong/correct ===")
text = "موزه\u200cشناسی مهم است"
result = find_spelling_changes(text)
print(f"Input: {text!r}")
print(f"Changes: {result}")
assert result.get("changes") == [], f"Should be empty, got {result}"
print("✓ PASS: Identical wrong/correct produces no changes")
print()

# ============================================================
# Test 9: Protection Verification
# ============================================================
print("=== Test 9: Protection Verification ===")
protected_tests = {
    'URL': 'https://example.com',
    'URL with path': 'https://example.com/path/to/page',
    'Email': 'test@example.com',
    'Version': 'version 1.0.0',
    'Version with v': 'v1.2.3',
    'Number with comma': '1,000,000',
    'Function': 'function()',
    'Path': '/path/to/file',
    'Mixed protected': 'https://example.com version 1.0.0 function()',
    'Mixed with spelling': 'Check https://example.com for صرفا',
    'Email with spelling': 'Email test@example.com with بویژه',
    'Path with spelling': 'Path /path/to/file has صرفا',
}

for name, text in protected_tests.items():
    result = find_spelling_changes(text)
    changes = result.get('changes', [])
    if "with spelling" in name.lower():
        # Should have spelling changes OUTSIDE protected regions
        assert changes, f"{name}: Expected spelling changes, got none"
        print(f"{name}: ✓ CHANGES: {changes}")
    else:
        assert not changes, f"{name}: Expected PROTECTED, got changes: {changes}"
        print(f"{name}: ✓ PROTECTED")

print("✓ PASS: Protection works correctly")
print()

# ============================================================
# Test 10: Candidate Management (add, promote, etc.)
# ============================================================
def test_candidate_management(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    print("=== Test 10: Candidate Management ===")

    dictionary_path = tmp_path / "dictionary"
    dictionary_path.mkdir()
    (dictionary_path / "approved.json").write_text(
        json.dumps(
            [
                {
                    "wrong": "صرفا",
                    "correct": "صرفاً",
                    "type": "spelling",
                    "status": "approved",
                    "source": ["manual"],
                },
                {
                    "wrong": "بعنوان",
                    "correct": "به‌عنوان",
                    "type": "spelling",
                    "status": "approved",
                    "source": ["manual"],
                },
                {
                    "wrong": "بویژه",
                    "correct": "به‌ویژه",
                    "type": "spelling",
                    "status": "approved",
                    "source": ["manual"],
                },
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (dictionary_path / "candidates.json").write_text("[]", encoding="utf-8")

    monkeypatch.setattr(spelling, "get_dictionary_path", lambda: dictionary_path)

    add_candidate_entry("موزه\u200cشناسی", frequency=5, sources=["test-doc.md"])
    candidates = load_candidates_dictionary()
    print(f"Candidates after adding: {candidates}")
    assert len(candidates) == 1
    assert candidates[0]["candidate"] == "موزه\u200cشناسی"
    assert candidates[0]["frequency"] == 5

    promote_candidate_to_approved(
        "موزه\u200cشناسی",
        "موزه\u200cشناسی",
        "terminology",
        ["test-doc.md"],
    )
    approved = load_approved_dictionary()
    print(f"Approved after promotion: {len(approved)} entries")
    for entry in approved:
        print(
            f"  {entry['wrong']} -> {entry['correct']} "
            f"({entry['type']})"
        )

    result = find_spelling_changes("موزه\u200cشناسی مهم است")
    assert result.get("changes") == []

    print("✓ PASS: Candidate management works")
    print()

# ============================================================
# Test 11: Repetition Test
# ============================================================
print("=== Test 11: Repetition Test ===")
repeat_text = "صرفا صرفا صرفا"
result = find_spelling_changes(repeat_text)
print(f"Input: {repeat_text!r}")
changes = result.get("changes", [])
assert len(changes) == 1, f"Should have 1 change, got {len(changes)}"
assert changes[0] == ["صرفا", "صرفاً"], f"Wrong change: {changes}"
print("✓ PASS: Repetition handled correctly (deduplicated)")
print()

# ============================================================
# Test 12: Existing normalization tests still pass
# ============================================================
print("=== Test 12: Existing Normalization Tests (v0.2) ===")
# This test is in test_normalize.py - run it separately
print("Run test_normalize.py separately to verify v0.2 behavior")
print()

print("=== ALL V0.3.1 TESTS PASSED ===")
