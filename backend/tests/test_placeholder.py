"""
Comprehensive pytest tests for Ubuntu Clinic backend.
All Oracle DB connections are mocked via unittest.mock so tests run in CI
without a live Oracle XE instance.

IMPORTANT: Patch paths use the module where get_connection is *imported*, not
where it is defined.  e.g. use "db.user_account_repo.get_connection" because
user_account_repo.py does `from db.oracle_connection import get_connection`.
"""
import json
import os
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_mock_conn(fetchone_returns=None, fetchall_return=None, rowcount=1):
    """
    Return (mock_connection, mock_cursor).

    fetchone_returns: list of values returned by successive fetchone() calls.
                      If a single non-list value is given it is wrapped in a list.
    fetchall_return:  list returned by fetchall().
    rowcount:         value for cursor.rowcount.
    """
    mock_cursor = MagicMock()

    if fetchone_returns is not None:
        if not isinstance(fetchone_returns, list):
            fetchone_returns = [fetchone_returns]
        mock_cursor.fetchone.side_effect = fetchone_returns
    # else fetchone returns a MagicMock (truthy but not meaningful); tests
    # that need None explicitly should pass fetchone_returns=[None, ...]

    if fetchall_return is not None:
        mock_cursor.fetchall.return_value = fetchall_return
    else:
        mock_cursor.fetchall.return_value = []

    mock_cursor.rowcount = rowcount

    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = MagicMock()
    mock_connection.rollback = MagicMock()
    return mock_connection, mock_cursor


# ===========================================================================
# user_account_repo
# ===========================================================================

class TestUserAccountRepo:

    @patch("db.user_account_repo.get_connection")
    def test_get_user_by_username_found(self, mock_get_conn):
        import db.user_account_repo as repo

        expected = (1, "john_doe", "hashed_pw", 10, None, "PATIENT", "ACTIVE")
        conn, cur = _make_mock_conn(fetchone_returns=[expected])
        mock_get_conn.return_value = conn

        result = repo.get_user_by_username("john_doe")
        assert result == expected

    @patch("db.user_account_repo.get_connection")
    def test_get_user_by_username_not_found(self, mock_get_conn):
        import db.user_account_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[None])
        mock_get_conn.return_value = conn

        result = repo.get_user_by_username("nobody")
        assert result is None

    @patch("db.user_account_repo.get_connection")
    def test_create_patient_user(self, mock_get_conn):
        import db.user_account_repo as repo

        # INSERT (no fetchone) + SELECT user_account_id → (42,)
        conn, cur = _make_mock_conn(fetchone_returns=[(42,)])
        mock_get_conn.return_value = conn

        result = repo.create_patient_user("john_doe", "hashed_pw", 10)
        assert result == 42
        conn.commit.assert_called_once()

    @patch("db.user_account_repo.get_connection")
    def test_update_user_status_active(self, mock_get_conn):
        import db.user_account_repo as repo

        conn, cur = _make_mock_conn()
        mock_get_conn.return_value = conn

        repo.update_user_status(1, True)
        assert cur.execute.called
        conn.commit.assert_called_once()

    @patch("db.user_account_repo.get_connection")
    def test_update_user_status_disabled(self, mock_get_conn):
        import db.user_account_repo as repo

        conn, cur = _make_mock_conn()
        mock_get_conn.return_value = conn

        repo.update_user_status(1, False)
        conn.commit.assert_called_once()

    @patch("db.user_account_repo.get_connection")
    def test_update_user_role(self, mock_get_conn):
        import db.user_account_repo as repo

        conn, cur = _make_mock_conn()
        mock_get_conn.return_value = conn

        repo.update_user_role(1, "ADMIN")
        assert cur.execute.called
        conn.commit.assert_called_once()

    @patch("db.user_account_repo.get_connection")
    def test_get_all_users_no_filter(self, mock_get_conn):
        import db.user_account_repo as repo

        rows = [(1, "alice", "a@b.com", "PATIENT", "ACTIVE", 5, None)]
        # fetchall for user rows + fetchone for COUNT(*)
        conn, cur = _make_mock_conn(fetchone_returns=[(1,)], fetchall_return=rows)
        mock_get_conn.return_value = conn

        results, total = repo.get_all_users()
        assert results == rows
        assert total == 1

    @patch("db.user_account_repo.get_connection")
    def test_get_all_users_with_role_filter(self, mock_get_conn):
        import db.user_account_repo as repo

        rows = [(1, "alice", "a@b.com", "PATIENT", "ACTIVE", 5, None)]
        conn, cur = _make_mock_conn(fetchone_returns=[(1,)], fetchall_return=rows)
        mock_get_conn.return_value = conn

        results, total = repo.get_all_users(role_filter="PATIENT")
        assert results == rows


# ===========================================================================
# patient_repo
# ===========================================================================

