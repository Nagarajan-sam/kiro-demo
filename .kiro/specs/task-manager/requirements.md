# Requirements — Task Manager

## Introduction

Task Manager is a simple, server-rendered web application built with Python and
Flask. It lets a user capture tasks, see them in a list, mark them complete, and
delete them. Tasks are stored in a SQLite database so they persist across
application restarts. The application renders HTML with Jinja2 and presents a
clean, responsive interface.

This document defines the functional and non-functional requirements. Each
requirement uses the EARS (Easy Approach to Requirements Syntax) format for its
acceptance criteria.

## Requirements

### Requirement 1: View all tasks on the home page

**User Story:** As a user, I want to see all my saved tasks on the home page, so
that I can review what I need to do at a glance.

#### Acceptance Criteria

1. WHEN a user navigates to the home page (`GET /`) THEN the system SHALL
   respond with HTTP 200 and render an HTML page listing all stored tasks.
2. WHEN the home page is rendered THEN the system SHALL display each task's
   title, its optional description, and its completion status.
3. IF there are no tasks stored THEN the system SHALL render the page with a
   clear "no tasks" empty-state message instead of an empty list.
4. WHEN tasks exist THEN the system SHALL visually distinguish completed tasks
   from open tasks.

### Requirement 2: Add a new task

**User Story:** As a user, I want to add a new task with a title and an optional
description, so that I can record something I need to do.

#### Acceptance Criteria

1. WHEN a user submits the add-task form (`POST /add`) with a non-empty title
   THEN the system SHALL create a new task, persist it to SQLite, and respond by
   redirecting (HTTP 302) back to the home page.
2. WHEN a task is created THEN the system SHALL store it as not completed by
   default.
3. WHERE a description is provided THEN the system SHALL store the description
   with the task.
4. WHERE no description is provided THEN the system SHALL create the task with an
   empty/absent description without error.
5. WHEN the newly created task is persisted THEN the home page SHALL display it
   in the task list.

### Requirement 3: Validate user input

**User Story:** As a user, I want the application to reject invalid task input,
so that I do not create meaningless or broken tasks.

#### Acceptance Criteria

1. WHEN a user submits the add-task form with an empty or whitespace-only title
   THEN the system SHALL NOT create a task.
2. WHEN task creation is rejected due to invalid input THEN the system SHALL
   respond with an appropriate status (re-render the form with HTTP 400, or
   redirect back with a visible validation message) and SHALL NOT persist any
   record.
3. WHEN input is rejected THEN the system SHALL inform the user why (validation
   message).
4. WHEN any user-supplied text is stored and later rendered THEN the system SHALL
   ensure it is safely escaped in the HTML output (no injection).

### Requirement 4: Mark a task as completed

**User Story:** As a user, I want to mark a task as completed, so that I can
track my progress.

#### Acceptance Criteria

1. WHEN a user submits the complete action for an existing task
   (`POST /complete/<task_id>`) THEN the system SHALL set that task's status to
   completed, persist the change, and redirect (HTTP 302) to the home page.
2. WHEN a task has been marked completed THEN the home page SHALL render it with
   its completed status.
3. IF the referenced task id does not exist THEN the system SHALL respond with
   HTTP 404 and SHALL NOT alter any data.

### Requirement 5: Delete a task

**User Story:** As a user, I want to delete a task, so that I can remove items I
no longer need.

#### Acceptance Criteria

1. WHEN a user submits the delete action for an existing task
   (`POST /delete/<task_id>`) THEN the system SHALL remove that task from
   storage and redirect (HTTP 302) to the home page.
2. WHEN a task has been deleted THEN the home page SHALL NOT display it.
3. IF the referenced task id does not exist THEN the system SHALL respond with
   HTTP 404 and SHALL NOT alter any data.

### Requirement 6: Persistent storage

**User Story:** As a user, I want my tasks to persist, so that they are still
there after the application restarts.

#### Acceptance Criteria

1. WHEN the application starts AND the database schema does not yet exist THEN
   the system SHALL initialize the SQLite schema automatically.
2. WHEN a task is created, completed, or deleted THEN the system SHALL persist
   the change to the SQLite database.
3. WHEN the application is restarted THEN previously stored tasks SHALL still be
   available.
