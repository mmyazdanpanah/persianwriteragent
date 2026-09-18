#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for Persian spelling/lexical correction layer.

Run this directly with Python to test the spelling module.
"""

import sys
sys.path.insert(0, "/Users/mostafa/Workspace/02_AI_Lab/Persian_Writing/Tools/writeragent")

from plugin.persian.spelling import (
    find_spelling_changes,
    load_approved_dictionary,
    add_candidate_entry,
    load_candidates_dictionary,
    promote_candidate_to_approved,
    extract_candidates_from_text,
)

# Test 1: Load approved dictionary
print("=== Test 1: Load Approved Dictionary ===")
approved = load_approved_dictionary()
print(f"Loaded {len(approved)} approved entries:")
for entry in approved:
    print(f"  {entry['wrong']} -> {entry['correct']} ({entry['type']}, {entry['status']})")
print()

# Test 2: Basic spelling changes
print("=== Test 2: Basic Spelling Changes ===")
test_texts = [
    "این متن صرفا برای تست است",
    "موزه بعنوان یک نهاد فرهنگی",
    "اهمیت بویژه دارد",
    "صرفا و بعنوان و بویژه در یک متن",
    "https://example.com version 1.0.0 function()",
]

for text in test_texts:
    result = find_spelling_changes(text)
    changes = result.get("changes", [])
    print(f"Input: {text!r}")
    if changes:
        for old, new in changes:
            print(f"  ✓ {old!r} -> {new!r}")
    else:
        print("  No changes")
    print()

# Test 3: Protection verification
print("=== Test 3: Protection Verification ===")
protected_tests = [
    "Check https://example.com for صرفا",
    "Email test@example.com with بویژه",
    "Version 1.0.0 has titulada issue",  # note: 'titulada' is not in our dict
]

for text in protected_tests:
    result = find_spelling_changes(text)
    changes = result.get("changes", [])
    print(f"Input: {text!r}")
    if changes:
        for old, new in changes:
            print(f"  ✓ {old!r} -> {new!r}")
    else:
        print("  No changes (protected or no match)")
    print()

# Test 4: Candidate management
print("=== Test 4: Candidate Management ===")
# Add a candidate
add_candidate_entry("موزه‌شناسی", frequency=5, sources=["test-doc.md"])
candidates = load_candidates_dictionary()
print(f"Candidates after adding: {candidates}")

# Promote to approved
promote_candidate_to_approved("موزه‌شناسی", "موزه‌شناسی", "terminology", ["test-doc.md"])
approved = load_approved_dictionary()
print(f"Approved after promotion: {len(approved)} entries")
for e in approved:
    print(f"  {e['wrong']} -> {e['correct']} ({e['type']})")

# Test 5: Candidate extraction
print("\n=== Test 5: Candidate Extraction ===")
test_doc = """
موزه‌شناسی یکی از حوزه‌های مهم است. موزه‌شناسی در ایران رشد کرده.
موزه شناسی نیز مورد بررسی قرار گرفته. موزه‌شناسی مهم است.
"""
candidates = extract_candidates_from_text(test_doc, "test-thesis.md")
print(f"Extracted candidates: {candidates}")

# Test 6: Repetition test
print("\n=== Test 6: Repetition Test ===")
repeat_text = "صرفا صرفا صرفا"
result = find_spelling_changes(repeat_text)
print(f"Input: {repeat_text!r}")
for old, new in result.get("changes", []):
    print(f"  ✓ {old!r} -> {new!r}")

print("\n=== All Tests Complete ===")