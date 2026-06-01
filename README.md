# Eddy SAT GOAT

A SAT practice and tutoring app with a Next.js UI and FastAPI APIs.

## Features

- FastAPI APIs with SQLite persistence
- Next.js UI for the student experience
- User registration, login, and session handling
- Question bank endpoint for SAT practice questions
- Progress save/load for authenticated users
- Chat tutoring via local fallback, OpenAI, or Codex integration
- API proxying from Next.js to FastAPI
- Environment-based configuration using `.env`

## Prerequisites

- Python 3.12 or newer
- `uv` launcher installed
- Node.js and npm for the Next.js UI

## Install

From the project root:

```bash
cd /Users/allenwang/dev/eddy-sat-agent
uv sync
cd ui
npm install
```

If npm is not available globally in the Codex desktop environment, use the locally bootstrapped npm helper described below.

## Run Next.js + FastAPI

FastAPI runs as the API service and Next.js runs as the UI.

Start FastAPI APIs on the API port:

```bash
AUTH_SECRET=local-dev-secret-change-me PORT=8000 ./start-apis.sh
```

Install and start the Next.js UI:

```bash
cd ui
npm install
FASTAPI_BASE_URL=http://127.0.0.1:8000 npm run dev
```

In the Codex desktop environment, npm may not be on `PATH`. If `.tools/npm` has been bootstrapped, use the helper from the project root instead:

```bash
FASTAPI_BASE_URL=http://127.0.0.1:8000 ./start-ui.sh
```

Open the app at:

```text
http://127.0.0.1:3000
```

Next.js proxies `/api/*` requests to FastAPI through `ui/next.config.mjs`.

## Environment Variables

The project loads `.env` values if present. Key settings include:

- `HOST` - bind host (default `127.0.0.1`)
- `PORT` - bind port (default `3000`)
- `OPENAI_API_KEY` - OpenAI API key for the tutoring endpoint
- `OPENAI_MODEL` - OpenAI model to use (default `gpt-4.1-mini`)
- `LOG_LEVEL` - application log level (default `INFO`)
- `LOG_FORMAT` - `json` or `text` (default `json`)
- `LOG_FILE` - optional structured log file path (default `data/runtime/logs/app.log`)
- `LOG_USER_HASH_SALT` - salt used to hash user IDs in logs (defaults to `AUTH_SECRET`)
- `UI_ORIGIN` - UI origin for OAuth return links in split Next.js/FastAPI mode
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
- `POST /api/events` - record lightweight client telemetry events
- `POST /api/chat` - send a tutoring/chat request

## Logging and Observability

The app uses structured JSON logging through `apis/shared/observability.py`. Logs include request IDs, HTTP method/path/status/duration, question-bank loads, auth lifecycle events, progress saves, tutor mode selection, and client events such as practice set start/completion.

By default, logs are written to stdout and `data/runtime/logs/app.log`:

```bash
LOG_LEVEL=INFO LOG_FORMAT=json AUTH_SECRET=local-dev-secret-change-me PORT=8000 ./start-apis.sh
```

User IDs are hashed before being written to logs. Avoid logging emails, raw prompts, passwords, session tokens, or access tokens. The JSON format is intentionally friendly to future log shipping into Splunk, OpenSearch, Datadog, or a small internal dashboard.

## Project structure

- `apis/app.py` - FastAPI application and route definitions
- `apis/` - API modules, authentication, OAuth, progress, questions, tutoring, repository and config
- `ui/` - Next.js UI and public assets
- `data/` - runtime and seed data storage
- `docs/` - project documentation and architecture notes

## Question Import Harness

After importing or regenerating exam questions, validate the seed bank before using it in the app:

```bash
python3 scripts/validate_question_bank.py \
  --expect-count total=240 \
  --expect-count Math=108 \
  --expect-count "Reading and Writing=132" \
  --expect-count free-response=28 \
  --warnings-as-errors
```

The harness catches common PDF import/display problems: missing fields, duplicate IDs, empty prompts, multiple-choice items without four choices, free-response items with choice keys, embedded choices trapped in prompts, likely graph/header artifacts, and missing figure images.

## Scoring

Practice Test 5 includes the official paper digital SAT score-range conversion table in `data/seed/scoringTables.json`. The scoring endpoint lives behind the scoring service boundary:

```bash
POST /api/scoring/score
```

The UI sends the active question IDs and answers, and `apis.modules.scoring.service` calculates raw module totals, section score ranges, and a total SAT score range when a full Reading/Writing + Math attempt has a scoring table.

## Documentation

See `docs/architecture.md` and `docs/authentication.md` for additional design and auth details.

## Notes

- The app uses `apis.repositories.sqlite_repositories.init_database()` at startup to initialize storage.
- UI content is served by Next.js from `ui/`; FastAPI is API-only.
- If `uv` is not installed, install it from https://docs.astral.sh/uv/.
