import time
from http import cookies

from backend.config import env
from backend.modules.oauth.service import read_user_codex_auth
from backend.repositories import sqlite_repositories as repo
from backend.shared.security import hash_password, normalize_email, random_url_token, verify_password


def public_user(user):
    if not user:
        return None
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "createdAt": user.get("createdAt"),
    }


def parse_cookie_header(cookie_header: str | None):
    jar = cookies.SimpleCookie()
    if cookie_header:
        jar.load(cookie_header)
    return {key: morsel.value for key, morsel in jar.items()}


def session_cookie(token: str, clear: bool = False):
    max_age = 0 if clear else env.SESSION_MAX_AGE_SECONDS
    secure = "; Secure" if env.NODE_ENV == "production" else ""
    return f"{env.SESSION_COOKIE_NAME}={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age={max_age}{secure}"


def get_session(cookie_header: str | None):
    token = parse_cookie_header(cookie_header).get(env.SESSION_COOKIE_NAME)
    if not token:
        return {"token": None, "user": None}
    session = repo.find_session(token)
    if not session or session.get("expires_at", 0) < int(time.time() * 1000):
        if session:
            repo.delete_session(token)
        return {"token": None, "user": None}
    return {"token": token, "user": repo.find_user_by_id(session["user_id"])}


def create_session(user_id: str):
    token = random_url_token(32)
    now_ms = int(time.time() * 1000)
    repo.create_session(token, user_id, now_ms, now_ms + env.SESSION_MAX_AGE_SECONDS * 1000)
    return token


def register_user(body):
    email = normalize_email(body.get("email", ""))
    password = str(body.get("password", ""))
    name = str(body.get("name", "")).strip() or "SAT Student"
    if not email or "@" not in email:
        return 400, {"error": "Valid email required"}, None
    if len(password) < 8:
        return 400, {"error": "Password must be at least 8 characters"}, None
    if repo.find_user_by_email(email):
        return 409, {"error": "Account already exists"}, None
    user = {
        "id": random_url_token(18),
        "name": name,
        "email": email,
        "password": hash_password(password),
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    repo.create_user(user)
    token = create_session(user["id"])
    return 201, {"user": public_user(user)}, token


def login_user(body):
    email = normalize_email(body.get("email", ""))
    user = repo.find_user_by_email(email)
    if not user or not verify_password(body.get("password", ""), user.get("password")):
        return 401, {"error": "Invalid email or password"}, None
    token = create_session(user["id"])
    return 200, {"user": public_user(user), "codexConnected": read_user_codex_auth(user["id"]) is not None}, token


def logout_user(cookie_header):
    session = get_session(cookie_header)
    if session["token"]:
        repo.delete_session(session["token"])
