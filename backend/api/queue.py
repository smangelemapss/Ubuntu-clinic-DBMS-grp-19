from flask import Blueprint, g, request

import services.queue_service as queue_service
from utils.error_handler import error_response, success_response
from utils.jwt_helper import require_auth

queue_bp = Blueprint("queue", __name__, url_prefix="/api/v1")

_QUEUE_ERRORS = {
    "APPOINTMENT_NOT_FOUND": (404, "Appointment not found"),
    "FORBIDDEN": (403, "You do not have permission to access this appointment"),
    "PATIENT_NOT_FOUND": (404, "Patient profile not found"),
    "APPOINTMENT_NOT_CHECKIN_ELIGIBLE": (
        409,
        "Only scheduled or confirmed appointments can be checked in",
    ),
}


def _handle_queue_error(exc):
    code = str(exc)
    if code in _QUEUE_ERRORS:
        message, status = _QUEUE_ERRORS[code]
        err_code = "FORBIDDEN" if status == 403 else (
            "NOT_FOUND" if status == 404 else "CONFLICT"
        )
        return error_response(message, err_code, status)
    return error_response("Failed to process queue request", "SERVER_ERROR", 500)


@queue_bp.route("/queue/check-in/", methods=["POST"])
@require_auth()
def check_in():
    data = request.get_json(silent=True) or {}
    appointment_id = data.get("appointment_id")
    if not appointment_id:
        return error_response("appointment_id is required", "VALIDATION_ERROR", 400)

    try:
        result = queue_service.check_in_patient(
            int(appointment_id), g.user_id, g.role
        )
    except ValueError as exc:
        return _handle_queue_error(exc)
    except Exception:
        return error_response("Failed to check in", "SERVER_ERROR", 500)
    return success_response(result, 201)


@queue_bp.route("/queue/<int:appointment_id>/", methods=["GET"])
@require_auth()
def queue_position(appointment_id):
    try:
        result = queue_service.get_queue_position(
            appointment_id, g.user_id, g.role
        )
    except ValueError as exc:
        return _handle_queue_error(exc)
    except Exception:
        return error_response("Failed to get queue position", "SERVER_ERROR", 500)

    if result is None:
        return error_response("Queue entry not found", "NOT_FOUND", 404)
    return success_response(result)
