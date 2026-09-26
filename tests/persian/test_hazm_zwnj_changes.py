from __future__ import annotations

import pytest

from plugin.persian.normalize import (
    extract_hazm_changes,
    find_hazm_zwnj_changes,
    normalize_with_hazm,
)


def test_find_hazm_zwnj_changes_handles_insertions_and_removals() -> None:
    assert find_hazm_zwnj_changes(
        "این رسانه های علمی و جنگ‌ جهانی دوم است.",
        "این رسانه‌های علمی و جنگ جهانی دوم است.",
    ) == [
        ("رسانه های", "رسانه‌های"),
        ("جنگ‌", "جنگ"),
    ]


def test_real_academic_paragraph_exposes_hazm_zwnj_changes() -> None:
    pytest.importorskip("hazm")

    text = """بسیاری
از رسانه های آمریکایی از جمله مجله لایف
در طول جنگ‌ جهانی دوم به عنوان ابزار
پروپاگاندای ایالات متحده عمل می کردند
تا افکار عمومی را در جهت بر آوردن اهداف
  سیاسی و نظامی در طول جنگهمراه کند. یکی
از اهداف ایا لات متحده در جنگ جهانی دوم
گسترش قدرت نظامی و سیاسی خود در اروپا
بود که این هدف در موقعیت فرانسه نیز دنبال
می شد."""

    normalized = normalize_with_hazm(text)
    changes = extract_hazm_changes(text)["changes"]
    change_pairs = {tuple(pair) for pair in changes}

    expected = {
        ("رسانه های", "رسانه‌های"),
        ("ایالات متحده", "ایالات‌متحده"),
        ("می کردند", "می‌کردند"),
        ("می شد", "می‌شد"),
        ("جنگ‌", "جنگ"),
    }

    assert expected <= change_pairs

    # These are lexical/word-boundary problems Hazm does not solve here.
    # They belong to the separately reviewed Persian spelling layer.
    for old, _new in changes:
        assert old not in {"بر آوردن", "جنگهمراه", "ایا لات"}