class TestPatientRepo:

    @patch("db.patient_repo.get_connection")
    def test_get_patient_by_user_id(self, mock_get_conn):
        import db.patient_repo as repo

        expected = (5, "S001", "Thabo", "Dlamini", "thabo@nwu.ac.za",
                    "0123456789", datetime(2000, 1, 1), "10 Main St", "Pretoria",
                    "0001", 1, datetime(2025, 1, 1))
        conn, cur = _make_mock_conn(fetchone_returns=[expected])
        mock_get_conn.return_value = conn

        result = repo.get_patient_by_user_id(1)
        assert result[0] == 5

    @patch("db.patient_repo.get_connection")
    def test_create_patient_returns_id(self, mock_get_conn):
        import db.patient_repo as repo

        # INSERT (no fetchone) + SELECT patient_id → (7,)
        conn, cur = _make_mock_conn(fetchone_returns=[(7,)])
        mock_get_conn.return_value = conn

        pid = repo.create_patient(
            "S001", "Thabo", "Dlamini", "thabo@nwu.ac.za",
            "0123456789", "2000-01-01", "10 Main St", "Pretoria", "0001"
        )
        assert pid == 7
        conn.commit.assert_called_once()

    @patch("db.patient_repo.get_connection")
    def test_get_dashboard_counts(self, mock_get_conn):
        import db.patient_repo as repo

        # Single round-trip with four scalar subqueries
        conn, cur = _make_mock_conn(fetchone_returns=[(3, 2, 1, 0)])
        mock_get_conn.return_value = conn

        upcoming, past, pending, cancelled = repo.get_dashboard_counts(5)
        assert upcoming == 3
        assert past == 2
        assert pending == 1
        assert cancelled == 0

    @patch("db.patient_repo.get_connection")
    def test_get_medical_records(self, mock_get_conn):
        import db.patient_repo as repo

        rows = [(1, "2025-01-01", "Dr. Nkosi", "Flu", "General")]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_medical_records(5)
        assert len(result) == 1
        assert result[0][2] == "Dr. Nkosi"

    @patch("db.patient_repo.get_connection")
    def test_get_medical_record_by_id(self, mock_get_conn):
        import db.patient_repo as repo

        row = (1, "2025-01-01", "Dr. Nkosi", "Flu", "Fever", "Paracetamol", "General")
        conn, cur = _make_mock_conn(fetchone_returns=[row])
        mock_get_conn.return_value = conn

        result = repo.get_medical_record_by_id(1, 5)
        assert result[3] == "Flu"

    @patch("db.patient_repo.get_connection")
    def test_get_emergency_contacts(self, mock_get_conn):
        import db.patient_repo as repo

        rows = [(1, "Jane Doe", "0111111111", "Emergency|Sister")]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_emergency_contacts(5)
        assert result[0][1] == "Jane Doe"

    @patch("db.patient_repo.get_connection")
    def test_create_emergency_contact(self, mock_get_conn):
        import db.patient_repo as repo

        # INSERT (commit) + SELECT patient_contact_id → (10,)
        conn, cur = _make_mock_conn(fetchone_returns=[(10,)])
        mock_get_conn.return_value = conn

        cid = repo.create_emergency_contact(5, "Jane Doe", "Sister", "0111111111", "Emergency")
        assert cid == 10
        conn.commit.assert_called_once()

    @patch("db.patient_repo.get_connection")
    def test_delete_emergency_contact_success(self, mock_get_conn):
        import db.patient_repo as repo

        conn, cur = _make_mock_conn(rowcount=1)
        mock_get_conn.return_value = conn

        result = repo.delete_emergency_contact(10, 5)
        assert result is True
        conn.commit.assert_called_once()

    @patch("db.patient_repo.get_connection")
    def test_delete_emergency_contact_not_found(self, mock_get_conn):
        import db.patient_repo as repo

        conn, cur = _make_mock_conn(rowcount=0)
        mock_get_conn.return_value = conn

        result = repo.delete_emergency_contact(999, 5)
        assert result is False

    @patch("db.patient_repo.get_connection")
    def test_update_emergency_contact_success(self, mock_get_conn):
        import db.patient_repo as repo

        existing = ("Jane Doe", "0111111111", "Emergency|Sister")
        conn, cur = _make_mock_conn(fetchone_returns=[existing])
        mock_get_conn.return_value = conn

        result = repo.update_emergency_contact(1, 5, name="Mary Doe")
        assert result == 1
        conn.commit.assert_called_once()

    @patch("db.patient_repo.get_connection")
    def test_update_emergency_contact_not_found(self, mock_get_conn):
        import db.patient_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[None])
        mock_get_conn.return_value = conn

        result = repo.update_emergency_contact(999, 5, name="Mary")
        assert result is None


# ===========================================================================
# appointment_repo
# ===========================================================================

class TestAppointmentRepo:

    @patch("db.appointment_repo.get_connection")
    def test_get_upcoming_appointments(self, mock_get_conn):
        import db.appointment_repo as repo

        rows = [(1, "2026-06-01", "09:00", "Dr. Nkosi", 3, "SICK", "SCHEDULED", "General")]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_upcoming_appointments(5)
        assert len(result) == 1
        assert result[0][3] == "Dr. Nkosi"

    @patch("db.appointment_repo.get_connection")
    def test_book_appointment_success(self, mock_get_conn):
        import db.appointment_repo as repo

        detail_row = (42, "2026-06-01", "09:00", "Dr. Nkosi")
        # fetchone: FOR UPDATE slot, existing appt check, then SELECT detail
        conn, cur = _make_mock_conn(fetchone_returns=[(1,), None, detail_row])
        mock_get_conn.return_value = conn

        result = repo.book_appointment(5, 3, 7, "Headache", "SICK", "uuid-token")
        assert result[0] == 42
        conn.commit.assert_called_once()

    @patch("db.appointment_repo.get_connection")
    def test_book_appointment_slot_unavailable(self, mock_get_conn):
        import db.appointment_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[(0,)])  # is_available = 0
        mock_get_conn.return_value = conn

        with pytest.raises(ValueError, match="SLOT_UNAVAILABLE"):
            repo.book_appointment(5, 3, 7, "Headache", "SICK", "uuid-token")

    @patch("db.appointment_repo.get_connection")
    def test_book_appointment_slot_not_found(self, mock_get_conn):
        import db.appointment_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[None])  # slot not found
        mock_get_conn.return_value = conn

        with pytest.raises(ValueError, match="SLOT_UNAVAILABLE"):
            repo.book_appointment(5, 3, 7, "Headache", "SICK", "uuid-token")

    @patch("db.appointment_repo.get_connection")
    def test_get_appointment_history(self, mock_get_conn):
        import db.appointment_repo as repo

        rows = [(1, "2025-01-01", "09:00", "Dr. Nkosi", "General", "Flu", "COMPLETED")]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_appointment_history(5)
        assert result[0][6] == "COMPLETED"

    @patch("db.appointment_repo.get_connection")
    def test_get_available_timeslots(self, mock_get_conn):
        import db.appointment_repo as repo

        rows = [(1, "09:00", 1), (2, "10:00", 1)]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_available_timeslots("2026-06-01")
        assert len(result) == 2

    @patch("db.appointment_repo.get_connection")
    def test_get_pending_results(self, mock_get_conn):
        import db.appointment_repo as repo

        rows = [(1, "2025-01-01", "SICK", "COMPLETED")]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_pending_results(5)
        assert len(result) == 1


