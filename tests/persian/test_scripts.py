from plugin.persian.scripts import get_persian_script_templates, run_persian


def test_persian_normalize_review():
    result = run_persian("این متن می پردازد و شکل گیری هنر را بررسی می کند.")
    assert result["changes"] == [
        ["می پردازد", "می‌پردازد"],
        ["شکل گیری", "شکل‌گیری"],
        ["می کند", "می‌کند"],
    ]


def test_persian_script_template():
    templates = get_persian_script_templates()
    assert list(templates) == ["Normalize & Review"]
    code = templates["Normalize & Review"]
    assert "from writeragent.persian.scripts import run_persian" in code
    assert "result = run_persian(text)" in code
