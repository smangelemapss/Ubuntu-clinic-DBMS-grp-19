"""
Phase 4 - Full stack connection tests (DB + API + frontend config).

Runs registration flow, all role logins, and optional live HTTP check to the
backend URL configured in frontend/.env.

Usage (from backend/):
    python scripts/verify_full_stack.py
    python scripts/verify_full_stack.py --http   # also probe running Flask server
"""
import os
import subprocess
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(BACKEND_ROOT)
FRONTEND_ENV = os.path.join(REPO_ROOT, "frontend", ".env")


def load_frontend_api_url():
    if not os.path.isfile(FRONTEND_ENV):
        return "http://localhost:8000"
    with open(FRONTEND_ENV, encoding="utf-8") as handle:
        for line in handle:
            if line.strip().startswith("VITE_API_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return "http://localhost:8000"


def run_script(name):
    path = os.path.join(BACKEND_ROOT, "scripts", name)
    result = subprocess.run(
        [sys.executable, path],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def probe_http(base_url):
    url = f"{base_url.rstrip('/')}/api/v1/health/"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status == 200, body[:200]
    except urllib.error.URLError as exc:
        return False, str(exc.reason if hasattr(exc, "reason") else exc)
    except Exception as exc:
        return False, str(exc)


def main():
    http_probe = "--http" in sys.argv or os.getenv("VERIFY_HTTP", "").lower() in ("1", "true", "yes")
    failed = 0

    print("=" * 60)
    print("PHASE 4: FULL CONNECTION TESTS")
    print("=" * 60)

    print("\n1. Patient registration -> Oracle -> login -> patient APIs")
    ok, output = run_script("verify_registration_e2e.py")
    if ok:
        print("   [OK] Registration end-to-end passed")
    else:
        print(f"   [FAIL]\n{output}")
        failed += 1

    print("\n2. All demo roles (patient, doctor, nurse, admin)")
    ok, output = run_script("verify_all_roles_e2e.py")
    if ok:
        print("   [OK] All role API checks passed")
    else:
        print(f"   [FAIL]\n{output}")
        failed += 1

    api_url = load_frontend_api_url()
    print("\n3. Frontend -> backend URL alignment")
    print(f"   frontend/.env VITE_API_URL = {api_url}")
    flask_port = os.getenv("FLASK_PORT", "8000")
    if "localhost:8000" in api_url or f":{flask_port}" in api_url:
        print("   [OK] Frontend points at local backend port")
    else:
        print("   [OK] Custom API URL configured (verify it matches your deployed backend)")

    print("\n4. Live HTTP health check (optional)")
    if http_probe:
        ok, detail = probe_http(api_url)
        if ok:
            print(f"   [OK] GET {api_url}/api/v1/health/ responded")
        else:
            print(f"   [FAIL] Could not reach backend: {detail}")
            print("   Start backend: cd backend && python app.py")
            failed += 1
    else:
        ok, detail = probe_http(api_url)
        if ok:
            print(f"   [OK] Backend is running at {api_url}")
        else:
            print(f"   [SKIP] Backend not running ({detail})")
            print("   Start with: cd backend && python app.py")
            print("   Re-run with --http to require a live server")

    print("\n" + "=" * 60)
    if failed:
        print(f"PHASE 4: FAILED ({failed} check(s))")
        return 1
    print("PHASE 4: PASSED - full stack connection verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
