# Task Manager

A simple task management web application built with **Python** and **Flask**.
Add tasks, view them, mark them complete, and delete them. Tasks are stored in a
**SQLite** database and pages are rendered with **Jinja2**.

## Features

- Add a task with a title and optional description
- View all tasks on a single, responsive page
- Mark a task as completed
- Delete a task
- Input validation (empty/whitespace-only titles are rejected)
- Persistent storage in SQLite
- Friendly error pages (404 / 405 / 500)

## Project structure

```
.
├── app.py                 # Flask app, routes, and SQLite persistence
├── templates/
│   ├── base.html          # Shared layout (responsive, viewport meta)
│   ├── index.html         # Main UI: add form + task list
│   └── error.html         # Error page (404/405/500)
├── static/
│   └── style.css          # Responsive styling
├── test_app.py            # pytest test suite (isolated temp database)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Requirements

- Python 3.11 or newer
- The dependencies in `requirements.txt` (Flask, pytest)

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Configuration

Configuration is read from environment variables. Sensible defaults are provided
for local development, and **no secrets are hardcoded**.

| Variable           | Purpose                                   | Default            |
| ------------------ | ----------------------------------------- | ------------------ |
| `FLASK_SECRET_KEY` | Session/signing secret (set in production)| `dev-only` value   |
| `DATABASE_PATH`    | Path to the SQLite database file          | `tasks.db`         |
| `FLASK_DEBUG`      | Set to `1` to enable debug mode           | `0` (off)          |

> In production, always set a strong `FLASK_SECRET_KEY`. The built-in default is
> for local development only and must not be used in production.

Example:

```bash
export FLASK_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export DATABASE_PATH="tasks.db"
```

## Running the application

```bash
python app.py
```

Then open <http://127.0.0.1:5000> in your browser.

## Running the tests

```bash
python -m pytest -q
```

The test suite creates a **fresh temporary SQLite database for each test**, so
it is fully isolated and never touches your development/production database. It
covers the home page, task creation (with and without a description), invalid
input (empty and whitespace-only titles), task completion, task deletion, and
error handling (404 for unknown URLs and missing tasks, 405 for wrong HTTP
methods).
