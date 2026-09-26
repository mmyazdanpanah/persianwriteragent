# PersianWriterAgent — Normalization Reference

This document defines the current normalization contract.

## 1. Two language layers

~~~text
Mechanical normalization
        ↓
       Hazm
        ↓
Project-controlled spelling
        ↓
Persian spelling dictionary
~~~

The layers remain conceptually separate.

## 2. Hazm is the normalization engine

Hazm is used as the full mechanical normalization engine. PersianWriterAgent should not maintain a second partial normalizer merely to reproduce a few observed cases.

Conceptually:

~~~python
normalized = normalizer.normalize(text)
~~~

PersianWriterAgent then extracts the exact differences that can safely be represented as replacements.

> Hazm determines the mechanical normalized form; PersianWriterAgent determines how those differences are represented and reviewed.

## 3. Spelling layer

The project spelling layer is separate from Hazm. It contains project-reviewed editorial corrections that belong to Persian spelling policy rather than generic mechanical normalization.

## 4. Representative examples

| Before | After |
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

These examples describe current observed behavior. They are not permission to generalize a new rule to every visually similar phrase.

## 5. Context-sensitive decisions

Persian orthography can depend on morphology, syntax, terminology, and meaning.

> Do not automatically invent a context-sensitive correction when the system cannot justify it deterministically.

A conservative no-change result is preferable to an unexplained rewrite.

## 6. Structured change extraction

The language layer returns edit instructions rather than manipulating the Writer document directly:

~~~python
{
    "changes": [
        ["old text", "new text"],
        ...
    ]
}
~~~

This creates a clean boundary:

~~~text
language logic
     ↓
structured changes
     ↓
document replacement
~~~

## 7. Exact replacement

The replacement bridge works only inside the current selection. It does not perform an unrestricted document-wide replacement.

Multiple replacements are applied in a safe order so earlier edits do not invalidate later ranges.

## 8. Track Changes

PersianWriterAgent does not implement a second redline system.

When LibreOffice Track Changes is recording, the exact document mutations are recorded by LibreOffice itself.

~~~text
PersianWriterAgent
    identifies:
        می پردازد → می‌پردازد

LibreOffice
    records:
        native deletion/insertion revision
~~~

## 9. Empty changes are a first-class result

An empty result:

~~~python
{"changes": []}
~~~

means the selected text needs no change.

It is a successful no-op.

The result must not fall through to generic document-result insertion. Otherwise an edit-instruction object could incorrectly become document text.

This contract should be tested explicitly.

## 10. Why no LLM is used here

Basic orthographic normalization does not require semantic inference.

Keeping this path deterministic gives reproducibility, simpler tests, easier debugging, predictable resource usage, and clearer linguistic accountability.

Semantic writing assistance is a separate problem.

## 11. Before adding a new rule

Ask:

1. Is the correction linguistically justified?
2. Is it deterministic?
3. Is it safe without additional context?
4. Is it already handled by Hazm?
5. If not, does it belong in the spelling layer?
6. Can it be represented as an exact replacement?
7. Can it be tested with positive and negative examples?
8. Could it damage legitimate Persian text?

If the last question is uncertain, do not auto-correct it yet.

## 12. Integration contract

A Persian rule is not complete merely because the pure Python normalizer returns the desired string.

The real path is:

~~~text
picker
→ selected text
→ Python worker
→ Persian language layer
→ exact replacement
→ LibreOffice
→ tracked revision
~~~

## 13. Current scope

The deterministic normalization layer does not attempt to provide full Persian grammar correction, semantic rewriting, academic style scoring, terminology adjudication, citation checking, argument evaluation, or general LLM proofreading.
