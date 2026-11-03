# Technology Stack

## Language

- **Python 3** (target Python 3.11 or newer).
- Follow **PEP 8** style conventions throughout the codebase.
- Use **type hints** on function signatures and public interfaces where they add
  clarity.
- Prefer clear, descriptive function and variable names over abbreviations.

## Web Framework

- **Flask** is the web framework.
- Use the **application factory pattern** (`create_app()`) so configuration can
  vary between development, testing, and production.
- Organize routes using **Blueprints** to keep the app modular.

## Templating

- **Jinja2** (Flask's built-in templating engine) for all HTML rendering.
- Keep templates free of business logic; pass prepared data from view functions.
- Use template inheritance (a shared `base.html`) to avoid duplication.

## Persistence

- **SQLite** for persistent storage.
- Access the database through Python's standard library `sqlite3` module (or a
  thin helper layer), with parameterized queries to prevent SQL injection.
- The database file path must be configurable (see Configuration below) so tests
  can use a separate/temporary database.

## Testing

- **pytest** for unit and integration tests.
- Tests must cover application behavior: route responses, task CRUD operations,
  and error handling.
- Tests must run against an isolated test database — never the development or
  production database.
- Use Flask's test client for exercising routes.

## Configuration

- Use **environment variables** for configuration where appropriate. Examples:
  - `FLASK_SECRET_KEY` — session/signing secret.
  - `DATABASE_PATH` — location of the SQLite database file.
  - `FLASK_ENV` / `FLASK_DEBUG` — environment and debug settings.
- Provide sensible defaults for local development, but **never hardcode
  secrets** in source code or commit them to version control.
- Sensitive values come from the environment only.

## Error Handling

- Validate and sanitize all user input.
- Handle expected failure cases explicitly (missing records, invalid form data,
  database errors) and return meaningful responses.
- Register handlers for common HTTP errors (e.g. 404, 500) rendered through
  Jinja2 templates.

## Common Commands

> These are the intended commands once the application is implemented.

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
python run.py

# Run the test suite
pytest
```

## Dependencies

- Pin dependencies in `requirements.txt`.
- Keep the dependency set minimal: Flask, pytest, and only what is strictly
  needed.
