"""Unit tests for NWU registration validation rules."""
import pytest

from utils.registration_validation import (
    expected_nwu_email,
    validate_nwu_email,
    validate_password,
    validate_registration,
    validate_student_number,
)


class TestStudentNumber:
    def test_valid(self):
        assert validate_student_number("48277444") is None

    def test_empty(self):
        assert validate_student_number("") == "STUDENT_NUMBER_REQUIRED"

    def test_too_short(self):
        assert validate_student_number("1234") == "STUDENT_NUMBER_INVALID"

    def test_too_long(self):
        assert validate_student_number("123456789") == "STUDENT_NUMBER_INVALID"

    def test_non_numeric(self):
        assert validate_student_number("4827744a") == "STUDENT_NUMBER_INVALID"


class TestNwuEmail:
    def test_valid(self):
        assert validate_nwu_email("48277444@mynwu.ac.za", "48277444") is None

    def test_wrong_domain(self):
        assert validate_nwu_email("48277444@nwu.ac.za", "48277444") == "EMAIL_INVALID"

    def test_mismatch(self):
        assert validate_nwu_email("11111111@mynwu.ac.za", "48277444") == "EMAIL_STUDENT_MISMATCH"

    def test_expected_helper(self):
        assert expected_nwu_email("48277444") == "48277444@mynwu.ac.za"


class TestPassword:
    def test_valid(self):
        assert validate_password("Clinic@123") is None

    def test_weak_no_digit(self):
        assert validate_password("password") == "PASSWORD_WEAK"

    def test_short(self):
        assert validate_password("Ab1") == "PASSWORD_TOO_SHORT"


class TestFullRegistration:
    def test_valid_payload(self):
        assert (
            validate_registration(
                "karabo.mabena",
                "48277444@mynwu.ac.za",
                "Pass1234",
                "48277444",
            )
            is None
        )

    def test_invalid_username(self):
        assert validate_registration("bob", "48277444@mynwu.ac.za", "Pass1234", "48277444") == "USERNAME_INVALID"
