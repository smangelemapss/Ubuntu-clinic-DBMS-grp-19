"""Admin reporting service — delegates to audit_repo and doctor_repo."""

import db.audit_repo as audit_repo
import db.doctor_repo as doctor_repo
import db.user_account_repo as user_account_repo


def get_summary_stats():
    return audit_repo.get_admin_summary()


def get_appointments_by_doctor():
    return audit_repo.get_appointments_by_doctor()


def get_daily_counts(days=30):
    return audit_repo.get_daily_appointment_counts(days=days)


def get_audit_log(page=1, per_page=20, user_filter=None, action_filter=None, date_from=None, date_to=None):
    return audit_repo.get_audit_log(
        page=page,
        per_page=per_page,
        user_filter=user_filter,
        action_filter=action_filter,
        date_from=date_from,
        date_to=date_to,
    )


def list_departments():
    return doctor_repo.get_all_departments()


def create_department(name, head_doctor_id=None):
    return doctor_repo.create_department(name, head_doctor_id)


def update_department(dept_id, **kwargs):
    return doctor_repo.update_department(dept_id, **kwargs)


def delete_department(dept_id):
    return doctor_repo.delete_department(dept_id)


def get_department_by_id(dept_id):
    return doctor_repo.get_department_by_id(dept_id)


def list_users(role_filter=None, page=1, per_page=20):
    return user_account_repo.get_all_users(role_filter=role_filter, page=page, per_page=per_page)


def update_user(user_id, is_active=None, role=None):
    if is_active is not None:
        user_account_repo.update_user_status(user_id, bool(is_active))
    if role is not None:
        user_account_repo.update_user_role(user_id, role)
