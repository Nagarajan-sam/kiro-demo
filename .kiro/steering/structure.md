# Project Structure

## Directory Layout

```
kiro-demo/
├── app/                      # Application package (all app logic lives here)
│   ├── __init__.py           # Application factory: create_app()
│   ├── routes.py             # View functions / Blueprint(s)
│   ├── db.py                 # Database connection + query helpers (SQLite)
│   ├── models.py             # Data access for tasks (CRUD functions)
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html         # Shared layout (template inheritance)
│   │   └── index.html        # Task list page
│   └── static/               # Static assets
│       └── style.css         # Stylesheet
├── tests/                    # Test suite (kept separate from app code)
│   ├── conftest.py           # Shared pytest fixtures (app, client, test DB)
│   ├── test_routes.py        # Tests for HTTP routes / views
│   └── test_models.py        # Tests for task data-access functions
├── .kiro/                    # Kiro configuration
│   ├── steering/             # Steering files (product, tech, structure)
│   ├── specs/                # Spec-mode feature documents
│   └── hooks/                # Agent hooks
├── run.py                    # Dev entry point (calls create_app and runs it)
├── requirements.txt          # Pinned dependencies
├── .gitignore                # Ignore venv, __pycache__, *.db, .env, etc.
└── README.md                 # Setup and usage instructions
```

## Separation of Concerns

- **Application logic** lives in the `app/` package only.
- **HTML templates** live in `app/templates/` and contain presentation markup
  only — no business logic.
- **Static assets** (CSS, JS, images) live in `app/static/`.
- **Tests** live in the top-level `tests/` directory, completely separate from
  application code. No test code belongs inside `app/`, and no application code
  belongs inside `tests/`.

### Layer responsibilities

| Layer        | File(s)              | Responsibility                                   |
|--------------|----------------------|--------------------------------------------------|
| Factory      | `app/__init__.py`    | Build and configure the Flask app                |
| Routing      | `app/routes.py`      | Map URLs to view functions; handle requests      |
| Data access  | `app/models.py`      | Task CRUD operations                             |
| Database     | `app/db.py`          | Open/close connections, run queries, schema init |
| Presentation | `app/templates/`     | Render HTML via Jinja2                            |

## Naming Conventions

- **Modules & packages:** lowercase `snake_case` (e.g. `routes.py`, `db.py`).
- **Functions & variables:** `snake_case` (e.g. `create_task`, `get_all_tasks`).
- **Classes:** `PascalCase` (e.g. `Config`, `Task`).
- **Constants:** `UPPER_SNAKE_CASE` (e.g. `DATABASE_PATH`, `DEFAULT_LIMIT`).
- **Templates:** lowercase with `.html` (e.g. `index.html`, `base.html`).
- **Tests:** files prefixed with `test_`; test functions prefixed with `test_`
  (required by pytest discovery).

## Import Conventions

- Use **absolute imports** rooted at the `app` package
  (e.g. `from app.models import create_task`), not relative imports, for
  clarity and easier refactoring.
- Group imports in three ordered blocks, separated by blank lines:
  1. Standard library
  2. Third-party packages
  3. Local application (`app.*`) imports
- Avoid wildcard imports (`from module import *`).
- Keep import side effects out of module top level where possible; do setup
  inside `create_app()`.

## General Conventions

- Follow **PEP 8**; keep lines readable (aim for ≤ 88 characters).
- Add **type hints** to function signatures where they improve clarity.
- Handle errors explicitly rather than letting exceptions surface raw.
- Never hardcode secrets — read them from environment variables.
- Every new behavior should have a corresponding test in `tests/`.
