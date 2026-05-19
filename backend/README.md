# Ubuntu Campus Clinic — Backend

Group 19 | CMPG 311 | DBMS Module  
Flask REST API backed by Oracle XE 21c.

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | `python --version` to verify |
| Oracle Database XE | 21c | Must be running locally on port 1521 |
| `oracledb` (thin mode) | 2.x | Included in `requirements.txt` — **no Oracle Instant Client required** |
| Oracle Instant Client | 21.x | Only if using optional `cx_Oracle` thick mode |
| pip | latest | Bundled with Python 3.10+ |

---

## Installation

### For running tests (no Oracle needed)

```bash
pip install -r requirements.txt
pytest -q
# Expected: 83 passed
```

### For running the live server (Oracle XE required)

```bash
pip install -r requirements.txt
python scripts/check_db.py   # must print [OK] before starting the API
```

Optional thick-mode driver (only if you prefer `cx_Oracle` + Instant Client):

```bash
pip install -r requirements-oracle.txt
```

For Oracle XE Docker setup (database + Instant Client), see **Run the Database Schema** below
and the main repo `README.md` → Getting Started → Set Up Oracle Database.

## Setup Steps

```bash
# 1. Clone the repo
git clone https://github.com/your-org/Ubuntu-clinic-DBMS-grp-19.git
cd Ubuntu-clinic-DBMS-grp-19

# 2. Install Python dependencies (from the backend/ folder)
cd backend
pip install -r requirements.txt

# 3. Copy the environment template and fill in your credentials
cp .env.example .env
```

Open `.env` in any text editor and set your Oracle credentials (see the [Environment Variables](#environment-variables) table below).

---

## Run the Database Schema

1. Open **Oracle SQL Developer**.
2. Connect to your local XE instance.
3. Open `sql/00_RUN_ALL.sql` from the **project root** directory.
4. Press **F5** (Run Script) — the master script calls all DDL and DML files in order.

> **Important:** SQL Developer must be opened from the project root (where the `sql/` folder lives).  
> The `@sql/...` paths in `00_RUN_ALL.sql` are relative to the working directory.  
> If you opened SQL Developer from inside the `sql/` folder the paths will fail.

After the schema runs, set real password hashes on the seed accounts:

```bash
# From the backend/ folder
python scripts/reset_seed_passwords.py
```

---

## Start the Server

### Development

```bash
# From the backend/ folder
python app.py
```

The API starts on **http://localhost:8000**.

### Production (WSGI)

Set `FLASK_ENV=production` and a strong `JWT_SECRET` in `.env`, then:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:app"
```

Update `CORS_ORIGINS` to your deployed frontend URL before going live.

---

## Run Tests

```bash
# From the backend/ folder
pytest
```

Expected result: **83 passed**.

### Deploy readiness (run phases in order)

```bash
# All phases: database -> backend -> frontend -> full connection
python scripts/verify_deploy_ready.py

# Or one phase at a time:
python scripts/verify_database.py --fix-passwords
python scripts/verify_backend.py
python scripts/verify_frontend.py
python scripts/verify_full_stack.py
```

Use `--http` on the full-stack or master script when the Flask server is already running.

Tests use an in-memory Oracle mock — no live Oracle Client is needed for CI (see [Oracle Mock Strategy](#oracle-mock-strategy-for-ci)).

---

## Environment Variables

All variables live in `backend/.env` (copied from `.env.example`).

| Variable | Default | Description |
|---|---|---|
| `ORA_USER` | `system` | Oracle DB username |
| `ORA_PASSWORD` | *(empty)* | Oracle DB password |
| `ORA_HOST` | `localhost` | Oracle DB hostname |
| `ORA_PORT` | `1521` | Oracle DB listener port |
| `ORA_SID` | `XE` | Oracle SID (service name for XE is `XE`) |
| `JWT_SECRET` | `changeme-secret` | Secret key for signing JWT tokens — **change before demo** |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRY_MINUTES` | `60` | Access token lifetime in minutes |
| `FLASK_ENV` | `development` | Flask environment (`development` / `production`) |
| `FLASK_PORT` | `8000` | Port the Flask dev server listens on |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Comma-separated allowed origins for CORS |

---

## Backend Assignment Map

| Developer | Assignment | Owned Files | Key Endpoints |
|---|---|---|---|
| **B1** | Auth & User Accounts | `api/auth.py`, `services/auth_service.py`, `db/user_account_repo.py`, `utils/jwt_helper.py` | `POST /auth/login`, `POST /auth/logout`, `POST /auth/refresh` |
| **B2** | Patients & Records | `api/patients.py`, `services/patient_service.py`, `db/patient_repo.py` | `GET/POST /patients`, `GET /patients/<id>`, `GET /patients/<id>/records` |
| **B3** | Appointments & Queue | `api/appointments.py`, `api/queue.py`, `services/appointment_service.py`, `services/queue_service.py`, `db/appointment_repo.py`, `db/queue_repo.py` | `GET/POST /appointments`, `GET/PUT /queue` |
| **B4** | Notifications & Admin Reporting | `api/notifications.py`, `api/admin_reporting.py`, `db/notification_repo.py`, `db/audit_repo.py`, `db/doctor_repo.py` | `GET /notifications`, `GET /admin/reports/*` |

---

## Oracle Mock Strategy for CI

The test suite (`backend/tests/`) does **not** require a live Oracle database or Oracle Instant Client.

`db/oracle_connection.py` gracefully handles a missing `cx_Oracle` import:

```python
try:
    import cx_Oracle as _cx_Oracle
    _CX_ORACLE_AVAILABLE = True
except ImportError:
    _cx_Oracle = None
    _CX_ORACLE_AVAILABLE = False
```

All repository classes and service layers are tested with `unittest.mock.patch` / `MagicMock` stubs that replace `get_connection()`.  
This means `pytest` passes in any CI environment (GitHub Actions, local without Oracle) without needing Oracle Instant Client installed.

---

## Seed Accounts

After running `scripts/reset_seed_passwords.py`, the following accounts are available for testing:

| Username | Role | Password |
|---|---|---|
| `karabo.mabena` | PATIENT | `Clinic@123` (student `10012345`, email `10012345@mynwu.ac.za`, 1 past + 1 upcoming appointment) |
| `dr.mokoena` | DOCTOR | `Clinic@123` |
| `nurse.molefe` | NURSE | `Clinic@123` |
| `admin.ndlovu` | ADMIN | `Clinic@123` |

*(The existing `student_10012345` … `admin_ndlovu` accounts from the original seed also exist but use placeholder hashes.)*
