from flask import Blueprint, g, request

import services.patient_service as patient_service
from utils.error_handler import error_response, success_response
from utils.jwt_helper import require_auth

patients_bp = Blueprint("patients", __name__, url_prefix="/api/v1")


@patients_bp.route("/patient/profile/", methods=["GET"])
@require_auth(roles=["PATIENT"])
def patient_profile():
    try:
        data = patient_service.get_profile(g.user_id)
    except ValueError:
        return error_response("Patient profile not found", "NOT_FOUND", 404)
    except Exception:
        return error_response("Failed to load profile", "SERVER_ERROR", 500)
    return success_response(data)


@patients_bp.route("/patient/profile/", methods=["PATCH"])
@require_auth(roles=["PATIENT"])
def update_patient_profile():
    data = request.get_json(silent=True) or {}
    try:
        profile = patient_service.update_profile(g.user_id, data)
    except ValueError as exc:
        if str(exc) == "PATIENT_NOT_FOUND":
            return error_response("Patient profile not found", "NOT_FOUND", 404)
        if str(exc) == "NO_FIELDS":
            return error_response("No updatable fields provided", "VALIDATION_ERROR", 400)
        return error_response(str(exc), "VALIDATION_ERROR", 400)
    except Exception:
        return error_response("Failed to update profile", "SERVER_ERROR", 500)

    from utils.audit_helper import log_audit

    log_audit(g.user_id, "UPDATE_PROFILE", "PATIENT", profile.get("patient_id"))
    return success_response(profile)


@patients_bp.route("/patient/dashboard/", methods=["GET"])
@require_auth(roles=["PATIENT"])
def dashboard():
    try:
        data = patient_service.get_dashboard(g.user_id)
    except ValueError:
        return error_response("Patient profile not found", "NOT_FOUND", 404)
    except Exception:
        return error_response("Failed to load dashboard", "SERVER_ERROR", 500)
    return success_response(data)


@patients_bp.route("/patient/qr-code/", methods=["GET"])
@require_auth(roles=["PATIENT"])
def qr_code():
    try:
        data = patient_service.get_qr_code(g.user_id)
    except ValueError:
        return error_response("Patient profile not found", "NOT_FOUND", 404)
    except Exception:
        return error_response("Unable to generate QR code", "SERVER_ERROR", 500)
    return success_response(data)


@patients_bp.route("/medical/records/", methods=["GET"])
@require_auth(roles=["PATIENT"])
def medical_records():
    try:
        data = patient_service.get_medical_records(g.user_id)
    except ValueError:
        return error_response("Patient profile not found", "NOT_FOUND", 404)
    except Exception:
        return error_response("Unable to load medical records", "SERVER_ERROR", 500)
    return success_response(data)


@patients_bp.route("/medical/records/<int:record_id>/", methods=["GET"])
@require_auth(roles=["PATIENT"])
def medical_record_detail(record_id):
    try:
        data = patient_service.get_medical_record_detail(g.user_id, record_id)
    except ValueError:
        return error_response("Patient profile not found", "NOT_FOUND", 404)
    except Exception:
        return error_response("Unable to load record", "SERVER_ERROR", 500)

    if data is None:
        return error_response("Record not found", "NOT_FOUND", 404)
    return success_response(data)


@patients_bp.route("/emergency-contacts/", methods=["GET"])
@require_auth(roles=["PATIENT"])
def list_emergency_contacts():
    try:
        data = patient_service.get_emergency_contacts(g.user_id)
    except ValueError:
        return error_response("Patient profile not found", "NOT_FOUND", 404)
    except Exception:
        return error_response("Unable to load contacts", "SERVER_ERROR", 500)
    return success_response(data)


@patients_bp.route("/emergency-contacts/", methods=["POST"])
@require_auth(roles=["PATIENT"])
def add_emergency_contact():
    data = request.get_json(silent=True) or {}
    try:
        result = patient_service.add_emergency_contact(g.user_id, data)
    except ValueError as exc:
        msg = str(exc)
        if msg.startswith("MISSING_FIELD:"):
            field = msg.split(":")[1]
            return error_response(f"Field '{field}' is required", "VALIDATION_ERROR", 400)
        return error_response(msg, "VALIDATION_ERROR", 400)
    except Exception:
        return error_response("Failed to add contact", "SERVER_ERROR", 500)
    return success_response(result, 201)


@patients_bp.route("/emergency-contacts/<int:contact_id>/", methods=["PATCH"])
@require_auth(roles=["PATIENT"])
def update_emergency_contact(contact_id):
    data = request.get_json(silent=True) or {}
    try:
        result = patient_service.update_emergency_contact(g.user_id, contact_id, data)
    except ValueError:
        return error_response("Patient profile not found", "NOT_FOUND", 404)
    except Exception:
        return error_response("Failed to update contact", "SERVER_ERROR", 500)

    if result is None:
        return error_response("Contact not found", "NOT_FOUND", 404)
    return success_response(result)


@patients_bp.route("/emergency-contacts/<int:contact_id>/", methods=["DELETE"])
@require_auth(roles=["PATIENT"])
def delete_emergency_contact(contact_id):
    try:
        deleted = patient_service.delete_emergency_contact(g.user_id, contact_id)
    except ValueError:
        return error_response("Patient profile not found", "NOT_FOUND", 404)
    except Exception:
        return error_response("Failed to delete contact", "SERVER_ERROR", 500)

    if not deleted:
        return error_response("Contact not found", "NOT_FOUND", 404)
    return success_response({"message": "Contact deleted successfully", "deleted_id": contact_id})