# ===========================================================================
# doctor_repo
# ===========================================================================

class TestDoctorRepo:

    @patch("db.doctor_repo.get_connection")
    def test_get_all_doctors(self, mock_get_conn):
        import db.doctor_repo as repo

        rows = [(1, "Dr. Nkosi", "Cardiology", 2)]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_all_doctors()
        assert result[0][1] == "Dr. Nkosi"

    @patch("db.doctor_repo.get_connection")
    def test_get_all_departments(self, mock_get_conn):
        import db.doctor_repo as repo

        rows = [(1, "Cardiology", "Dr. Nkosi", 5)]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_all_departments()
        assert result[0][1] == "Cardiology"
        assert result[0][2] == "Dr. Nkosi"
        assert result[0][3] == 5

    @patch("db.doctor_repo.get_connection")
    def test_delete_department_has_staff(self, mock_get_conn):
        import db.doctor_repo as repo

        # fetchone: dept_exists → (1,), staff_count → (3,)
        conn, cur = _make_mock_conn(fetchone_returns=[(1,), (3,)])
        mock_get_conn.return_value = conn

        result = repo.delete_department(1)
        assert result == "HAS_STAFF"

    @patch("db.doctor_repo.get_connection")
    def test_delete_department_not_found(self, mock_get_conn):
        import db.doctor_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[None])
        mock_get_conn.return_value = conn

        result = repo.delete_department(999)
        assert result is None

    @patch("db.doctor_repo.get_connection")
    def test_delete_department_success(self, mock_get_conn):
        import db.doctor_repo as repo

        # dept exists, no staff
        conn, cur = _make_mock_conn(fetchone_returns=[(1,), (0,)])
        mock_get_conn.return_value = conn

        result = repo.delete_department(1)
        assert result is True
        conn.commit.assert_called_once()

    @patch("db.doctor_repo.get_connection")
    def test_create_department(self, mock_get_conn):
        import db.doctor_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[(5,)])
        mock_get_conn.return_value = conn

        dept_id = repo.create_department("Radiology", 3)
        assert dept_id == 5
        conn.commit.assert_called_once()

    @patch("db.doctor_repo.get_connection")
    def test_update_department_not_found(self, mock_get_conn):
        import db.doctor_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[None])
        mock_get_conn.return_value = conn

        result = repo.update_department(999, name="New Name")
        assert result is None


# ===========================================================================
# audit_repo
# ===========================================================================

class TestAuditRepo:

    @patch("db.audit_repo.get_connection")
    def test_log_action(self, mock_get_conn):
        import db.audit_repo as repo

        conn, cur = _make_mock_conn()
        mock_get_conn.return_value = conn

        repo.log_action(1, "CREATE", "PATIENT", 5, "127.0.0.1")
        assert cur.execute.called
        conn.commit.assert_called_once()

    @patch("db.audit_repo.get_connection")
    def test_get_admin_summary(self, mock_get_conn):
        import db.audit_repo as repo

        # 5 COUNT queries
        conn, cur = _make_mock_conn(fetchone_returns=[(100,), (10,), (5,), (3,), (50,)])
        mock_get_conn.return_value = conn

        summary = repo.get_admin_summary()
        assert summary["total_patients"] == 100
        assert summary["total_doctors"] == 10
        assert summary["appointments_today"] == 5
        assert summary["cancellation_rate"] == 6.0

    @patch("db.audit_repo.get_connection")
    def test_get_admin_summary_zero_appointments(self, mock_get_conn):
        import db.audit_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[(0,), (0,), (0,), (0,), (0,)])
        mock_get_conn.return_value = conn

        summary = repo.get_admin_summary()
        assert summary["cancellation_rate"] == 0.0

    @patch("db.audit_repo.get_connection")
    def test_get_appointments_by_doctor(self, mock_get_conn):
        import db.audit_repo as repo

        rows = [("Dr. Nkosi", 24), ("Dr. Sithole", 17)]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_appointments_by_doctor()
        assert result["labels"] == ["Dr. Nkosi", "Dr. Sithole"]
        assert result["data"] == [24, 17]

    @patch("db.audit_repo.get_connection")
    def test_get_daily_appointment_counts(self, mock_get_conn):
        import db.audit_repo as repo

        rows = [("2026-05-01", 4), ("2026-05-02", 7)]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_daily_appointment_counts(30)
        assert result["labels"] == ["2026-05-01", "2026-05-02"]
        assert result["data"] == [4, 7]

    @patch("db.audit_repo.get_connection")
    def test_get_audit_log(self, mock_get_conn):
        import db.audit_repo as repo

        now = datetime(2026, 5, 14, 10, 0)
        rows = [(1, "admin", "CREATE", now, "127.0.0.1", "PATIENT #5")]
        conn, cur = _make_mock_conn(fetchall_return=rows, fetchone_returns=[(1,)])
        mock_get_conn.return_value = conn

        results, total = repo.get_audit_log()
        assert total == 1


