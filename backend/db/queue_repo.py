from db.oracle_connection import get_connection


def get_queue_for_appointment(appointment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT queue_entry_id, appointment_id, status,
               checked_in_at, consult_start_time, consult_end_time, room_number
        FROM QUEUE_ENTRY
        WHERE appointment_id = :1
        """,
        [appointment_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_queue_entry(appointment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO QUEUE_ENTRY (appointment_id, status)
        VALUES (:1, 'WAITING')
        """,
        [appointment_id],
    )
    conn.commit()

    cursor.execute(
        "SELECT queue_entry_id FROM QUEUE_ENTRY WHERE appointment_id = :1",
        [appointment_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def update_queue_status(queue_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE QUEUE_ENTRY SET status = :1 WHERE queue_entry_id = :2",
        [status, queue_id],
    )
    conn.commit()
    cursor.close()
    conn.close()
