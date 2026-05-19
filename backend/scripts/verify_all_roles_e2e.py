"""Verify login + role-gated APIs for patient, doctor, admin seed accounts."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app import create_app

ACCOUNTS = [
    ("karabo.mabena", "Clinic@123", "PATIENT", [
        ("GET", "/api/v1/patient/dashboard/"),
        ("GET", "/api/v1/patient/profile/"),
        ("GET", "/api/v1/appointments/upcoming/"),
        ("GET", "/api/v1/doctors/"),
    ]),
    ("dr.mokoena", "Clinic@123", "DOCTOR", [
        ("GET", "/api/v1/notifications/"),
    ]),
    ("nurse.molefe", "Clinic@123", "NURSE", [
        ("GET", "/api/v1/notifications/"),
    ]),
    ("admin.ndlovu", "Clinic@123", "ADMIN", [
        ("GET", "/api/v1/admin/reports/summary/"),
        ("GET", "/api/v1/admin/users/"),
        ("GET", "/api/v1/admin/departments/"),
    ]),
]


def login(client, username, password):
    r = client.post("/api/v1/auth/login/", json={"username": username, "password": password})
    if r.status_code != 200:
        return None, r.get_json()
    return r.get_json().get("access"), r.get_json()


def main():
    app = create_app()
    client = app.test_client()
    failed = 0

    for username, password, role, endpoints in ACCOUNTS:
        print(f"\n=== {username} ({role}) ===")
        token, body = login(client, username, password)
        if not token:
            print(f"[FAIL] login: {body}")
            failed += 1
            continue
        print("[OK] login, role=", body.get("role"))
        headers = {"Authorization": f"Bearer {token}"}
        for method, path in endpoints:
            r = client.open(path, method=method, headers=headers)
            ok = r.status_code < 400
            print(f"  {'[OK]' if ok else '[FAIL]'} {method} {path} -> {r.status_code}")
            if not ok:
                print("       ", r.get_json())
                failed += 1

    if failed:
        print(f"\n[FAIL] {failed} check(s) failed")
        return 1
    print("\n[OK] All role API checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
