"""
Update existing Oracle DB so demo patient karabo.mabena matches current app rules.

- PATIENT emails: {student_number}@mynwu.ac.za
- karabo.mabena: one upcoming SCHEDULED appointment (if missing)

Usage (from backend/):
    python scripts/patch_karabo_demo_seed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from db.oracle_connection import get_connection

KARABO_USERNAME = "karabo.mabena"
KARABO_PATIENT_ID = 1
KARABO_STUDENT_NUMBER = "10012345"
KARABO_EMAIL = f"{KARABO_STUDENT_NUMBER}@mynwu.ac.za"
UPCOMING_QR = "a1b2c3d4-karabo-upcoming-0001"


def main():
    conn = get_connection()
    cur = conn.cursor()

    print("=== 1. Update patient emails to @mynwu.ac.za ===")
    cur.execute(
        """
        UPDATE PATIENT
        SET email = student_number || '@mynwu.ac.za'
        WHERE email LIKE '%@student.nwu.ac.za'
           OR email NOT LIKE '%@mynwu.ac.za'
        """
    )
    print(f"   [OK] Updated {cur.rowcount} patient email(s)")

    cur.execute(
        "SELECT email FROM PATIENT WHERE patient_id = :1",
        [KARABO_PATIENT_ID],
    )
    row = cur.fetchone()
    print(f"   karabo.mabena email: {row[0] if row else 'NOT FOUND'}")

    print("\n=== 2. Upcoming appointment for karabo.mabena ===")
    cur.execute(
        """
        SELECT COUNT(*) FROM APPOINTMENT a
        JOIN TIMESLOT t ON a.slot_id = t.slot_id
        WHERE a.patient_id = :1
          AND a.status IN ('SCHEDULED', 'CONFIRMED')
          AND t.slot_date >= TRUNC(SYSDATE)
        """,
        [KARABO_PATIENT_ID],
    )
    upcoming = cur.fetchone()[0]
    if upcoming > 0:
        print(f"   [OK] Already has {upcoming} upcoming appointment(s) — skipped insert")
    else:
        cur.execute(
            """
            SELECT t.slot_id, t.slot_date, t.start_time
            FROM TIMESLOT t
            WHERE t.is_available = 1
              AND t.slot_date >= TRUNC(SYSDATE)
              AND NOT EXISTS (
                  SELECT 1 FROM APPOINTMENT a WHERE a.slot_id = t.slot_id
              )
            ORDER BY t.slot_date, t.start_time
            FETCH FIRST 1 ROW ONLY
            """,
        )
        slot = cur.fetchone()
        if not slot:
            print("   [WARN] No free future timeslot — book manually in the app")
        else:
            slot_id, slot_date, start_time = slot
            cur.execute(
                """
                INSERT INTO APPOINTMENT
                    (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
                VALUES (:1, :2, 1, 'SCHEDULED', 'FOLLOW_UP', 'NORMAL', :3)
                """,
                [slot_id, KARABO_PATIENT_ID, UPCOMING_QR],
            )
            cur.execute(
                "UPDATE TIMESLOT SET is_available = 0 WHERE slot_id = :1",
                [slot_id],
            )
            cur.execute(
                """
                SELECT appointment_id FROM APPOINTMENT
                WHERE qr_code_token = :1
                """,
                [UPCOMING_QR],
            )
            appt_id = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
                VALUES (:1, NULL, :2, 'EMAIL', 'PENDING',
                    'Reminder: Your follow-up at Ubuntu Clinic is scheduled.')
                """,
                [KARABO_PATIENT_ID, appt_id],
            )
            print(
                f"   [OK] Booked appointment_id={appt_id} on slot {slot_id} "
                f"({slot_date} {start_time})"
            )

    conn.commit()
    cur.close()
    conn.close()

    print("\n=== 3. Verify demo login ===")
    print(f"   Username: {KARABO_USERNAME}")
    print(f"   Password: Clinic@123")
    print(f"   Email:    {KARABO_EMAIL}")
    print("\n[OK] Demo patient seed patch complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
