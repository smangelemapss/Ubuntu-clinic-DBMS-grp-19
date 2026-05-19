"""
Run all deploy-readiness phases in order:
  1. Database
  2. Backend
  3. Frontend
  4. Full connection tests

Usage (from backend/):
    python scripts/verify_deploy_ready.py
    python scripts/verify_deploy_ready.py --http
"""
import subprocess
import sys
import os

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PHASES = [
    ("verify_database.py", ["--fix-passwords"]),
    ("verify_sql_mastery.py", []),
    ("verify_backend.py", []),
    ("verify_frontend.py", []),
    ("verify_integrated_journey.py", []),
    ("verify_full_stack.py", []),
]


def main():
    extra = [a for a in sys.argv[1:] if a.startswith("--")]
    failed_phase = None

    print("\nUbuntu Clinic - Deploy Readiness Check\n")

    for script, default_args in PHASES:
        args = default_args.copy()
        if script == "verify_full_stack.py" and "--http" in sys.argv:
            args.append("--http")
        path = os.path.join(BACKEND_ROOT, "scripts", script)
        result = subprocess.run(
            [sys.executable, path, *args],
            cwd=BACKEND_ROOT,
        )
        if result.returncode != 0:
            failed_phase = script
            break
        print()

    if failed_phase:
        print(f"\n*** STOPPED at {failed_phase} - fix issues above, then re-run ***\n")
        return 1

    print("=" * 60)
    print("ALL PHASES PASSED - PROJECT IS DEPLOY/DEMO READY")
    print("=" * 60)
    print("\nStart locally:")
    print("  start-dev.bat")
    print("\nOr manually:")
    print("  cd backend  && python app.py")
    print("  cd frontend && npm run dev")
    print("\nProduction API:")
    print("  cd backend && gunicorn -w 4 -b 0.0.0.0:8000 \"app:app\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
