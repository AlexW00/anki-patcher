# Copilot project instructions for anki-patcher

Purpose: make AI agents productive fast. Keep edits minimal, repo-specific, and CLI-safe.

## Big picture

- CLI to run per-note operations on Anki via AnkiConnect.
- Entry: `anki_patcher/main.py` exposes `anki-patcher` (see `pyproject.toml`).
- Flow: parse args -> load YAML config -> resolve op -> fetch notes (`findNotes` -> `notesInfo`) -> call `execute(card_id, fields, config)` for each -> update with `updateNoteFields`.
- Async mode uses `multiprocessing.Pool(10)`.

## Conventions

- Operation file in `anki_patcher/patcher/operations/` with `def execute(card_id, fields, config)`.
- Fields shape: `fields[FieldName]['value']`. Guard for missing fields.
- Helpers in `anki_patcher/util.py`: `parse_env`, `parse_config`, `parse_fields`, `remove_html_tags*`, `clean_text_for_tts`, `trim_list_points`.
- `.env` loaded in `main.py`. Common vars: `ANKI_CONNECT_URL`, `ANKI_MEDIA_FOLDER`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `CX`.
- YAML configs live in `configs/` and `example_configs/`.

## Dev workflow

- Install: `poetry install`; shell: `poetry shell`; JP deps: `python -m unidic download`.
- List ops: `poetry run anki-patcher list`.
- Run: `poetry run anki-patcher patch -o <op> -d "Deck::Name" -c path/to/config.yml`.
- Async: `poetry run anki-patcher patch-async -o <op> -d ... -c ...`.

## Key modules and examples

- `patcher/patcher.py`: op discovery/import, sync/async patchers.
- `patcher/anki.py`: `invoke(action, params)` HTTP bridge (default `http://localhost:8765`).
- Ops: `add_image.py` (Google CSE -> media file -> `<img>`), `replace.py` (regex over fields), `export_md.py` (template to file; modtime skip), `gpt.py` (ChatCompletion; `do_overwrite_output`).

## Gotchas

- Not all notes have all fields; skip gracefully. HTML often present in field values.
- Validate/media-type when writing to `ANKI_MEDIA_FOLDER`.
- Handle AnkiConnect non-200s; continue patching others.
- `openai` is 0.x; `gpt.py` uses ChatCompletion with model default `gpt-5`.

## Add a new operation

- Create `anki_patcher/patcher/operations/<name>.py` with `execute(...)`.
- Parse config/fields via `util` helpers; update via `invoke('updateNoteFields', {"note": {"id": card_id, "fields": {...}}})`.
- It appears automatically in `anki-patcher list`.
