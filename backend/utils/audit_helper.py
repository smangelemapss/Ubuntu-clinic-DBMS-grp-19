"""Best-effort audit logging; never fails the caller's main operation."""

from flask import has_request_context, request

import db.audit_repo as audit_repo


def log_audit(user_id, action, table_affected, record_id):
    ip = request.remote_addr if has_request_context() else None
    try:
        audit_repo.log_action(user_id, action, table_affected, record_id, ip)
    except Exception:
        pass
