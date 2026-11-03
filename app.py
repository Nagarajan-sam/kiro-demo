"""Task Manager — a simple Flask web application.

A single-module Flask app that lets a user add, view, complete, and delete
tasks, persisting them in a SQLite database. HTML is rendered with Jinja2.

Configuration comes from environment variables (no hardcoded secrets):
    FLASK_SECRET_KEY  session/signing secret (required in production)
    DATABASE_PATH     path to the SQLite database file (default: tasks.db)

Run the development server with:  python app.py
Run the tests with:               python -m pytest -q
"""

from __future__ import annotations

import os
import sqlite3
from datetime import UTC, datetime

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

# Default SQLite file used for local development when DATABASE_PATH is unset.
DEFAULT_DATABASE_PATH = "tasks.db"

# Schema for the single tasks table. Created on startup if it does not exist.
SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    completed   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL
);
"""


# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------
def get_db() -> sqlite3.Connection:
    """Return a SQLite connection for the current request, creating one if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(current_database_path())
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception: BaseException | None = None) -> None:
    """Close the request-scoped database connection, if any."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def current_database_path() -> str:
    """Resolve the database path from app config (falls back to the default)."""
    from flask import current_app

    return current_app.config["DATABASE_PATH"]


def init_db() -> None:
    """Create the tasks table if it does not already exist."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


# ---------------------------------------------------------------------------
# Task data-access functions (all queries are parameterized)
# ---------------------------------------------------------------------------
def get_all_tasks() -> list[sqlite3.Row]:
    """Return all tasks, newest first."""
    db = get_db()
    rows = db.execute(
        "SELECT id, title, description, completed, created_at "
        "FROM tasks ORDER BY created_at DESC, id DESC"
    ).fetchall()
    return list(rows)


def get_task(task_id: int) -> sqlite3.Row | None:
    """Return a single task by id, or None if it does not exist."""
    db = get_db()
    return db.execute(
        "SELECT id, title, description, completed, created_at "
        "FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()


def create_task(title: str, description: str = "") -> int:
    """Insert a new (incomplete) task and return its new id."""
    db = get_db()
    created_at = datetime.now(UTC).isoformat()
    cursor = db.execute(
        "INSERT INTO tasks (title, description, completed, created_at) "
        "VALUES (?, ?, 0, ?)",
        (title, description, created_at),
    )
    db.commit()
    return int(cursor.lastrowid)


def complete_task(task_id: int) -> bool:
    """Mark a task completed. Return True if a row was updated."""
    db = get_db()
    cursor = db.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ?",
        (task_id,),
    )
    db.commit()
    return cursor.rowcount > 0


def delete_task(task_id: int) -> bool:
    """Delete a task. Return True if a row was deleted."""
    db = get_db()
    cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
def create_app(config: dict | None = None) -> Flask:
    """Build and configure the Flask application.

    Args:
        config: Optional overrides (e.g. {"TESTING": True,
            "DATABASE_PATH": "/tmp/test.db"}) merged over the defaults. Tests
            use this to point at an isolated temporary database.
    """
    app = Flask(__name__)

    # Secret key: read from the environment. A non-secret default is used only
    # so local development works out of the box; production MUST set the env var.
    app.config["SECRET_KEY"] = os.environ.get(
        "FLASK_SECRET_KEY", "dev-only-insecure-key"
    )
    app.config["DATABASE_PATH"] = os.environ.get(
        "DATABASE_PATH", DEFAULT_DATABASE_PATH
    )

    if config:
        app.config.update(config)

    # Close the DB connection at the end of every request.
    app.teardown_appcontext(close_db)

    _register_routes(app)
    _register_error_handlers(app)

    # Ensure the schema exists before the first request is served.
    with app.app_context():
        init_db()

    return app


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
def _register_routes(app: Flask) -> None:
    @app.route("/", methods=["GET"])
    def index() -> str:
        """Render the home page listing all tasks."""
        tasks = get_all_tasks()
        return render_template("index.html", tasks=tasks)

    @app.route("/add", methods=["POST"])
    def add():
        """Create a new task after validating the title."""
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()

        if not title:
            # Invalid input: do not persist. Surface a message and return 400.
            flash("Task title is required.")
            tasks = get_all_tasks()
            return render_template("index.html", tasks=tasks), 400

        create_task(title, description)
        return redirect(url_for("index"))

    @app.route("/complete/<int:task_id>", methods=["POST"])
    def complete(task_id: int):
        """Mark an existing task completed, or 404 if it does not exist."""
        if get_task(task_id) is None:
            abort(404)
        complete_task(task_id)
        return redirect(url_for("index"))

    @app.route("/delete/<int:task_id>", methods=["POST"])
    def delete(task_id: int):
        """Delete an existing task, or 404 if it does not exist."""
        if get_task(task_id) is None:
            abort(404)
        delete_task(task_id)
        return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Error handlers (do not leak internal details)
# ---------------------------------------------------------------------------
def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            render_template("error.html", code=405, message="Method not allowed"),
            405,
        )

    @app.errorhandler(500)
    def server_error(error):
        return (
            render_template(
                "error.html", code=500, message="Something went wrong"
            ),
            500,
        )


# Module-level app so `flask run` / `python app.py` work out of the box.
app = create_app()


if __name__ == "__main__":
    # Debug is controlled via the environment; defaults to off.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
