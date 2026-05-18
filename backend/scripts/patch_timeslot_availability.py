"""
Ensure bookable TIMESLOT rows exist for today and the next 14 days.

The base seed only places slots on SYSDATE+1, +2, +3, +7 and many are
already booked — the Book Appointment page often shows an empty time list.

Usage (from backend/):
    python scripts/patch_timeslot_availability.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from db.oracle_connection import get_connection

# Standard clinic hours (start, end) — inserted when missing for each day
DAILY_SLOTS = [
    ("08:30", "09:00"),
    ("09:00", "09:30"),
    ("10:00", "10:30"),
    ("11:00", "11:30"),
    ("14:00", "14:30"),
    ("15:00", "15:30"),
]


def main():
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0

    print("=== Ensuring TIMESLOT rows for TRUNC(SYSDATE) .. +14 ===")
    for day_offset in range(0, 15):
        for start_time, end_time in DAILY_SLOTS:
            cur.execute(
                """
                SELECT COUNT(*) FROM TIMESLOT
                WHERE slot_date = TRUNC(SYSDATE) + :1
                  AND start_time = :2
                """,
                [day_offset, start_time],
            )
            if cur.fetchone()[0]:
                continue
            cur.execute(
                """
                INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
                VALUES (TRUNC(SYSDATE) + :1, :2, :3, 1)
                """,
                [day_offset, start_time, end_time],
            )
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"   [OK] Inserted {inserted} new timeslot(s)")


if __name__ == "__main__":
    main()
