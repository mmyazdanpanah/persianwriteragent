# PersianWriterAgent

> **Persian-first scholarly writing assistance for LibreOffice.**

PersianWriterAgent adds a focused Persian language layer to [WriterAgent](https://github.com/KeithCu/writeragent). It is intended for Persian academic, research, and professional writing where corrections should be useful **without silently rewriting the author's text**.

The Persian layer currently provides:

- deterministic Persian normalization powered by Hazm
- a separate reviewed Persian spelling layer
- a built-in **Persian Helpers → Normalize & Review** script in WriterAgent's Run Python Script picker
- exact replacement of selected text
- native LibreOffice Track Changes for reviewable edits
- a true no-op when the selected text needs no change

The central rule is simple:

> **Suggest mechanically where it is safe; let the writer decide what becomes part of the document.**

## Start here

If you only want to use PersianWriterAgent:

**[→ Persian user guide](docs/persian/user-guide.md)**

For troubleshooting:

**[→ Persian troubleshooting](docs/persian/troubleshooting.md)**

For the normalization rules and examples:

**[→ Normalization reference](docs/persian/normalization-reference.md)**

For developers:

**[→ Persian architecture](docs/persian/developer-architecture.md)**

## What PersianWriterAgent is — and is not

PersianWriterAgent is a **thin Persian-focused layer**, not a reimplementation of WriterAgent.

WriterAgent remains responsible for the general LibreOffice extension, Python execution environment, document integration, script picker, AI tooling, and broader application infrastructure.

PersianWriterAgent adds Persian-specific behavior in `plugin/persian/` and connects it to the existing WriterAgent scripting infrastructure.

For WriterAgent's general installation, features, architecture, and scripting system, use the [upstream WriterAgent repository](https://github.com/KeithCu/writeragent) and its documentation.

This repository documents **what is specific to PersianWriterAgent** rather than copying the upstream project's large documentation set.

## Current Persian workflow

```text
Persian text selected in Writer
        ↓
WriterAgent → Run Python Script
        ↓
[Persian] Persian Helpers
        ↓
Normalize & Review
        ↓
Hazm normalization
        +
reviewed Persian spelling layer
        ↓
exact changes extracted
        ↓
native LibreOffice tracked replacements
        ↓
Accept / Reject each change
```

When nothing needs changing:

```text
selected text
    ↓
Normalize & Review
    ↓
No Persian changes needed
    ↓
document remains untouched
```

No manual script copying or saving is required for the normal workflow.

## Design principles

PersianWriterAgent is deliberately conservative.

### Human review comes first

The Persian helper does not silently overwrite the selected text. When changes are found, they are applied through LibreOffice's native revision system when Track Changes is enabled.

This means the author can inspect individual edits and choose **Accept** or **Reject**.

### Deterministic language processing first

The current language layer is deliberately small:

```text
Hazm normalization
        ↓
reviewed Persian spelling dictionary
        ↓
future Persian language layers
```

Hazm is used as the full mechanical normalization engine. The project's own spelling dictionary is a separate editorial layer for controlled corrections that are not simply normalization.

Ambiguous or context-dependent changes should not be invented by the project.

### No unnecessary AI in the normalization path

The current normalization/review workflow is deterministic and reproducible. It does not require a language model to decide whether a basic orthographic normalization should happen.

Future semantic assistance may build on the existing WriterAgent architecture, but it is not part of the current normalization contract.

## Project structure

The Persian-specific code is intentionally concentrated:

```text
plugin/persian/
├── normalize.py       # Hazm normalization and exact change extraction
├── spelling.py        # reviewed Persian spelling rules
├── scripts.py         # built-in Persian script picker integration
└── tracked_replace.py # exact-range replacement bridge

docs/persian/
├── user-guide.md
├── troubleshooting.md
├── normalization-reference.md
└── developer-architecture.md
```

The surrounding WriterAgent code remains upstream infrastructure.

## Contributing

For Persian-specific contributions, start with:

- [Persian developer architecture](docs/persian/developer-architecture.md)
- [Contributing guide](CONTRIBUTING.md)
- [Project principles](IDEA.md)
- [Repository invariants](AGENTS.md)

Language changes should include before/after examples and a clear reason for the correction. Prefer small, deterministic, reviewable changes.

## License

GNU GPL v3 or later. See [LICENSE](LICENSE).
