from datetime import date

from db.oracle_connection import get_connection


def get_patient_by_student_number(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT patient_id FROM PATIENT WHERE student_number = :1",
        [student_number],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def get_patient_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT patient_id FROM PATIENT WHERE email = :1",
        [email],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def get_patient_by_user_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.patient_id, p.student_number, p.first_name, p.last_name,
               p.email, p.contact_number, p.date_of_birth,
               p.street, p.city, p.postal_code, p.consent_given, p.registration_date
        FROM PATIENT p
        JOIN USER_ACCOUNT ua ON ua.patient_id = p.patient_id
        WHERE ua.user_account_id = :1
        """,
        [user_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_patient(
    student_number, first_name, last_name, email,
    contact_number, date_of_birth, street, city, postal_code
):
    if isinstance(date_of_birth, str):
        date_of_birth = date(2000, 1, 1)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO PATIENT
            (student_number, first_name, last_name, email,
             contact_number, date_of_birth, street, city, postal_code, consent_given)
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, 1)
        """,
        [student_number, first_name, last_name, email,
         contact_number, date_of_birth, street, city, postal_code],
    )
    conn.commit()

    cursor.execute(
        "SELECT patient_id FROM PATIENT WHERE student_number = :1",
        [student_number],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def get_dashboard_counts(patient_id):
    """Returns (upcoming_count, past_visits_count, pending_results_count, cancelled_count)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            (SELECT COUNT(*)
             FROM APPOINTMENT a
             JOIN TIMESLOT t ON a.slot_id = t.slot_id
             WHERE a.patient_id = :1
               AND a.status IN ('SCHEDULED', 'CONFIRMED')
               AND t.slot_date >= TRUNC(SYSDATE)),
            (SELECT COUNT(*)
             FROM APPOINTMENT
             WHERE patient_id = :2
               AND status IN ('COMPLETED', 'NO_SHOW')),
            (SELECT COUNT(*)
             FROM APPOINTMENT a
             WHERE a.patient_id = :3
               AND a.status = 'COMPLETED'
               AND NOT EXISTS (
                   SELECT 1 FROM MEDICAL_RECORD mr
                   WHERE mr.appointment_id = a.appointment_id
               )),
            (SELECT COUNT(*)
             FROM APPOINTMENT
             WHERE patient_id = :4 AND status = 'CANCELLED')
        FROM DUAL
        """,
        [patient_id, patient_id, patient_id, patient_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0], row[1], row[2], row[3]


def get_medical_records(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT mr.medical_record_id,
               TO_CHAR(mr.created_at, 'YYYY-MM-DD') AS visit_date,
               s.first_name || ' ' || s.last_name AS doctor_name,
               mr.diagnosis,
               d.department_name
        FROM MEDICAL_RECORD mr
        JOIN APPOINTMENT a  ON mr.appointment_id = a.appointment_id
        JOIN STAFF s        ON a.staff_id         = s.staff_id
        LEFT JOIN DEPARTMENT d ON s.department_id = d.department_id
        WHERE mr.patient_id = :1
        ORDER BY mr.created_at DESC
        """,
        [patient_id],
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_medical_record_by_id(record_id, patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT mr.medical_record_id,
               TO_CHAR(mr.created_at, 'YYYY-MM-DD') AS visit_date,
               s.first_name || ' ' || s.last_name AS doctor_name,
               mr.diagnosis,
               mr.treatment_notes AS symptoms,
               mr.prescription,
               d.department_name
        FROM MEDICAL_RECORD mr
        JOIN APPOINTMENT a  ON mr.appointment_id = a.appointment_id
        JOIN STAFF s        ON a.staff_id         = s.staff_id
        LEFT JOIN DEPARTMENT d ON s.department_id = d.department_id
        WHERE mr.medical_record_id = :1
          AND mr.patient_id        = :2
        """,
        [record_id, patient_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_emergency_contacts(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT patient_contact_id, contact_name, phone_number, relationship
        FROM PATIENT_CONTACT
        WHERE patient_id = :1
        ORDER BY patient_contact_id
        """,
        [patient_id],
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def create_emergency_contact(patient_id, name, relationship, phone, label):
    """
    PATIENT_CONTACT has no 'label' column, so we encode it as 'label|relationship'
    in the relationship field.
    """
    encoded_relationship = f"{label}|{relationship}" if label else relationship
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship)
        VALUES (:1, :2, :3, :4)
        """,
        [patient_id, name, phone, encoded_relationship],
    )
    conn.commit()

    cursor.execute(
        """
        SELECT patient_contact_id FROM PATIENT_CONTACT
        WHERE patient_id = :1 AND contact_name = :2 AND phone_number = :3
        ORDER BY patient_contact_id DESC
        """,
        [patient_id, name, phone],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def update_emergency_contact(contact_id, patient_id, **fields):
    """Partial update. Supported keys: name, relationship, phone, label."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT contact_name, phone_number, relationship
        FROM PATIENT_CONTACT
        WHERE patient_contact_id = :1 AND patient_id = :2
        """,
        [contact_id, patient_id],
    )
    existing = cursor.fetchone()
    if not existing:
        cursor.close()
        conn.close()
        return None

    current_name, current_phone, current_rel = existing

    # Decode existing label|relationship
    if current_rel and "|" in current_rel:
        current_label, current_relationship = current_rel.split("|", 1)
    else:
        current_label = ""
        current_relationship = current_rel or ""

    new_name = fields.get("name", current_name)
    new_phone = fields.get("phone", current_phone)
    new_label = fields.get("label", current_label)
    new_relationship = fields.get("relationship", current_relationship)
    encoded_relationship = f"{new_label}|{new_relationship}" if new_label else new_relationship

    cursor.execute(
        """
        UPDATE PATIENT_CONTACT
        SET contact_name = :1, phone_number = :2, relationship = :3
        WHERE patient_contact_id = :4 AND patient_id = :5
        """,
        [new_name, new_phone, encoded_relationship, contact_id, patient_id],
    )
    conn.commit()
    cursor.close()
    conn.close()
    return contact_id


def delete_emergency_contact(contact_id, patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM PATIENT_CONTACT
        WHERE patient_contact_id = :1 AND patient_id = :2
        """,
        [contact_id, patient_id],
    )
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return deleted > 0


def update_patient_profile(patient_id, **fields):
    """Update allowed PATIENT columns. Returns True if a row was updated."""
    allowed = {
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email",
        "phone": "contact_number",
        "contact_number": "contact_number",
        "date_of_birth": "date_of_birth",
        "street": "street",
        "city": "city",
        "postal_code": "postal_code",
        "address": None,
    }
    sets = []
    params = []
    for key, col in allowed.items():
        if key not in fields or fields[key] is None or col is None:
            continue
        sets.append(f"{col} = :{len(params) + 1}")
        params.append(fields[key])

    if not sets:
        return False

    params.append(patient_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE PATIENT SET {', '.join(sets)} WHERE patient_id = :{len(params)}",
        params,
    )
    updated = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return updated > 0


def get_qr_code_data(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT patient_id, student_number, first_name, last_name, email
        FROM PATIENT
        WHERE patient_id = :1
        """,
        [patient_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row
