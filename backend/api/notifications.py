from flask import Blueprint, g

import services.notification_service as notification_service
from utils.error_handler import error_response, success_response
from utils.jwt_helper import require_auth

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/v1")


@notifications_bp.route("/notifications/", methods=["GET"])
@require_auth()
def list_notifications():
    try:
        data = notification_service.get_notifications_for_user(g.user_id)
    except Exception:
        return error_response("Unable to load notifications", "SERVER_ERROR", 500)
    return success_response(data)


@notifications_bp.route("/notifications/<int:notif_id>/read/", methods=["PATCH"])
@require_auth()
def mark_read(notif_id):
    try:
        found = notification_service.mark_notification_read(notif_id, g.user_id)
    except Exception:
        return error_response("Failed to mark notification as read", "SERVER_ERROR", 500)

    if not found:
        return error_response("Notification not found", "NOT_FOUND", 404)
    return success_response({"id": notif_id, "read": True})


@notifications_bp.route("/notifications/read-all/", methods=["PATCH"])
@require_auth()
def mark_all_read():
    try:
        updated_count = notification_service.mark_all_read(g.user_id)
    except Exception:
        return error_response("Failed to mark all notifications as read", "SERVER_ERROR", 500)
    return success_response({"message": "All notifications marked as read", "updated_count": updated_count})


@notifications_bp.route("/notifications/<int:notif_id>/", methods=["DELETE"])
@require_auth(roles=["ADMIN"])
def delete_notification(notif_id):
    try:
        found = notification_service.delete_notification(notif_id)
    except Exception:
        return error_response("Failed to delete notification", "SERVER_ERROR", 500)

    if not found:
        return error_response("Notification not found", "NOT_FOUND", 404)
    return success_response({"message": "Notification deleted", "deleted_id": notif_id})
