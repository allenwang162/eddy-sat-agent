# Authentication Plan

The standalone SAT app cannot honestly implement "Sign in with ChatGPT" as a normal supported social-login button because OpenAI does not currently expose a public OAuth/OIDC login product for arbitrary third-party web apps.

There is an important nuance: tools such as Hermes Agent and OpenAI Codex CLI can use ChatGPT/OpenAI OAuth for the **Codex** product path. Hermes calls this provider `openai-codex`; it stores ChatGPT OAuth tokens locally and sends requests to the Codex backend rather than to the ordinary public OpenAI API. This can let a local developer tool use a user's ChatGPT/Codex entitlement, but it is not the same as a supported, general-purpose "Login with ChatGPT" integration for a family SAT web app.

The correct production shape is:

1. Authenticate students with an app-owned provider such as Auth0, Clerk, Firebase Auth, Cognito, or a school Google/Microsoft login.
2. Store student progress under the app user ID.
3. Call OpenAI from the server with `OPENAI_API_KEY` for tutoring, question analysis, and question-bank generation.
4. If this later becomes a ChatGPT App or GPT Action, use ChatGPT's OAuth support in the opposite direction: ChatGPT can authenticate to this SAT app's API.

Experimental option:

- A local-only Codex OAuth provider could be built by following the Codex-style OAuth flow and storing tokens per user.
- This should be treated as experimental and Codex-specific, with possible entitlement limits, token refresh complexity, and breakage if the Codex backend changes.
- It should not be used as a production auth basis for minors without careful privacy, consent, and terms review.

Current prototype behavior:

- The login panel creates or signs into an Eddy account using server-side password hashing.
- Sessions are stored in an HTTP-only `eddy_session` cookie.
- `/api/auth/openai-status` reports whether server-side OpenAI tutoring or per-user Codex tutoring is configured.
- `/api/chat` uses the signed-in user's encrypted Codex token when present, then `OPENAI_API_KEY` when present, then local SAT hints.

Implemented experimental Codex path:

- `/api/auth/codex/start` creates a PKCE challenge and returns an OpenAI authorization URL.
- The OAuth redirect target is `http://localhost:1455/auth/callback`, matching the Codex-style local callback pattern.
- The server stores the resulting token data encrypted inside the signed-in user's record.
- `/api/chat` tries the Codex backend first when a Codex token exists, then falls back to OpenAI API key mode, then local hints.
- The server discovers available Codex models from `/models?client_version=...` and chooses an available non-review model automatically unless `CODEX_MODEL` is set.

Updated per-user storage:

- User records and sessions live in `data/runtime/eddy.db` for this prototype.
- Passwords are hashed with PBKDF2-SHA256 and per-user salts.
- Codex OAuth token records are encrypted at rest by the Python prototype using an authenticated HMAC-derived stream construction from `AUTH_SECRET`.
- Set `AUTH_SECRET` in production. Changing `AUTH_SECRET` invalidates encrypted Codex token records.
- For production, replace local SQLite with Postgres and store sessions in Redis or a database table.

Operational notes:

- This is local-only. Do not deploy this token storage design to the public internet.
- For production token storage, use a vetted encryption library or managed KMS instead of the current standard-library-only prototype encryption.
- Local SQLite is acceptable for a private prototype but should not be the long-term production store for multiple students.
- Each deployed environment must use HTTPS and a strong `AUTH_SECRET`.
- The Codex model name and backend behavior may change; set `CODEX_MODEL` or `CODEX_BASE_URL` if the provider changes.
- If the Codex endpoint rejects the request, tutor chat will still fall back to the supported API-key path or local hints.
