"""Authorization helpers for resource-scoped access."""

STAFF_ROLES = frozenset({"DOCTOR", "NURSE", "RECEPTIONIST", "ADMIN"})
CHECK_IN_STATUSES = frozenset({"SCHEDULED", "CONFIRMED"})


def is_staff_role(role):
    return role in STAFF_ROLES


def can_access_appointment(role, patient_id_on_appt, caller_patient_id):
    """
    Patients may only access their own appointments.
    Clinic staff may access any appointment.
    """
    if is_staff_role(role):
        return True
    if role == "PATIENT" and caller_patient_id is not None:
        return patient_id_on_appt == caller_patient_id
    return False


def assert_check_in_eligible(status):
    if status not in CHECK_IN_STATUSES:
        raise ValueError("APPOINTMENT_NOT_CHECKIN_ELIGIBLE")
