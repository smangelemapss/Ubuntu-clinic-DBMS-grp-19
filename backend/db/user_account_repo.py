from db.oracle_connection import get_connection


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_account_id, username, password_hash, patient_id, staff_id, role, status
        FROM USER_ACCOUNT
        WHERE username = :1
        """,
        [username],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_user_by_id(user_id):
    """Returns (user_account_id, username, email, role, status, patient_id, staff_id)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ua.user_account_id,
               ua.username,
               COALESCE(p.email, s.email) AS email,
               ua.role,
               ua.status,
               ua.patient_id,
               ua.staff_id
        FROM USER_ACCOUNT ua
        LEFT JOIN PATIENT p ON ua.patient_id = p.patient_id
        LEFT JOIN STAFF   s ON ua.staff_id   = s.staff_id
        WHERE ua.user_account_id = :1
        """,
        [user_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_patient_user(username, password_hash, patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, role, status)
        VALUES (:1, :2, :3, 'PATIENT', 'ACTIVE')
        """,
        [username, password_hash, patient_id],
    )
    conn.commit()

    # Fetch the newly created user id
    cursor.execute(
        "SELECT user_account_id FROM USER_ACCOUNT WHERE username = :1",
        [username],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def update_user_status(user_id, is_active):
    status = "ACTIVE" if is_active else "DISABLED"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE USER_ACCOUNT SET status = :1 WHERE user_account_id = :2",
        [status, user_id],
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_user_role(user_id, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE USER_ACCOUNT SET role = :1 WHERE user_account_id = :2",
        [role, user_id],
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_users(role_filter=None, page=1, per_page=20):
    offset = (page - 1) * per_page
    conn = get_connection()
    cursor = conn.cursor()

    if role_filter:
        cursor.execute(
            """
            SELECT ua.user_account_id,
                   ua.username,
                   COALESCE(p.email, s.email) AS email,
                   ua.role,
                   ua.status,
                   ua.patient_id,
                   ua.staff_id
            FROM USER_ACCOUNT ua
            LEFT JOIN PATIENT p ON ua.patient_id = p.patient_id
            LEFT JOIN STAFF   s ON ua.staff_id   = s.staff_id
            WHERE ua.role = :1
            ORDER BY ua.user_account_id
            OFFSET :2 ROWS FETCH NEXT :3 ROWS ONLY
            """,
            [role_filter, offset, per_page],
        )
    else:
        cursor.execute(
            """
            SELECT ua.user_account_id,
                   ua.username,
                   COALESCE(p.email, s.email) AS email,
                   ua.role,
                   ua.status,
                   ua.patient_id,
                   ua.staff_id
            FROM USER_ACCOUNT ua
            LEFT JOIN PATIENT p ON ua.patient_id = p.patient_id
            LEFT JOIN STAFF   s ON ua.staff_id   = s.staff_id
            ORDER BY ua.user_account_id
            OFFSET :1 ROWS FETCH NEXT :2 ROWS ONLY
            """,
            [offset, per_page],
        )

    rows = cursor.fetchall()

    # Total count
    if role_filter:
        cursor.execute(
            "SELECT COUNT(*) FROM USER_ACCOUNT WHERE role = :1",
            [role_filter],
        )
    else:
        cursor.execute("SELECT COUNT(*) FROM USER_ACCOUNT")

    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return rows, total