# ===========================================================================
# notification_repo
# ===========================================================================

class TestNotificationRepo:

    @patch("db.notification_repo.get_connection")
    def test_get_notifications_for_user(self, mock_get_conn):
        import db.notification_repo as repo

        msg = json.dumps({"title": "Hello", "text": "You have an appointment"})
        now = datetime(2026, 5, 14, 10, 0, 0)
        rows = [(1, msg, now, "PENDING", None)]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_notifications_for_user(1)
        assert len(result) == 1
        assert result[0]["title"] == "Hello"
        assert result[0]["read"] is False

    @patch("db.notification_repo.get_connection")
    def test_get_notifications_sent_means_read(self, mock_get_conn):
        import db.notification_repo as repo

        msg = json.dumps({"title": "Hi", "text": "Done"})
        now = datetime(2026, 5, 14, 10, 0, 0)
        rows = [(2, msg, now, "SENT", now)]
        conn, cur = _make_mock_conn(fetchall_return=rows)
        mock_get_conn.return_value = conn

        result = repo.get_notifications_for_user(1)
        assert result[0]["read"] is True

    @patch("db.notification_repo.get_connection")
    def test_mark_notification_read_success(self, mock_get_conn):
        import db.notification_repo as repo

        # ownership check returns a row → notification found
        conn, cur = _make_mock_conn(fetchone_returns=[(1,)])
        mock_get_conn.return_value = conn

        result = repo.mark_notification_read(1, 1)
        assert result is True
        conn.commit.assert_called_once()

    @patch("db.notification_repo.get_connection")
    def test_mark_notification_read_not_found(self, mock_get_conn):
        import db.notification_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[None])
        mock_get_conn.return_value = conn

        result = repo.mark_notification_read(999, 1)
        assert result is False

    @patch("db.notification_repo.get_connection")
    def test_delete_notification_success(self, mock_get_conn):
        import db.notification_repo as repo

        # SELECT (found), then DELETE
        conn, cur = _make_mock_conn(fetchone_returns=[(1,)])
        mock_get_conn.return_value = conn

        result = repo.delete_notification(1)
        assert result is True
        conn.commit.assert_called_once()

    @patch("db.notification_repo.get_connection")
    def test_delete_notification_not_found(self, mock_get_conn):
        import db.notification_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[None])
        mock_get_conn.return_value = conn

        result = repo.delete_notification(999)
        assert result is False

    @patch("db.notification_repo.get_connection")
    def test_mark_all_notifications_read(self, mock_get_conn):
        import db.notification_repo as repo

        conn, cur = _make_mock_conn(rowcount=3)
        mock_get_conn.return_value = conn

        count = repo.mark_all_notifications_read(1)
        assert count == 3
        conn.commit.assert_called_once()


# ===========================================================================
# queue_repo
# ===========================================================================

class TestQueueRepo:

    @patch("db.queue_repo.get_connection")
    def test_create_queue_entry(self, mock_get_conn):
        import db.queue_repo as repo

        conn, cur = _make_mock_conn(fetchone_returns=[(1,)])
        mock_get_conn.return_value = conn

        entry_id = repo.create_queue_entry(42)
        assert entry_id == 1
        conn.commit.assert_called_once()

    @patch("db.queue_repo.get_connection")
    def test_get_queue_for_appointment(self, mock_get_conn):
        import db.queue_repo as repo

        row = (1, 42, "WAITING", datetime(2026, 5, 14), None, None, "Room 1")
        conn, cur = _make_mock_conn(fetchone_returns=[row])
        mock_get_conn.return_value = conn

        result = repo.get_queue_for_appointment(42)
        assert result[2] == "WAITING"

    @patch("db.queue_repo.get_connection")
    def test_update_queue_status(self, mock_get_conn):
        import db.queue_repo as repo

        conn, cur = _make_mock_conn()
        mock_get_conn.return_value = conn

        repo.update_queue_status(1, "IN_PROGRESS")
        assert cur.execute.called
        conn.commit.assert_called_once()


# ===========================================================================
# auth_service
# ===========================================================================

