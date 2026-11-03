# Design — Task Manager

## Overview

Task Manager is a small Flask web application rendering server-side HTML with
Jinja2 and persisting data in SQLite. The design favors simplicity and
maintainability: a single application module exposes the routes, a small data
layer wraps SQLite access with parameterized queries, and one Jinja2 template
renders the UI. Configuration (secret key, database path) comes from environment
variables so no secrets are hardcoded.

## Structure Note (steering reconciliation)

The `structure.md` steering file describes a package layout (`app/` package with
`routes.py`, `db.py`, `models.py`). This feature's requirements, however,
explicitly specify a **flat layout** (`app.py`, `templates/index.html`,
`test_app.py` at the repo root). Because the feature request is the more
specific instruction — and because it matches the `app.py` pattern already
configured in the "Run Python Unit Tests" agent hook — this design follows the
**flat layout**. The spirit of the steering file (clear separation of app logic,
templates, and tests; PEP 8; type hints; env-based config; parameterized SQL) is
preserved; only the physical file layout differs.

## Project Layout

```
kiro-demo/
├── app.py                 # Flask app factory, config, DB layer, routes, error handlers
├── schema.sql             # SQLite schema (tasks table)   [optional; may inline in app.py]
├── templates/
│   ├── base.html          # Shared layout (viewport, responsive CSS include)
│   └── index.html         # Task list + add-task form + per-task actions
├── static/
│   └── style.css          # Responsive styling
├── test_app.py            # pytest suite (temporary DB)
├── requirements.txt       # Flask, pytest (pinned)
├── README.md              # Setup and usage
└── .gitignore             # .venv, __pycache__, *.db, .env
```

## Application Architecture

### Application factory

`app.py` exposes `create_app(config: dict | None = None) -> Flask`:

- Reads configuration from environment variables with safe local defaults:
  - `FLASK_SECRET_KEY` → `app.config["SECRET_KEY"]` (default only for local dev).
  - `DATABASE_PATH` → `app.config["DATABASE_PATH"]` (default `tasks.db`).
- Accepts an optional `config` override dict so tests can inject a temporary
  `DATABASE_PATH` and `TESTING=True`.
- Initializes the database schema if it does not exist.
- Registers routes and error handlers.
- Returns the configured `Flask` instance.

A module-level `app = create_app()` and a `run.py`-style `__main__` guard allow
running the dev server with `python app.py`.

### Data layer (within `app.py`)

Thin helpers over the standard-library `sqlite3` module:

| Function | Signature | Responsibility |
|----------|-----------|----------------|
| `get_db` | `get_db() -> sqlite3.Connection` | Return a per-request connection (via Flask `g`), `row_factory = sqlite3.Row`. |
| `close_db` | `close_db(exception=None) -> None` | Close the connection at request teardown. |
| `init_db` | `init_db() -> None` | Create the `tasks` table if absent. |
| `get_all_tasks` | `get_all_tasks() -> list[sqlite3.Row]` | Return all tasks ordered newest-first. |
| `get_task` | `get_task(task_id: int) -> sqlite3.Row \| None` | Return one task or `None`. |
| `create_task` | `create_task(title: str, description: str) -> int` | Insert a task; return new id. |
| `complete_task` | `complete_task(task_id: int) -> bool` | Mark complete; return whether a row changed. |
| `delete_task` | `delete_task(task_id: int) -> bool` | Delete; return whether a row changed. |

All SQL uses parameterized queries (`?` placeholders). No string interpolation of
user input into SQL.

### Data model

`tasks` table:

| Column        | Type                      | Notes                                  |
|---------------|---------------------------|----------------------------------------|
| `id`          | INTEGER PRIMARY KEY       | Autoincrement rowid.                   |
| `title`       | TEXT NOT NULL             | Required; validated non-empty.         |
| `description` | TEXT NOT NULL DEFAULT ''  | Optional; empty string when omitted.   |
| `completed`   | INTEGER NOT NULL DEFAULT 0| 0 = open, 1 = completed.               |
| `created_at`  | TEXT NOT NULL             | ISO-8601 timestamp for ordering.       |

### Routes

| Method & Path          | View                | Behavior                                                                 | Success | Error |
|------------------------|---------------------|--------------------------------------------------------------------------|---------|-------|
| `GET /`                | `index`             | Render `index.html` with all tasks.                                      | 200     | 500   |
| `POST /add`            | `add`               | Validate title; create task; redirect to `/`.                           | 302     | 400   |
| `POST /complete/<int:task_id>` | `complete`  | Mark task complete; redirect to `/`.                                     | 302     | 404   |
| `POST /delete/<int:task_id>`   | `delete`    | Delete task; redirect to `/`.                                            | 302     | 404   |

- State-changing routes use **POST**; the only read view uses **GET** (Req 9.4).
- `<int:task_id>` converter ensures non-integer ids yield 404 automatically.
- Unsupported methods on these routes yield **405** via Flask's default routing.

### Input validation

`add` view logic:

1. Read `title` and `description` from `request.form`.
2. Strip whitespace from `title`.
3. If the stripped title is empty → do not persist; flash a validation message
   and respond (re-render with 400 or redirect with flashed message per Req 3).
4. Otherwise persist with the trimmed title and the description (default `''`).
5. Jinja2 autoescaping ensures stored text is HTML-escaped on render (Req 3.4).

### Error handling

- `@app.errorhandler(404)` → render a friendly "not found" response (404).
- `@app.errorhandler(405)` → method-not-allowed response (405).
- `@app.errorhandler(500)` → generic error page without leaking internals (500).
- `get_task` returning `None` in `complete`/`delete` → `abort(404)`.

### Configuration & secrets

- `SECRET_KEY` from `FLASK_SECRET_KEY`; a default is used only for local dev and
  never represents a real secret. Production must set the env var.
- `DATABASE_PATH` from env, default `tasks.db`.
- Tests pass an overriding config with a temp DB path and never touch the dev DB.

## UI / Templates

- `base.html`: HTML skeleton with `<meta name="viewport" ...>`, links
  `static/style.css`, and a `{% block content %}`.
- `index.html`: extends `base.html`; renders:
  - An add-task form (`POST /add`) with a required title input and optional
    description textarea.
  - A flash-message area for validation feedback.
  - The task list; each item shows title, description, status, and two small
    forms (`POST /complete/<id>`, `POST /delete/<id>`).
  - An empty-state message when there are no tasks.
- `style.css`: minimal responsive styling (fluid container, readable spacing,
  completed tasks visually distinguished, e.g. strikethrough/dimmed).

## Testing Strategy

Framework: **pytest**, using Flask's test client.

Fixtures (in `test_app.py`) — kept simple for a beginner:

- A `client` fixture that:
  1. Creates a fresh temporary database file (e.g. via `tempfile`) per test,
     so tests never share state and never depend on each other.
  2. Calls `create_app({"TESTING": True, "DATABASE_PATH": <temp>})` so the app
     points at the temp DB, never the default development DB.
  3. Yields `app.test_client()`.
  4. Tears down afterward by removing the temp DB file, leaving nothing behind.
- This guarantees isolation from the development/production database (Req 8.3,
  10.1, 10.3, 10.8–10.11). A per-test temp DB is the simplest way to get a clean
  known state for every test without extra reset logic.

Planned tests (map to Req 10.2 and the expanded Req 10.5–10.14):

| Test | Asserts | Reqs |
|------|---------|------|
| `test_home_page_empty` | `GET /` returns 200 and shows empty-state. | 10.2 |
| `test_create_task` | `POST /add` with valid title → 302; task appears on `/`. | 10.2 |
| `test_create_task_without_description` | valid title, no description → task created (description optional). | 10.7 |
| `test_empty_title_rejected` | `POST /add` with `""` title → not persisted; validation status returned. | 10.5 |
| `test_whitespace_title_rejected` | `POST /add` with `"   "` title → not persisted (trimmed to empty). | 10.6 |
| `test_complete_task` | `POST /complete/<id>` → 302; task shows completed. | 10.2 |
| `test_delete_task` | `POST /delete/<id>` → 302; task gone from `/`. | 10.2 |
| `test_unknown_url_404` | `GET` an unknown URL → 404. | 10.12 |
| `test_complete_missing_task_404` | `POST /complete/<bad id>` → 404; no data changed. | 10.13 |
| `test_delete_missing_task_404` | `POST /delete/<bad id>` → 404; no data changed. | 10.13 |
| `test_wrong_method_405` | `GET` on an add/complete/delete route → 405. | 10.14 |
| `test_dev_db_untouched` | the default development DB file is not created/modified by tests. | 10.11 |

`python -m pytest -q` is the canonical command (also used by the agent hook).

> **Beginner note:** these tests only use Flask's built-in test client and
> Python's standard library (`tempfile`, `os`) — no extra testing libraries are
> needed.

## Quality & Conventions

- PEP 8 throughout; lines kept readable (≤ 88 chars).
- Type hints on data-layer and view helper signatures.
- Parameterized SQL only.
- No hardcoded secrets.
- Minimal dependencies pinned in `requirements.txt` (Flask, pytest).

## Dependencies

```
Flask>=3.0,<4.0
pytest>=8.0,<9.0
```

## Traceability (requirements → design)

- Req 1 → `index` route + `index.html` + `get_all_tasks` + empty-state.
- Req 2 → `add` route + `create_task` + default `completed=0`.
- Req 3 → validation in `add`, Jinja2 autoescape, flash messages.
- Req 4 → `complete` route + `complete_task` + 404 on missing.
- Req 5 → `delete` route + `delete_task` + 404 on missing.
- Req 6 → `init_db`, SQLite persistence, parameterized queries.
- Req 7 → `base.html`/`index.html`/`style.css`, viewport + responsive CSS.
- Req 8 → env-based `SECRET_KEY`/`DATABASE_PATH`, temp DB in tests.
- Req 9 → error handlers (404/405/500), POST for mutations, GET for views.
- Req 10 → `test_app.py` pytest suite with temp-DB fixture.
