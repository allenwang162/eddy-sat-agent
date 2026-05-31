import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

PUBLIC_DIR = ROOT_DIR / "public"
DATA_DIR = ROOT_DIR / "data"
SEED_DATA_DIR = DATA_DIR / "seed"
RUNTIME_DATA_DIR = DATA_DIR / "runtime"

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "3000"))
APP_ORIGIN = f"http://{HOST}:{PORT}"
NODE_ENV = os.getenv("NODE_ENV", "development")

AUTH_SECRET = os.getenv("AUTH_SECRET", "dev-only-change-before-deploy")
SESSION_COOKIE_NAME = "eddy_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 14

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

CODEX_CLIENT_ID = os.getenv("CODEX_CLIENT_ID", "app_EMoamEEZ73f0CkXaXp7hrann")
CODEX_REDIRECT_URI = os.getenv("CODEX_REDIRECT_URI", "http://localhost:1455/auth/callback")
CODEX_BASE_URL = os.getenv("CODEX_BASE_URL", "https://chatgpt.com/backend-api/codex")
CODEX_CLIENT_VERSION = os.getenv("CODEX_CLIENT_VERSION", "0.104.0")
CODEX_MODEL = os.getenv("CODEX_MODEL", "")
