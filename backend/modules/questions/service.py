from backend.repositories import sqlite_repositories as repo


def list_questions():
    return repo.list_questions()
