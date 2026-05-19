from db.oracle_connection import get_connection


def get_upcoming_appointments(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.appointment_id,
               TO_CHAR(t.slot_date, 'YYYY-MM-DD') AS appt_date,
               t.start_time,
               s.first_name || ' ' || s.last_name AS doctor_name,
               a.staff_id,
               a.booking_type,
               a.status,
               d.department_name
        FROM APPOINTMENT a
        JOIN TIMESLOT   t ON a.slot_id    = t.slot_id
        JOIN STAFF      s ON a.staff_id   = s.staff_id
        LEFT JOIN DEPARTMENT d ON s.department_id = d.department_id
        WHERE a.patient_id = :1
          AND a.status IN ('SCHEDULED', 'CONFIRMED')
          AND t.slot_date >= TRUNC(SYSDATE)
        ORDER BY t.slot_date, t.start_time
        """,
        [patient_id],
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_appointment_history(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.appointment_id,
               TO_CHAR(t.slot_date, 'YYYY-MM-DD') AS appt_date,
               t.start_time,
               s.first_name || ' ' || s.last_name AS doctor_name,
               d.department_name,
               mr.diagnosis,
               a.status
        FROM APPOINTMENT a
        JOIN TIMESLOT   t  ON a.slot_id        = t.slot_id
        JOIN STAFF      s  ON a.staff_id        = s.staff_id
        LEFT JOIN DEPARTMENT  d  ON s.department_id  = d.department_id
        LEFT JOIN MEDICAL_RECORD mr ON mr.appointment_id = a.appointment_id
        WHERE a.patient_id = :1
          AND a.status IN ('COMPLETED', 'CANCELLED', 'NO_SHOW')
        ORDER BY t.slot_date DESC
        """,
        [patient_id],
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_pending_results(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.appointment_id,
               TO_CHAR(t.slot_date, 'YYYY-MM-DD') AS appt_date,
               a.booking_type,
               a.status
        FROM APPOINTMENT a
        JOIN TIMESLOT t ON a.slot_id = t.slot_id
        WHERE a.patient_id = :1
          AND a.status = 'COMPLETED'
          AND NOT EXISTS (
              SELECT 1 FROM MEDICAL_RECORD mr WHERE mr.appointment_id = a.appointment_id
          )
        ORDER BY t.slot_date DESC
        """,
        [patient_id],
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_available_timeslots(date_str, doctor_id=None):
    """
    date_str: 'YYYY-MM-DD'
    TIMESLOT is not linked to a specific doctor in the schema, so doctor_id filter
    checks that no APPOINTMENT already exists for that staff on overlapping slots.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if doctor_id:
        cursor.execute(
            """
            SELECT t.slot_id, t.start_time, t.is_available
            FROM TIMESLOT t
            WHERE t.is_available = 1
              AND t.slot_date = TO_DATE(:1, 'YYYY-MM-DD')
              AND NOT EXISTS (
                  SELECT 1 FROM APPOINTMENT a
                  WHERE a.slot_id = t.slot_id AND a.staff_id = :2
              )
            ORDER BY t.start_time
            """,
            [date_str, doctor_id],
        )
    else:
        cursor.execute(
            """
            SELECT slot_id, start_time, is_available
            FROM TIMESLOT
            WHERE is_available = 1
              AND slot_date = TO_DATE(:1, 'YYYY-MM-DD')
            ORDER BY start_time
            """,
            [date_str],
        )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_appointment_by_id(appointment_id):
    """Returns (patient_id, staff_id, status) or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT patient_id, staff_id, status
        FROM APPOINTMENT
        WHERE appointment_id = :1
        """,
        [appointment_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def book_appointment(patient_id, staff_id, slot_id, reason, booking_type, qr_token):
    """
    Implements SELECT FOR UPDATE pattern.
    Returns (appointment_id, slot_date, start_time, doctor_name) or raises RuntimeError on conflict.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Lock the timeslot row
        cursor.execute(
            "SELECT is_available FROM TIMESLOT WHERE slot_id = :1 FOR UPDATE",
            [slot_id],
        )
        row = cursor.fetchone()
        if not row or row[0] != 1:
            conn.rollback()
            cursor.close()
            conn.close()
            raise ValueError("SLOT_UNAVAILABLE")

        cursor.execute(
            "SELECT appointment_id FROM APPOINTMENT WHERE slot_id = :1",
            [slot_id],
        )
        if cursor.fetchone():
            conn.rollback()
            cursor.close()
            conn.close()
            raise ValueError("SLOT_UNAVAILABLE")

        cursor.execute(
            """
            INSERT INTO APPOINTMENT
                (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
            VALUES (:1, :2, :3, 'SCHEDULED', :4, 'NORMAL', :5)
            """,
            [slot_id, patient_id, staff_id, booking_type, qr_token],
        )

        cursor.execute(
            "UPDATE TIMESLOT SET is_available = 0 WHERE slot_id = :1",
            [slot_id],
        )

        conn.commit()

        # Fetch created appointment details
        cursor.execute(
            """
            SELECT a.appointment_id,
                   TO_CHAR(t.slot_date, 'YYYY-MM-DD'),
                   t.start_time,
                   s.first_name || ' ' || s.last_name
            FROM APPOINTMENT a
            JOIN TIMESLOT t ON a.slot_id  = t.slot_id
            JOIN STAFF    s ON a.staff_id = s.staff_id
            WHERE a.qr_code_token = :1
            """,
            [qr_token],
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    except Exception:
        conn.rollback()
        cursor.close()
        conn.close()
        raise


def get_appointments_by_doctor_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.first_name || ' ' || s.last_name AS doctor_name,
               COUNT(a.appointment_id) AS appt_count
        FROM APPOINTMENT a
        JOIN STAFF s ON a.staff_id = s.staff_id
        WHERE s.role = 'DOCTOR'
        GROUP BY s.first_name || ' ' || s.last_name
        ORDER BY appt_count DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def cancel_appointment(patient_id, appointment_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT a.appointment_id, a.slot_id, a.status
            FROM APPOINTMENT a
            WHERE a.appointment_id = :1 AND a.patient_id = :2
            FOR UPDATE
            """,
            [appointment_id, patient_id],
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return None
        _, slot_id, status = row
        if status in ("COMPLETED", "CANCELLED", "NO_SHOW"):
            conn.rollback()
            return False

        cursor.execute(
            "UPDATE APPOINTMENT SET status = 'CANCELLED' WHERE appointment_id = :1",
            [appointment_id],
        )
        cursor.execute(
            "UPDATE TIMESLOT SET is_available = 1 WHERE slot_id = :1",
            [slot_id],
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_daily_appointment_counts(days=30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT TO_CHAR(t.slot_date, 'YYYY-MM-DD') AS day_label,
               COUNT(a.appointment_id) AS appt_count
        FROM APPOINTMENT a
        JOIN TIMESLOT t ON a.slot_id = t.slot_id
        WHERE t.slot_date >= TRUNC(SYSDATE) - :1
          AND t.slot_date <  TRUNC(SYSDATE) + 1
        GROUP BY TO_CHAR(t.slot_date, 'YYYY-MM-DD')
        ORDER BY day_label
        """,
        [days],
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
