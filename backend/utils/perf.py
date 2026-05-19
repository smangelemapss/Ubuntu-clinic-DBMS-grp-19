"""Performance-related Flask hooks (response timing, cache headers)."""

import os
import time

from flask import g, request


def register_performance_hooks(app):
    @app.before_request
    def _perf_start():
        g._request_start = time.perf_counter()

    @app.after_request
    def _perf_headers(response):
        start = getattr(g, "_request_start", None)
        if start is not None:
            elapsed_ms = (time.perf_counter() - start) * 1000
            response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"

        if request.method == "GET" and request.path.rstrip("/").endswith("/doctors"):
            response.headers["Cache-Control"] = "private, max-age=120"

        if os.getenv("FLASK_ENV", "production") == "production":
            response.headers.setdefault("X-Content-Type-Options", "nosniff")
            response.headers.setdefault("X-Frame-Options", "DENY")

        return response
