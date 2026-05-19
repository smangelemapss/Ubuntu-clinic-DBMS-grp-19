from datetime import date

from werkzeug.security import check_password_hash, generate_password_hash

import db.user_account_repo as user_account_repo
import db.patient_repo as patient_repo
from utils import jwt_helper
from utils.registration_validation import (
    normalize_nwu_email,
    normalize_student_number,
    validate_registration,
)


def login(username, password):
    row = user_account_repo.get_user_by_username(username)
    if not row:
        raise ValueError("INVALID_CREDENTIALS")

    # row: (user_account_id, username, password_hash, patient_id, staff_id, role, status)
    user_id, uname, password_hash, patient_id, staff_id, role, status = row

    if status != "ACTIVE":
        raise ValueError("ACCOUNT_DISABLED")

    if password_hash == "CHANGEME":
        raise ValueError("SEED_PASSWORDS_NOT_CONFIGURED")

    if not check_password_hash(password_hash, password):
        raise ValueError("INVALID_CREDENTIALS")

    user_row = user_account_repo.get_user_by_id(user_id)
    # user_row: (user_account_id, username, email, role, status, patient_id, staff_id, date_joined)
    email = user_row[2] if user_row else ""

    payload = {"user_id": user_id, "username": uname, "role": role}
    access_token = jwt_helper.encode_token(payload)
    refresh_token = jwt_helper.encode_refresh_token(payload)

    user_payload = {"id": user_id, "username": uname, "email": email, "role": role}
    if patient_id:
        user_payload["patient_id"] = patient_id
        patient_row = patient_repo.get_patient_by_user_id(user_id)
        if patient_row:
            user_payload.update(_patient_profile_dict(patient_row))

    return {
        "access": access_token,
        "refresh": refresh_token,
        "role": role,
        "user": user_payload,
    }


def register(username, email, password, student_number=None):
    username = (username or "").strip().lower()
    student_number = normalize_student_number(student_number)
    email = normalize_nwu_email(email)

    validation_error = validate_registration(username, email, password, student_number)
    if validation_error:
        raise ValueError(validation_error)

    existing = user_account_repo.get_user_by_username(username)
    if existing:
        raise ValueError("USERNAME_EXISTS")

    if patient_repo.get_patient_by_student_number(student_number):
        raise ValueError("STUDENT_NUMBER_EXISTS")
    if patient_repo.get_patient_by_email(email):
        raise ValueError("EMAIL_EXISTS")

    password_hash = generate_password_hash(password)

    parts = username.split(".", 1)
    first_name = parts[0].capitalize() if parts else username
    last_name = parts[1].capitalize() if len(parts) > 1 else "User"

    patient_id = patient_repo.create_patient(
        student_number=student_number,
        first_name=first_name,
        last_name=last_name,
        email=email,
        contact_number="0000000000",
        date_of_birth=date(2000, 1, 1),
        street="Unknown",
        city="Unknown",
        postal_code="0000",
    )

    user_id = user_account_repo.create_patient_user(username, password_hash, patient_id)

    return {
        "message": "Registration successful",
        "user": {
            "id": user_id,
            "username": username,
            "email": email,
            "role": "PATIENT",
            "student_number": student_number,
        },
    }


def logout(refresh_token):
    jwt_helper.blacklist_token(refresh_token)


def get_current_user(user_id):
    row = user_account_repo.get_user_by_id(user_id)
    if not row:
        return None
    # row: (user_account_id, username, email, role, status, patient_id, staff_id)
    user = {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "role": row[3],
        "patient_id": row[5],
    }
    if row[5]:
        patient_row = patient_repo.get_patient_by_user_id(user_id)
        if patient_row:
            user.update(_patient_profile_dict(patient_row))
    return user


def _patient_profile_dict(patient_row):
    """patient_row from get_patient_by_user_id."""
    pid, student_number, first_name, last_name, email, phone, dob, street, city, postal, *_ = (
        patient_row + (None,) * 12
    )[:12]
    address_parts = [p for p in (street, city, postal) if p]
    return {
        "patient_id": pid,
        "student_number": student_number,
        "first_name": first_name,
        "last_name": last_name,
        "email": email or "",
        "phone": phone or "",
        "date_of_birth": _format_oracle_date(dob),
        "address": ", ".join(address_parts) if address_parts else "",
        "street": street or "",
        "city": city or "",
        "postal_code": postal or "",
    }


def _format_oracle_date(value):
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)
