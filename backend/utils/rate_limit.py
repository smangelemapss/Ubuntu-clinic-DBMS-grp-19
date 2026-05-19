"""Lightweight in-memory rate limiting for auth endpoints."""

import os
import time
from collections import defaultdict
from functools import wraps

from flask import request

from utils.error_handler import error_response

_hits = defaultdict(list)
_WINDOW_SEC = int(os.getenv("AUTH_RATE_LIMIT_WINDOW_SEC", "60"))
_MAX_REQUESTS = int(os.getenv("AUTH_RATE_LIMIT_MAX", "15"))


def rate_limit_auth(f):
    """Limit login/register attempts per client IP per window."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        if os.getenv("DISABLE_RATE_LIMIT", "").lower() in ("1", "true", "yes"):
            return f(*args, **kwargs)

        client = request.remote_addr or "unknown"
        now = time.time()
        recent = [t for t in _hits[client] if now - t < _WINDOW_SEC]
        if len(recent) >= _MAX_REQUESTS:
            return error_response(
                "Too many attempts. Please wait a minute and try again.",
                "RATE_LIMITED",
                429,
            )
        recent.append(now)
        _hits[client] = recent
        return f(*args, **kwargs)

    return wrapper
