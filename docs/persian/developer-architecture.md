# PersianWriterAgent — Developer Architecture

PersianWriterAgent is intentionally a thin layer over WriterAgent. It adds Persian behavior without reimplementing WriterAgent's general LibreOffice, Python, scripting, or document infrastructure.

For upstream architecture, see [WriterAgent](https://github.com/KeithCu/writeragent).

## 1. Boundary

~~~text
WriterAgent
────────────────────────────────
LibreOffice integration
Python worker
Run Python Script picker
selection handling
generic script execution
generic result handling
document mutation
Track Changes
────────────────────────────────
PersianWriterAgent
────────────────────────────────
plugin/persian/
    normalize.py
    spelling.py
    scripts.py
    tracked_replace.py
~~~

The Persian layer should use existing WriterAgent extension points whenever possible.

## 2. Built-in script picker

The normal product entry point is WriterAgent's existing Run Python Script picker.

The Persian layer registers:

~~~text
PICKER_WIRING
    ↓
[Persian] Persian Helpers
    ↓
Normalize & Review
~~~

The helper is therefore a built-in selectable feature. Users should not have to create or save a My Script to use Persian normalization.

## 3. Script execution

The helper ultimately calls:

~~~python
run_persian(text)
~~~

where text is the selected Writer text supplied by WriterAgent.

It returns structured edit instructions:

~~~python
{
    "changes": [
        ["old", "new"],
        ...
    ]
}
~~~

It does not directly manipulate UNO objects.

## 4. Normalization pipeline

~~~text
selected text
      ↓
run_persian(text)
      ↓
extract_hazm_changes(text)
      ↓
find_spelling_changes(text)
      ↓
merge and deduplicate
      ↓
{"changes": [...]}
~~~

Mechanical normalization and project spelling remain separate concerns.

## 5. Exact replacement bridge

tracked_replace.py is not a Track Changes implementation.

It receives exact replacements, finds the literal source strings inside the current selection, orders the ranges safely, and performs the replacements.

If Track Changes is enabled, LibreOffice records those mutations as native revisions.

## 6. Result handling and the no-op contract

There are two valid structured results.

Changes exist:

~~~python
{"changes": [["old", "new"]]}
~~~

The Persian replacement bridge runs.

No changes exist:

~~~python
{"changes": []}
~~~

The operation succeeds as a no-op.

It must not fall through to generic result insertion, because generic insertion assumes a script result is document content. Persian normalization returns edit instructions.

## 7. Installed OXT versus source tree

A critical operational boundary is:

~~~text
repository source
      ↓
build/deploy
      ↓
WriterAgent.oxt
      ↓
LibreOffice extension cache
      ↓
running worker
~~~

If source code changed but LibreOffice behaves like an older version, first suspect a stale installed OXT.

For the local development checkout:

~~~bash
cd ~/Workspace/02_AI_Lab/Persian_Writing/Tools/persianwriteragent
make deploy

osascript -e 'quit app "LibreOffice"'
sleep 3
open -a "LibreOffice"
~~~

Do not rewrite working language logic merely because the installed extension is stale.

## 8. Testing layers

### Language layer
Test Hazm and spelling change extraction with ordinary Python tests.

### Replacement layer
Test exact-range matching and ordering.

### Native LibreOffice layer
When behavior depends on document revisions, use the existing native UNO test infrastructure.

The integration contract is:

~~~text
input selection
→ expected tracked changes
→ Reject restores original
→ Accept leaves normalized text
~~~

## 9. Manual fixtures versus product UX

A manually runnable Python fixture can be useful for debugging.

It is not the product UX.

The product UX is:

~~~text
[Persian] Persian Helpers
    → Normalize & Review
~~~

Keep that distinction clear in documentation and tests.

## 10. Adding future Persian features

Prefer:

~~~text
new Persian behavior
      ↓
plugin/persian/
      ↓
existing WriterAgent extension point
      ↓
existing WriterAgent UI/execution path
~~~

Examples:

- deterministic language rule → Persian language layer
- Persian built-in script → picker wiring
- reviewable edit → existing document/revision mechanism
- semantic Persian assistant → existing WriterAgent AI architecture

Avoid parallel Persian subsystems when an existing WriterAgent extension point already solves the problem.

## 11. What belongs upstream?

If a change is useful independently of Persian, it should be considered for upstream WriterAgent.

Examples include generic Python Script picker behavior, selected-text injection, generic result handling, and reusable document/revision infrastructure.

Persian-specific rules and UI should remain here.

## 12. Core invariant

> **PersianWriterAgent owns Persian language behavior; WriterAgent owns the general LibreOffice application machinery.**

This boundary keeps the fork maintainable and makes clean upstream contributions possible.
