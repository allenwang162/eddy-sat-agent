# Eddy SAT Agent Architecture

## Project layout

```text
.
├── docs/                 Documentation and screenshots
├── ui/                   Next.js browser app
│   ├── app/              App Router pages, layout, and global styles
│   ├── public/           Images, media, and browser assets
│   └── next.config.mjs   API proxy configuration
├── scripts/              Local utility scripts
├── apis/
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
├── start-apis.sh         FastAPI API start helper
└── start-ui.sh           Next.js UI start helper
```

## Data boundaries

- `data/seed/questionBank.json` is versionable SAT-style seed content.
- `data/seed/extracted-sat-practice-test-4.json` is local extracted PDF text for development.
- `data/seed/scoringTables.json` stores versionable official score conversion ranges keyed by practice test.
- `data/runtime/eddy.db` stores local users, sessions, encrypted per-user Codex tokens, question-bank imports, and per-user progress.

For production, replace the local SQLite adapter with Postgres. Keep `data/seed/` as import/bootstrap content.

## Service-oriented APIs

The APIs are organized by domain module:

- `apis/modules/auth`: account registration, login, logout, session lookup
- `apis/modules/oauth`: ChatGPT/Codex OAuth and encrypted token storage
- `apis/modules/tutoring`: Ask Eddy LLM orchestration and fallback tutor hints
- `apis/modules/progress`: attempt history and concept stats
- `apis/modules/questions`: question-bank reads
- `apis/modules/scoring`: raw score totals and official score-range conversion

The FastAPI app in `apis/app.py` handles HTTP routing and delegates business behavior to service modules. Repositories hide storage details, so `apis/repositories/sqlite_repositories.py` can be replaced with a Postgres repository without rewriting the UI or business services.

## Database target

`apis/db/schema.sql` describes the intended Postgres schema for:

- users and sessions
- encrypted OAuth tokens
- question bank items
- exam bundles
- attempts and attempt answers

The current runtime uses SQLite through the repository layer. The code now has the boundaries needed to swap in Postgres cleanly.

## Local development

- Run FastAPI with `AUTH_SECRET=local-dev-secret-change-me PORT=8000 ./start-apis.sh`.
- Run Next.js with `FASTAPI_BASE_URL=http://127.0.0.1:8000 ./start-ui.sh`.
- Open the UI at `http://127.0.0.1:3000`.
- Next.js proxies `/api/*` to FastAPI through `ui/next.config.mjs`.

## Deployment notes

- Set `AUTH_SECRET` in every deployed environment.
- Use HTTPS in production so session cookies and OAuth redirects are protected.
- Install uv from https://docs.astral.sh/uv/ if it is not already on your machine.
- Install and sync dependencies with `uv sync`.
- Deploy FastAPI and Next.js as separate services, or use a platform that supports both.
- Move runtime storage to Postgres/Redis before real student use.
