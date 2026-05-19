from flask import Blueprint, g, request

import services.admin_service as admin_service
import db.user_account_repo as user_account_repo
from utils.audit_helper import log_audit
from utils.error_handler import error_response, success_response
from utils.jwt_helper import require_auth
from utils.pagination import normalize_pagination

_VALID_ROLES = frozenset({"PATIENT", "DOCTOR", "NURSE", "ADMIN", "RECEPTIONIST"})

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@admin_bp.route("/reports/summary/", methods=["GET"])
@require_auth(roles=["ADMIN"])
def summary():
    try:
        data = admin_service.get_summary_stats()
    except Exception:
        return error_response("Unable to load summary stats", "SERVER_ERROR", 500)
    return success_response(data)


@admin_bp.route("/reports/appointments/", methods=["GET"])
@require_auth(roles=["ADMIN"])
def appointments_by_doctor():
    try:
        data = admin_service.get_appointments_by_doctor()
    except Exception:
        return error_response("Unable to load appointment report", "SERVER_ERROR", 500)
    return success_response(data)


@admin_bp.route("/reports/daily-counts/", methods=["GET"])
@require_auth(roles=["ADMIN"])
def daily_counts():
    try:
        data = admin_service.get_daily_counts(days=30)
    except Exception:
        return error_response("Unable to load daily counts", "SERVER_ERROR", 500)
    return success_response(data)


@admin_bp.route("/audit-log/", methods=["GET"])
@require_auth(roles=["ADMIN"])
def audit_log():
    user_filter = request.args.get("user")
    action_filter = request.args.get("action")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    page, per_page = normalize_pagination(
        request.args.get("page", 1),
        request.args.get("per_page", 20),
    )

    try:
        rows, total = admin_service.get_audit_log(
            page=page,
            per_page=per_page,
            user_filter=user_filter,
            action_filter=action_filter,
            date_from=date_from,
            date_to=date_to,
        )
    except Exception:
        return error_response("Unable to load audit log", "SERVER_ERROR", 500)

    results = [
        {
            "id": r[0],
            "user": r[1],
            "action": r[2],
            "timestamp": r[3].isoformat() if r[3] else None,
            "ip_address": r[4],
            "detail": r[5],
        }
        for r in rows
    ]

    has_next = (page * per_page) < total
    has_prev = page > 1

    return success_response({
        "count": total,
        "next": f"?page={page + 1}&per_page={per_page}" if has_next else None,
        "previous": f"?page={page - 1}&per_page={per_page}" if has_prev else None,
        "results": results,
    })


@admin_bp.route("/departments/", methods=["GET"])
@require_auth(roles=["ADMIN"])
def list_departments():
    try:
        rows = admin_service.list_departments()
    except Exception:
        return error_response("Unable to load departments", "SERVER_ERROR", 500)

    data = [
        {
            "id": r[0],
            "name": r[1],
            "head_doctor": r[2],
            "staff_count": r[3],
        }
        for r in rows
    ]
    return success_response(data)


@admin_bp.route("/departments/", methods=["POST"])
@require_auth(roles=["ADMIN"])
def create_department():
    body = request.get_json(silent=True) or {}
    name = body.get("name", "").strip()
    head_doctor_id = body.get("head_doctor_id")

    if not name:
        return error_response("Department name is required", "VALIDATION_ERROR", 400)

    try:
        dept_id = admin_service.create_department(name, head_doctor_id)
    except Exception as exc:
        msg = str(exc)
        if "ORA-00001" in msg or "unique constraint" in msg.lower():
            return error_response("Department name already exists", "DUPLICATE_DEPT", 409)
        return error_response("Failed to create department", "SERVER_ERROR", 500)

    row = admin_service.get_department_by_id(dept_id)
    log_audit(g.user_id, "CREATE_DEPARTMENT", "DEPARTMENT", dept_id)
    return success_response(
        {
            "id": row[0],
            "name": row[1],
            "head_doctor": row[2],
            "staff_count": row[3],
        },
        201,
    )


