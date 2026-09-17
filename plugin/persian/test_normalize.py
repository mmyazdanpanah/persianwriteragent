#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for Persian Hazm normalization change extraction.

Run this directly with Python to test the algorithm without LibreOffice.
"""

import sys
sys.path.insert(0, "/Users/mostafa/Workspace/02_AI_Lab/Persian_Writing/Tools/writeragent")

from plugin.persian.normalize import extract_hazm_changes, normalize_with_hazm

TEST_TEXT = """در پژوهش‌های معاصر درباره موزه هنر، موزه شناسی به عنوان یکی از حوزه‌های مهم مطالعات هنر، به بررسی شکل گیری و تحولات موزه‌ها می‌پردازد. در این زمینه، معنا سازی و تجربه مخاطب اهمیت ویژه‌ای دارد و نمی‌توان نقش زمینه‌های اجتماعی، تاریخی و فرهنگی را نادیده گرفت.

این پژوهش می‌کوشد نشان دهد که موزه بعنوان یک نهاد فرهنگی، صرفا محل نگهداری و نمایش آثار نیست، بلکه می‌تواند در شکل گیری رابطه میان هنر و جامعه نیز نقش داشته باشد. بویژه در موزه‌های هنر مدرن و معاصر، نحوه ارائه آثار و سازمان دهی فضا می‌تواند بر تجربه مخاطب تأثیر بگذارد.

از سوی دیگر، پژوهشگرها و دانشگاه‌ها در سال‌های اخیر توجه بیشتری به این موضوع نشان داده‌اند. همکاری های علمی میان پژوهشگران نیز می‌تواند به شکل گیری رویکردهای تازه در مطالعات موزه کمک کند. با این حال، همه ترکیب‌های زبانی را نمی‌توان صرفا بر اساس یک قاعده ثابت اصلاح کرد؛ برای مثال، برخی موارد مانند به عنوان، به ویژه، معنا سازی و موزه شناسی ممکن است به بررسی دقیق‌تری نیاز داشته باشند.

بنابراین، می‌توان گفت که ویرایش متن علمی فارسی باید میان استانداردسازی زبانی و حفظ معنای دقیق متن تعادل برقرار کند. هدف از این فرایند، نه تنها اصلاح خطاهای نوشتاری، بلکه بهبود خوانایی، انسجام و دقت علمی متن است."""

def main():
    print("=" * 60)
    print("Testing Persian Hazm Normalization Change Extraction")
    print("=" * 60)

    print("\n--- Original Text (first 200 chars) ---")
    print(TEST_TEXT[:200] + "...")

    print("\n--- Normalized Text (first 200 chars) ---")
    normalized = normalize_with_hazm(TEST_TEXT)
    print(normalized[:200] + "...")

    print("\n--- Full Normalized Text ---")
    print(normalized)

    print("\n--- Extracted Changes ---")
    result = extract_hazm_changes(TEST_TEXT)
    changes = result.get("changes", [])

    if not changes:
        print("No changes detected!")
        return

    for i, (old, new) in enumerate(changes, 1):
        print(f"  {i}. [{old!r}] -> [{new!r}]")

    print(f"\nTotal changes: {len(changes)}")

    # Expected changes from the task description
    expected = [
        ("شکل گیری", "شکل‌گیری"),
        ("سازمان دهی", "سازمان‌دهی"),
        ("همکاری های", "همکاری‌های"),
        ("نه تنها", "نه‌تنها"),
    ]

    print("\n--- Expected vs Detected ---")
    for exp_old, exp_new in expected:
        found = False
        for old, new in changes:
            if exp_old in old and exp_new in new:
                print(f"  ✓ Found: [{exp_old}] -> [{exp_new}]")
                found = True
                break
        if not found:
            print(f"  ✗ MISSING: [{exp_old}] -> [{exp_new}]")

    # Check for unwanted changes (should NOT be detected)
    unwanted = [
        "موزه شناسی",
        "معنا سازی",
        "به عنوان",
        "به ویژه",
        "بعنوان",
        "صرفا",
        "بویژه",
    ]

    print("\n--- Unwanted Changes Check (should NOT appear) ---")
    for unwanted_term in unwanted:
        for old, new in changes:
            if unwanted_term in old:
                print(f"  ⚠ UNWANTED DETECTED: [{old}] -> [{new}] (contains '{unwanted_term}')")

    print("\n" + "=" * 60)
    print("Test complete")
    print("=" * 60)

if __name__ == "__main__":
    main()