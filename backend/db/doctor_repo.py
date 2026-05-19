from db.oracle_connection import get_connection


def get_all_doctors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.staff_id,
               s.first_name || ' ' || s.last_name AS doctor_name,
               d.specialisation,
               s.department_id
        FROM STAFF s
        JOIN DOCTOR d ON s.staff_id = d.staff_id
        WHERE s.role = 'DOCTOR'
        ORDER BY s.last_name, s.first_name
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_doctor_by_id(staff_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.staff_id,
               s.first_name || ' ' || s.last_name AS doctor_name,
               d.specialisation,
               s.department_id,
               s.email,
               s.contact_number
        FROM STAFF s
        JOIN DOCTOR d ON s.staff_id = d.staff_id
        WHERE s.staff_id = :1
          AND s.role = 'DOCTOR'
        """,
        [staff_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_departments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT dep.department_id,
               dep.department_name,
               s.first_name || ' ' || s.last_name AS head_doctor_name,
               (SELECT COUNT(*) FROM STAFF st WHERE st.department_id = dep.department_id) AS staff_count
        FROM DEPARTMENT dep
        LEFT JOIN STAFF s ON dep.head_staff_id = s.staff_id
        ORDER BY dep.department_name
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_department_by_id(dept_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT dep.department_id,
               dep.department_name,
               s.first_name || ' ' || s.last_name AS head_doctor_name,
               (SELECT COUNT(*) FROM STAFF st WHERE st.department_id = dep.department_id) AS staff_count
        FROM DEPARTMENT dep
        LEFT JOIN STAFF s ON dep.head_staff_id = s.staff_id
        WHERE dep.department_id = :1
        """,
        [dept_id],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def create_department(name, head_doctor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO DEPARTMENT (department_name, head_staff_id)
        VALUES (:1, :2)
        """,
        [name, head_doctor_id],
    )
    conn.commit()

    cursor.execute(
        "SELECT department_id FROM DEPARTMENT WHERE department_name = :1",
        [name],
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def update_department(dept_id, **fields):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT department_name, head_staff_id FROM DEPARTMENT WHERE department_id = :1",
        [dept_id],
    )
    existing = cursor.fetchone()
    if not existing:
        cursor.close()
        conn.close()
        return None

    current_name, current_head = existing
    new_name = fields.get("name", current_name)
    new_head = fields.get("head_doctor_id", current_head)

    cursor.execute(
        """
        UPDATE DEPARTMENT
        SET department_name = :1, head_staff_id = :2
        WHERE department_id = :3
        """,
        [new_name, new_head, dept_id],
    )
    conn.commit()
    cursor.close()
    conn.close()
    return dept_id


def get_department_staff_count(dept_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM STAFF WHERE department_id = :1",
        [dept_id],
    )
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def delete_department(dept_id):
    """
    Returns 'HAS_STAFF' signal if the department has active staff.
    Returns True on successful deletion.
    Returns None if department not found.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT department_id FROM DEPARTMENT WHERE department_id = :1",
        [dept_id],
    )
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return None

    cursor.execute(
        "SELECT COUNT(*) FROM STAFF WHERE department_id = :1",
        [dept_id],
    )
    staff_count = cursor.fetchone()[0]
    if staff_count > 0:
        cursor.close()
        conn.close()
        return "HAS_STAFF"

    cursor.execute(
        "DELETE FROM DEPARTMENT WHERE department_id = :1",
        [dept_id],
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True
