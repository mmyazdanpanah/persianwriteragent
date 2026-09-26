# PersianWriterAgent — Dependencies

PersianWriterAgent has two different dependency contexts. Keeping them separate prevents a common setup mistake.

## 1. Runtime dependency

The Persian normalization code imports **Hazm**.

Hazm is therefore required in the Python environment configured in WriterAgent's **Settings → Python**.

Current project target:

~~~text
Hazm 0.12.1
~~~

The repository records this explicitly in `requirements-persian.txt`.

Install it into the environment used by WriterAgent:

~~~bash
python3 -m venv ~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env
~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env/bin/python -m pip install --upgrade pip
~/Workspace/02_AI_Lab/Persian_Writing/Persian_NLP/hazm_env/bin/python -m pip install -r requirements-persian.txt
~~~

Then configure WriterAgent to use that environment.

If the environment already exists, do not recreate it; install/update the declared requirements into the existing environment.

## 2. WriterAgent dependencies

PersianWriterAgent is built on WriterAgent and reuses its general Python, LibreOffice, UNO, scripting, and extension infrastructure.

Those dependencies belong to the upstream project rather than being duplicated here.

See [WriterAgent](https://github.com/KeithCu/writeragent) for the general application setup.

## 3. Development dependencies

The repository's `pyproject.toml` defines the general WriterAgent development environment.

For contributor development, use:

~~~bash
uv sync
~~~

The Persian runtime environment is separate from the repository `.venv`.

~~~text
repository .venv
    ↓
development / tests / tooling

hazm_env
    ↓
WriterAgent Persian runtime
~~~

Do not assume that installing Hazm into `.venv` makes it available to the running LibreOffice worker.

## 4. Why Hazm is separate

WriterAgent's general environment is broad and serves many features. Persian normalization has a smaller, language-specific runtime dependency.

Keeping Hazm in the dedicated Persian environment makes the runtime requirement explicit, keeps the Persian layer reproducible, and makes debugging easier without silently changing the general WriterAgent dependency set.

## 5. Current dependency boundary

~~~text
LibreOffice
    ↓
WriterAgent
    ↓
configured Python environment
    ↓
Hazm
    ↓
Persian normalization
~~~

The current Persian normalization path does not require an LLM, cloud API, database, or external service.

## 6. Adding future dependencies

Before introducing a new package, ask whether it is actually required, whether the existing stack already solves the problem, whether it belongs to deterministic normalization or a separate feature, and whether it materially increases installation or maintenance cost.

Keep the stable Persian normalization path small and reproducible.
