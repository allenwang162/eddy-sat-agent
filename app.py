from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import env
from backend.modules.auth.service import (
    get_session,
    login_user,
    logout_user,
    public_user,
    register_user,
    session_cookie,
)
from backend.modules.oauth.service import create_codex_authorize_url, read_user_codex_auth, write_user_codex_auth
from backend.modules.progress.service import get_progress_for_user, save_progress_for_user
from backend.modules.questions.service import list_questions
from backend.modules.tutoring.service import codex_tutor_reply, local_tutor_reply, openai_tutor_reply
from backend.repositories.sqlite_repositories import init_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_database()
    yield


app = FastAPI(title="Eddy SAT Agent API", version="0.1.0", lifespan=lifespan)


def session_from_request(request: Request):
    return get_session(request.headers.get("cookie"))


def require_session(request: Request):
    session = session_from_request(request)
    if not session["user"]:
        raise HTTPException(status_code=401, detail="Sign in required")
    return session


def codex_connected(user):
    return read_user_codex_auth(user["id"]) is not None if user else False


@app.get("/api/questions")
def api_questions():
    return {"questions": list_questions()}


@app.get("/api/auth/me")
def api_auth_me(request: Request):
    session = session_from_request(request)
    return {
        "user": public_user(session["user"]),
        "codexConnected": codex_connected(session["user"]),
    }


@app.get("/api/auth/openai-status")
def api_openai_status(request: Request):
    session = session_from_request(request)
    return {
        "chatModelAvailable": bool(env.OPENAI_API_KEY),
        "signedIn": bool(session["user"]),
        "codexConnected": codex_connected(session["user"]),
        "accountSsoAvailable": False,
        "experimentalCodexOauthPossible": True,
        "reason": (
            "OpenAI does not provide a supported generic Sign in with ChatGPT flow for arbitrary standalone "
            "web apps. Some tools use ChatGPT OAuth for the Codex product endpoint, but that is a "
            "Codex-specific path and not the normal public OpenAI API."
        ),
    }


@app.get("/api/auth/codex/start")
def api_codex_start(request: Request):
    session = require_session(request)
    return {
        "authUrl": create_codex_authorize_url(session["user"]["id"]),
        "redirectUri": env.CODEX_REDIRECT_URI,
    }


@app.post("/api/auth/register")
async def api_register(request: Request, response: Response):
    status, body, token = register_user(await request.json())
    response.status_code = status
    if token:
        response.headers.append("set-cookie", session_cookie(token))
    return body


@app.post("/api/auth/login")
async def api_login(request: Request, response: Response):
    status, body, token = login_user(await request.json())
    response.status_code = status
    if token:
        response.headers.append("set-cookie", session_cookie(token))
    return body


@app.post("/api/auth/logout")
def api_logout(request: Request, response: Response):
    session = session_from_request(request)
    if session["user"]:
        write_user_codex_auth(session["user"]["id"], {})
    logout_user(request.headers.get("cookie"))
    response.headers.append("set-cookie", session_cookie("", clear=True))
    return {"ok": True}


@app.post("/api/auth/codex/logout")
def api_codex_logout(request: Request):
    session = require_session(request)
    write_user_codex_auth(session["user"]["id"], {})
    return {"ok": True}


@app.get("/api/progress")
def api_get_progress(request: Request):
    session = require_session(request)
    return {"progress": get_progress_for_user(session["user"])}


@app.post("/api/progress")
async def api_save_progress(request: Request):
    session = require_session(request)
    progress = save_progress_for_user(session["user"], await request.json())
    return {"ok": True, "progress": progress}


@app.post("/api/chat")
async def api_chat(request: Request):
    body = await request.json()
    session = require_session(request)
    try:
        codex_result = codex_tutor_reply(body, session["user"]["id"])
        if codex_result:
            return {
                "reply": codex_result["reply"],
                "mode": "codex",
                "model": codex_result["model"],
            }
        ai_reply = openai_tutor_reply(body)
        return {
            "reply": ai_reply or local_tutor_reply(body),
            "mode": "openai" if ai_reply else "local",
        }
    except Exception as exc:
        return {
            "reply": local_tutor_reply(body),
            "mode": "local",
            "warning": str(exc),
        }


@app.get("/")
def index():
    return FileResponse(env.PUBLIC_DIR / "index.html")


app.mount("/", StaticFiles(directory=env.PUBLIC_DIR, html=True), name="public")
