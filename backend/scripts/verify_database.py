"""
Phase 1 - Oracle database readiness check.

Verifies connectivity, schema tables, seed row counts, and demo login accounts.
Auto-fixes demo passwords when they still use the CHANGEME placeholder.

Usage (from backend/):
    python scripts/verify_database.py
    python scripts/verify_database.py --fix-passwords
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from db.oracle_connection import get_connection  # noqa: E402

REQUIRED_TABLES = [
    "PATIENT",
    "TIMESLOT",
    "DEPARTMENT",
    "PATIENT_CONTACT",
    "STAFF",
    "DOCTOR",
    "USER_ACCOUNT",
    "APPOINTMENT",
    "AUDIT_LOG",
    "QUEUE_ENTRY",
    "MEDICAL_RECORD",
    "NOTIFICATION",
]

MIN_ROW_COUNTS = {
    "DEPARTMENT": 5,
    "STAFF": 6,
    "DOCTOR": 3,
    "PATIENT": 8,
    "USER_ACCOUNT": 12,
    "TIMESLOT": 12,
    "APPOINTMENT": 9,
}

DEMO_ACCOUNTS = [
    ("karabo.mabena", "PATIENT"),
    ("dr.mokoena", "DOCTOR"),
    ("nurse.molefe", "NURSE"),
    ("admin.ndlovu", "ADMIN"),
]


def table_exists(cursor, name):
    cursor.execute(
        """
        SELECT COUNT(*) FROM user_tables
        WHERE UPPER(table_name) = UPPER(:1)
        """,
        [name],
    )
    return cursor.fetchone()[0] > 0


def count_rows(cursor, table):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]


def check_demo_accounts(cursor):
    issues = []
    for username, role in DEMO_ACCOUNTS:
        cursor.execute(
            """
            SELECT password_hash, role, status
            FROM USER_ACCOUNT
            WHERE username = :1
            """,
            [username],
        )
        row = cursor.fetchone()
        if not row:
            issues.append(f"Missing demo account: {username} ({role})")
            continue
        password_hash, db_role, status = row
        if db_role != role:
            issues.append(f"{username}: expected role {role}, got {db_role}")
        if status != "ACTIVE":
            issues.append(f"{username}: status is {status}, expected ACTIVE")
        if password_hash == "CHANGEME":
            issues.append(f"{username}: password still CHANGEME — run reset_seed_passwords.py")
    return issues


def fix_passwords():
    import subprocess

    script = os.path.join(os.path.dirname(__file__), "reset_seed_passwords.py")
    subprocess.run([sys.executable, script], check=True)


def main():
    fix = "--fix-passwords" in sys.argv
    failed = 0

    print("=" * 60)
    print("PHASE 1: DATABASE")
    print("=" * 60)

    if not os.getenv("ORA_PASSWORD"):
        print("[FAIL] ORA_PASSWORD is empty in backend/.env")
        return 1

    print(
        f"\n1. Connectivity ({os.getenv('ORA_HOST', 'localhost')}:"
        f"{os.getenv('ORA_PORT', '1521')}/{os.getenv('ORA_SID', 'XE')})"
    )
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM DUAL")
        cur.fetchone()
        print("   [OK] Connected to Oracle")
    except Exception as exc:
        print(f"   [FAIL] {type(exc).__name__}: {exc}")
        return 1

    print("\n2. Schema tables")
    missing_tables = []
    for table in REQUIRED_TABLES:
        if table_exists(cur, table):
            print(f"   [OK] {table}")
        else:
            print(f"   [FAIL] {table} — missing")
            missing_tables.append(table)
            failed += 1

    if missing_tables:
        print("\n   Run sql/00_RUN_ALL.sql in SQL Developer, then re-run this script.")
        cur.close()
        conn.close()
        return 1

    print("\n3. Seed data row counts")
    for table, minimum in MIN_ROW_COUNTS.items():
        count = count_rows(cur, table)
        if count >= minimum:
            print(f"   [OK] {table}: {count} rows (min {minimum})")
        else:
            print(f"   [FAIL] {table}: {count} rows (expected >= {minimum})")
            failed += 1

    print("\n4. Demo login accounts")
    account_issues = check_demo_accounts(cur)
    if account_issues:
        for issue in account_issues:
            print(f"   [WARN] {issue}")
        if fix or any("CHANGEME" in i for i in account_issues):
            print("\n   Applying password fix (reset_seed_passwords)...")
            cur.close()
            conn.close()
            fix_passwords()
            conn = get_connection()
            cur = conn.cursor()
            account_issues = check_demo_accounts(cur)
            if account_issues:
                for issue in account_issues:
                    print(f"   [FAIL] {issue}")
                    failed += 1
            else:
                print("   [OK] Demo passwords updated to Clinic@123")
        else:
            print("   Re-run with --fix-passwords to auto-update CHANGEME hashes")
            failed += len(account_issues)
    else:
        print("   [OK] All demo accounts present with real password hashes")

    cur.close()
    conn.close()

    print("\n" + "=" * 60)
    if failed:
        print(f"PHASE 1: FAILED ({failed} issue(s))")
        return 1
    print("PHASE 1: PASSED - database ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
