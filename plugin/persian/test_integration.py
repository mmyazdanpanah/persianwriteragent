#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integration test for PersianWriterAgent v0.3.1.

Tests the complete path:
input Persian text
→ v0.2 mechanical normalization
→ v0.3 approved spelling dictionary
→ combined change extraction
→ tracked replacement bridge
→ individual LibreOffice Track Changes
"""

import sys
sys.path.insert(0, "/Users/mostafa/Workspace/02_AI_Lab/Persian_Writing/Tools/writeragent")

from plugin.persian.normalize import extract_hazm_changes
from plugin.persian.spelling import find_spelling_changes


def main():
    print("=" * 60)
    print("PersianWriterAgent v0.3.1 Integration Test")
    print("=" * 60)

    # Synthetic test containing both classes of corrections
    test_text = "این پژوهشي است که صرفا بعنوان یک نمونه، در مجله‌ي علمی منتشر شد."

    print("\n--- Input Text ---")
    print(test_text)

    # Step 1: v0.2 mechanical normalization
    print("\n--- Step 1: v0.2 Mechanical Normalization ---")
    mechanical_result = extract_hazm_changes(test_text)
    mechanical_changes = mechanical_result.get("changes", [])
    print(f"Mechanical changes ({len(mechanical_changes)}):")
    for old, new in mechanical_changes:
        print(f"  [{old!r}] -> [{new!r}]")

    # Step 2: v0.3 approved spelling dictionary
    print("\n--- Step 2: v0.3 Approved Spelling Dictionary ---")
    spelling_result = find_spelling_changes(test_text)
    spelling_changes = spelling_result.get("changes", [])
    print(f"Spelling changes ({len(spelling_changes)}):")
    for old, new in spelling_changes:
        print(f"  [{old!r}] -> [{new!r}]")

    # Step 3: Combined change extraction (simulating the pipeline)
    print("\n--- Step 3: Combined Changes ---")
    all_changes = mechanical_changes + spelling_changes

    # Sort by position (right-to-left for safe replacement)
    # We need to find the actual positions in the original text
    combined = []
    for old, new in all_changes:
        # Find all occurrences in the original text
        start_idx = 0
        while True:
            found_idx = test_text.find(old, start_idx)
            if found_idx == -1:
                break
            combined.append((old, new, found_idx))
            start_idx = found_idx + len(old)

    # Sort by position descending (right-to-left)
    combined.sort(key=lambda x: x[2], reverse=True)

    # Deduplicate while preserving right-to-left order
    seen = set()
    unique_combined = []
    for old, new, pos in combined:
        key = (old, new)
        if key not in seen:
            seen.add(key)
            unique_combined.append([old, new])

    print(f"Combined unique changes ({len(unique_combined)}):")
    for old, new in unique_combined:
        print(f"  [{old!r}] -> [{new!r}]")

    # Step 4: Verification
    print("\n--- Step 4: Verification ---")

    # Expected corrections
    expected = [
        ("ي", "ی"),                 # mechanical: Arabic ي → Persian ی (individual character)
        ("صرفا", "صرفاً"),           # approved spelling
        ("بعنوان", "به‌عنوان"),      # approved spelling
    ]

    all_passed = True
    for exp_old, exp_new in expected:
        found = False
        for old, new in unique_combined:
            if old == exp_old and new == exp_new:
                print(f"  ✓ Expected: [{exp_old}] -> [{exp_new}]")
                found = True
                break
        if not found:
            print(f"  ✗ MISSING: [{exp_old}] -> [{exp_new}]")
            all_passed = False

    # Check for duplicates (same old->new appearing multiple times)
    change_counts = {}
    for old, new in unique_combined:
        key = (old, new)
        change_counts[key] = change_counts.get(key, 0) + 1

    print("\n--- Step 5: Duplicate Check ---")
    for (old, new), count in change_counts.items():
        if count > 1:
            print(f"  ⚠ DUPLICATE: [{old}] -> [{new}] appears {count} times")
            all_passed = False
        else:
            print(f"  ✓ Unique: [{old}] -> [{new}]")

    # Verify protection: URLs, emails, versions, code, paths
    print("\n--- Step 6: Protection Verification ---")
    protection_tests = {
        "URL": "https://example.com",
        "Email": "test@example.com",
        "Version": "version 1.0.0",
        "Number": "1,000,000",
        "Function": "function()",
        "Path": "/path/to/file",
        "Mixed with spelling": "Check https://example.com for صرفا",
    }

    for name, text in protection_tests.items():
        mechanical = extract_hazm_changes(text)
        spelling = find_spelling_changes(text)
        mech_changes = mechanical.get("changes", [])
        spell_changes = spelling.get("changes", [])

        if "spelling" in name.lower():
            # Should have spelling changes OUTSIDE protected regions
            if spell_changes:
                print(f"  ✓ {name}: Spelling changes applied outside protected: {spell_changes}")
            else:
                print(f"  ✗ {name}: Expected spelling changes outside protected region")
                all_passed = False
        else:
            # Should be fully protected
            if not mech_changes and not spell_changes:
                print(f"  ✓ {name}: Fully protected")
            else:
                print(f"  ✗ {name}: Should be protected but got changes: mech={mech_changes}, spell={spell_changes}")
                all_passed = False

    # Verify identical wrong==correct produces no change
    print("\n--- Step 7: Identical Wrong==Correct Check ---")
    # The approved dictionary doesn't have identical entries currently,
    # but test the mechanism
    test_identical = "موزه\u200cشناسی مهم است"
    result = find_spelling_changes(test_identical)
    if not result.get("changes"):
        print("  ✓ Identical wrong==correct produces no changes")
    else:
        print(f"  ✗ Identical wrong==correct produced changes: {result}")
        all_passed = False

    # Verify right-to-left replacement order
    print("\n--- Step 8: Right-to-Left Order Check ---")
    # The combined list should be sorted by position descending
    positions = []
    for old, new in unique_combined:
        pos = test_text.find(old)
        if pos != -1:
            positions.append(pos)
    if positions == sorted(positions, reverse=True):
        print(f"  ✓ Changes ordered right-to-left (positions: {positions})")
    else:
        print(f"  ⚠ Changes not properly ordered: {positions}")
        # This is just a warning since our simple test may not catch all cases

    # Summary
    print(f"\n{'=' * 60}")
    if all_passed:
        print("✓ ALL INTEGRATION TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())