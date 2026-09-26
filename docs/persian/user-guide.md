# PersianWriterAgent — User Guide

This is the human-facing guide for the Persian-specific features. PersianWriterAgent is a thin layer over WriterAgent; general WriterAgent documentation is linked rather than copied here.

## Daily workflow

~~~text
select Persian text
  ↓
Run Python Script
  ↓
[Persian] Persian Helpers → Normalize & Review
  ↓
review native LibreOffice changes
  ↓
Accept / Reject
~~~

## 1. Install

Install the PersianWriterAgent .oxt package through LibreOffice Extension Manager, then restart LibreOffice.

For general WriterAgent installation and UI documentation, use the upstream project: https://github.com/KeithCu/writeragent

Persian-specific setup is documented in ../install-troubleshooting.md.

## 2. Prepare the Persian Python environment

Hazm is the required Persian runtime dependency. The exact dependency is pinned in [requirements-persian.txt](../../requirements-persian.txt).

For a fresh local environment:

~~~bash
python3 -m venv ~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env
~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env/bin/python -m pip install --upgrade pip
~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env/bin/python -m pip install -r requirements-persian.txt
~~~

If you already have the environment, do not recreate it; update it from the requirements file instead.

See the [dependency reference](dependencies.md) for the runtime/development dependency boundary.

## 3. Configure Python once

Open WriterAgent → Settings → Python and set the Python environment containing the Persian dependencies.

The development environment used by this project is:

~~~text
~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env
~~~

Use the equivalent absolute path on your machine. You normally configure this once rather than before every use.

## 3. Use the built-in Persian helper

Open a Writer document and select the Persian text you want to review.

Open Run Python Script and choose:

~~~text
[Persian] Persian Helpers
    └── Normalize & Review
~~~

Run it.

You do not need to write Python, copy a script from GitHub, create a My Script, or manually save a script. The Persian helper is shipped through the built-in script picker.

## 4. Use Track Changes for review

For academic and professional writing, enable LibreOffice Track Changes before running the helper:

**Edit → Track Changes → Record**

Then run Normalize & Review. Proposed edits are recorded through LibreOffice's native revision mechanism.

The Persian layer does not create a second review system.

## 5. Example

Selected text:

~~~text
این متن می پردازد و شکل گیری هنر را بررسی می کند.
~~~

Representative changes:

~~~text
می پردازد  →  می‌پردازد
شکل گیری  →  شکل‌گیری
می کند    →  می‌کند
~~~

Review each change in LibreOffice. Accept the changes you want and reject the ones you do not.

## 6. Already-correct text

If the selection is already correct, the expected result is:

~~~text
No Persian changes needed.
~~~

The selection remains untouched. No deletion or insertion revision should be created.

## 7. Current examples

| Input | Normalized form |
|---|---|
| می پردازد | می‌پردازد |
| شکل گیری | شکل‌گیری |
| خانه ها | خانه‌ها |
| می رود | می‌رود |
| همکاری های علمی | همکاری‌های علمی |
| نه تنها | نه‌تنها |
| مجله‌ي | مجله‌ی |
| میان رشته ای | میان‌رشته‌ای |
| بین رشته ای | بین‌رشته‌ای |

See normalization-reference.md for the rule contract.

## 8. What it intentionally does not decide

The current deterministic layer does not try to infer ambiguous meaning, choose between context-dependent alternatives, judge terminology, rewrite academic arguments, or perform general semantic proofreading.

The goal is safe, explainable normalization rather than invisible rewriting.

## 9. Recommended academic workflow

Draft normally.

During a cleanup pass, select a manageable passage, enable Track Changes, and run Normalize & Review.

Review the proposed changes in context and accept or reject them individually.

This makes normalization an editorial pass rather than an intrusive correction system.

## 10. If the Persian helper is missing

Check:

1. LibreOffice was restarted after installation or update.
2. The extension is installed and enabled.
3. The document is a Writer document.
4. WriterAgent is configured for the intended Python environment.
5. The installed OXT is the current build.

See troubleshooting.md.

## Quick reference

~~~text
1. Open Writer.
2. Select Persian text.
3. Enable Track Changes if you want reviewable edits.
4. Open Run Python Script.
5. Choose [Persian] Persian Helpers → Normalize & Review.
6. Run.
7. Accept or Reject the changes.
~~~
