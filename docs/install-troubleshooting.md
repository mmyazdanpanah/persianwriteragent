# PersianWriterAgent — Installation and Troubleshooting

This page covers the **Persian-specific** setup path.

PersianWriterAgent is built on [WriterAgent](https://github.com/KeithCu/writeragent). General WriterAgent installation, menus, UI modes, AI configuration, and broader features are maintained upstream and are linked rather than copied into this repository.

## 1. Install the extension

Install the PersianWriterAgent .oxt package through LibreOffice Extension Manager:

**Tools → Extension Manager → Add**

Select the package and complete the installation.

Then completely restart LibreOffice.

For the general WriterAgent installation model, see the [upstream WriterAgent repository](https://github.com/KeithCu/writeragent).

## 2. Configure the Python environment

Persian normalization runs through WriterAgent's existing Python Script infrastructure.

Open:

**WriterAgent → Settings → Python**

Set the Python environment to one containing the Persian dependencies.

The development environment used by this project is:

~~~text
~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env
~~~

Use the corresponding absolute path on another machine.

After changing the environment, restart LibreOffice if the extension does not immediately see it.

## 3. Verify the Persian helper

Open a Writer document.

Select some Persian text.

Open **Run Python Script**.

The built-in picker should contain:

~~~text
[Persian] Persian Helpers
    └── Normalize & Review
~~~

The normal workflow does not require copying or saving a Python script.

## 4. Recommended review workflow

For academic and professional documents:

1. Select the Persian passage.
2. Enable **Edit → Track Changes → Record**.
3. Run **[Persian] Persian Helpers → Normalize & Review**.
4. Inspect the proposed revisions.
5. Accept or reject them individually.

The Persian layer uses LibreOffice's native revision system. It does not maintain a second review mechanism.

## 5. Already-correct text

A clean selection should produce:

~~~text
No Persian changes needed.
~~~

The document must remain untouched.

An empty result is a successful no-op, not a request to insert result text.

## 6. If the Persian helper is missing

Check these in order:

1. Restart LibreOffice completely.
2. Confirm the extension is installed and enabled.
3. Confirm the current document is Writer.
4. Check WriterAgent's Python environment.
5. Confirm the installed OXT is the current PersianWriterAgent build.
6. Redeploy the extension if you are developing from source.

For development:

~~~bash
cd ~/Workspace/02_AI_Lab/Persian_Writing/Tools/persianwriteragent
make deploy

osascript -e 'quit app "LibreOffice"'
sleep 3
open -a "LibreOffice"
~~~

## 7. If behavior looks old

The repository source and the installed LibreOffice extension are different states:

~~~text
source tree
   ↓
build/deploy
   ↓
WriterAgent.oxt
   ↓
LibreOffice extension cache
   ↓
running worker
~~~

A changed source file does not automatically change the running extension.

Redeploy and restart before changing working language code.

## 8. If only some changes appear

Compare the result at these stages:

1. pure Persian normalization
2. Persian helper inside the WriterAgent worker
3. installed OXT
4. native LibreOffice document result

If pure Python and the installed worker disagree, suspect a stale OXT, wrong Python environment, or different Hazm version before adding a new language rule.

## 9. If changes appear without revisions

Enable:

**Edit → Track Changes → Record**

before running the helper.

The Persian bridge performs exact document replacements; LibreOffice records them as revisions when Track Changes is active.

## 10. Debug log

For failures that reach the WriterAgent runtime, the upstream WriterAgent debug log is normally the useful diagnostic source.

See the upstream project's troubleshooting and bug-reporting documentation rather than duplicating its general logging documentation here.

Do not attach API keys, private documents, or complete private logs to an issue.

## 11. Reporting a Persian bug

Provide:

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

A tiny reproducible Persian example is much more useful than a large private document.

## Related documentation

- [Persian User Guide](persian/user-guide.md)
- [Persian Normalization Reference](persian/normalization-reference.md)
- [Persian Developer Architecture](persian/developer-architecture.md)
- [Persian Troubleshooting](persian/troubleshooting.md)
- [Upstream WriterAgent](https://github.com/KeithCu/writeragent)