class TestAuthService:

    @patch("db.patient_repo.get_patient_by_user_id")
    @patch("db.user_account_repo.get_user_by_id")
    @patch("db.user_account_repo.get_user_by_username")
    def test_login_success(self, mock_get_by_username, mock_get_by_id, mock_patient):
        from werkzeug.security import generate_password_hash
        import services.auth_service as svc

        pw_hash = generate_password_hash("secret123")
        mock_get_by_username.return_value = (
            1, "john_doe", pw_hash, 10, None, "PATIENT", "ACTIVE"
        )
        mock_get_by_id.return_value = (
            1, "john_doe", "john@nwu.ac.za", "PATIENT", "ACTIVE", 10, None
        )
        mock_patient.return_value = (
            10, "48277444", "John", "Doe", "john@nwu.ac.za", "0820000000",
            None, "Street", "City", "0000", 1, None,
        )

        result = svc.login("john_doe", "secret123")
        assert "access" in result
        assert "refresh" in result
        assert result["role"] == "PATIENT"
        assert result["user"]["username"] == "john_doe"

    @patch("db.user_account_repo.get_user_by_username")
    def test_login_user_not_found(self, mock_get_by_username):
        import services.auth_service as svc

        mock_get_by_username.return_value = None

        with pytest.raises(ValueError, match="INVALID_CREDENTIALS"):
            svc.login("nobody", "wrong")

    @patch("db.user_account_repo.get_user_by_username")
    def test_login_wrong_password(self, mock_get_by_username):
        from werkzeug.security import generate_password_hash
        import services.auth_service as svc

        pw_hash = generate_password_hash("correct_password")
        mock_get_by_username.return_value = (
            1, "john_doe", pw_hash, 10, None, "PATIENT", "ACTIVE"
        )

        with pytest.raises(ValueError, match="INVALID_CREDENTIALS"):
            svc.login("john_doe", "wrong_password")

    @patch("db.user_account_repo.get_user_by_username")
    def test_login_disabled_account(self, mock_get_by_username):
        from werkzeug.security import generate_password_hash
        import services.auth_service as svc

        pw_hash = generate_password_hash("pass123")
        mock_get_by_username.return_value = (
            1, "john_doe", pw_hash, 10, None, "PATIENT", "DISABLED"
        )

        with pytest.raises(ValueError, match="ACCOUNT_DISABLED"):
            svc.login("john_doe", "pass123")

    @patch("db.user_account_repo.create_patient_user")
    @patch("db.patient_repo.create_patient")
    @patch("db.patient_repo.get_patient_by_email")
    @patch("db.patient_repo.get_patient_by_student_number")
    @patch("db.user_account_repo.get_user_by_username")
    def test_register_success(
        self,
        mock_get_by_username,
        mock_get_by_student,
        mock_get_by_email,
        mock_create_patient,
        mock_create_user,
    ):
        import services.auth_service as svc

        mock_get_by_username.return_value = None
        mock_get_by_student.return_value = None
        mock_get_by_email.return_value = None
        mock_create_patient.return_value = 5
        mock_create_user.return_value = 1

        result = svc.register(
            "john.doe", "48277444@mynwu.ac.za", "Pass1234", "48277444"
        )
        assert result["user"]["username"] == "john.doe"
        assert result["user"]["role"] == "PATIENT"
        assert result["user"]["email"] == "48277444@mynwu.ac.za"
        assert result["user"]["student_number"] == "48277444"

    @patch("db.user_account_repo.get_user_by_username")
    def test_register_student_number_required(self, mock_get_by_username):
        import services.auth_service as svc

        mock_get_by_username.return_value = None

        with pytest.raises(ValueError, match="STUDENT_NUMBER_REQUIRED"):
            svc.register("john.doe", "48277444@mynwu.ac.za", "Pass1234")

    @patch("db.user_account_repo.get_user_by_username")
    def test_register_invalid_student_number(self, mock_get_by_username):
        import services.auth_service as svc

        mock_get_by_username.return_value = None

        with pytest.raises(ValueError, match="STUDENT_NUMBER_INVALID"):
            svc.register("john.doe", "48277444@mynwu.ac.za", "Pass1234", "1234")

    @patch("db.user_account_repo.get_user_by_username")
    def test_register_invalid_nwu_email(self, mock_get_by_username):
        import services.auth_service as svc

        mock_get_by_username.return_value = None

        with pytest.raises(ValueError, match="EMAIL_INVALID"):
            svc.register("john.doe", "john@gmail.com", "Pass1234", "48277444")

    @patch("db.user_account_repo.get_user_by_username")
    def test_register_email_student_mismatch(self, mock_get_by_username):
        import services.auth_service as svc

        mock_get_by_username.return_value = None

        with pytest.raises(ValueError, match="EMAIL_STUDENT_MISMATCH"):
            svc.register("john.doe", "11111111@mynwu.ac.za", "Pass1234", "48277444")

    @patch("db.user_account_repo.get_user_by_username")
    def test_register_weak_password(self, mock_get_by_username):
        import services.auth_service as svc

        mock_get_by_username.return_value = None

        with pytest.raises(ValueError, match="PASSWORD_WEAK"):
            svc.register("john.doe", "48277444@mynwu.ac.za", "password", "48277444")

    @patch("db.user_account_repo.get_user_by_username")
    def test_register_duplicate_username(self, mock_get_by_username):
        import services.auth_service as svc

        mock_get_by_username.return_value = (1, "john_doe", "hash", 10, None, "PATIENT", "ACTIVE")

        with pytest.raises(ValueError, match="USERNAME_EXISTS"):
            svc.register("john.doe", "48277444@mynwu.ac.za", "Pass1234", "48277444")

    @patch("db.patient_repo.get_patient_by_user_id")
    @patch("db.user_account_repo.get_user_by_id")
    def test_get_current_user(self, mock_get_by_id, mock_patient):
        import services.auth_service as svc

        mock_get_by_id.return_value = (
            1, "john_doe", "john@nwu.ac.za", "PATIENT", "ACTIVE", 10, None
        )
        mock_patient.return_value = (
            10, "48277444", "John", "Doe", "john@nwu.ac.za", "0820000000",
            None, "Street", "City", "0000", 1, None,
        )

        result = svc.get_current_user(1)
        assert result["id"] == 1
        assert result["username"] == "john_doe"
        assert result["role"] == "PATIENT"

    def test_logout_blacklists_token(self):
        import services.auth_service as svc
        from utils.jwt_helper import is_blacklisted

        token = "fake.test.token.xyz"
        svc.logout(token)
        assert is_blacklisted(token)


# ===========================================================================
# patient_service
# ===========================================================================

