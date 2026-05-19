import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS

from api.admin_reporting import admin_bp
from api.appointments import appointments_bp
from api.auth import auth_bp
from api.notifications import notifications_bp
from api.patients import patients_bp
from api.queue import queue_bp
from utils.error_handler import error_response, success_response
from utils.perf import register_performance_hooks

load_dotenv()


def _validate_production_config():
    if os.getenv("FLASK_ENV", "development") != "production":
        return
    secret = os.getenv("JWT_SECRET", "changeme-secret")
    if not secret or secret == "changeme-secret":
        raise RuntimeError(
            "JWT_SECRET must be set to a strong value when FLASK_ENV=production"
        )


def _frontend_dist_dir():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    )


def _register_website(app):
    """
    Serve the Vite production build from frontend/dist on the same origin as the API.
    Enable with SERVE_WEBSITE=true (used by serve-website.bat for one-URL deployment).
    """
    dist = _frontend_dist_dir()
    if os.getenv("SERVE_WEBSITE", "").lower() not in ("1", "true", "yes"):
        return
    if not os.path.isdir(dist) or not os.path.isfile(os.path.join(dist, "index.html")):
        raise RuntimeError(
            f"SERVE_WEBSITE=true but {dist} is missing. "
            "Run: cd frontend && npm run build"
        )

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        if path.startswith("api/"):
            return error_response("The requested resource was not found", "NOT_FOUND", 404)
        target = os.path.join(dist, path)
        if path and os.path.isfile(target):
            return send_from_directory(dist, path)
        return send_from_directory(dist, "index.html")


def create_app():
    _validate_production_config()
    app = Flask(__name__)

    cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    cors_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]
    CORS(app, origins=cors_origins, supports_credentials=True)

    app.url_map.strict_slashes = False
    register_performance_hooks(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(queue_bp)

    @app.route("/api/v1/health/", methods=["GET"])
    def health():
        db_ok = False
        db_error = None
        db_message = None
        try:
            from db.oracle_connection import get_connection

            conn = get_connection()
            conn.close()
            db_ok = True
        except Exception as exc:
            db_error = type(exc).__name__
            db_message = str(exc).split("\n")[0][:200]
        else:
            db_message = None

        hint = None
        if not db_ok and db_message:
            if "DPI-1047" in db_message or "Oracle Client library" in db_message:
                hint = "Install oracledb: pip install oracledb (thin mode needs no Instant Client)"
            elif (
                "10061" in db_message
                or "refused" in db_message.lower()
                or "DPY-6005" in db_message
            ):
                hint = "Start Oracle XE and confirm listener on ORA_HOST:ORA_PORT"
            elif "ORA-01017" in db_message:
                hint = "Check ORA_USER and ORA_PASSWORD in backend/.env"

        return success_response(
            {
                "status": "ok" if db_ok else "degraded",
                "database": "connected" if db_ok else "unavailable",
                "db_error": db_error,
                "db_message": db_message if not db_ok else None,
                "hint": hint,
            }
        )

    @app.errorhandler(404)
    def not_found(e):
        return error_response("The requested resource was not found", "NOT_FOUND", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("Method not allowed", "METHOD_NOT_ALLOWED", 405)

    @app.errorhandler(500)
    def internal_error(e):
        return error_response("An internal server error occurred", "SERVER_ERROR", 500)

    _register_website(app)
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "8000"))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(port=port, debug=debug)
