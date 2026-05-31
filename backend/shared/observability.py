import contextvars
import hashlib
import json
import logging
import sys
import time
from pathlib import Path

from backend.config import env


request_id_var = contextvars.ContextVar("request_id", default="")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None) or request_id_var.get()
        if request_id:
            payload["request_id"] = request_id
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key, value in getattr(record, "fields", {}).items():
            payload[key] = value
        return json.dumps(payload, ensure_ascii=False, default=str)


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


def user_hash(user_id):
    if not user_id:
        return None
    return hashlib.sha256(f"{env.LOG_USER_HASH_SALT}:{user_id}".encode("utf-8")).hexdigest()[:16]


def get_logger(name):
    return logging.getLogger(f"eddy.{name}")


def configure_logging():
    level = getattr(logging, env.LOG_LEVEL.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    formatter = JsonFormatter() if env.LOG_FORMAT == "json" else logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s"
    )
    context_filter = RequestContextFilter()

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    stream.addFilter(context_filter)
    root.addHandler(stream)

    if env.LOG_FILE:
        log_path = Path(env.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        root.addHandler(file_handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(logger_name).setLevel(level)


def log_event(logger, event, level=logging.INFO, **fields):
    logger.log(level, event, extra={"fields": {"event": event, **fields}})
