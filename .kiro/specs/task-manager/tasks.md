# Implementation Plan — Task Manager

> Execute tasks in order. After implementing functionality, run
> `python -m pytest -q`, investigate and fix any failures, and do not mark a
> task complete until its acceptance criteria are verified. Follow the project
> steering files (PEP 8, type hints, env-based config, parameterized SQL, no
> hardcoded secrets).

- [ ] 1. Scaffold project files and dependencies
  - Create `requirements.txt` with pinned `Flask` and `pytest`.
  - Create `.gitignore` (`.venv/`, `__pycache__/`, `*.db`, `.env`).
  - Create empty `templates/` and `static/` directories (placeholder as needed).
  - _Requirements: 6, 8_

- [ ] 2. Implement the database layer in `app.py`
  - Add `get_db`, `close_db`, and `init_db` (create `tasks` table if absent) using
    `sqlite3` with `row_factory = sqlite3.Row`.
  - Register `close_db` on app teardown.
  - Use the `DATABASE_PATH` config value for the connection.
  - _Requirements: 6.1, 6.2, 6.4_

- [ ] 3. Implement task data-access functions in `app.py`
  - Add `get_all_tasks`, `get_task`, `create_task`, `complete_task`,
    `delete_task`, all using parameterized queries and type hints.
  - `create_task` defaults `completed` to 0 and `description` to `''`.
  - _Requirements: 2.2, 2.3, 2.4, 4.1, 5.1, 6.4_

- [ ] 4. Implement the application factory and configuration
  - Implement `create_app(config=None)` reading `FLASK_SECRET_KEY` and
    `DATABASE_PATH` from the environment with safe local defaults (no hardcoded
    real secret), and accepting a config override for tests.
  - Call `init_db()` during app setup.
  - Add module-level `app = create_app()` and a `__main__` guard to run the dev
    server with `python app.py`.
  - _Requirements: 6.1, 8.1, 8.2_

- [ ] 5. Implement the home route and task-list rendering
  - Add `GET /` (`index`) that loads all tasks and renders `index.html`.
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 6. Implement add-task route with input validation
  - Add `POST /add` (`add`): trim title; reject empty/whitespace-only title
    without persisting (400 or redirect with flashed message); otherwise create
    the task and redirect (302) to `/`.
  - _Requirements: 2.1, 2.5, 3.1, 3.2, 3.3_

- [ ] 7. Implement complete and delete routes
  - Add `POST /complete/<int:task_id>` (`complete`): mark complete, redirect
    (302); `abort(404)` when the task does not exist.
  - Add `POST /delete/<int:task_id>` (`delete`): delete, redirect (302);
    `abort(404)` when the task does not exist.
  - _Requirements: 4.1, 4.3, 5.1, 5.3_

- [ ] 8. Implement error handlers
  - Register 404, 405, and 500 handlers returning appropriate responses without
    leaking internal details.
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 9. Build the Jinja2 templates
  - Create `templates/base.html` (viewport meta, link to `static/style.css`,
    content block) and `templates/index.html` (add-task form, flash area, task
    list with per-task complete/delete POST forms, empty state, completed styling).
  - Ensure user text is autoescaped.
  - _Requirements: 1.2, 1.3, 1.4, 3.4, 7.1, 7.3_

- [ ] 10. Add responsive styling
  - Create `static/style.css` with a fluid container, readable spacing, and a
    clear visual treatment for completed tasks.
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 11. Write the pytest suite in `test_app.py`
  - Add a fixture that creates a FRESH temporary SQLite DB per test and builds
    the app via `create_app({"TESTING": True, "DATABASE_PATH": <temp>})`, yields
    a test client, and removes the temp DB afterward. Use only `tempfile`/`os`
    from the standard library (keep it beginner-simple).
  - Database isolation: confirm each test starts from a clean state, and that
    the default development DB is never created/read/modified by the tests.
  - Empty-title tests: assert empty title (`""`) and whitespace-only title
    (`"   "`) are rejected and not persisted; assert a valid title with no
    description IS created.
  - Error-handling tests: unknown URL → 404; complete/delete of a missing id →
    404 (no data changed); wrong HTTP method on a state-changing route → 405.
  - Core tests: home page (empty state), task creation, task completion, task
    deletion.
  - _Requirements: 10.1–10.14, 8.3_

- [ ] 12. Run tests, verify, and finalize
  - Run `python -m pytest -q`; investigate and fix any failures (fix root causes,
    not tests) until the suite exits 0.
  - Confirm each requirement's acceptance criteria are met.
  - _Requirements: 10.4, plus verification of all above_

- [ ] 13. Write `README.md`
  - Document setup (venv, `pip install -r requirements.txt`), required/optional
    environment variables (`FLASK_SECRET_KEY`, `DATABASE_PATH`), how to run
    (`python app.py`), and how to test (`python -m pytest -q`).
  - _Requirements: (project structure item 3.5), 8_