class TestPatientService:

    @patch("db.patient_repo.get_dashboard_counts")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_get_dashboard(self, mock_get_patient, mock_get_counts):
        import services.patient_service as svc

        mock_get_patient.return_value = (5, "S001", "Thabo", "Dlamini",
                                         "t@nwu.ac.za", "0123456789",
                                         datetime(2000, 1, 1), "Str", "Pretoria",
                                         "0001", 1, datetime(2025, 1, 1))
        mock_get_counts.return_value = (3, 2, 1, 0)

        result = svc.get_dashboard(1)
        assert result["upcomingCount"] == 3
        assert result["pastVisitsCount"] == 2
        assert result["pendingResultsCount"] == 1
        assert result["cancelledCount"] == 0

    @patch("db.patient_repo.get_patient_by_user_id")
    def test_get_dashboard_patient_not_found(self, mock_get_patient):
        import services.patient_service as svc

        mock_get_patient.return_value = None

        with pytest.raises(ValueError, match="PATIENT_NOT_FOUND"):
            svc.get_dashboard(999)

    @patch("db.patient_repo.get_emergency_contacts")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_get_emergency_contacts_with_label(self, mock_get_patient, mock_get_contacts):
        import services.patient_service as svc

        mock_get_patient.return_value = (5,) + ("x",) * 11
        mock_get_contacts.return_value = [(1, "Jane Doe", "0111111111", "Emergency|Sister")]

        result = svc.get_emergency_contacts(1)
        assert result[0]["label"] == "Emergency"
        assert result[0]["relationship"] == "Sister"
        assert result[0]["name"] == "Jane Doe"

    @patch("db.patient_repo.get_emergency_contacts")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_get_emergency_contacts_no_label(self, mock_get_patient, mock_get_contacts):
        import services.patient_service as svc

        mock_get_patient.return_value = (5,) + ("x",) * 11
        mock_get_contacts.return_value = [(1, "Jane Doe", "0111111111", "Sister")]

        result = svc.get_emergency_contacts(1)
        assert result[0]["label"] == "Emergency"
        assert result[0]["relationship"] == "Sister"

    @patch("db.patient_repo.get_patient_by_user_id")
    def test_add_emergency_contact_missing_field_name(self, mock_get_patient):
        import services.patient_service as svc

        mock_get_patient.return_value = (5,) + ("x",) * 11

        with pytest.raises(ValueError, match="MISSING_FIELD:name"):
            svc.add_emergency_contact(1, {"relationship": "Sister", "phone": "011"})

    @patch("db.patient_repo.get_patient_by_user_id")
    def test_add_emergency_contact_missing_phone(self, mock_get_patient):
        import services.patient_service as svc

        mock_get_patient.return_value = (5,) + ("x",) * 11

        with pytest.raises(ValueError, match="MISSING_FIELD:phone"):
            svc.add_emergency_contact(1, {"name": "Jane", "relationship": "Sister"})

    @patch("db.patient_repo.get_medical_records")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_get_medical_records(self, mock_get_patient, mock_get_records):
        import services.patient_service as svc

        mock_get_patient.return_value = (5,) + ("x",) * 11
        mock_get_records.return_value = [(1, "2025-01-01", "Dr. Nkosi", "Flu", "General")]

        result = svc.get_medical_records(1)
        assert len(result) == 1
        assert result[0]["doctor"] == "Dr. Nkosi"
        assert result[0]["diagnosis"] == "Flu"


# ===========================================================================
# appointment_service
# ===========================================================================

