from apis.repositories import sqlite_repositories as repo


def get_progress_for_user(user):
    if not user:
        return repo.get_progress("demo-user")
    return repo.get_progress(user["id"]) or repo.get_progress(user["email"])


def save_progress_for_user(user, body):
    user_id = user["id"] if user else body.get("userId", "demo-user")
    snapshot = {
        "attempts": body.get("attempts", []),
        "conceptStats": body.get("conceptStats", {}),
        "updatedAt": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
    }
    repo.save_progress(user_id, snapshot)
    return snapshot
