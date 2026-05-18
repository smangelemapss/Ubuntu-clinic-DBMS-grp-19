from flask import Blueprint, g, request

import services.auth_service as auth_service
from utils.error_handler import error_response, success_response
from utils.jwt_helper import decode_token, encode_token, is_blacklisted, require_auth
from utils.rate_limit import rate_limit_auth

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/login/", methods=["POST"])
@rate_limit_auth
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if " " in username:
        username = ".".join(username.split()).lower()

    if not username or not password:
        return error_response("Username and password are required", "VALIDATION_ERROR", 400)

    try:
        result = auth_service.login(username, password)
    except ValueError as exc:
        code = str(exc)
        if code == "ACCOUNT_DISABLED":
            return error_response("Account is disabled", "ACCOUNT_DISABLED", 401)
        if code == "SEED_PASSWORDS_NOT_CONFIGURED":
            return error_response(
                "Demo passwords are not set yet. From the backend folder run: "
                "python scripts/reset_seed_passwords.py",
                "SEED_PASSWORDS_NOT_CONFIGURED",
                503,
            )
        return error_response("Invalid username or password", "INVALID_CREDENTIALS", 401)
    except Exception:
        return error_response("Login failed", "SERVER_ERROR", 500)

    from utils.audit_helper import log_audit

    user_id = result.get("user", {}).get("id")
    if user_id:
        log_audit(user_id, "LOGIN", "USER_ACCOUNT", user_id)
    return success_response(result)


@auth_bp.route("/register/", methods=["POST"])
@rate_limit_auth
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip().lower()
    if " " in username:
        username = ".".join(username.split())
    email = data.get("email", "").strip()
    password = data.get("password", "")
    student_number = data.get("student_number", "").strip()

    if not username or not email or not password or not student_number:
        return error_response(
            "username, student_number, email and password are required",
            "VALIDATION_ERROR",
            400,
        )

    try:
        result = auth_service.register(username, email, password, student_number)
    except ValueError as exc:
        code = str(exc)
        if code in ("USERNAME_EXISTS", "STUDENT_NUMBER_EXISTS", "EMAIL_EXISTS"):
            return error_response("Username, student number, or email already exists", "DUPLICATE_USER", 409)
        messages = {
            "STUDENT_NUMBER_REQUIRED": "Student number is required",
            "STUDENT_NUMBER_INVALID": "Student number must be exactly 8 digits (e.g. 48277444)",
            "EMAIL_REQUIRED": "NWU email is required",
            "EMAIL_INVALID": "Email must be yournumber@mynwu.ac.za (e.g. 48277444@mynwu.ac.za)",
            "EMAIL_STUDENT_MISMATCH": "Email must use the same student number you entered",
            "PASSWORD_REQUIRED": "Password is required",
            "PASSWORD_TOO_SHORT": "Password must be at least 8 characters",
            "PASSWORD_WEAK": "Password must include at least one letter and one number",
            "USERNAME_REQUIRED": "Username is required",
            "USERNAME_INVALID": "Username must be firstname.lastname (e.g. karabo.mabena)",
        }
        if code in messages:
            return error_response(messages[code], "VALIDATION_ERROR", 400)
        return error_response(str(exc), "VALIDATION_ERROR", 400)
    except Exception as exc:
        msg = str(exc)
        if "ORA-00001" in msg or "unique constraint" in msg.lower():
            return error_response("Username or email already exists", "DUPLICATE_USER", 409)
        return error_response("Registration failed", "SERVER_ERROR", 500)

    from utils.audit_helper import log_audit

    user_id = result.get("user", {}).get("id")
    if user_id:
        log_audit(user_id, "REGISTER", "USER_ACCOUNT", user_id)
    return success_response(result, 201)


@auth_bp.route("/logout/", methods=["POST"])
@require_auth()
def logout():
    from utils.jwt_helper import blacklist_token

    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh", "")
    if refresh_token:
        auth_service.logout(refresh_token)

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        blacklist_token(auth_header.split(" ", 1)[1])

    return success_response({"message": "Logged out successfully"})


@auth_bp.route("/me/", methods=["GET"])
@require_auth()
def me():
    user = auth_service.get_current_user(g.user_id)
    if not user:
        return error_response("User not found", "NOT_FOUND", 404)
    return success_response(user)


@auth_bp.route("/token/refresh/", methods=["POST"])
def token_refresh():
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh", "")

    if not refresh_token:
        return error_response("Refresh token required", "MISSING_TOKEN", 400)

    if is_blacklisted(refresh_token):
        return error_response("Token has been revoked", "TOKEN_REVOKED", 401)

    try:
        payload = decode_token(refresh_token)
    except Exception:
        return error_response("Invalid or expired refresh token", "INVALID_TOKEN", 401)

    if payload.get("token_type") != "refresh":
        return error_response("Not a refresh token", "INVALID_TOKEN", 401)

    new_payload = {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "role": payload.get("role"),
    }
    new_access = encode_token(new_payload)
    return success_response({"access": new_access})
