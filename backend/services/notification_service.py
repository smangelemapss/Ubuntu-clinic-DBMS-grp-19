"""Notification service — delegates to notification_repo."""

import db.notification_repo as notification_repo


def get_notifications_for_user(user_id):
    return notification_repo.get_notifications_for_user(user_id)


def mark_notification_read(notification_id, user_id):
    return notification_repo.mark_notification_read(notification_id, user_id)


def mark_all_read(user_id):
    return notification_repo.mark_all_notifications_read(user_id)


def delete_notification(notification_id):
    return notification_repo.delete_notification(notification_id)
