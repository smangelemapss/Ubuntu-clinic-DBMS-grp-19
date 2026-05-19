import db.appointment_repo as appointment_repo
import db.patient_repo as patient_repo
import db.queue_repo as queue_repo
from utils.access_control import assert_check_in_eligible, can_access_appointment


def _resolve_caller_patient_id(user_id, role):
    if role != "PATIENT":
        return None
    row = patient_repo.get_patient_by_user_id(user_id)
    if not row:
        raise ValueError("PATIENT_NOT_FOUND")
    return row[0]


def _authorize_appointment(appointment_id, user_id, role):
    appt = appointment_repo.get_appointment_by_id(appointment_id)
    if not appt:
        raise ValueError("APPOINTMENT_NOT_FOUND")

    patient_id_on_appt, _staff_id, status = appt
    caller_patient_id = _resolve_caller_patient_id(user_id, role)

    if not can_access_appointment(role, patient_id_on_appt, caller_patient_id):
        raise ValueError("FORBIDDEN")

    return patient_id_on_appt, status


def check_in_patient(appointment_id, user_id, role):
    _patient_id, status = _authorize_appointment(appointment_id, user_id, role)
    assert_check_in_eligible(status)

    existing = queue_repo.get_queue_for_appointment(appointment_id)
    if existing:
        return {
            "queue_entry_id": existing[0],
            "appointment_id": existing[1],
            "status": existing[2],
        }
    entry_id = queue_repo.create_queue_entry(appointment_id)
    return {
        "queue_entry_id": entry_id,
        "appointment_id": appointment_id,
        "status": "WAITING",
    }


def get_queue_position(appointment_id, user_id, role):
    _authorize_appointment(appointment_id, user_id, role)

    entry = queue_repo.get_queue_for_appointment(appointment_id)
    if not entry:
        return None
    return {
        "queue_entry_id": entry[0],
        "appointment_id": entry[1],
        "status": entry[2],
        "checked_in_at": entry[3].isoformat() if entry[3] else None,
        "room_number": entry[6],
    }
