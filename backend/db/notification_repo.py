import json

from db.oracle_connection import get_connection


def _parse_notification_row(row):
    """
    Converts a raw NOTIFICATION row into the API shape.
    Row order: (notification_id, message, created_at, status, sent_at)
    message field stores JSON: {"title": "...", "text": "..."}
    PENDING = unread, SENT = read
    """
    notif_id, message, created_at, status, sent_at = row
    try:
        payload = json.loads(message)
    except (TypeError, ValueError):
        payload = {"title": "Notification", "text": message or ""}
    return {
        "id": notif_id,
        "title": payload.get("title", "Notification"),
        "text": payload.get("text", ""),
        "time": created_at.isoformat() if created_at else None,
        "read": status == "SENT",
    }


def get_notifications_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT n.notification_id, n.message, n.created_at, n.status, n.sent_at
        FROM NOTIFICATION n
        JOIN USER_ACCOUNT ua ON (
            (ua.patient_id IS NOT NULL AND n.patient_id = ua.patient_id)
            OR
            (ua.staff_id IS NOT NULL AND n.staff_id = ua.staff_id)
        )
        WHERE ua.user_account_id = :1
        ORDER BY n.created_at DESC
        """,
        [user_id],
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [_parse_notification_row(r) for r in rows]


def mark_notification_read(notification_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT n.notification_id
        FROM NOTIFICATION n
        JOIN USER_ACCOUNT ua ON (
            (ua.patient_id IS NOT NULL AND n.patient_id = ua.patient_id)
            OR
            (ua.staff_id IS NOT NULL AND n.staff_id = ua.staff_id)
        )
        WHERE n.notification_id = :1
          AND ua.user_account_id = :2
        """,
        [notification_id, user_id],
    )
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return False

    cursor.execute(
        """
        UPDATE NOTIFICATION
        SET status = 'SENT', sent_at = CURRENT_TIMESTAMP
        WHERE notification_id = :1
        """,
        [notification_id],
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True


def mark_all_notifications_read(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE NOTIFICATION n
        SET n.status = 'SENT', n.sent_at = CURRENT_TIMESTAMP
        WHERE n.status = 'PENDING'
          AND (
              n.patient_id IN (SELECT patient_id FROM USER_ACCOUNT WHERE user_account_id = :1 AND patient_id IS NOT NULL)
              OR
              n.staff_id IN (SELECT staff_id FROM USER_ACCOUNT WHERE user_account_id = :2 AND staff_id IS NOT NULL)
          )
        """,
        [user_id, user_id],
    )
    updated = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return updated


def delete_notification(notification_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT notification_id FROM NOTIFICATION WHERE notification_id = :1",
        [notification_id],
    )
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return False

    cursor.execute(
        "DELETE FROM NOTIFICATION WHERE notification_id = :1",
        [notification_id],
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True


def create_notification(user_id, title, text, appointment_id):
    """
    Stores title+text as JSON in the message field.
    Looks up patient_id or staff_id from USER_ACCOUNT.
    appointment_id is required due to the NOT NULL DB constraint.
    """
    if not appointment_id:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT patient_id, staff_id FROM USER_ACCOUNT WHERE user_account_id = :1",
        [user_id],
    )
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None

    patient_id, staff_id = row
    message = json.dumps({"title": title, "text": text})

    if patient_id:
        cursor.execute(
            """
            INSERT INTO NOTIFICATION
                (patient_id, appointment_id, channel, status, message)
            VALUES (:1, :2, 'EMAIL', 'PENDING', :3)
            """,
            [patient_id, appointment_id, message],
        )
    else:
        cursor.execute(
            """
            INSERT INTO NOTIFICATION
                (staff_id, appointment_id, channel, status, message)
            VALUES (:1, :2, 'EMAIL', 'PENDING', :3)
            """,
            [staff_id, appointment_id, message],
        )

    conn.commit()

    cursor.execute(
        """
        SELECT notification_id FROM NOTIFICATION
        WHERE message = :1
        ORDER BY notification_id DESC
        """,
        [message],
    )
    new_row = cursor.fetchone()
    cursor.close()
    conn.close()
    return new_row[0] if new_row else None
