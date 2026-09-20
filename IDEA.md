# PersianWriterAgent

PersianWriterAgent is a Persian-first scholarly writing environment for LibreOffice, built on top of WriterAgent.

Its purpose is to make professional Persian academic writing more precise, consistent, and reviewable by combining deterministic Persian language processing with WriterAgent and LibreOffice's native editing capabilities.

The project focuses on Persian academic writing rather than general-purpose chat: normalization, spelling, terminology, style, and eventually context-aware scholarly assistance.

The guiding principle is **human-controlled, precise, and explainable assistance**: AI should propose useful changes while the writer remains in control of what is accepted into the text.

PersianWriterAgent is an extension of the existing WriterAgent ecosystem, not a replacement for it.

## Principle

When a normalization is ambiguous or context-dependent, do not change it automatically.

PersianWriterAgent prefers a smaller number of deterministic, explainable corrections over aggressive normalization. Every automatic correction must be safe, reproducible, and reviewable by the writer.

## Next Phase: Persian LLM Integration

The next development phase is an optional, configurable integration of a Persian-tuned language model.

The integration will use WriterAgent's existing functions and extension architecture rather than creating a separate writing-assistant system. It is intended to add contextual Persian assistance for scholarly writing, editing, terminology, and style while preserving the existing WriterAgent foundation.

Model choice will remain adjustable so compatible models can be evaluated and selected according to hardware constraints, task requirements, and workflow needs.

This work is planned for the next release and is not part of the current v0.3.1 mechanical normalization and reviewed spelling milestone.