class TestAppointmentService:

    @patch("db.appointment_repo.book_appointment")
    @patch("db.appointment_repo.get_available_timeslots")
    @patch("db.patient_repo.get_patient_by_user_id")
    @patch("db.doctor_repo.get_doctor_by_id")
    def test_book_appointment_success(self, mock_doctor, mock_patient, mock_slots, mock_book):
        import services.appointment_service as svc

        mock_patient.return_value = (5,) + ("x",) * 11
        mock_doctor.return_value = (3, "Dr. Nkosi", "GP", 1)
        mock_slots.return_value = [(7, "09:00", 1)]
        mock_book.return_value = (42, "2026-06-01", "09:00", "Dr. Nkosi")

        result = svc.book_appointment(1, {
            "doctor_id": 3,
            "date": "2026-06-01",
            "time_slot": "09:00",
            "reason": "Headache",
            "type": "in-person",
        })
        assert result["id"] == 42
        assert result["status"] == "confirmed"
        assert "qr_code_token" in result

    @patch("db.appointment_repo.get_available_timeslots")
    @patch("db.patient_repo.get_patient_by_user_id")
    @patch("db.doctor_repo.get_doctor_by_id")
    def test_book_appointment_no_slot_found(self, mock_doctor, mock_patient, mock_slots):
        import services.appointment_service as svc

        mock_patient.return_value = (5,) + ("x",) * 11
        mock_doctor.return_value = (3, "Dr. Nkosi", "GP", 1)
        mock_slots.return_value = [(7, "10:00", 1)]  # 09:00 not available

        with pytest.raises(LookupError, match="NO_SLOT_FOUND"):
            svc.book_appointment(1, {
                "doctor_id": 3,
                "date": "2026-06-01",
                "time_slot": "09:00",
                "reason": "Headache",
                "type": "in-person",
            })

    @patch("db.appointment_repo.book_appointment")
    @patch("db.appointment_repo.get_available_timeslots")
    @patch("db.patient_repo.get_patient_by_user_id")
    @patch("db.doctor_repo.get_doctor_by_id")
    def test_book_appointment_slot_conflict(self, mock_doctor, mock_patient, mock_slots, mock_book):
        import services.appointment_service as svc

        mock_patient.return_value = (5,) + ("x",) * 11
        mock_doctor.return_value = (3, "Dr. Nkosi", "GP", 1)
        mock_slots.return_value = [(7, "09:00", 1)]
        mock_book.side_effect = ValueError("SLOT_UNAVAILABLE")

        with pytest.raises(ValueError, match="SLOT_UNAVAILABLE"):
            svc.book_appointment(1, {
                "doctor_id": 3,
                "date": "2026-06-01",
                "time_slot": "09:00",
                "reason": "Headache",
                "type": "in-person",
            })

    @patch("db.appointment_repo.book_appointment")
    @patch("db.appointment_repo.get_available_timeslots")
    @patch("db.patient_repo.get_patient_by_user_id")
    @patch("db.doctor_repo.get_doctor_by_id")
    def test_book_appointment_virtual_maps_to_virtual_triage(
        self, mock_doctor, mock_patient, mock_slots, mock_book
    ):
        import services.appointment_service as svc

        mock_patient.return_value = (5,) + ("x",) * 11
        mock_doctor.return_value = (3, "Dr. Nkosi", "GP", 1)
        mock_slots.return_value = [(7, "09:00", 1)]
        mock_book.return_value = (1, "2026-06-01", "09:00", "Dr. A")

        svc.book_appointment(1, {
            "doctor_id": 3,
            "date": "2026-06-01",
            "time_slot": "09:00",
            "reason": "Check-up",
            "type": "virtual",
        })
        _args, kwargs = mock_book.call_args
        assert kwargs.get("booking_type") == "VIRTUAL_TRIAGE" or \
               "VIRTUAL_TRIAGE" in str(mock_book.call_args)

    def test_book_appointment_missing_required_field(self):
        import services.appointment_service as svc

        with pytest.raises(ValueError, match="MISSING_FIELD"):
            svc.book_appointment(1, {"doctor_id": 3, "date": "2026-06-01"})

    @patch("db.doctor_repo.get_all_doctors")
    def test_get_all_doctors(self, mock_doctors):
        import services.appointment_service as svc

        mock_doctors.return_value = [(1, "Dr. Nkosi", "Cardiology", 2)]

        result = svc.get_all_doctors()
        assert result[0]["id"] == 1
        assert result[0]["specialization"] == "Cardiology"
        assert result[0]["available"] is True

    @patch("db.appointment_repo.get_upcoming_appointments")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_get_upcoming(self, mock_patient, mock_appts):
        import services.appointment_service as svc

        mock_patient.return_value = (5,) + ("x",) * 11
        mock_appts.return_value = [
            (1, "2026-06-01", "09:00", "Dr. Nkosi", 3, "SICK", "SCHEDULED", "General")
        ]

        result = svc.get_upcoming(1)
        assert len(result) == 1
        assert result[0]["doctor"] == "Dr. Nkosi"
        assert result[0]["status"] == "upcoming"

    @patch("db.appointment_repo.get_appointment_history")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_get_history(self, mock_patient, mock_hist):
        import services.appointment_service as svc

        mock_patient.return_value = (5,) + ("x",) * 11
        mock_hist.return_value = [
            (1, "2025-01-01", "09:00", "Dr. Nkosi", "General", "Flu", "COMPLETED")
        ]

        result = svc.get_history(1)
        assert result[0]["status"] == "Completed"


# ===========================================================================
# Flask route integration tests (test client)
# ===========================================================================

