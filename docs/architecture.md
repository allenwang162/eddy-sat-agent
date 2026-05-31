# Eddy SAT Agent Architecture

## Project layout

```text
.
├── docs/                 Documentation and screenshots
├── public/               Browser app assets
│   ├── assets/           Images and static media
│   ├── app.js            Frontend state and UI behavior
│   ├── index.html        App shell
│   └── styles.css        Theme and responsive layout
├── scripts/              Local utility scripts
├── backend/
│   ├── config/           Environment and path configuration
│   ├── db/               Target database schema/migrations
│   ├── modules/          Business domains
│   ├── repositories/     Data access adapters
│   └── shared/           Cross-cutting utilities
├── data/
│   ├── seed/             Versionable app seed data
│   └── runtime/          Local/private runtime state, ignored by git
├── app.py                FastAPI app and API controller
├── pyproject.toml        uv project dependencies
├── uv.lock               Resolved dependency lockfile
├── .python-version       Local Python version pin
├── .env.example          Local environment template
└── start.sh              Local start helper
```

## Data boundaries

- `data/seed/questionBank.json` is versionable SAT-style seed content.
- `data/seed/extracted-sat-practice-test-4.json` is local extracted PDF text for development.
- `data/runtime/eddy.db` stores local users, sessions, encrypted per-user Codex tokens, question-bank imports, and per-user progress.

For production, replace the local SQLite adapter with Postgres. Keep `data/seed/` as import/bootstrap content.

## Service-oriented backend

The backend is organized by domain module:

- `backend/modules/auth`: account registration, login, logout, session lookup
- `backend/modules/oauth`: ChatGPT/Codex OAuth and encrypted token storage
- `backend/modules/tutoring`: Ask Eddy LLM orchestration and fallback tutor hints
- `backend/modules/progress`: attempt history and concept stats
- `backend/modules/questions`: question-bank reads

The FastAPI app in `app.py` handles HTTP routing and delegates business behavior to service modules. Repositories hide storage details, so `backend/repositories/sqlite_repositories.py` can be replaced with a Postgres repository without rewriting the UI or business services.

## Database target

`backend/db/schema.sql` describes the intended Postgres schema for:

- users and sessions
- encrypted OAuth tokens
- question bank items
- exam bundles
- attempts and attempt answers

The current runtime uses SQLite through the repository layer. The code now has the boundaries needed to swap in Postgres cleanly.

## Deployment notes

- Set `AUTH_SECRET` in every deployed environment.
- Use HTTPS in production so session cookies and OAuth redirects are protected.
- Install uv from https://docs.astral.sh/uv/ if it is not already on your machine.
- Install and sync dependencies with `uv sync`.
- Run locally with `./start.sh` or `uv run uvicorn app:app --host 127.0.0.1 --port 3000`.
- Prefer Render, Railway, or Fly.io for the current Python server.
- Move runtime storage to Postgres/Redis before real student use.
