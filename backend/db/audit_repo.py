from db.oracle_connection import get_connection


def log_action(user_id, action, table_affected, record_id, ip_address=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO AUDIT_LOG
            (user_id, action, table_affected, record_affected_id, ip_address)
        VALUES (:1, :2, :3, :4, :5)
        """,
        [user_id, action, table_affected, record_id, ip_address],
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_audit_log(page=1, per_page=20, user_filter=None,
                  action_filter=None, date_from=None, date_to=None):
    offset = (page - 1) * per_page
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if user_filter:
        conditions.append("ua.username LIKE :usr")
        params.append(f"%{user_filter}%")
    if action_filter:
        conditions.append("al.action = :act")
        params.append(action_filter.upper())
    if date_from:
        conditions.append("TRUNC(al.log_timestamp) >= TO_DATE(:df, 'YYYY-MM-DD')")
        params.append(date_from)
    if date_to:
        conditions.append("TRUNC(al.log_timestamp) <= TO_DATE(:dt, 'YYYY-MM-DD')")
        params.append(date_to)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    cursor.execute(
        f"""
        SELECT al.audit_log_id,
               ua.username,
               al.action,
               al.log_timestamp,
               al.ip_address,
               al.table_affected || ' #' || al.record_affected_id AS detail
        FROM AUDIT_LOG al
        JOIN USER_ACCOUNT ua ON al.user_id = ua.user_account_id
        {where_clause}
        ORDER BY al.log_timestamp DESC
        OFFSET :off ROWS FETCH NEXT :lim ROWS ONLY
        """,
        params + [offset, per_page],
    )
    rows = cursor.fetchall()

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM AUDIT_LOG al
        JOIN USER_ACCOUNT ua ON al.user_id = ua.user_account_id
        {where_clause}
        """,
        params,
    )
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return rows, total


def get_admin_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM PATIENT")
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM STAFF WHERE role = 'DOCTOR'")
    total_doctors = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM APPOINTMENT a
        JOIN TIMESLOT t ON a.slot_id = t.slot_id
        WHERE TRUNC(t.slot_date) = TRUNC(SYSDATE)
        """
    )
    appointments_today = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM APPOINTMENT WHERE status = 'CANCELLED'
        """
    )
    cancelled_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM APPOINTMENT")
    total_appointments = cursor.fetchone()[0]

    cancellation_rate = (
        round(cancelled_count / total_appointments * 100, 2)
        if total_appointments > 0 else 0.0
    )

    cursor.close()
    conn.close()
    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "appointments_today": appointments_today,
        "cancellation_rate": cancellation_rate,
    }


def get_appointments_by_doctor():
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
    labels = [r[0] for r in rows]
    data = [r[1] for r in rows]
    return {"labels": labels, "data": data}


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
    labels = [r[0] for r in rows]
    data = [r[1] for r in rows]
    return {"labels": labels, "data": data}
