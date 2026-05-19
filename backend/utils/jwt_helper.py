import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import g, request

from utils.error_handler import error_response

load_dotenv()

_JWT_SECRET = os.getenv("JWT_SECRET", "changeme-secret")
_JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
_JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", "60"))

_blacklisted_tokens: set = set()


def encode_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=_JWT_EXPIRY_MINUTES)
    return jwt.encode(data, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


def encode_refresh_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
    data["token_type"] = "refresh"
    return jwt.encode(data, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])


def blacklist_token(token: str):
    _blacklisted_tokens.add(token)


def is_blacklisted(token: str) -> bool:
    return token in _blacklisted_tokens


def require_auth(roles=None):
    """
    Decorator factory.  Works both as @require_auth() and @require_auth(roles=['ADMIN']).
    Stores user_id, role, username on Flask g.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return error_response("Authentication required", "AUTH_REQUIRED", 401)

            token = auth_header.split(" ", 1)[1]

            if is_blacklisted(token):
                return error_response("Token has been revoked", "TOKEN_REVOKED", 401)

            try:
                payload = decode_token(token)
            except jwt.ExpiredSignatureError:
                return error_response("Token has expired", "TOKEN_EXPIRED", 401)
            except jwt.InvalidTokenError:
                return error_response("Invalid token", "INVALID_TOKEN", 401)

            g.user_id = payload.get("user_id")
            g.role = payload.get("role")
            g.username = payload.get("username")

            # RECEPTIONIST is a valid role that can authenticate and receive a JWT.
            # It currently has no role-gated endpoints (no decorator passes
            # roles=['RECEPTIONIST']), so it reaches any @require_auth() endpoint
            # without a roles list.  Do NOT add RECEPTIONIST to a blanket deny list
            # here — doing so would silently break RECEPTIONIST logins.
            if roles and g.role not in roles:
                return error_response(
                    "You do not have permission to access this resource",
                    "FORBIDDEN",
                    403,
                )

            return f(*args, **kwargs)

        return wrapper

    # Support both @require_auth and @require_auth() usage
    if callable(roles):
        # Called as @require_auth (no parentheses) — roles is actually the function
        func = roles
        roles = None
        return decorator(func)

    return decorator