4. WHEN executing database queries THEN the system SHALL use parameterized
   statements to prevent SQL injection.

### Requirement 7: Clean and responsive interface

**User Story:** As a user, I want a clean interface that works on different
screen sizes, so that the app is pleasant and usable on desktop and mobile.

#### Acceptance Criteria

1. WHEN any page is rendered THEN the system SHALL serve valid, semantic HTML via
   Jinja2 templates.
2. WHEN the page is viewed on narrow (mobile) or wide (desktop) viewports THEN
   the layout SHALL remain usable and readable (responsive).
3. WHEN the page is rendered THEN it SHALL include a meta viewport tag and basic
   responsive styling.

### Requirement 8: Configuration and secrets

**User Story:** As an operator, I want configuration to come from the
environment, so that secrets are never hardcoded in source.

#### Acceptance Criteria

1. WHERE a secret key is required THEN the system SHALL read it from an
   environment variable (e.g. `FLASK_SECRET_KEY`) and SHALL NOT hardcode a
   secret in source.
2. WHERE the database file path is configurable THEN the system SHALL read it
   from an environment variable (e.g. `DATABASE_PATH`) with a sensible local
   default.
3. WHEN running tests THEN the system SHALL use a separate temporary database and
   SHALL NOT read or write the development/production database.

### Requirement 9: Error handling and HTTP correctness

**User Story:** As a user, I want the app to behave predictably on errors, so
that failures are clear rather than confusing.

#### Acceptance Criteria

1. WHEN a request targets a non-existent route or resource THEN the system SHALL
   respond with HTTP 404.
2. WHEN an action route is requested with an unsupported HTTP method THEN the
   system SHALL respond with HTTP 405.
3. WHEN an unexpected server error occurs THEN the system SHALL respond with
   HTTP 500 and SHALL NOT leak sensitive internal details to the user.
4. WHEN state-changing actions (add, complete, delete) are performed THEN the
   system SHALL use the POST method, and read-only views SHALL use GET.

### Requirement 10: Automated tests

**User Story:** As a developer, I want automated tests covering the core
behavior, so that regressions are caught early.

#### Acceptance Criteria

1. WHEN the test suite runs THEN it SHALL use pytest and run against a separate
   temporary SQLite database.
2. WHEN the test suite runs THEN it SHALL include tests for: the home page,
   task creation, task completion, task deletion, and invalid input.
3. WHEN tests complete THEN they SHALL NOT have read from or written to the
   development/production database.
4. WHEN `python -m pytest -q` is executed THEN a passing suite SHALL exit with
   status 0, and a failing suite SHALL exit non-zero.

##### Empty task title tests

5. WHEN a test submits the add-task form with an empty title (`""`) THEN the
   test SHALL assert that no task is created AND that the response status is the
   expected validation status (e.g. 400 or a redirect with a visible message).
6. WHEN a test submits the add-task form with a whitespace-only title (e.g.
   `"   "`) THEN the test SHALL assert that no task is created (whitespace is
   trimmed and treated as empty).
7. WHEN a test submits a valid title with NO description THEN the test SHALL
   assert the task is created successfully (confirming the description is
   optional, not that empty titles are allowed).

##### Database isolation tests

8. WHEN the test suite sets up THEN it SHALL create a fresh temporary SQLite
   database for the tests (e.g. using a temp file) and point the application at
   it via the `DATABASE_PATH` configuration override — never the default
   development database path.
9. WHEN each test runs THEN it SHALL start from a known database state so that
   one test does not depend on data left behind by another test.
10. WHEN the test suite finishes THEN it SHALL remove the temporary database
    file it created, leaving no test data behind.
11. WHEN the test suite runs THEN the application's default/development database
    file SHALL remain untouched (not created, read, or modified by the tests).

##### Error-handling tests

12. WHEN a test requests a URL that does not exist THEN the test SHALL assert the
    response status is 404.
13. WHEN a test sends a completion or deletion action for a task id that does not
    exist THEN the test SHALL assert the response status is 404 and that no data
    is changed.
14. WHEN a test sends a state-changing route using the wrong HTTP method (e.g.
    `GET` on an add/complete/delete route) THEN the test SHALL assert the
    response status is 405.
