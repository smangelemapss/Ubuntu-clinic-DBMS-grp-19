"""Compare frontend api.js paths to Flask registered routes."""
import os
import sys

from werkzeug.exceptions import NotFound

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app import create_app

# Paths used in frontend/src/services/api.js (method, path)
FRONTEND_ROUTES = [
    ("GET", "/api/v1/health/"),
    ("GET", "/api/v1/patient/dashboard/"),
    ("GET", "/api/v1/patient/profile/"),
    ("GET", "/api/v1/medical/records/"),
    ("GET", "/api/v1/emergency-contacts/"),
    ("POST", "/api/v1/emergency-contacts/"),
    ("GET", "/api/v1/appointments/upcoming/"),
    ("GET", "/api/v1/appointments/history/"),
    ("POST", "/api/v1/appointments/book/"),
    ("PATCH", "/api/v1/appointments/1/cancel/"),
    ("GET", "/api/v1/doctors/"),
    ("GET", "/api/v1/timeslots/"),
    ("POST", "/api/v1/auth/register/"),
    ("GET", "/api/v1/notifications/"),
    ("PATCH", "/api/v1/notifications/1/read/"),
    ("GET", "/api/v1/admin/reports/summary/"),
    ("GET", "/api/v1/admin/departments/"),
    ("GET", "/api/v1/admin/users/"),
    ("POST", "/api/v1/auth/login/"),
    ("GET", "/api/v1/auth/me/"),
]


def route_exists(app, method, path):
    adapter = app.url_map.bind("")
    try:
        adapter.match(path, method=method)
        return True
    except NotFound:
        return False


def main():
    app = create_app()
    registered = set()
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        methods = rule.methods - {"HEAD", "OPTIONS"}
        for m in methods:
            registered.add((m, rule.rule))

    missing = []
    for method, path in FRONTEND_ROUTES:
        if not route_exists(app, method, path):
            missing.append(f"{method} {path}")

    print("Registered API routes:", len(registered))
    if missing:
        print("\n[FAIL] Frontend calls with no matching Flask route:")
        for m in missing:
            print(" ", m)
        return 1
    print("[OK] All frontend api.js paths match Flask routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
