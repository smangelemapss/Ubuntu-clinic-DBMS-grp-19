"""
Benchmark key API paths against NFR response-time targets (local demo / CI with Oracle).

Targets (typical DBMS non-functional requirements for a campus clinic MVP):
  - Health:     < 500 ms
  - Login:      < 1500 ms
  - Dashboard:  < 1000 ms (authenticated)
  - Doctors:    < 800 ms (authenticated, cache-friendly)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

TARGETS_MS = {
    "GET /api/v1/health/": 500,
    "POST /api/v1/auth/login/": 1500,
    "GET /api/v1/patient/dashboard/": 1000,
    "GET /api/v1/doctors/": 800,
}

DEMO_USER = os.getenv("NFR_DEMO_USER", "karabo.mabena")
DEMO_PASS = os.getenv("NFR_DEMO_PASS", "Clinic@123")


def _ms(start):
    return (time.perf_counter() - start) * 1000


def main():
    os.environ.setdefault("DISABLE_RATE_LIMIT", "true")

    from app import create_app

    app = create_app()
    client = app.test_client()
    failures = []

    print("=" * 60)
    print("NFR performance verification")
    print("=" * 60)

    t0 = time.perf_counter()
    r = client.get("/api/v1/health/")
    label = "GET /api/v1/health/"
    elapsed = _ms(t0)
    ok = r.status_code == 200 and elapsed <= TARGETS_MS[label]
    print(f"  {'[OK]' if ok else '[FAIL]'} {label} -> {elapsed:.0f} ms (target < {TARGETS_MS[label]} ms)")
    if not ok:
        failures.append(label)

    t0 = time.perf_counter()
    r = client.post(
        "/api/v1/auth/login/",
        json={"username": DEMO_USER, "password": DEMO_PASS},
    )
    label = "POST /api/v1/auth/login/"
    elapsed = _ms(t0)
    ok = r.status_code == 200 and elapsed <= TARGETS_MS[label]
    print(f"  {'[OK]' if ok else '[FAIL]'} {label} -> {elapsed:.0f} ms (target < {TARGETS_MS[label]} ms)")
    if not ok:
        failures.append(label)

    if r.status_code != 200:
        print(f"  [SKIP] Authenticated routes (login failed: {r.status_code})")
        print("=" * 60)
        return 1 if failures else 0

    token = r.get_json().get("access") or r.get_json().get("data", {}).get("access")
    headers = {"Authorization": f"Bearer {token}"}

    for path, target in (
        ("/api/v1/patient/dashboard/", TARGETS_MS["GET /api/v1/patient/dashboard/"]),
        ("/api/v1/doctors/", TARGETS_MS["GET /api/v1/doctors/"]),
    ):
        label = f"GET {path}"
        t0 = time.perf_counter()
        resp = client.get(path, headers=headers)
        elapsed = _ms(t0)
        ok = resp.status_code == 200 and elapsed <= target
        timing_hdr = resp.headers.get("X-Response-Time-Ms", "n/a")
        print(
            f"  {'[OK]' if ok else '[FAIL]'} {label} -> {elapsed:.0f} ms "
            f"(server {timing_hdr} ms, target < {target} ms)"
        )
        if not ok:
            failures.append(label)

    print("=" * 60)
    if failures:
        print(f"FAILED: {len(failures)} endpoint(s) over target")
        return 1
    print("PASSED: all endpoints within NFR targets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
