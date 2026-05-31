import json
import sqlite3
import time
from pathlib import Path

from backend.config import env
from backend.shared.json_store import read_json

DB_PATH = env.RUNTIME_DATA_DIR / "eddy.db"
LEGACY_AUTH_PATH = env.RUNTIME_DATA_DIR / "authStore.json"
LEGACY_PROGRESS_PATH = env.RUNTIME_DATA_DIR / "progress.json"


def _connect():
    env.RUNTIME_DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("pragma foreign_keys = on")
    return connection


def _json(value):
    return json.dumps(value or {})


def _from_json(value, fallback=None):
    if value is None:
        return fallback
    try:
        return json.loads(value)
    except Exception:
        return fallback


def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def init_database():
    with _connect() as db:
        db.executescript(
            """
            create table if not exists users (
              id text primary key,
              name text not null,
              email text not null unique,
              password_json text not null,
              created_at text,
              updated_at text
            );

            create table if not exists sessions (
              token text primary key,
              user_id text not null references users(id) on delete cascade,
              created_at integer not null,
              expires_at integer not null
            );

            create table if not exists oauth_tokens (
              user_id text not null references users(id) on delete cascade,
              provider text not null,
              encrypted_payload text,
              updated_at text,
              primary key (user_id, provider)
            );

            create table if not exists progress_snapshots (
              user_id text primary key,
              attempts_json text not null,
              concept_stats_json text not null,
              updated_at text
            );

            create table if not exists question_bank_items (
              id text primary key,
              payload_json text not null
            );
            """
        )
    migrate_legacy_json()
    import_seed_questions()


def migrate_legacy_json():
    if LEGACY_AUTH_PATH.exists():
        store = read_json(LEGACY_AUTH_PATH, {"users": {}, "sessions": {}})
        for user in store.get("users", {}).values():
            create_user(user, replace=True)
            if user.get("codexAuth"):
                write_user_codex_auth(user["id"], user.get("codexAuth"))
        for token, session in store.get("sessions", {}).items():
            create_session(token, session.get("userId"), session.get("createdAt"), session.get("expiresAt"), replace=True)
        LEGACY_AUTH_PATH.unlink()

    if LEGACY_PROGRESS_PATH.exists():
        progress = read_json(LEGACY_PROGRESS_PATH, {})
        for user_id, snapshot in progress.items():
            save_progress(user_id, snapshot)
        LEGACY_PROGRESS_PATH.unlink()


def import_seed_questions():
    questions = read_json(env.SEED_DATA_DIR / "questionBank.json", [])
    if not questions:
        return
    with _connect() as db:
        for question in questions:
            db.execute(
                """
                insert into question_bank_items (id, payload_json)
                values (?, ?)
                on conflict(id) do update set payload_json = excluded.payload_json
                """,
                (question["id"], _json(question)),
            )


def _row_to_user(row):
    if not row:
        return None
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "password": _from_json(row["password_json"], {}),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def create_user(user, replace=False):
    sql = """
        insert into users (id, name, email, password_json, created_at, updated_at)
        values (?, ?, ?, ?, ?, ?)
        on conflict(id) do update set
          name = excluded.name,
          email = excluded.email,
          password_json = excluded.password_json,
          created_at = excluded.created_at,
          updated_at = excluded.updated_at
    """ if replace else """
        insert into users (id, name, email, password_json, created_at, updated_at)
        values (?, ?, ?, ?, ?, ?)
    """
    with _connect() as db:
        db.execute(sql, (
            user["id"],
            user["name"],
            user["email"],
            _json(user["password"]),
            user.get("createdAt") or _now_iso(),
            user.get("updatedAt") or _now_iso(),
        ))


def find_user_by_email(email):
    with _connect() as db:
        row = db.execute("select * from users where email = ?", (email,)).fetchone()
    return _row_to_user(row)


def find_user_by_id(user_id):
    with _connect() as db:
        row = db.execute("select * from users where id = ?", (user_id,)).fetchone()
    return _row_to_user(row)


def create_session(token, user_id, created_at, expires_at, replace=False):
    sql = """
        insert or replace into sessions (token, user_id, created_at, expires_at)
        values (?, ?, ?, ?)
    """ if replace else """
        insert into sessions (token, user_id, created_at, expires_at)
        values (?, ?, ?, ?)
    """
    with _connect() as db:
        db.execute(sql, (token, user_id, int(created_at), int(expires_at)))


def find_session(token):
    with _connect() as db:
        row = db.execute("select * from sessions where token = ?", (token,)).fetchone()
    return dict(row) if row else None


def delete_session(token):
    with _connect() as db:
        db.execute("delete from sessions where token = ?", (token,))


def write_user_codex_auth(user_id, encrypted_payload):
    with _connect() as db:
        if encrypted_payload:
            db.execute(
                """
                insert into oauth_tokens (user_id, provider, encrypted_payload, updated_at)
                values (?, 'openai-codex', ?, ?)
                on conflict(user_id, provider) do update set
                  encrypted_payload = excluded.encrypted_payload,
                  updated_at = excluded.updated_at
                """,
                (user_id, _json(encrypted_payload), _now_iso()),
            )
        else:
            db.execute("delete from oauth_tokens where user_id = ? and provider = 'openai-codex'", (user_id,))


def read_user_codex_auth(user_id):
    with _connect() as db:
        row = db.execute(
            "select encrypted_payload from oauth_tokens where user_id = ? and provider = 'openai-codex'",
            (user_id,),
        ).fetchone()
    return _from_json(row["encrypted_payload"]) if row else None


def save_progress(user_id, snapshot):
    with _connect() as db:
        db.execute(
            """
            insert into progress_snapshots (user_id, attempts_json, concept_stats_json, updated_at)
            values (?, ?, ?, ?)
            on conflict(user_id) do update set
              attempts_json = excluded.attempts_json,
              concept_stats_json = excluded.concept_stats_json,
              updated_at = excluded.updated_at
            """,
            (
                user_id,
                _json(snapshot.get("attempts", [])),
                _json(snapshot.get("conceptStats", {})),
                snapshot.get("updatedAt") or _now_iso(),
            ),
        )


def get_progress(user_id):
    with _connect() as db:
        row = db.execute("select * from progress_snapshots where user_id = ?", (user_id,)).fetchone()
    if not row:
        return None
    return {
        "attempts": _from_json(row["attempts_json"], []),
        "conceptStats": _from_json(row["concept_stats_json"], {}),
        "updatedAt": row["updated_at"],
    }


def list_questions():
    with _connect() as db:
        rows = db.execute("select payload_json from question_bank_items order by rowid").fetchall()
    return [_from_json(row["payload_json"], {}) for row in rows]
