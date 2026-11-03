"""Unit tests for the Task Manager application.

Each test runs against a FRESH temporary SQLite database so tests are isolated
from one another and never touch the development/production database. Only the
standard library (``tempfile``, ``os``) and Flask's test client are used.

Run with:  python -m pytest -q
"""

from __future__ import annotations

import os
import tempfile

import pytest

from app import create_app, get_all_tasks


@pytest.fixture()
def app_client():
    """Yield (app, client) backed by a fresh temporary database per test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    app = create_app({"TESTING": True, "DATABASE_PATH": db_path})
    client = app.test_client()
    try:
        yield app, client
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


@pytest.fixture()
def client(app_client):
    """Convenience fixture exposing just the test client."""
    _, test_client = app_client
    return test_client


def _tasks(app):
    """Return all tasks within an application context."""
    with app.app_context():
        return get_all_tasks()


# ---------------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------------
def test_home_page_empty(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"No tasks yet" in response.data


# ---------------------------------------------------------------------------
# Task creation
# ---------------------------------------------------------------------------
def test_create_task(app_client):
    app, client = app_client
    response = client.post("/add", data={"title": "Buy milk"})
    assert response.status_code == 302  # redirect to index

    tasks = _tasks(app)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy milk"
    assert tasks[0]["completed"] == 0

    # It is rendered on the home page.
    page = client.get("/")
    assert b"Buy milk" in page.data


def test_create_task_without_description(app_client):
    app, client = app_client
    response = client.post("/add", data={"title": "No description task"})
    assert response.status_code == 302

    tasks = _tasks(app)
    assert len(tasks) == 1
    assert tasks[0]["description"] == ""


def test_create_task_with_description(app_client):
    app, client = app_client
    client.post(
        "/add",
        data={"title": "Write report", "description": "Due Friday"},
    )
    tasks = _tasks(app)
    assert tasks[0]["description"] == "Due Friday"


# ---------------------------------------------------------------------------
# Invalid input (empty / whitespace titles)
# ---------------------------------------------------------------------------
def test_empty_title_rejected(app_client):
    app, client = app_client
    response = client.post("/add", data={"title": ""})
    assert response.status_code == 400
    assert _tasks(app) == []


def test_whitespace_title_rejected(app_client):
    app, client = app_client
    response = client.post("/add", data={"title": "   "})
    assert response.status_code == 400
    assert _tasks(app) == []


# ---------------------------------------------------------------------------
# Task completion
# ---------------------------------------------------------------------------
def test_complete_task(app_client):
    app, client = app_client
    client.post("/add", data={"title": "Finish me"})
    task_id = _tasks(app)[0]["id"]

    response = client.post(f"/complete/{task_id}")
    assert response.status_code == 302
    assert _tasks(app)[0]["completed"] == 1


def test_complete_missing_task_404(client):
    response = client.post("/complete/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Task deletion
# ---------------------------------------------------------------------------
def test_delete_task(app_client):
    app, client = app_client
    client.post("/add", data={"title": "Remove me"})
    task_id = _tasks(app)[0]["id"]

    response = client.post(f"/delete/{task_id}")
    assert response.status_code == 302
    assert _tasks(app) == []


def test_delete_missing_task_404(client):
    response = client.post("/delete/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Error handling: unknown URL + wrong HTTP method
# ---------------------------------------------------------------------------
def test_unknown_url_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404


def test_wrong_method_405(client):
    # /add only accepts POST; a GET should be 405 Method Not Allowed.
    response = client.get("/add")
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# Database isolation: the default development DB must not be created/used.
# ---------------------------------------------------------------------------
def test_dev_db_untouched(app_client):
    app, client = app_client
    # The app under test must be pointed at a temp DB, not the default.
    assert app.config["DATABASE_PATH"] != "tasks.db"
    client.post("/add", data={"title": "Temp-only task"})
    # Writing a task must not create the default development database file.
    assert not os.path.exists("tasks.db")
