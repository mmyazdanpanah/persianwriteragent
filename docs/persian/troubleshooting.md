# PersianWriterAgent — Troubleshooting

Use this page when the normal workflow does not behave as expected.

## 1. Locate the failing boundary

~~~text
Extension
   ↓
Python environment
   ↓
Script picker
   ↓
Persian language layer
   ↓
Document replacement
   ↓
LibreOffice Track Changes
~~~

## 2. Persian helper is not visible

Expected:

~~~text
[Persian] Persian Helpers
    └── Normalize & Review
~~~

Check:

1. LibreOffice was fully restarted after installation or update.
2. The extension is installed and enabled.
3. You are working in Writer.
4. WriterAgent is configured for the intended Python environment.
5. The installed OXT is the current PersianWriterAgent build.

If source code changed locally, remember that LibreOffice executes the installed OXT, not the repository source directly.

## 3. Import or dependency failure

Check the configured Python environment first.

The development environment used by this project is:

~~~text
~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env
~~~

Restart LibreOffice after changing the environment.

## 4. The helper runs but no change appears

This can be correct behavior.

For already-normalized text:

~~~text
No Persian changes needed.
~~~

No revision should be created.

To test the actual path, use:

~~~text
می پردازد
~~~

with Track Changes enabled. The expected normalized form is:

~~~text
می‌پردازد
~~~

## 5. Changes are returned but the document is not edited

The language layer probably worked, but document mutation did not.

Check that:

- the selection is still active
- the current document is Writer
- the installed OXT contains the current Python runner
- LibreOffice was restarted after deployment

Developer boundary:

~~~text
{"changes": [...]}
        ↓
apply_tracked_replacements(...)
~~~

## 6. An empty result changes the document

A result equivalent to:

~~~python
{"changes": []}
~~~

must be a successful no-op.

If the selection is replaced by result text or gets a deletion/insertion revision, the installed result-handling path is wrong or stale.

## 7. Only some expected changes appear

Compare:

1. pure Persian normalization output
2. Persian output inside the WriterAgent worker
3. behavior of the installed OXT

If they differ, suspect:

- stale OXT
- wrong Python environment
- different Hazm version
- old Persian source loaded by the worker

Do not add language rules until this is resolved.

## 8. Changes appear without Track Changes revisions

The Persian bridge does not implement its own revision system.

Enable:

**Edit → Track Changes → Record**

before running the helper.

If text changes but no revisions appear, LibreOffice was not recording the mutation at that time.

## 9. Clean text gets a revision

That should never happen.

The intended path is:

~~~text
changes = []
      ↓
successful no-op
      ↓
no document mutation
~~~

Check for an old installed OXT first.

## 10. Behavior looks like an old version

Redeploy and restart LibreOffice:

~~~bash
cd ~/Workspace/02_AI_Lab/Persian_Writing/Tools/persianwriteragent
make deploy

osascript -e 'quit app "LibreOffice"'
sleep 3
open -a "LibreOffice"
~~~

Then reproduce the issue.

## 11. Bug report contents

Provide the smallest reproducible case:

~~~text
Input:
...

Expected:
...

Actual:
...

Track Changes:
on/off

Python environment:
...

PersianWriterAgent commit/version:
...

LibreOffice version:
...

Operating system:
...
~~~

Do not attach private documents, API credentials, or complete private logs.

## 12. Developer debugging order

~~~text
1. Reproduce with a tiny selection.
2. Test pure Persian normalization.
3. Test exact change extraction.
4. Test the built-in picker path.
5. Test the installed OXT.
6. Test native LibreOffice replacement.
7. Test Track Changes behavior.
~~~

This prevents packaging problems from being mistaken for language problems.

## 13. Generic upstream problems

If the failure is clearly in generic WriterAgent infrastructure rather than Persian behavior, use the [upstream WriterAgent project](https://github.com/KeithCu/writeragent) rather than duplicating the same infrastructure fix here.
