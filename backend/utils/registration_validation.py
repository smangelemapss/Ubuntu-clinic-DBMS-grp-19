import re

STUDENT_NUMBER_RE = re.compile(r"^\d{8}$")
NWU_EMAIL_RE = re.compile(r"^(\d{8})@mynwu\.ac\.za$", re.IGNORECASE)
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")

NWU_EMAIL_DOMAIN = "@mynwu.ac.za"


def normalize_student_number(value):
    return (value or "").strip()


def normalize_nwu_email(value):
    return (value or "").strip().lower()


def expected_nwu_email(student_number):
    return f"{student_number}{NWU_EMAIL_DOMAIN}"


def validate_student_number(student_number):
    student_number = normalize_student_number(student_number)
    if not student_number:
        return "STUDENT_NUMBER_REQUIRED"
    if not STUDENT_NUMBER_RE.match(student_number):
        return "STUDENT_NUMBER_INVALID"
    return None


def validate_nwu_email(email, student_number):
    email = normalize_nwu_email(email)
    student_number = normalize_student_number(student_number)
    if not email:
        return "EMAIL_REQUIRED"
    match = NWU_EMAIL_RE.match(email)
    if not match:
        return "EMAIL_INVALID"
    if match.group(1) != student_number:
        return "EMAIL_STUDENT_MISMATCH"
    return None


def validate_password(password):
    if not password:
        return "PASSWORD_REQUIRED"
    if len(password) < 8:
        return "PASSWORD_TOO_SHORT"
    if not PASSWORD_RE.match(password):
        return "PASSWORD_WEAK"
    return None


def validate_registration(username, email, password, student_number):
    student_number = normalize_student_number(student_number)
    email = normalize_nwu_email(email)

    err = validate_student_number(student_number)
    if err:
        return err
    err = validate_nwu_email(email, student_number)
    if err:
        return err
    err = validate_password(password)
    if err:
        return err
    if not (username or "").strip():
        return "USERNAME_REQUIRED"
    if "." not in username.strip():
        return "USERNAME_INVALID"
    return None
