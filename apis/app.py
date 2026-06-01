from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI, HTTPException, Request, Response
from apis.config import env
from apis.modules.auth.service import (
    get_session,
    login_user,
    logout_user,
    public_user,
    register_user,
    session_cookie,
)
from apis.modules.oauth.service import create_codex_authorize_url, read_user_codex_auth, write_user_codex_auth
from apis.modules.progress.service import get_progress_for_user, save_progress_for_user
from apis.modules.questions.service import list_questions
from apis.modules.scoring.service import score_practice_attempt
from apis.modules.tutoring.service import codex_tutor_reply, local_tutor_reply, openai_tutor_reply
from apis.repositories.sqlite_repositories import init_database
from apis.shared.observability import configure_logging, get_logger, log_event, request_id_var, user_hash


logger = get_logger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    init_database()
    log_event(logger, "app.startup", host=env.HOST, port=env.PORT, node_env=env.NODE_ENV)
    yield
    log_event(logger, "app.shutdown")


app = FastAPI(title="Eddy SAT Agent API", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    token = request_id_var.set(request_id)
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        path = request.url.path
        if response and path == "/api/questions":
            response.headers["cache-control"] = "no-store"
        if response:
            response.headers["x-request-id"] = request_id
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log_event(
            logger,
            "http.request",
            method=request.method,
            path=path,
            status_code=getattr(response, "status_code", 500),
            duration_ms=duration_ms,
            client_host=request.client.host if request.client else None,
        )
        request_id_var.reset(token)


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
    questions = list_questions()
    log_event(logger, "questions.list", question_count=len(questions))
    return {"questions": questions}


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
    log_event(
        logger,
        "auth.register",
        status_code=status,
        success=status < 400,
        user_hash=user_hash(body.get("user", {}).get("id")),
    )
    return body


@app.post("/api/auth/login")
async def api_login(request: Request, response: Response):
    status, body, token = login_user(await request.json())
    response.status_code = status
    if token:
        response.headers.append("set-cookie", session_cookie(token))
    log_event(
        logger,
        "auth.login",
        status_code=status,
        success=status < 400,
        user_hash=user_hash(body.get("user", {}).get("id")),
    )
    return body


@app.post("/api/auth/logout")
def api_logout(request: Request, response: Response):
    session = session_from_request(request)
    if session["user"]:
        write_user_codex_auth(session["user"]["id"], {})
    logout_user(request.headers.get("cookie"))
    response.headers.append("set-cookie", session_cookie("", clear=True))
    log_event(logger, "auth.logout", user_hash=user_hash(session["user"]["id"] if session["user"] else None))
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
    body = await request.json()
    progress = save_progress_for_user(session["user"], body)
    log_event(
        logger,
        "progress.save",
        user_hash=user_hash(session["user"]["id"]),
        attempt_count=len(body.get("attempts", [])),
        concept_count=len(body.get("conceptStats", {})),
    )
    return {"ok": True, "progress": progress}


@app.post("/api/events")
async def api_events(request: Request):
    session = session_from_request(request)
    body = await request.json()
    log_event(
        logger,
        "client.event",
        user_hash=user_hash(session["user"]["id"] if session["user"] else None),
        event_name=str(body.get("event", "unknown"))[:80],
        properties=body.get("properties", {}),
    )
    return {"ok": True}


@app.post("/api/scoring/score")
async def api_score_attempt(request: Request):
    session = require_session(request)
    scoring = score_practice_attempt(await request.json())
    log_event(
        logger,
        "scoring.score_attempt",
        user_hash=user_hash(session["user"]["id"]),
        practice_test=scoring.get("practiceTest"),
        score_type=scoring.get("scoreType"),
        correct=scoring.get("correct"),
        total=scoring.get("total"),
    )
    return {"scoring": scoring}


@app.post("/api/chat")
async def api_chat(request: Request):
    body = await request.json()
    session = require_session(request)
    try:
        codex_result = codex_tutor_reply(body, session["user"]["id"])
        if codex_result:
            log_event(logger, "tutor.reply", user_hash=user_hash(session["user"]["id"]), mode="codex", model=codex_result["model"])
            return {
                "reply": codex_result["reply"],
                "mode": "codex",
                "model": codex_result["model"],
            }
        ai_reply = openai_tutor_reply(body)
        log_event(logger, "tutor.reply", user_hash=user_hash(session["user"]["id"]), mode="openai" if ai_reply else "local")
        return {
            "reply": ai_reply or local_tutor_reply(body),
            "mode": "openai" if ai_reply else "local",
        }
    except Exception as exc:
        log_event(logger, "tutor.error", user_hash=user_hash(session["user"]["id"]), error=str(exc))
        return {
            "reply": local_tutor_reply(body),
            "mode": "local",
            "warning": str(exc),
        }
