# PersianWriterAgent

PersianWriterAgent is the Persian-focused development layer of WriterAgent for LibreOffice.

The project keeps the upstream WriterAgent architecture intact and adds Persian language support incrementally rather than creating a separate implementation.

## Scope

Initial goals:

- Persian academic and research writing
- Persian text normalization
- Persian tokenization and sentence processing
- نیم‌فاصله and punctuation utilities
- Persian proofreading and editorial workflows
- Persian-aware AI writing assistance

## Architecture

```text
PersianWriterAgent
│
├── upstream WriterAgent
│   ├── LibreOffice / UNO
│   ├── AI sidebar
│   ├── MCP
│   └── ACP agent backends
│
└── Persian language layer
    ├── Hazm
    ├── deterministic Persian rules
    └── future DadmaTools bridge
```

The deterministic linguistic layer and semantic AI layer remain separate:

```text
Deterministic language        Semantic reasoning
        │                              │
       Hazm                           Qwen
        │
   future DadmaTools
```

## Development environments

The project deliberately keeps the environments separate:

- WriterAgent development environment: repository `.venv`
- Persian NLP environment: `Persian_NLP/hazm_env`
- Heavier Persian NLP/ML experiments: `Persian_NLP/dadma_env`

Hazm should not be merged blindly into the heavier DadmaTools environment. The first Persian integration uses the already-tested Hazm environment.

## Integration policy

Persian-specific functionality belongs in this fork. General WriterAgent fixes should remain upstream-compatible and, where appropriate, be contributed upstream.

Keep the Persian layer small and modular so that syncing future upstream WriterAgent changes remains practical.

## Current milestone

**PersianWriterAgent v0.1 development foundation**

1. Public fork established.
2. Persian architecture documented.
3. Hazm integration tested locally through WriterAgent's venv scripting layer.
4. Persian sandbox authorization is being validated before inclusion in a release build.

This is development documentation, not a stable release announcement.

## License and attribution

PersianWriterAgent remains based on WriterAgent and its upstream contributors. Preserve the upstream license, copyright notices, and attribution requirements when modifying or redistributing the project.
