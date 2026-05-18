import re
import time
import uuid

import db.appointment_repo as appointment_repo
import db.doctor_repo as doctor_repo
import db.patient_repo as patient_repo

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_DOCTORS_CACHE = {"data": None, "expires_at": 0.0}
_DOCTORS_CACHE_TTL_SEC = 120

_BOOKING_TYPE_MAP = {
    "virtual": "VIRTUAL_TRIAGE",
    "online": "VIRTUAL_TRIAGE",
    "in-person": "SICK",
    "in_person": "SICK",
    "sick": "SICK",
    "follow-up": "FOLLOW_UP",
    "follow_up": "FOLLOW_UP",
    "walk-in": "WALK_IN",
    "walk_in": "WALK_IN",
}


def _format_slot_time(value):
    """Normalize Oracle TIME / string values to HH:MM for API and booking match."""
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    text = str(value).strip()
    if "T" in text:
        text = text.split("T", 1)[1]
    if len(text) >= 8 and text[2] == ":" and text[5] == ":":
        return text[:5]
    if len(text) >= 5 and text[2] == ":":
        return text[:5]
    return text


def _get_patient_id(user_id):
    row = patient_repo.get_patient_by_user_id(user_id)
    if not row:
        raise ValueError("PATIENT_NOT_FOUND")
    return row[0]


def get_upcoming(user_id):
    patient_id = _get_patient_id(user_id)
    rows = appointment_repo.get_upcoming_appointments(patient_id)
    return [
        {
            "id": r[0],
            "date": r[1],
            "time": r[2],
            "doctor": r[3],
            "doctor_id": r[4],
            "type": r[5],
            "status": "upcoming",
            "department": r[7],
        }
        for r in rows
    ]


def get_history(user_id):
    patient_id = _get_patient_id(user_id)
    rows = appointment_repo.get_appointment_history(patient_id)
    return [
        {
            "id": r[0],
            "date": r[1],
            "time": r[2],
            "doctor": r[3],
            "department": r[4],
            "diagnosis": r[5],
            "status": r[6].capitalize() if r[6] else "Unknown",
        }
        for r in rows
    ]


def get_pending_results(user_id):
    patient_id = _get_patient_id(user_id)
    rows = appointment_repo.get_pending_results(patient_id)
    return [
        {
            "id": r[0],
            "date": r[1],
            "test": r[2],
            "status": r[3],
        }
        for r in rows
    ]


def book_appointment(user_id, data):
    required = ["doctor_id", "date", "time_slot", "reason", "type"]
    for field in required:
        if data.get(field) is None:
            raise ValueError(f"MISSING_FIELD:{field}")

    patient_id = _get_patient_id(user_id)
    doctor_id = int(data["doctor_id"])
    date_str = str(data["date"]).strip()
    if not _DATE_RE.match(date_str):
        raise ValueError("INVALID_DATE")

    if not doctor_repo.get_doctor_by_id(doctor_id):
        raise ValueError("INVALID_DOCTOR")

    time_slot = data["time_slot"]
    booking_type_raw = data.get("type", "in-person").lower()
    booking_type = _BOOKING_TYPE_MAP.get(booking_type_raw, "SICK")

    slots = appointment_repo.get_available_timeslots(date_str, doctor_id)
    matching_slot = None
    for slot in slots:
        slot_id, start_time, is_available = slot
        if _format_slot_time(start_time) == _format_slot_time(time_slot):
            matching_slot = slot
            break

    if not matching_slot:
        raise LookupError("NO_SLOT_FOUND")

    slot_id = matching_slot[0]
    qr_token = str(uuid.uuid4())

    result = appointment_repo.book_appointment(
        patient_id=patient_id,
        staff_id=doctor_id,
        slot_id=slot_id,
        reason=data["reason"],
        booking_type=booking_type,
        qr_token=qr_token,
    )

    if not result:
        raise RuntimeError("BOOKING_FAILED")

    appt_id, appt_date, start_time, doctor_name = result
    return {
        "id": appt_id,
        "appointment_date": appt_date,
        "time": start_time,
        "doctor_name": doctor_name,
        "status": "confirmed",
        "qr_code_token": qr_token,
    }


def get_available_slots(date_str, doctor_id=None):
    rows = appointment_repo.get_available_timeslots(date_str, doctor_id)
    return [
        {
            "id": r[0],
            "time": _format_slot_time(r[1]),
            "is_available": bool(r[2]),
        }
        for r in rows
    ]


def cancel_appointment(user_id, appointment_id, reason=None):
    patient_id = _get_patient_id(user_id)
    result = appointment_repo.cancel_appointment(patient_id, appointment_id)
    if result is None:
        return None
    if result is False:
        raise ValueError("ALREADY_FINALIZED")
    return {
        "id": appointment_id,
        "status": "cancelled",
        "cancellation_reason": reason or "",
    }


def get_all_doctors():
    now = time.time()
    if _DOCTORS_CACHE["data"] is not None and now < _DOCTORS_CACHE["expires_at"]:
        return _DOCTORS_CACHE["data"]

    rows = doctor_repo.get_all_doctors()
    result = [
        {
            "id": r[0],
            "name": r[1],
            "specialization": r[2],
            "available": True,
        }
        for r in rows
    ]
    _DOCTORS_CACHE["data"] = result
    _DOCTORS_CACHE["expires_at"] = now + _DOCTORS_CACHE_TTL_SEC
    return result