@admin_bp.route("/departments/<int:dept_id>/", methods=["PATCH"])
@require_auth(roles=["ADMIN"])
def update_department(dept_id):
    body = request.get_json(silent=True) or {}
    try:
        result = admin_service.update_department(dept_id, **body)
    except Exception:
        return error_response("Failed to update department", "SERVER_ERROR", 500)

    if result is None:
        return error_response("Department not found", "NOT_FOUND", 404)

    row = admin_service.get_department_by_id(dept_id)
    log_audit(g.user_id, "UPDATE_DEPARTMENT", "DEPARTMENT", dept_id)
    return success_response(
        {
            "id": row[0],
            "name": row[1],
            "head_doctor": row[2],
            "staff_count": row[3],
        }
    )


@admin_bp.route("/departments/<int:dept_id>/", methods=["DELETE"])
@require_auth(roles=["ADMIN"])
def delete_department(dept_id):
    try:
        result = admin_service.delete_department(dept_id)
    except Exception:
        return error_response("Failed to delete department", "SERVER_ERROR", 500)

    if result is None:
        return error_response("Department not found", "NOT_FOUND", 404)
    if result == "HAS_STAFF":
        return error_response(
            "Cannot delete department with active staff members",
            "DEPT_HAS_STAFF",
            409,
        )
    log_audit(g.user_id, "DELETE_DEPARTMENT", "DEPARTMENT", dept_id)
    return success_response({"message": "Department deleted successfully", "deleted_id": dept_id})


@admin_bp.route("/users/", methods=["GET"])
@require_auth(roles=["ADMIN"])
def list_users():
    role_filter = request.args.get("role")
    if role_filter and role_filter.upper() not in _VALID_ROLES:
        return error_response(
            f"Role must be one of: {', '.join(sorted(_VALID_ROLES))}",
            "VALIDATION_ERROR",
            400,
        )
    page, per_page = normalize_pagination(
        request.args.get("page", 1),
        request.args.get("per_page", 20),
    )

    try:
        rows, total = user_account_repo.get_all_users(
            role_filter=role_filter, page=page, per_page=per_page
        )
    except Exception:
        return error_response("Unable to load users", "SERVER_ERROR", 500)

    results = [
        {
            "id": r[0],
            "username": r[1],
            "email": r[2],
            "role": r[3],
            "is_active": r[4] == "ACTIVE",
        }
        for r in rows
    ]

    has_next = (page * per_page) < total
    has_prev = page > 1

    return success_response({
        "count": total,
        "next": f"?page={page + 1}&per_page={per_page}" if has_next else None,
        "previous": f"?page={page - 1}&per_page={per_page}" if has_prev else None,
        "results": results,
    })


@admin_bp.route("/users/<int:user_id>/", methods=["PATCH"])
@require_auth(roles=["ADMIN"])
def update_user(user_id):
    body = request.get_json(silent=True) or {}

    row = user_account_repo.get_user_by_id(user_id)
    if not row:
        return error_response("User not found", "NOT_FOUND", 404)

    if user_id == g.user_id:
        if "is_active" in body and not bool(body["is_active"]):
            return error_response(
                "You cannot disable your own admin account",
                "FORBIDDEN",
                403,
            )
        if "role" in body and body["role"] != row[3]:
            return error_response(
                "You cannot change your own role",
                "FORBIDDEN",
                403,
            )

    try:
        if "is_active" in body:
            user_account_repo.update_user_status(user_id, bool(body["is_active"]))
        if "role" in body:
            if body["role"] not in _VALID_ROLES:
                return error_response(
                    f"Role must be one of: {', '.join(sorted(_VALID_ROLES))}",
                    "VALIDATION_ERROR",
                    400,
                )
            user_account_repo.update_user_role(user_id, body["role"])
    except Exception:
        return error_response("Failed to update user", "SERVER_ERROR", 500)

    log_audit(g.user_id, "UPDATE_USER", "USER_ACCOUNT", user_id)
    updated_row = user_account_repo.get_user_by_id(user_id)
    return success_response({
        "id": updated_row[0],
        "username": updated_row[1],
        "email": updated_row[2],
        "role": updated_row[3],
        "is_active": updated_row[4] == "ACTIVE",
    })
