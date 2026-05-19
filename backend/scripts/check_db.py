"""Verify Oracle connectivity and print actionable setup hints."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from db.oracle_connection import get_connection  # noqa: E402


def main():
    print("Ubuntu Clinic — database connectivity check")
    print(
        f"  host={os.getenv('ORA_HOST', 'localhost')}"
        f" port={os.getenv('ORA_PORT', '1521')}"
        f" sid={os.getenv('ORA_SID', 'XE')}"
        f" user={os.getenv('ORA_USER', 'system')}"
    )
    if not os.getenv("ORA_PASSWORD"):
        print("\n[FAIL] ORA_PASSWORD is empty. Copy backend/.env.example to backend/.env")
        return 1
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM DUAL")
        cur.fetchone()
        cur.close()
        conn.close()
        print("\n[OK] Connected to Oracle successfully.")
        return 0
    except Exception as exc:
        print(f"\n[FAIL] {type(exc).__name__}: {exc}")
        msg = str(exc)
        if "10061" in msg or "refused" in msg.lower():
            print("  -> Start Oracle Database XE (Windows Services or Docker).")
        elif "ORA-01017" in msg:
            print("  -> Wrong password. Update ORA_PASSWORD in backend/.env")
        elif "DPI-1047" in msg:
            print("  -> Run: pip install oracledb (thin mode, no Instant Client)")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
