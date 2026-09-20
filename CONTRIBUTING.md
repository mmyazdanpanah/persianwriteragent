# Contributing to PersianWriterAgent

Thank you for your interest in PersianWriterAgent.

PersianWriterAgent is a Persian-first scholarly writing and research assistant for LibreOffice, built as a focused layer on top of WriterAgent. The project aims to make Persian academic writing more precise, consistent, explainable, and reviewable while keeping the writer in control.

We welcome contributions from developers, Persian-language researchers, linguists, writers, LibreOffice users, and anyone interested in better open-source tools for Persian writing.

## Before you start

Please read:

- [README.md](README.md) for the project overview and setup.
- [IDEA.md](IDEA.md) for the project's design principles.
- [AGENTS.md](AGENTS.md) for repository invariants and development rules.
- The relevant topic documentation under [docs/](docs/) before changing an established subsystem.

Persian-specific code lives primarily under `plugin/persian/`.

## What we welcome

Useful contributions include:

- Persian spelling and normalization improvements
- Conservative, well-supported terminology rules
- Tests based on real Persian writing problems
- LibreOffice/UNO integration fixes
- Documentation improvements
- Reproducible bug reports
- Accessibility and usability improvements
- Performance improvements that reduce unnecessary work
- Improvements that remain compatible with the upstream WriterAgent architecture

For Persian language rules, please include a short explanation of why the correction is linguistically justified and whether it is deterministic or context-dependent.

## What we try to avoid

PersianWriterAgent deliberately favors small, explainable changes.

Please do not introduce automatic corrections that are:

- ambiguous without context
- difficult to review or reproduce
- based only on a single example
- likely to alter URLs, paths, code, identifiers, numbers, or other mixed content
- duplicating functionality already provided by WriterAgent or its existing dependencies

When a correction is context-dependent, prefer a reviewed dictionary/terminology mechanism or the planned configurable Persian-tuned LLM layer rather than an aggressive normalization rule.

## Development setup

The project uses Python 3.13 for development and `uv` for dependency management.

```bash
git clone https://github.com/mmyazdanpanah/persianwriteragent.git
cd persianwriteragent
uv python install 3.13
uv sync
```

Useful commands:

```bash
make check-setup
make typecheck
make pytest
make test
make build
```

For ordinary changes, run the tests relevant to the code you changed and `make typecheck`. Use the full `make test` suite for large or cross-cutting changes.

If your change affects LibreOffice/UNO behavior, follow the native test guidance in `AGENTS.md` and the relevant topic documentation.

## Development environment

The project is currently developed primarily on macOS with Apple Silicon and LibreOffice.

This is the maintainer's development environment, not a project requirement. Contributors may develop and test on macOS, Linux, or Windows.

Pull requests are automatically validated by GitHub Actions on Ubuntu. Additional macOS or Windows validation may be run when platform-specific changes require it.

When reporting a platform-specific issue, please include your operating system, architecture, LibreOffice version, and WriterAgent/PersianWriterAgent version or commit.

## Persian development workflow

For Persian-specific changes, keep the processing layers separate:

```text
mechanical normalization
        ↓
reviewed spelling dictionary
        ↓
future terminology layer
        ↓
optional configurable Persian-tuned LLM assistance
```

Deterministic changes should be conservative and reviewable through LibreOffice Track Changes. The planned LLM layer is a separate contextual assistance layer and should remain optional, configurable, and compatible with the existing WriterAgent architecture.

Every automatic correction should be:

1. safe for unrelated content,
2. deterministic and reproducible,
3. covered by a test,
4. explainable to a Persian-language user.

## Pull requests

Please open a pull request against `master`.

A good pull request should:

- explain the problem and the proposed solution
- keep the change focused
- include tests for behavior changes
- update documentation when behavior or workflow changes
- mention any known limitations
- avoid unrelated formatting or generated-file churn

For Persian language changes, include before/after examples and explain why the proposed form should be preferred.

Please do not commit generated translation templates or unrelated build artifacts unless the change intentionally updates them.

## Reporting bugs

Before opening an issue, search existing issues if possible.

A useful bug report includes:

- operating system
- LibreOffice version
- WriterAgent/PersianWriterAgent version or commit
- reproduction steps
- minimal input text or document description
- expected behavior
- actual behavior
- relevant logs or screenshots, with secrets and personal data removed

For language-related bugs, a minimal Persian example is especially valuable.

## First contributions

If you are new to the project, documentation, tests, reproducible examples, and conservative Persian-language corrections are all valuable contributions.

If you are unsure where to begin, open an issue describing the problem or idea before implementing a large change. Small, focused pull requests are easier to review and maintain.

Thank you for helping build better open-source Persian writing tools.
