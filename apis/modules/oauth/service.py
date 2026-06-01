import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

from apis.config import env
from apis.repositories import sqlite_repositories as repo
from apis.shared.security import decrypt_json, encrypt_json, random_url_token, sha256_base64_url

pending_codex_logins = {}
callback_server_started = False


def _post_form(url, data):
    encoded = urlencode(data).encode("utf-8")
    req = Request(url, data=encoded, headers={"content-type": "application/x-www-form-urlencoded"})
    with urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def exchange_codex_token(params):
    body = {
        "client_id": env.CODEX_CLIENT_ID,
        "grant_type": params["grantType"],
    }
    if params.get("code"):
        body["code"] = params["code"]
    if params.get("codeVerifier"):
        body["code_verifier"] = params["codeVerifier"]
    if params.get("refreshToken"):
        body["refresh_token"] = params["refreshToken"]
    if params.get("redirectUri"):
        body["redirect_uri"] = params["redirectUri"]

    token = _post_form("https://auth.openai.com/oauth/token", body)
    return {
        "provider": "openai-codex",
        "accessToken": token.get("access_token"),
        "refreshToken": token.get("refresh_token") or params.get("refreshToken"),
        "idToken": token.get("id_token"),
        "scope": token.get("scope"),
        "tokenType": token.get("token_type", "Bearer"),
        "expiresAt": int(__import__("time").time() * 1000) + max(30, int(token.get("expires_in", 3600)) - 60) * 1000,
        "updatedAt": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
    }


def read_user_codex_auth(user_id):
    encrypted = repo.read_user_codex_auth(user_id)
    try:
        return decrypt_json(encrypted) if encrypted else None
    except Exception:
        return None


def write_user_codex_auth(user_id, auth):
    if not repo.find_user_by_id(user_id):
        raise ValueError("User not found")
    repo.write_user_codex_auth(user_id, encrypt_json(auth) if auth else None)


def get_codex_access_token(user_id):
    auth = read_user_codex_auth(user_id)
    if not auth or not auth.get("accessToken"):
        return None
    if auth.get("expiresAt", 0) > int(__import__("time").time() * 1000):
        return auth["accessToken"]
    if not auth.get("refreshToken"):
        return None
    refreshed = exchange_codex_token({"grantType": "refresh_token", "refreshToken": auth["refreshToken"]})
    auth.update(refreshed)
    write_user_codex_auth(user_id, auth)
    return auth["accessToken"]


def _get_json(url, headers):
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def choose_codex_model(access_token):
    if env.CODEX_MODEL:
        return env.CODEX_MODEL
    models_url = f"{env.CODEX_BASE_URL}/models?client_version={env.CODEX_CLIENT_VERSION}"
    data = _get_json(models_url, {"authorization": f"Bearer {access_token}", "accept": "application/json"})
    slugs = [model.get("slug") for model in data.get("models", []) if model.get("slug")]
    return next((slug for slug in slugs if "mini" in slug and "auto-review" not in slug), None) or next((slug for slug in slugs if "auto-review" not in slug), None) or "gpt-5.4-mini"


class CodexCallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        return

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            if parsed.path != "/auth/callback":
                self.send_response(404)
                self.end_headers()
                return
            query = parse_qs(parsed.query)
            state = query.get("state", [""])[0]
            code = query.get("code", [""])[0]
            pending = pending_codex_logins.pop(state, None)
            if not state or not code or not pending:
                raise ValueError("Missing or expired Codex OAuth state.")
            token = exchange_codex_token({
                "grantType": "authorization_code",
                "code": code,
                "codeVerifier": pending["codeVerifier"],
                "redirectUri": env.CODEX_REDIRECT_URI,
            })
            write_user_codex_auth(pending["userId"], token)
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f'<!doctype html><script>location.href="{env.UI_ORIGIN}/?codex_auth=success"</script><p>Codex connected.</p>'.encode("utf-8"))
        except Exception as exc:
            self.send_response(500)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<p>{exc}</p><p><a href='{env.UI_ORIGIN}'>Return</a></p>".encode("utf-8"))


def ensure_callback_server():
    global callback_server_started
    if callback_server_started:
        return
    port = urlparse(env.CODEX_REDIRECT_URI).port or 1455
    server = ThreadingHTTPServer(("127.0.0.1", port), CodexCallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    callback_server_started = True


def create_codex_authorize_url(user_id):
    ensure_callback_server()
    state = random_url_token(24)
    code_verifier = random_url_token(48)
    pending_codex_logins[state] = {"userId": user_id, "codeVerifier": code_verifier}
    query = urlencode({
        "response_type": "code",
        "client_id": env.CODEX_CLIENT_ID,
        "redirect_uri": env.CODEX_REDIRECT_URI,
        "scope": "openid profile email offline_access",
        "code_challenge": sha256_base64_url(code_verifier),
        "code_challenge_method": "S256",
        "state": state,
        "id_token_add_organizations": "true",
        "codex_cli_simplified_flow": "true",
        "originator": "eddy_sat_agent",
    })
    return f"https://auth.openai.com/oauth/authorize?{query}"
