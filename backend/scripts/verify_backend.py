"""
Phase 2 - Backend API readiness check.

Verifies environment, unit tests, route alignment, health endpoint, and live DB probe.

Usage (from backend/):
    python scripts/verify_backend.py
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_env():
    issues = []
    if not os.getenv("ORA_PASSWORD"):
        issues.append("ORA_PASSWORD is empty")
    secret = os.getenv("JWT_SECRET", "")
    if not secret or secret == "changeme-secret":
        issues.append("JWT_SECRET is default or empty (set a strong secret for production)")
    cors = os.getenv("CORS_ORIGINS", "")
    if not cors:
        issues.append("CORS_ORIGINS is empty")
    return issues


def run_pytest():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no"],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip() + result.stderr.strip()


def run_route_check():
    result = subprocess.run(
        [sys.executable, "scripts/verify_api_routes.py"],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip()


def check_health_live():
    from app import create_app

    app = create_app()
    client = app.test_client()
    resp = client.get("/api/v1/health/")
    data = resp.get_json() or {}
    ok = resp.status_code == 200 and data.get("database") == "connected"
    return ok, data


def check_gunicorn():
    try:
        import gunicorn  # noqa: F401

        return True
    except ImportError:
        return False


def main():
    failed = 0
    warnings = 0

    print("=" * 60)
    print("PHASE 2: BACKEND")
    print("=" * 60)

    print("\n1. Environment (.env)")
    env_issues = check_env()
    flask_env = os.getenv("FLASK_ENV", "production")
    print(f"   FLASK_ENV={flask_env}")
    print(f"   FLASK_PORT={os.getenv('FLASK_PORT', '8000')}")
    for issue in env_issues:
        if "JWT_SECRET" in issue and flask_env == "development":
            print(f"   [WARN] {issue}")
            warnings += 1
        else:
            print(f"   [FAIL] {issue}")
            failed += 1
    if not env_issues or (len(env_issues) == 1 and "JWT_SECRET" in env_issues[0] and flask_env == "development"):
        if not env_issues:
            print("   [OK] Required variables set")

    print("\n2. Unit tests (pytest)")
    passed, output = run_pytest()
    if passed:
        last_line = output.splitlines()[-1] if output else "passed"
        print(f"   [OK] {last_line}")
    else:
        print(f"   [FAIL] Tests failed:\n{output}")
        failed += 1

    print("\n3. API route alignment (frontend api.js vs Flask)")
    routes_ok, route_output = run_route_check()
    if routes_ok:
        print(f"   [OK] {route_output.splitlines()[-1]}")
    else:
        print(f"   [FAIL]\n{route_output}")
        failed += 1

    print("\n4. Health endpoint + live Oracle probe")
    health_ok, health_data = check_health_live()
    if health_ok:
        print(f"   [OK] status={health_data.get('status')}, database={health_data.get('database')}")
    else:
        print(f"   [FAIL] {health_data}")
        failed += 1

    print("\n5. Production server (gunicorn)")
    if check_gunicorn():
        print("   [OK] gunicorn installed")
    else:
        print("   [WARN] gunicorn not installed - run: pip install -r requirements.txt")
        warnings += 1

    print("\n6. NFR response-time targets (requires live Oracle + seed user)")
    if health_ok:
        nfr = subprocess.run(
            [sys.executable, "scripts/verify_nfr_performance.py"],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "DISABLE_RATE_LIMIT": "true"},
        )
        for line in nfr.stdout.strip().splitlines():
            print(f"   {line}")
        if nfr.returncode != 0:
            print("   [WARN] One or more endpoints exceeded NFR targets (see above)")
            warnings += 1
        else:
            print("   [OK] All benchmarked endpoints within targets")
    else:
        print("   [SKIP] Database not connected")

    print("\n" + "=" * 60)
    if failed:
        print(f"PHASE 2: FAILED ({failed} issue(s), {warnings} warning(s))")
        return 1
    if warnings:
        print(f"PHASE 2: PASSED with {warnings} warning(s) - backend ready for dev/demo")
    else:
        print("PHASE 2: PASSED - backend ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
