# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal AI writing tool (Japanese UI/output). Python + Streamlit + Gemini API (`google-genai` SDK). No database, no auth, no tests or linter configured.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # setup
cp .env.example .env                                                  # then set GEMINI_API_KEY
.venv/bin/streamlit run app.py                                        # run (http://localhost:8501)
```

Headless smoke test without an API key (checks the script renders and a feature switch doesn't raise):

```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("app.py").run(timeout=30)
assert not at.exception
```

## Architecture

Three modules, data-driven:

- `features.py` — the single source of truth for every writing feature. Each `Feature` holds a system prompt, a `template` string, and a list of `Field`s (text / textarea / select / slider). `build_prompt()` fills `{key}` placeholders from the form values; empty values become `指定なし`.
- `app.py` — generic UI. The sidebar radio and the input form are generated entirely from `FEATURES`; there is no per-feature UI code. Widget keys are `"{feature.id}_{field.key}"`. Results are stored in `st.session_state.result[feature.id]` (so they survive reruns/feature switching) and `history` (session-only, newest first).
- `gemini_client.py` — `stream_text()` generator wrapping `generate_content_stream`; `app.py` consumes it with `st.write_stream`. Model list (`MODELS`, `DEFAULT_MODEL`) lives here.

API key resolution: sidebar input overrides `GEMINI_API_KEY` from `.env` (loaded via `python-dotenv`).

## Adding a feature

Append a `Feature(...)` to `FEATURES` in `features.py`. Every `{placeholder}` in `template` must match a `Field.key`, or `build_prompt()` raises `KeyError`. No changes to `app.py` are needed. Fields with `required=True` are validated in `app.py` before the API call.
