# Eddy SAT Agent

A FastAPI-based SAT practice and tutoring app that serves a static frontend and exposes API endpoints for authentication, questions, progress tracking, and tutoring chat.

## Features

- FastAPI backend with SQLite persistence
- User registration, login, and session handling
- Question bank endpoint for SAT practice questions
- Progress save/load for authenticated users
- Chat tutoring via local fallback, OpenAI, or Codex integration
- Static web frontend served from `public/`
- Environment-based configuration using `.env`

## Prerequisites

- Python 3.12 or newer
- `uv` launcher installed
- `pip` available for dependency installation

## Install

From the project root:

```bash
cd /Users/allenwang/dev/eddy-sat-agent
python3 -m pip install fastapi==0.115.6 "uvicorn[standard]==0.34.0" python-dotenv==1.0.1
```

If you use a virtual environment, activate it before installing.

## Run

Start the app with the project helper script:

```bash
./start.sh
```

If the default port `3000` is already in use, set a different port:

```bash
PORT=3001 ./start.sh
```

You can also override the host and port with environment variables:

```bash
HOST=0.0.0.0 PORT=3000 ./start.sh
```

The server runs the FastAPI app defined in `app.py` and serves the frontend from `public/`.

## Environment Variables

The project loads `.env` values if present. Key settings include:

- `HOST` - bind host (default `127.0.0.1`)
- `PORT` - bind port (default `3000`)
- `OPENAI_API_KEY` - OpenAI API key for the tutoring endpoint
- `OPENAI_MODEL` - OpenAI model to use (default `gpt-4.1-mini`)
- `CODEX_CLIENT_ID` - Codex client ID
- `CODEX_REDIRECT_URI` - Codex OAuth redirect URI
- `CODEX_BASE_URL` - Codex backend URL
- `CODEX_MODEL` - Codex model identifier

## API Endpoints

- `GET /api/questions` - retrieve available practice questions
- `GET /api/auth/me` - get current authenticated user info
- `GET /api/auth/openai-status` - check availability of OpenAI/chat model status
- `GET /api/auth/codex/start` - start Codex OAuth for authenticated users
- `POST /api/auth/register` - register a new user
- `POST /api/auth/login` - login existing user
- `POST /api/auth/logout` - logout user
- `POST /api/auth/codex/logout` - disconnect Codex auth
- `GET /api/progress` - load saved progress for authenticated user
- `POST /api/progress` - save progress for authenticated user
- `POST /api/chat` - send a tutoring/chat request

## Project structure

- `app.py` - FastAPI application and route definitions
- `backend/` - backend modules, authentication, OAuth, progress, questions, tutoring, repository and config
- `public/` - static frontend assets
- `data/` - runtime and seed data storage
- `docs/` - project documentation and architecture notes

## Documentation

See `docs/architecture.md` and `docs/authentication.md` for additional design and auth details.

## Notes

- The app uses `backend.repositories.sqlite_repositories.init_database()` at startup to initialize storage.
- Static site content is served from `public/` by the FastAPI app.
- If `uv` is not installed, install it from https://docs.astral.sh/uv/.
