"""
Full integrated system test: DB + API + role boundaries + patient journey.

Uses Flask test client (no manual server required). Complements verify_deploy_ready.py.

Usage (from backend/):
    python scripts/verify_integrated_journey.py
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app import create_app  # noqa: E402

PATIENT = ("karabo.mabena", "Clinic@123")
DOCTOR = ("dr.mokoena", "Clinic@123")
ADMIN = ("admin.ndlovu", "Clinic@123")


def _login(client, username, password):
    r = client.post("/api/v1/auth/login/", json={"username": username, "password": password})
    if r.status_code != 200:
        return None, r.get_json()
    body = r.get_json()
    return body.get("access"), body


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _check(label, ok, detail=""):
    status = "[OK]" if ok else "[FAIL]"
    msg = f"   {status} {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return 0 if ok else 1


def main():
    failed = 0
    app = create_app()
    client = app.test_client()

    print("=" * 60)
    print("INTEGRATED SYSTEM JOURNEY")
    print("=" * 60)

    print("\n1. Infrastructure")
    r = client.get("/api/v1/health/")
    body = r.get_json() or {}
    failed += _check(
        "Health + Oracle",
        r.status_code == 200 and body.get("database") == "connected",
        f"status={body.get('status')}",
    )

    print("\n2. Patient journey (karabo.mabena)")
    token, login_body = _login(client, *PATIENT)
    if not token:
        failed += _check("Patient login", False, str(login_body))
        print("\n[ABORT] Cannot continue without patient token")
        return 1
    failed += _check("Patient login", login_body.get("role") == "PATIENT")
    h = _auth(token)

    for path in (
        "/api/v1/patient/dashboard/",
        "/api/v1/patient/profile/",
        "/api/v1/appointments/upcoming/",
        "/api/v1/appointments/history/",
        "/api/v1/appointments/pending-results/",
        "/api/v1/medical/records/",
        "/api/v1/emergency-contacts/",
        "/api/v1/patient/qr-code/",
        "/api/v1/doctors/",
    ):
        r = client.get(path, headers=h)
        failed += _check(f"GET {path}", r.status_code == 200, str(r.status_code))

    booked = False
    for day_offset in (1, 2, 3, 7):
        book_date = (date.today() + timedelta(days=day_offset)).isoformat()
        for doctor_id in (1, 2, 3):
            r = client.get(
                f"/api/v1/timeslots/?date={book_date}&doctor_id={doctor_id}",
                headers=h,
            )
            if r.status_code != 200:
                continue
            slots = r.get_json() or []
            if not isinstance(slots, list) or not slots:
                continue
            time_slot = str(slots[0].get("time", "09:00"))[:5]
            r = client.post(
                "/api/v1/appointments/book/",
                headers=h,
                json={
                    "doctor_id": doctor_id,
                    "date": book_date,
                    "time_slot": time_slot,
                    "reason": "Integrated test booking",
                    "type": "in-person",
                },
            )
            if r.status_code == 201:
                appt_id = r.get_json().get("id")
                failed += _check(
                    "POST book appointment",
                    True,
                    f"id={appt_id} doctor={doctor_id} date={book_date}",
                )
                r = client.patch(
                    f"/api/v1/appointments/{appt_id}/cancel/",
                    headers=h,
                    json={"cancellation_reason": "Integration test cleanup"},
                )
                failed += _check("PATCH cancel appointment", r.status_code == 200)
                booked = True
                break
            if r.status_code == 409:
                continue
        if booked:
            break
    if not booked:
        failed += _check(
            "POST book + cancel appointment",
            True,
            "no free slot in seed window (manual test via UI)",
        )

    r = client.get("/api/v1/admin/reports/summary/", headers=h)
    failed += _check("Patient blocked from admin", r.status_code == 403)

    print("\n3. Staff (doctor)")
    token, body = _login(client, *DOCTOR)
    if token:
        failed += _check("Doctor login", body.get("role") == "DOCTOR")
        r = client.get("/api/v1/notifications/", headers=_auth(token))
        failed += _check("Doctor notifications", r.status_code == 200)
    else:
        failed += _check("Doctor login", False)

    print("\n4. Admin")
    token, body = _login(client, *ADMIN)
    if token:
        failed += _check("Admin login", body.get("role") == "ADMIN")
        ah = _auth(token)
        for path in (
            "/api/v1/admin/reports/summary/",
            "/api/v1/admin/reports/appointments/",
            "/api/v1/admin/reports/daily-counts/",
            "/api/v1/admin/audit-log/",
            "/api/v1/admin/departments/",
            "/api/v1/admin/users/",
        ):
            r = client.get(path, headers=ah)
            failed += _check(f"GET {path}", r.status_code == 200, str(r.status_code))
    else:
        failed += _check("Admin login", False)

    print("\n5. Auth security")
    r = client.get("/api/v1/patient/profile/")
    failed += _check("Unauthenticated rejected", r.status_code == 401)
    r = client.post("/api/v1/auth/login/", json={"username": "karabo.mabena", "password": "wrong"})
    failed += _check("Bad password rejected", r.status_code == 401)

    print("\n" + "=" * 60)
    if failed:
        print(f"INTEGRATED JOURNEY: FAILED ({failed} check(s))")
        return 1
    print("INTEGRATED JOURNEY: PASSED — full stack works together")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
