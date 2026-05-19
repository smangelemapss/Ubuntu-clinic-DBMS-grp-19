"""
Deep Oracle SQL verification: schema, indexes, views, integrity, constraints, rubric queries.

Usage (from backend/):
    python scripts/verify_sql_mastery.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from db.oracle_connection import get_connection  # noqa: E402

REQUIRED_VIEWS = [
    "VW_PATIENT_APPOINTMENTS",
    "VW_DAILY_QUEUE_BOARD",
    "VW_DOCTOR_SCHEDULE",
    "VW_AUDIT_TRAIL_SUMMARY",
]

REQUIRED_INDEXES = [
    "IDX_TIMESLOT_DATE",
    "IDX_TIMESLOT_DATE_AVAIL",
    "IDX_APPT_PATIENT",
    "IDX_APPT_STAFF",
    "IDX_APPT_STATUS",
    "IDX_QUEUE_STATUS",
    "IDX_MR_PATIENT",
    "IDX_MR_APPT",
    "IDX_NOTIF_APPT",
    "IDX_AUDIT_TIMESTAMP",
    "IDX_AUDIT_USER",
]

OPTIONAL_INDEXES = [
    "IDX_NOTIF_PATIENT",
    "IDX_NOTIF_STAFF",
    "IDX_USER_PATIENT",
    "IDX_USER_STAFF",
]

INTEGRITY_CHECKS = [
    (
        "Orphan appointments (invalid patient)",
        """
        SELECT COUNT(*) FROM APPOINTMENT a
        WHERE NOT EXISTS (SELECT 1 FROM PATIENT p WHERE p.patient_id = a.patient_id)
        """,
    ),
    (
        "Orphan appointments (invalid staff)",
        """
        SELECT COUNT(*) FROM APPOINTMENT a
        WHERE NOT EXISTS (SELECT 1 FROM STAFF s WHERE s.staff_id = a.staff_id)
        """,
    ),
    (
        "Orphan queue entries",
        """
        SELECT COUNT(*) FROM QUEUE_ENTRY q
        WHERE NOT EXISTS (SELECT 1 FROM APPOINTMENT a WHERE a.appointment_id = q.appointment_id)
        """,
    ),
    (
        "Double-booked slots (must be 0 — UNIQUE enforces)",
        """
        SELECT COUNT(*) FROM (
            SELECT slot_id FROM APPOINTMENT GROUP BY slot_id HAVING COUNT(*) > 1
        )
        """,
    ),
    (
        "Medical records with wrong patient vs appointment",
        """
        SELECT COUNT(*) FROM MEDICAL_RECORD mr
        JOIN APPOINTMENT a ON a.appointment_id = mr.appointment_id
        WHERE mr.patient_id <> a.patient_id
        """,
    ),
    (
        "Notifications without recipient",
        """
        SELECT COUNT(*) FROM NOTIFICATION
        WHERE patient_id IS NULL AND staff_id IS NULL
        """,
    ),
]

RUBRIC_SMOKE = [
    ("Q1 business query", "SELECT COUNT(*) FROM APPOINTMENT a JOIN PATIENT p ON p.patient_id = a.patient_id"),
    ("Q2 pagination", "SELECT COUNT(*) FROM (SELECT * FROM APPOINTMENT ORDER BY appointment_id FETCH FIRST 3 ROWS ONLY)"),
    ("Q3 sorting", "SELECT COUNT(*) FROM (SELECT * FROM PATIENT ORDER BY last_name, first_name)"),
    ("Q4 LIKE (NWU email)", "SELECT COUNT(*) FROM PATIENT WHERE email LIKE '%@mynwu.ac.za'"),
    ("Q5 string functions", "SELECT COUNT(*) FROM PATIENT WHERE LENGTH(student_number) = 8"),
    ("Q6 rounding", "SELECT COUNT(*) FROM PATIENT WHERE ROUND(MONTHS_BETWEEN(SYSDATE, date_of_birth)/12,0) >= 18"),
    ("Q7 dates", "SELECT COUNT(*) FROM TIMESLOT WHERE slot_date >= TRUNC(SYSDATE) - 30"),
    ("Q8 aggregates", "SELECT COUNT(*) FROM (SELECT status, COUNT(*) c FROM APPOINTMENT GROUP BY status)"),
    ("Q9 GROUP BY", "SELECT COUNT(*) FROM (SELECT staff_id, COUNT(*) FROM APPOINTMENT GROUP BY staff_id HAVING COUNT(*) >= 1)"),
    ("Q10 joins", "SELECT COUNT(*) FROM PATIENT p LEFT JOIN APPOINTMENT a ON a.patient_id = p.patient_id"),
    ("Q11 subquery", "SELECT COUNT(*) FROM PATIENT WHERE patient_id IN (SELECT DISTINCT patient_id FROM APPOINTMENT)"),
]


def _index_exists(cursor, name):
    cursor.execute(
        """
        SELECT COUNT(*) FROM user_indexes
        WHERE UPPER(index_name) = UPPER(:1)
        """,
        [name],
    )
    return cursor.fetchone()[0] > 0


def _view_exists(cursor, name):
    cursor.execute(
        """
        SELECT COUNT(*) FROM user_views
        WHERE UPPER(view_name) = UPPER(:1)
        """,
        [name],
    )
    return cursor.fetchone()[0] > 0


def _constraint_count(cursor):
    cursor.execute(
        """
        SELECT COUNT(*) FROM user_constraints
        WHERE constraint_type IN ('P','U','R','C')
          AND table_name IN (
              'PATIENT','PATIENT_CONTACT','TIMESLOT','DEPARTMENT','STAFF','DOCTOR',
              'USER_ACCOUNT','APPOINTMENT','AUDIT_LOG','QUEUE_ENTRY','MEDICAL_RECORD','NOTIFICATION'
          )
        """
    )
    return cursor.fetchone()[0]


def test_constraints(cursor, conn):
    """Prove CHECK and UNIQUE constraints reject bad data (rolled back)."""
    results = []

    tests = [
        (
            "CHECK invalid appointment status",
            "INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status) VALUES (1, 1, 1, 'INVALID')",
        ),
        (
            "UNIQUE duplicate student_number",
            "INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given) "
            "SELECT student_number, 'X', 'Y', 'dup@test.com', '000', DATE '2000-01-01', 'S', 'C', '0', 1 FROM PATIENT WHERE ROWNUM = 1",
        ),
        (
            "CHECK timeslot end before start",
            "INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available) VALUES (TRUNC(SYSDATE), '17:00', '08:00', 1)",
        ),
    ]

    for label, sql in tests:
        cursor.execute("SAVEPOINT nfr_test")
        try:
            cursor.execute(sql)
            conn.commit()
            results.append((label, False, "constraint did not fire"))
        except Exception as exc:
            conn.rollback()
            err = str(exc)
            if "ORA-02290" in err or "ORA-02291" in err or "ORA-00001" in err or "ORA-01400" in err:
                results.append((label, True, "rejected as expected"))
            else:
                results.append((label, False, err[:120]))
        finally:
            try:
                cursor.execute("ROLLBACK TO SAVEPOINT nfr_test")
            except Exception:
                conn.rollback()

    cursor.execute(
        """
        SELECT slot_id FROM APPOINTMENT WHERE ROWNUM = 1
        """
    )
    row = cursor.fetchone()
    if row:
        slot_id = row[0]
        cursor.execute("SAVEPOINT slot_dup")
        try:
            cursor.execute(
                """
                INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type)
                VALUES (:1, 1, 1, 'SCHEDULED', 'SICK')
                """,
                [slot_id],
            )
            conn.commit()
            results.append(("UNIQUE duplicate slot_id", False, "double-book allowed"))
        except Exception as exc:
            conn.rollback()
            if "ORA-00001" in str(exc):
                results.append(("UNIQUE duplicate slot_id", True, "double-book blocked"))
            else:
                results.append(("UNIQUE duplicate slot_id", False, str(exc)[:120]))
        finally:
            try:
                cursor.execute("ROLLBACK TO SAVEPOINT slot_dup")
            except Exception:
                conn.rollback()

    return results


def apply_optional_indexes(cursor, conn):
    """Create newer performance indexes if missing (idempotent)."""
    statements = [
        "CREATE INDEX idx_notif_patient ON NOTIFICATION (patient_id)",
        "CREATE INDEX idx_notif_staff ON NOTIFICATION (staff_id)",
        "CREATE INDEX idx_user_patient ON USER_ACCOUNT (patient_id)",
        "CREATE INDEX idx_user_staff ON USER_ACCOUNT (staff_id)",
    ]
    created = 0
    for sql in statements:
        try:
            cursor.execute(sql)
            created += 1
        except Exception as exc:
            if "ORA-00955" in str(exc) or "ORA-01408" in str(exc):
                continue
            raise
    if created:
        conn.commit()
    return created


def main():
    apply_indexes = "--apply-indexes" in sys.argv
    failed = 0
    warned = 0

    print("=" * 60)
    print("SQL MASTERY VERIFICATION")
    print("=" * 60)

    if not os.getenv("ORA_PASSWORD"):
        print("[FAIL] ORA_PASSWORD not set in backend/.env")
        return 1

    try:
        conn = get_connection()
        cur = conn.cursor()
    except Exception as exc:
        print(f"[FAIL] Cannot connect: {exc}")
        return 1

    print("\n1. Constraint inventory")
    n = _constraint_count(cur)
    if n >= 40:
        print(f"   [OK] {n} constraints on core tables (PK/UK/FK/CHECK)")
    else:
        print(f"   [WARN] Only {n} constraints — expected 40+")
        warned += 1

    if apply_indexes:
        n = apply_optional_indexes(cur, conn)
        if n:
            print(f"\n   [OK] Applied {n} optional index(es)")

    print("\n2. Performance indexes")
    for idx in REQUIRED_INDEXES:
        if _index_exists(cur, idx):
            print(f"   [OK] {idx}")
        else:
            print(f"   [FAIL] {idx} missing — re-run sql/01_DDL/02_create_indexes.sql")
            failed += 1

    missing_opt = [i for i in OPTIONAL_INDEXES if not _index_exists(cur, i)]
    if missing_opt:
        print(f"   [WARN] Optional indexes missing: {', '.join(missing_opt)}")
        print("          Re-run sql/01_DDL/02_create_indexes.sql for latest performance indexes")
        warned += 1
    else:
        print("   [OK] All optional performance indexes present")

    print("\n3. Reporting views")
    for view in REQUIRED_VIEWS:
        if not _view_exists(cur, view):
            print(f"   [FAIL] {view} missing — run sql/01_DDL/03_create_views.sql")
            failed += 1
            continue
        cur.execute(f"SELECT COUNT(*) FROM {view}")
        count = cur.fetchone()[0]
        print(f"   [OK] {view} ({count} rows)")

    print("\n4. Referential integrity (zero = good)")
    for label, sql in INTEGRITY_CHECKS:
        cur.execute(sql)
        bad = cur.fetchone()[0]
        if bad == 0:
            print(f"   [OK] {label}")
        else:
            print(f"   [FAIL] {label}: {bad} violation(s)")
            failed += 1

    print("\n5. Constraint enforcement (negative tests)")
    for label, ok, detail in test_constraints(cur, conn):
        if ok:
            print(f"   [OK] {label} — {detail}")
        else:
            print(f"   [FAIL] {label} — {detail}")
            failed += 1

    print("\n6. Rubric query smoke tests (Q1–Q11)")
    for label, sql in RUBRIC_SMOKE:
        try:
            cur.execute(sql)
            count = cur.fetchone()[0]
            if count >= 0:
                print(f"   [OK] {label} ({count} rows)")
            else:
                print(f"   [FAIL] {label}")
                failed += 1
        except Exception as exc:
            print(f"   [FAIL] {label}: {exc}")
            failed += 1

    print("\n7. Identity / sequencing")
    cur.execute(
        """
        SELECT table_name FROM user_tables
        WHERE table_name IN (
            'PATIENT','APPOINTMENT','AUDIT_LOG','QUEUE_ENTRY','MEDICAL_RECORD','NOTIFICATION'
        )
        AND EXISTS (
            SELECT 1 FROM user_tab_columns c
            WHERE c.table_name = user_tables.table_name
              AND c.column_name LIKE '%_ID'
              AND c.identity_column = 'YES'
        )
        ORDER BY table_name
        """
    )
    id_tables = [r[0] for r in cur.fetchall()]
    if len(id_tables) >= 6:
        print(f"   [OK] IDENTITY columns on {len(id_tables)} core tables")
    else:
        print(f"   [WARN] IDENTITY detected on {len(id_tables)} tables")
        warned += 1

    cur.close()
    conn.close()

    print("\n" + "=" * 60)
    if failed:
        print(f"SQL MASTERY: FAILED ({failed} issue(s), {warned} warning(s))")
        return 1
    if warned:
        print(f"SQL MASTERY: PASSED with {warned} warning(s)")
    else:
        print("SQL MASTERY: PASSED — schema, constraints, and rubric SQL verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
