# Product: Task Manager

## Overview

Task Manager is a lightweight web application for creating, tracking, and
organizing day-to-day tasks. It provides a simple, server-rendered interface
where users can capture work items, mark them complete, and remove them when
they are no longer needed. The goal is a focused, no-friction tool that does the
essentials well rather than an all-in-one project management suite.

## Intended Users

- **Individuals** who want a simple personal to-do list to track daily work.
- **Small teams or students** who need a shared, self-hosted task list without
  the overhead of a commercial SaaS product.
- **Developers** learning Flask who want a clean, well-structured reference
  application to build on.

## Core Features

- **Create tasks** — add a task with a title and optional description.
- **View tasks** — see all tasks in a single list, showing status at a glance.
- **Update tasks** — edit a task's title/description and toggle it between
  "open" and "completed".
- **Delete tasks** — remove tasks that are no longer relevant.
- **Persistent storage** — tasks are saved so they survive application
  restarts.

## Future / Out of Scope (for now)

The following are explicitly **not** part of the initial scope but may be
considered later:

- User accounts and authentication.
- Due dates, reminders, and notifications.
- Task categories, tags, or priorities.
- A REST/JSON API for external clients.

## Product Principles

- **Simplicity first** — keep the UI and data model minimal and understandable.
- **Reliability** — user data must never be silently lost; errors are handled
  gracefully and surfaced clearly.
- **Maintainability** — the codebase should be easy for a new contributor to
  read, run, and extend.
