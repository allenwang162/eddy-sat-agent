# Next.js + FastAPI Architecture

This project now uses a split architecture:

- `ui/`: Next.js UI.
- `apis/app.py` and `apis/`: FastAPI APIs, auth, scoring, tutoring, PDF import, logging, and persistence.

## Local Development

Run FastAPI on the API port:

```bash
AUTH_SECRET=local-dev-secret-change-me PORT=8000 ./start-apis.sh
```

`start-apis.sh` defaults `UI_ORIGIN=http://127.0.0.1:3000`, which is where OAuth callback flows return after the APIs store the token. FastAPI is API-only; it does not serve the UI.

Run Next.js on the UI port:

```bash
cd ui
npm install
FASTAPI_BASE_URL=http://127.0.0.1:8000 npm run dev
```

If npm is not available globally in this Codex environment, the repository can use the locally bootstrapped npm in `.tools/npm` through:

```bash
FASTAPI_BASE_URL=http://127.0.0.1:8000 ./start-ui.sh
```

Open:

```text
http://127.0.0.1:3000
```

Next.js proxies `/api/*` to FastAPI through `ui/next.config.mjs`.

## Frontend Notes

Next.js owns the browser app:

- `ui/app/page.jsx` renders the current app shell.
- `ui/app/globals.css` contains the current styles.
- `ui/components/EddyApp.jsx` contains the current browser behavior as React state and components.

FastAPI remains API-only from the browser's point of view. Future UI work can split `EddyApp` into smaller focused components and hooks as the product grows.
