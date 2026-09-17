# PersianWriterAgent

**A Persian-first writing and research assistant for LibreOffice, built on WriterAgent.**

PersianWriterAgent is a focused development layer on top of [WriterAgent](https://github.com/KeithCu/writeragent). It adds Persian-language capabilities while preserving the upstream architecture, so Persian-specific work can evolve without turning the project into an unrelated rewrite.

## Project position

PersianWriterAgent is not a replacement implementation of WriterAgent. It is a Persian-focused fork and development layer.

```text
WriterAgent
    │
    └── PersianWriterAgent
          │
          ├── Persian language layer
          │   ├── Hazm
          │   ├── Persian normalization
          │   ├── Persian text utilities
          │   └── future DadmaTools integration
          │
          ├── Persian writing features
          │   ├── proofreading
          │   ├── نیم‌فاصله
          │   ├── punctuation
          │   └── academic/editorial writing
          │
          └── AI writing layer
              └── configurable LLMs
```

The project deliberately separates deterministic language processing from semantic AI assistance:

```text
Deterministic language processing     Semantic reasoning
             │                              │
            Hazm                         Qwen / LLM
             │
     future DadmaTools
```

This separation keeps linguistic rules testable and predictable while leaving higher-level rewriting, drafting, and reasoning to the configured language model.

## Initial scope

The first development phase focuses on practical Persian writing support:

- Persian academic and research writing
- Persian text normalization
- tokenization and sentence processing
- نیم‌فاصله and punctuation utilities
- Persian proofreading and editorial workflows
- Persian-aware AI writing assistance
- LibreOffice Writer integration

The scope is intentionally narrow. Features should be added when they solve a real Persian writing problem rather than simply increasing the dependency footprint.

## Language stack

### Hazm — first-line linguistic layer

[Hazm](https://github.com/roshan-research/hazm) is the initial Persian NLP dependency. It provides lightweight, deterministic functionality suitable for normalization, tokenization, sentence segmentation, and related text processing.

### DadmaTools — future advanced NLP layer

[DadmaTools](https://github.com/Dadmatech/DadmaTools) is kept as a separate, heavier environment for advanced Persian NLP and ML experiments. It is not part of the minimum WriterAgent runtime at this stage.

The project therefore avoids forcing PyTorch, Transformers, spaCy, and other heavyweight dependencies into the lightweight Hazm environment unless a concrete feature requires them.

## Development environments

Keep the environments separate:

```text
Persian_NLP/
├── hazm_env/
└── dadmatools_env/
```

- `hazm_env` — lightweight Persian linguistic processing used by the first integration.
- `dadmatools_env` — heavier DadmaTools/NLP/ML experimentation.
- repository `.venv` — WriterAgent development, build, and test environment.

The environments have different purposes and should not be merged merely for convenience.

## Repository architecture

Persian-specific implementation belongs in a small, isolated namespace:

```text
plugin/
└── persian/
    ├── __init__.py
    ├── normalize.py
    ├── text.py
    └── rules.py
```

The exact module set will grow only when functionality is implemented. Avoid creating placeholder abstractions before they are needed.

## Upstream relationship

PersianWriterAgent follows a thin-fork strategy:

1. Keep the upstream WriterAgent architecture intact.
2. Keep Persian-specific functionality isolated.
3. Keep general bug fixes upstream-compatible.
4. Contribute generally useful fixes upstream when appropriate.
5. Make upstream synchronization practical by keeping the Persian delta small.

This approach reduces maintenance burden and makes it clear which parts belong to WriterAgent and which parts are PersianWriterAgent contributions.

## Current development status

**Foundation phase — experimental.**

Completed:

- public PersianWriterAgent fork established
- Persian project architecture documented
- Persian NLP environments identified and separated
- Hazm environment tested independently
- WriterAgent's Python venv scripting path verified locally
- Persian integration isolated as a small, reversible change

Next:

- finalize the Hazm sandbox authorization change
- build and install a PersianWriterAgent development extension
- test Hazm operations through WriterAgent's scripting layer
- add the first `plugin/persian/` utilities only after the integration is stable
- document reproducible installation and development steps

No stable release is claimed yet.

## Naming

The project name is **PersianWriterAgent**.

Use these names consistently:

| Purpose | Name |
| --- | --- |
| Project / product | `PersianWriterAgent` |
| GitHub repository | `persianwriteragent` |
| Upstream project | `WriterAgent` |
| Persian NLP environment | `hazm_env` |
| Advanced NLP/ML environment | `dadmatools_env` |
| Persian implementation namespace | `plugin.persian` |

Avoid introducing alternative names such as `Persian Writer Agent`, `Persian NLP Agent`, or `PersianWriter` for the same project. Consistent naming matters as the project becomes public.

## License and attribution

PersianWriterAgent is based on WriterAgent and remains subject to the upstream project's license and attribution requirements. Preserve upstream copyright notices, license text, and contributor attribution when modifying or redistributing the project.

Persian-specific code and documentation should clearly identify their origin in this fork while avoiding any implication that the upstream project endorses this fork.
