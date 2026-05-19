"""End-to-end: register patient -> Oracle rows -> login -> patient API."""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app import create_app
from db.oracle_connection import get_connection


def main():
    suffix = uuid.uuid4().hex[:6]
    student_number = f"{uuid.uuid4().int % 100_000_000:08d}"
    username = f"test.{suffix}.user"
    email = f"{student_number}@mynwu.ac.za"
    password = "TestPass123!"

    app = create_app()
    client = app.test_client()

    print("=== 1. Health ===")
    r = client.get("/api/v1/health/")
    print(r.status_code, r.get_json())
    if r.get_json().get("database") != "connected":
        print("[FAIL] Database not connected")
        return 1

    print("\n=== 2. Register ===")
    r = client.post(
        "/api/v1/auth/register/",
        json={
            "username": username,
            "student_number": student_number,
            "email": email,
            "password": password,
        },
    )
    body = r.get_json()
    print(r.status_code, body)
    if r.status_code != 201:
        print("[FAIL] Registration failed")
        return 1

    print("\n=== 3. Oracle PATIENT + USER_ACCOUNT ===")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.patient_id, p.student_number, p.first_name, p.last_name, p.email,
               ua.user_account_id, ua.username, ua.role, ua.status
        FROM PATIENT p
        JOIN USER_ACCOUNT ua ON ua.patient_id = p.patient_id
        WHERE ua.username = :1
        """,
        [username],
    )
    row = cur.fetchone()
    if row and row[1] != student_number:
        print(f"[WARN] student_number mismatch: expected {student_number}, got {row[1]}")
    cur.close()
    conn.close()
    if not row:
        print(f"[FAIL] No rows in Oracle for username {username}")
        return 1
    print("[OK] Oracle row:", row)

    print("\n=== 4. Login ===")
    r = client.post(
        "/api/v1/auth/login/",
        json={"username": username, "password": password},
    )
    body = r.get_json()
    print(r.status_code, {k: body.get(k) for k in ("role", "access") if k in body})
    if r.status_code != 200 or not body.get("access"):
        print("[FAIL] Login failed")
        return 1
    token = body["access"]

    print("\n=== 5. Patient dashboard API ===")
    r = client.get(
        "/api/v1/patient/dashboard/",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(r.status_code, r.get_json())

    print("\n=== 6. Patient profile API ===")
    r = client.get(
        "/api/v1/patient/profile/",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(r.status_code, r.get_json())

    print("\n[OK] End-to-end registration flow verified.")
    print(f"    Test user: {username} / {password}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