class TestAuthRoutes:

    @pytest.fixture
    def client(self):
        import importlib
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True
        with app_module.app.test_client() as c:
            yield c

    @patch("services.auth_service.login")
    def test_login_route_success(self, mock_login, client):
        mock_login.return_value = {
            "access": "tok", "refresh": "ref", "role": "PATIENT",
            "user": {"id": 1, "username": "john_doe", "email": "j@nwu.ac.za"}
        }
        resp = client.post(
            "/api/v1/auth/login/",
            json={"username": "john_doe", "password": "secret123"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["role"] == "PATIENT"

    def test_login_route_missing_fields(self, client):
        resp = client.post("/api/v1/auth/login/", json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data
        assert "code" in data

    @patch("services.auth_service.login")
    def test_login_route_invalid_credentials(self, mock_login, client):
        mock_login.side_effect = ValueError("INVALID_CREDENTIALS")
        resp = client.post(
            "/api/v1/auth/login/",
            json={"username": "nobody", "password": "bad"},
        )
        assert resp.status_code == 401

    @patch("services.auth_service.register")
    def test_register_route_success(self, mock_register, client):
        mock_register.return_value = {
            "message": "Registration successful",
            "user": {
                "id": 1,
                "username": "alice",
                "email": "a@nwu.ac.za",
                "role": "PATIENT",
                "student_number": "S12345678",
            },
        }
        resp = client.post(
            "/api/v1/auth/register/",
            json={
                "username": "alice",
                "student_number": "48277444",
                "email": "48277444@mynwu.ac.za",
                "password": "Pass1234",
            },
        )
        assert resp.status_code == 201

    @patch("services.auth_service.register")
    def test_register_route_duplicate_user(self, mock_register, client):
        mock_register.side_effect = ValueError("USERNAME_EXISTS")
        resp = client.post(
            "/api/v1/auth/register/",
            json={
                "username": "alice",
                "student_number": "48277444",
                "email": "48277444@mynwu.ac.za",
                "password": "Pass1234",
            },
        )
        assert resp.status_code == 409
        data = resp.get_json()
        assert data["code"] == "DUPLICATE_USER"

    def test_register_route_missing_fields(self, client):
        resp = client.post("/api/v1/auth/register/", json={"username": "bob"})
        assert resp.status_code == 400

    def test_register_route_missing_student_number(self, client):
        resp = client.post(
            "/api/v1/auth/register/",
            json={"username": "bob", "email": "b@nwu.ac.za", "password": "pass123"},
        )
        assert resp.status_code == 400

    def test_register_route_rejects_invalid_student_number(self, client):
        resp = client.post(
            "/api/v1/auth/register/",
            json={
                "username": "test.user",
                "student_number": "1234",
                "email": "48277444@mynwu.ac.za",
                "password": "Pass1234",
            },
        )
        assert resp.status_code == 400
        assert resp.get_json()["code"] == "VALIDATION_ERROR"

    def test_register_route_rejects_invalid_email(self, client):
        resp = client.post(
            "/api/v1/auth/register/",
            json={
                "username": "test.user",
                "student_number": "48277444",
                "email": "bad@gmail.com",
                "password": "Pass1234",
            },
        )
        assert resp.status_code == 400

    def test_register_route_rejects_email_mismatch(self, client):
        resp = client.post(
            "/api/v1/auth/register/",
            json={
                "username": "test.user",
                "student_number": "48277444",
                "email": "11111111@mynwu.ac.za",
                "password": "Pass1234",
            },
        )
        assert resp.status_code == 400

    def test_register_route_rejects_weak_password(self, client):
        resp = client.post(
            "/api/v1/auth/register/",
            json={
                "username": "test.user",
                "student_number": "48277444",
                "email": "48277444@mynwu.ac.za",
                "password": "password",
            },
        )
        assert resp.status_code == 400

    def test_register_route_rejects_username_without_dot(self, client):
        resp = client.post(
            "/api/v1/auth/register/",
            json={
                "username": "testuser",
                "student_number": "48277444",
                "email": "48277444@mynwu.ac.za",
                "password": "Pass1234",
            },
        )
        assert resp.status_code == 400

    def test_me_route_no_token(self, client):
        resp = client.get("/api/v1/auth/me/")
        assert resp.status_code == 401
        data = resp.get_json()
        assert "code" in data

    def test_404_returns_error_envelope(self, client):
        resp = client.get("/api/v1/nonexistent-endpoint/")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data
        assert "code" in data

    def test_token_refresh_no_token(self, client):
        resp = client.post("/api/v1/auth/token/refresh/", json={})
        assert resp.status_code == 400


# ===========================================================================
# queue_service (authorization)
# ===========================================================================

class TestQueueService:

    @patch("db.queue_repo.create_queue_entry")
    @patch("db.queue_repo.get_queue_for_appointment")
    @patch("db.appointment_repo.get_appointment_by_id")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_patient_can_check_in_own_appointment(
        self, mock_patient, mock_appt, mock_get_queue, mock_create
    ):
        import services.queue_service as svc

        mock_appt.return_value = (10, 5, "SCHEDULED")
        mock_patient.return_value = (10, "48277444", "A", "B", None, None, None, None, None, None, None, None)
        mock_get_queue.return_value = None
        mock_create.return_value = 99

        result = svc.check_in_patient(1, user_id=7, role="PATIENT")
        assert result["queue_entry_id"] == 99

    @patch("db.appointment_repo.get_appointment_by_id")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_patient_cannot_check_in_other_appointment(self, mock_patient, mock_appt):
        import services.queue_service as svc

        mock_appt.return_value = (10, 5, "SCHEDULED")
        mock_patient.return_value = (99, "11111111", "A", "B", None, None, None, None, None, None, None, None)

        with pytest.raises(ValueError, match="FORBIDDEN"):
            svc.check_in_patient(1, user_id=7, role="PATIENT")

    @patch("db.queue_repo.get_queue_for_appointment")
    @patch("db.appointment_repo.get_appointment_by_id")
    def test_staff_can_access_any_appointment(self, mock_appt, mock_get_queue):
        import services.queue_service as svc

        mock_appt.return_value = (10, 5, "SCHEDULED")
        mock_get_queue.return_value = (1, 1, "WAITING", None, None, None, None)

        result = svc.get_queue_position(1, user_id=3, role="NURSE")
        assert result["queue_entry_id"] == 1

    @patch("db.appointment_repo.get_appointment_by_id")
    @patch("db.patient_repo.get_patient_by_user_id")
    def test_check_in_rejects_cancelled_appointment(self, mock_patient, mock_appt):
        import services.queue_service as svc

        mock_appt.return_value = (10, 5, "CANCELLED")
        mock_patient.return_value = (10, "48277444", "A", "B", None, None, None, None, None, None, None, None)

        with pytest.raises(ValueError, match="APPOINTMENT_NOT_CHECKIN_ELIGIBLE"):
            svc.check_in_patient(1, user_id=7, role="PATIENT")


# ===========================================================================
# pagination
# ===========================================================================

class TestPagination:

    def test_clamps_per_page(self):
        from utils.pagination import normalize_pagination

        page, per_page = normalize_pagination(1, 9999)
        assert per_page == 100

    def test_invalid_page_defaults_to_one(self):
        from utils.pagination import normalize_pagination

        page, per_page = normalize_pagination("x", "y")
        assert page == 1
        assert per_page == 20


# ===========================================================================
# access_control
# ===========================================================================

class TestRateLimit:

    def test_rate_limit_blocks_after_max(self):
        from utils.rate_limit import _hits, rate_limit_auth
        from flask import Flask

        app = Flask(__name__)
        _hits.clear()

        @app.route("/t", methods=["POST"])
        @rate_limit_auth
        def stub():
            return "ok", 200

        client = app.test_client()
        with app.test_request_context():
            pass

        for _ in range(15):
            resp = client.post("/t")
            assert resp.status_code == 200

        resp = client.post("/t")
        assert resp.status_code == 429


class TestAccessControl:

    def test_patient_own_appointment(self):
        from utils.access_control import can_access_appointment

        assert can_access_appointment("PATIENT", 10, 10) is True
        assert can_access_appointment("PATIENT", 10, 99) is False

    def test_staff_any_appointment(self):
        from utils.access_control import can_access_appointment

        assert can_access_appointment("DOCTOR", 10, None) is True
        assert can_access_appointment("ADMIN", 10, None) is True
