# Ubuntu Campus Clinic - Appointment System
## Complete System Design Blueprint - Phase 3 - Oracle SQL Migration

> **Group 19 - CMPG 311 - DBMS Module - Phase 3**
>
> This document is the single source of truth for the system architecture, Oracle database design, API contracts, security model, and implementation sequence. All architectural decisions reflect the Phase 3 migration from Django ORM + PostgreSQL to raw Oracle SQL + a SQL Repository Pattern.

---

## Table of Contents

1. [Document Identity](#1-document-identity)
2. [System Context](#2-system-context)
3. [Phase 3 Migration - What Changed and Why](#3-phase-3-migration---what-changed-and-why)
4. [Architecture Overview](#4-architecture-overview)
5. [System File Structure](#5-system-file-structure)
6. [Oracle Database Design](#6-oracle-database-design)
7. [SQL Repository Pattern](#7-sql-repository-pattern)
8. [Transaction Management & Concurrency](#8-transaction-management--concurrency)
9. [API Design & Contracts](#9-api-design--contracts)
10. [Security Architecture](#10-security-architecture)
11. [SQL Files Reference](#11-sql-files-reference)
12. [Module Ownership](#12-module-ownership)
13. [Design Decisions Log](#13-design-decisions-log)

---

## 1. Document Identity

| Field | Detail |
|---|---|
| **System Name** | Ubuntu Campus Clinic - Appointment System |
| **Project** | CMPG 311 - DBMS Module - Phase 3 |
| **Group** | Group 19 |
| **Primary Deliverable** | Oracle SQL database - DDL schema, DML seed data, indexes, views, and raw SQL queries demonstrated in Oracle SQL Developer |
| **Secondary Deliverable** | Python REST API using the SQL Repository Pattern + React 18 frontend |
| **DB Lead / Architect** | S1 - owns all SQL files, Oracle schema, seed data, and `backend/db/oracle_connection.py` |
| **Migration** | Django ORM + PostgreSQL -> raw Oracle SQL + SQL Repository Pattern |
| **Issue / Branch** | GitHub Issue #5 - `feature/5-oracle-raw-sql-migration` |

---

## 2. System Context

### What the System Is

A web-based appointment management platform replacing the manual paper-based scheduling system at Ubuntu Campus Clinic. The system manages the complete patient lifecycle: registration, appointment booking, queue management, consultation, medical record creation, and automated notification.

The Phase 3 version is database-first. The Oracle SQL database is the primary deliverable, and the backend and frontend exist to demonstrate that database working end-to-end through a realistic clinic workflow.

### The Problem It Solves

| Problem | How the System Solves It |
|---|---|
| Appointment delays of several days | 24/7 online booking with same-day slot allocation |
| Limited operating hours for booking | Browser-based portal accessible outside clinic hours |
| Manual scheduling errors | Validated digital booking with database-enforced constraints |
| Long in-clinic waiting times | Queue tracking with status transitions and room assignment |
| Lost or inaccurate paper records | Centralized Oracle medical history tables |
| No visibility into clinic performance | SQL views and raw reporting queries |
| No audit trail for sensitive data | `AUDIT_LOG` captures traceable system actions |

### System Actors

| Actor | Role |
|---|---|
| **Patient (Student)** | Registers, books appointments, checks in via QR token, views own medical history and notifications |
| **Doctor** | Views assigned appointments, manages timeslot availability, records diagnoses and treatment notes |
| **Nurse / Staff** | Manages the live queue and updates consultation status |
| **Admin** | Manages departments and staff, views reports, monitors audit logs |
| **System** | Generates tokens, writes notifications, records audit actions |

### System Boundaries

The system does not provide:

- Integration with external hospitals or national health systems
- AI diagnosis or automated medical treatment recommendations
- Billing, medical aid claims, or payment processing
- Emergency dispatch or ambulance services
- A dedicated mobile application
- Physical medical equipment management

---

## 3. Phase 3 Migration - What Changed and Why

Phase 3 changed the project direction from an ORM-managed web application to a database-first Oracle SQL project. This aligns the implementation with the DBMS rubric, where the examiner must be able to inspect and run the raw SQL directly in Oracle SQL Developer.

### What Was Removed

| Removed | Reason |
|---|---|
| Django ORM `models.py` approach | ORM hides the SQL that the rubric requires us to demonstrate |
| Django migrations | Migration files are generated Python, not hand-written Oracle DDL |
| PostgreSQL | The Phase 3 database target is Oracle SQL Developer / Oracle XE |
| `psycopg2` driver | PostgreSQL-specific driver replaced by `cx_Oracle` |
| Django-specific dependency set | Replaced with lightweight Python REST API dependencies |
| Raw SQL in views/controllers | SQL must be isolated in repository files only |

### What Was Added

| Added | Purpose |
|---|---|
| `sql/01_DDL/01_create_tables.sql` | Oracle DDL - 12 tables with full constraints |
| `sql/01_DDL/02_create_indexes.sql` | Performance and integrity indexes |
| `sql/01_DDL/03_create_views.sql` | Reporting and dashboard views |
| `sql/02_DML/04_insert_data.sql` | Realistic seed data using `INSERT INTO` statements |
| `sql/04_queries/05_queries.sql` | All required SQL query categories for the rubric |
| `sql/00_RUN_ALL.sql` | Master script for Oracle SQL Developer |
| `backend/db/oracle_connection.py` | Oracle connection factory using `cx_Oracle` |
| `backend/db/*_repo.py` | Repository files where all backend SQL is stored |

### Migration Mapping

| Before: Django ORM + PostgreSQL | After: Oracle SQL + Repository Pattern |
|---|---|
| `class Patient(models.Model):` | `CREATE TABLE PATIENT (...)` |
| `python manage.py makemigrations` | Edit `sql/01_DDL/01_create_tables.sql` |
| `python manage.py migrate` | Run `sql/00_RUN_ALL.sql` with F5 in Oracle SQL Developer |
| `python manage.py seed_db` | Run `sql/02_DML/04_insert_data.sql` |
| `Patient.objects.all()` | `SELECT * FROM PATIENT` inside `patient_repo.py` |
| `Patient.objects.filter(city='Potchefstroom')` | `SELECT * FROM PATIENT WHERE city = :1` |
| Django ORM transactions | Manual Oracle transaction with `commit()` / `rollback()` |

---

## 4. Architecture Overview

### The Four-Layer Architecture

```text
+----------------------------------------------------------------+
| LAYER 1 - PRESENTATION LAYER                                   |
|                                                                |
| React 18 - React Router v6 - Tailwind CSS - axios              |
| Renders UI, manages interaction, displays data                 |
| Never calls the database and never contains SQL                |
+----------------------------------------------------------------+
         |
         | HTTP/JSON - /api/v1/ - Authorization: Bearer <token>
         v
+----------------------------------------------------------------+
| LAYER 2 - APPLICATION / BUSINESS LAYER                         |
|                                                                |
| Python REST API - PyJWT - permission middleware                |
| Enforces rules, validates requests, authorizes users           |
| Calls service functions and returns JSON responses             |
+----------------------------------------------------------------+
         |
         | Function calls to service layer
         v
+----------------------------------------------------------------+
| LAYER 3 - SQL REPOSITORY LAYER                                 |
|                                                                |
| backend/db/*_repo.py - oracle_connection.py                    |
| Executes raw Oracle SQL and returns rows to the service layer   |
| All backend SQL lives here, with bind variables only           |
+----------------------------------------------------------------+
         |
         | cx_Oracle - Oracle SQL statements with bind variables
         v
+----------------------------------------------------------------+
| LAYER 4 - DATABASE LAYER                                       |
|                                                                |
| Oracle Database XE - 12 tables - indexes - views               |
| FK constraints - UNIQUE constraints - CHECK constraints        |
| ACID compliance - append-only AUDIT_LOG - POPIA traceability   |
|                                                                |
| PRIMARY EXAM DELIVERABLE                                      |
+----------------------------------------------------------------+
```

### Repository Rule

```text
React component
      |
      v
src/services/*.js
      |
      v
Python API route handler
      |
      v
backend/services/*.py
      |
      v
backend/db/*_repo.py       <- ALL BACKEND SQL LIVES HERE
      |
      v
cx_Oracle cursor.execute()
      |
      v
Oracle Database
```

No SQL string may appear in any backend file outside `backend/db/`. API files handle HTTP only. Service files handle business workflow only. Repository files handle SQL only.

### Layer Responsibilities

| Layer | Responsibility | Must Never Do |
|---|---|---|
| Presentation | Render UI and call frontend service functions | Contain SQL or business rules |
| Application | Validate, authorize, orchestrate workflow | Build SQL strings |
| SQL Repository | Execute parameterized Oracle SQL | Make UI or role-based decisions |
| Database | Store data and enforce integrity | Rely on the app for constraints it should own |

---

## 5. System File Structure

```text
Ubuntu-clinic-DBMS-grp-19/
|
+-- .gitignore
+-- .github/
|   +-- workflows/
|       +-- ci.yml
|
+-- sql/                              <- PRIMARY EXAM DELIVERABLE
|   +-- 00_RUN_ALL.sql                # Master script - F5 in SQL Developer
|   +-- 01_DDL/
|   |   +-- 01_create_tables.sql      # 12 Oracle tables
|   |   +-- 02_create_indexes.sql     # Performance indexes
|   |   +-- 03_create_views.sql       # Reporting views
|   +-- 02_DML/
|   |   +-- 04_insert_data.sql        # INSERT statements + COMMIT
|   +-- 04_queries/
|       +-- 05_queries.sql            # Rubric query categories
|
+-- backend/
|   +-- app.py                        # Backend entry point
|   +-- api/                          # Route handlers - HTTP only, no SQL
|   |   +-- auth.py
|   |   +-- patients.py
|   |   +-- appointments.py
|   |   +-- queue.py
|   |   +-- admin_reporting.py
|   |   +-- notifications.py
|   +-- services/                     # Business logic - calls repo functions
|   |   +-- auth_service.py
|   |   +-- patient_service.py
|   |   +-- appointment_service.py
|   |   +-- queue_service.py
|   +-- db/                           <- ALL BACKEND SQL LIVES HERE
|   |   +-- oracle_connection.py      # cx_Oracle connection factory
|   |   +-- user_account_repo.py      # USER_ACCOUNT auth queries
|   |   +-- patient_repo.py           # PATIENT + PATIENT_CONTACT + MEDICAL_RECORD
|   |   +-- appointment_repo.py       # APPOINTMENT + TIMESLOT
|   |   +-- doctor_repo.py            # STAFF + DOCTOR + DEPARTMENT
|   |   +-- queue_repo.py             # QUEUE_ENTRY
|   |   +-- notification_repo.py      # NOTIFICATION
|   |   +-- audit_repo.py             # AUDIT_LOG + reporting queries
|   +-- utils/
|   |   +-- jwt_helper.py
|   |   +-- error_handler.py
|   +-- tests/
|   +-- requirements.txt
|   +-- .env.example
|
+-- frontend/
|   +-- package.json
|   +-- vite.config.js
|   +-- README.md
|   +-- src/
|       +-- routes/
|       +-- context/                  # AuthContext - JWT - role
|       +-- services/                 # All axios calls
|       +-- pages/
|       |   +-- auth/
|       |   +-- patient/
|       |   +-- doctor/
|       |   +-- admin/
|       +-- components/
|       +-- utils/
|
+-- docs/
|   +-- SYSTEM_DESIGN.md              # This document
|
+-- README.md
+-- CONTRIBUTING.md
+-- TEAM_WORKFLOW.md
```

---

## 6. Oracle Database Design

### Entity-to-Table Rule

The approved database design has exactly 12 core entities. Therefore the Oracle DDL must create exactly these 12 core tables unless S1 approves a schema change.

Repository files do not have to be one-to-one with tables. A repo file can own a related group of tables, but it must not introduce extra database entities.

| # | Entity | Oracle Table | Backend Repo Owner |
|---|---|---|---|
| 1 | Patient | `PATIENT` | `patient_repo.py` |
| 2 | Patient Contact | `PATIENT_CONTACT` | `patient_repo.py` |
| 3 | User Account | `USER_ACCOUNT` | `user_account_repo.py` |
| 4 | Department | `DEPARTMENT` | `doctor_repo.py` |
| 5 | Staff | `STAFF` | `doctor_repo.py` |
| 6 | Doctor | `DOCTOR` | `doctor_repo.py` |
| 7 | Timeslot | `TIMESLOT` | `appointment_repo.py` |
| 8 | Appointment | `APPOINTMENT` | `appointment_repo.py` |
| 9 | Queue Entry | `QUEUE_ENTRY` | `queue_repo.py` |
| 10 | Medical Record | `MEDICAL_RECORD` | `patient_repo.py` |
| 11 | Notification | `NOTIFICATION` | `notification_repo.py` |
| 12 | Audit Log | `AUDIT_LOG` | `audit_repo.py` |

### The 12 Tables - Grouped by Domain

#### Identity Domain

| Table | Purpose | Key Constraints |
|---|---|---|
| `PATIENT` | Core patient entity - student profile and consent | `UNIQUE(student_number)` - `UNIQUE(email)` - `CHECK(consent_given IN (0,1))` |
| `PATIENT_CONTACT` | Emergency contact numbers | `FK -> PATIENT` with `ON DELETE CASCADE` |
| `USER_ACCOUNT` | Login credentials, role, account status | `CHECK(patient_id IS NOT NULL OR staff_id IS NOT NULL)` - `UNIQUE(username)` |

#### Staff Domain

| Table | Purpose | Key Constraints |
|---|---|---|
| `DEPARTMENT` | Clinic organisational structure | `UNIQUE(department_name)` - nullable department head FK |
| `STAFF` | All clinic employees | `UNIQUE(email)` - `FK -> DEPARTMENT` - role `CHECK` |
| `DOCTOR` | Doctor-specific subtype of staff | `PK = FK -> STAFF` - `UNIQUE(license_number)` |

#### Scheduling Domain

| Table | Purpose | Key Constraints |
|---|---|---|
| `TIMESLOT` | Available date and time blocks | `CHECK(is_available IN (0,1))` - `CHECK(end_time > start_time)` |
| `APPOINTMENT` | Core transactional booking entity | `UNIQUE(slot_id)` prevents double-booking at DB level |

#### Operations Domain

| Table | Purpose | Key Constraints |
|---|---|---|
| `QUEUE_ENTRY` | Check-in, consultation tracking, room assignment | `UNIQUE(appointment_id)` - queue status `CHECK` |
| `MEDICAL_RECORD` | Diagnosis, prescription, treatment notes | `FK -> APPOINTMENT` - `FK -> PATIENT` |

#### System Domain

| Table | Purpose | Key Constraints |
|---|---|---|
| `NOTIFICATION` | Email / SMS / portal notification delivery log | `CHECK(patient_id IS NOT NULL OR staff_id IS NOT NULL)` |
| `AUDIT_LOG` | Complete action history for POPIA traceability | `FK -> USER_ACCOUNT` - timestamp default |

### Oracle Data Types Used

| Concept | Oracle Type | Example |
|---|---|---|
| Auto-increment primary key | `NUMBER GENERATED ALWAYS AS IDENTITY` | `patient_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY` |
| Short text | `VARCHAR2(n)` | `first_name VARCHAR2(100) NOT NULL` |
| Long text | `VARCHAR2(4000)` | `diagnosis VARCHAR2(4000)` |
| Boolean-style flag | `NUMBER(1)` | `consent_given NUMBER(1) DEFAULT 0 NOT NULL` |
| Date only | `DATE` | `date_of_birth DATE NOT NULL` |
| Date and time | `TIMESTAMP` | `log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

### FK Dependency Graph - Creation Order

```text
LEVEL 1 - No FK dependencies - create first
+-- PATIENT
+-- TIMESLOT
+-- DEPARTMENT

LEVEL 2 - Depends on Level 1
+-- PATIENT_CONTACT -> PATIENT
+-- STAFF           -> DEPARTMENT
    +-- ALTER TABLE DEPARTMENT ADD head_staff FK -> STAFF

LEVEL 3 - Depends on Level 2
+-- DOCTOR       -> STAFF
+-- USER_ACCOUNT -> PATIENT optional + STAFF optional

LEVEL 4 - Depends on Level 3
+-- APPOINTMENT -> PATIENT + STAFF + TIMESLOT
+-- AUDIT_LOG   -> USER_ACCOUNT

LEVEL 5 - Create last
+-- QUEUE_ENTRY    -> APPOINTMENT
+-- MEDICAL_RECORD -> APPOINTMENT + PATIENT
+-- NOTIFICATION   -> APPOINTMENT optional + PATIENT optional + STAFF optional
```

### Status Lifecycles

#### Appointment Lifecycle

```text
SCHEDULED
    |
    v
CONFIRMED
    |
    +-- patient checks in -> QUEUE_ENTRY created
    |
    v
COMPLETED

Alternative exits:
SCHEDULED or CONFIRMED -> CANCELLED
CONFIRMED              -> NO_SHOW
```

#### Queue Entry Lifecycle

```text
WAITING
    |
    v
IN_PROGRESS
    |
    v
COMPLETED

Alternative exit:
WAITING -> LEFT_WITHOUT_SEEN
```

### Critical Constraints

| Constraint | Table | What It Prevents |
|---|---|---|
| `UNIQUE(slot_id)` | `APPOINTMENT` | Double-booking the same timeslot |
| `UNIQUE(appointment_id)` | `QUEUE_ENTRY` | Duplicate check-ins for one appointment |
| `UNIQUE(student_number)` | `PATIENT` | Duplicate student registration |
| `UNIQUE(email)` | `PATIENT`, `STAFF` | Duplicate identity records |
| `UNIQUE(license_number)` | `DOCTOR` | Duplicate doctor registration |
| `UNIQUE(username)` | `USER_ACCOUNT` | Duplicate login accounts |
| `CHECK(patient_id IS NOT NULL OR staff_id IS NOT NULL)` | `USER_ACCOUNT`, `NOTIFICATION` | Ownerless accounts or notifications |
| Status `CHECK` constraints | `APPOINTMENT`, `QUEUE_ENTRY` | Invalid lifecycle values |
| `CHECK(end_time > start_time)` | `TIMESLOT` | Invalid slot time ranges |
| Foreign keys | All relationship tables | Orphan records and invalid references |

### Index Strategy

| Index | Table | Columns | Justification |
|---|---|---|---|
| `idx_timeslot_date` | `TIMESLOT` | `slot_date` | Availability queries by date |
| `idx_timeslot_date_avail` | `TIMESLOT` | `slot_date, is_available` | Most frequent query - booking form |
| `idx_appt_patient` | `APPOINTMENT` | `patient_id` | Patient appointment history |
| `idx_appt_staff` | `APPOINTMENT` | `staff_id` | Doctor schedule queries |
| `idx_appt_status` | `APPOINTMENT` | `status` | Filter scheduled, confirmed, completed records |
| `idx_queue_appt` | `QUEUE_ENTRY` | `appointment_id` | Check-in lookup |
| `idx_queue_status` | `QUEUE_ENTRY` | `status` | Live queue board filtering |
| `idx_mr_patient` | `MEDICAL_RECORD` | `patient_id` | Full patient history |
| `idx_mr_appt` | `MEDICAL_RECORD` | `appointment_id` | Records per appointment |
| `idx_notif_appt` | `NOTIFICATION` | `appointment_id` | Notifications per appointment |
| `idx_audit_timestamp` | `AUDIT_LOG` | `log_timestamp` | Date-range admin reports |
| `idx_audit_user` | `AUDIT_LOG` | `user_id` | Per-user activity history |

### Views

| View | Purpose | Tables Joined |
|---|---|---|
| `vw_patient_appointments` | Patient dashboard - full booking history | `PATIENT` + `APPOINTMENT` + `TIMESLOT` + `STAFF` |
| `vw_daily_queue_board` | Live queue for nurses and admin | `QUEUE_ENTRY` + `APPOINTMENT` + `PATIENT` + `TIMESLOT` + `STAFF` |
| `vw_doctor_schedule` | Doctor schedule with patient details | `STAFF` + `DOCTOR` + `DEPARTMENT` + `APPOINTMENT` + `TIMESLOT` + `PATIENT` |
| `vw_audit_trail_summary` | POPIA audit trail in readable form | `AUDIT_LOG` + `USER_ACCOUNT` + `PATIENT` + `STAFF` |

### Normalisation - 3NF Compliance

**1NF:** All attributes are atomic. Address fields are split into street, city, and postal code. `PATIENT_CONTACT` stores multiple emergency contacts as separate rows.

**2NF:** Tables use single-column surrogate primary keys. No composite primary key creates partial dependency risk.

**3NF:** The `DOCTOR` table separates doctor-specific attributes such as `license_number` and `specialisation` from the general `STAFF` table. These attributes depend on being a doctor, not merely on being a staff member.

---

## 7. SQL Repository Pattern

### Connection Factory

```python
# backend/db/oracle_connection.py
import os
import cx_Oracle
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    dsn = cx_Oracle.makedsn(
        os.getenv("ORA_HOST", "localhost"),
        int(os.getenv("ORA_PORT", "1521")),
        sid=os.getenv("ORA_SID", "XE"),
    )

    return cx_Oracle.connect(
        user=os.getenv("ORA_USER"),
        password=os.getenv("ORA_PASSWORD"),
        dsn=dsn,
    )
```

### Repository Function Pattern

Every repository function follows this structure:

```python
def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT patient_id, student_number, first_name, last_name "
            "FROM PATIENT "
            "ORDER BY last_name"
        )
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()
```

### Bind Variables - Mandatory

```python
# Wrong - SQL injection risk and no plan reuse
cursor.execute(f"SELECT * FROM PATIENT WHERE city = '{city}'")

# Correct - bind variable
cursor.execute(
    "SELECT * FROM PATIENT WHERE city = :1",
    [city],
)
```

All user-controlled values must be passed as bind variables. String concatenation into SQL is prohibited.

### DML with Commit and Rollback

```python
def create_patient(student_number, first_name, last_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO PATIENT (student_number, first_name, last_name) "
            "VALUES (:1, :2, :3)",
            [student_number, first_name, last_name],
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
```

Oracle does not auto-commit DML. Every write operation must explicitly `commit()` on success and `rollback()` on failure.

---

## 8. Transaction Management & Concurrency

### The Double-Booking Problem

When two patients try to book the same slot at the same time, an application-level availability check is not enough. Both requests can read `is_available = 1` before either request inserts the appointment.

### The Two-Layer Defence

**Layer 1 - Row lock using `SELECT FOR UPDATE`:**

```sql
SELECT slot_id, is_available
FROM TIMESLOT
WHERE slot_id = :1
FOR UPDATE;
```

This locks the selected timeslot row until the current transaction commits or rolls back. A competing booking request must wait before it can read or modify that row.

**Layer 2 - `UNIQUE(slot_id)` on `APPOINTMENT`:**

Even if a bug bypasses the row-lock workflow, the database still rejects a second appointment for the same slot. The constraint is the final enforcer.

### Booking Transaction Shape

```text
1. Open Oracle connection
2. SELECT TIMESLOT ... FOR UPDATE
3. If unavailable, rollback and return 409 SLOT_UNAVAILABLE
4. INSERT APPOINTMENT
5. UPDATE TIMESLOT SET is_available = 0
6. INSERT AUDIT_LOG
7. COMMIT
8. Return appointment confirmation
```

### ACID in Oracle

| Property | Oracle Implementation |
|---|---|
| **Atomicity** | The whole booking commits or rolls back as one transaction |
| **Consistency** | `UNIQUE`, `CHECK`, `FK`, and `NOT NULL` constraints are enforced on every write |
| **Isolation** | `SELECT FOR UPDATE` blocks concurrent stale reads during booking |
| **Durability** | Oracle redo logs preserve committed transactions after restart |

---

## 9. API Design & Contracts

### Design Principles

- All endpoints are versioned under `/api/v1/`
- All responses are JSON
- Protected endpoints require `Authorization: Bearer <access_token>`
- API route handlers do not contain SQL
- Service files call repository functions
- Repository files use Oracle bind variables
- Error responses follow one standard shape

### Frontend API Contract Handoff

The detailed frontend-to-backend API handoff lives in [`docs/UBUNTU_CLINIC_API_CONTRACT_v1_2.md`](./UBUNTU_CLINIC_API_CONTRACT_v1_2.md). The original Word handoff is preserved as [`docs/UBUNTU_CLINIC_API_CONTRACT_v1_2.docx`](./UBUNTU_CLINIC_API_CONTRACT_v1_2.docx). These documents were prepared by the frontend teams because frontend development began before backend implementation.

Backend remains the source of truth after review. If the mock contract conflicts with the Oracle schema, repository pattern, or security model in this system design, S1 and the backend owners resolve the conflict before implementation.

### Endpoint Reference

| Method | Endpoint | Access | Repository Called |
|---|---|---|---|
| `POST` | `/api/v1/auth/login/` | Public | `user_account_repo.get_by_username()` |
| `POST` | `/api/v1/auth/register/` | Public | `patient_repo.create_patient()` + `user_account_repo.create_user()` |
| `GET` | `/api/v1/patients/` | Admin | `patient_repo.get_all_patients()` |
| `GET` | `/api/v1/patients/{id}/` | Patient / Admin | `patient_repo.get_patient_by_id()` |
| `PATCH` | `/api/v1/patients/{id}/` | Patient | `patient_repo.update_patient()` |
| `GET` | `/api/v1/patients/{id}/records/` | Doctor / Patient | `patient_repo.get_medical_records()` |
| `GET` | `/api/v1/timeslots/` | Auth | `appointment_repo.get_available_slots()` |
| `POST` | `/api/v1/appointments/` | Patient | `appointment_repo.create_appointment()` |
| `GET` | `/api/v1/appointments/` | Auth | `appointment_repo.get_appointments_for_user()` |
| `PATCH` | `/api/v1/appointments/{id}/cancel/` | Patient / Admin | `appointment_repo.cancel_appointment()` |
| `POST` | `/api/v1/queue/check-in/` | Patient / Staff | `queue_repo.create_queue_entry()` |
| `GET` | `/api/v1/queue/` | Doctor / Admin | `queue_repo.get_live_queue()` |
| `PATCH` | `/api/v1/queue/{id}/status/` | Doctor / Admin | `queue_repo.update_status()` |
| `GET` | `/api/v1/admin/reports/daily/` | Admin | `audit_repo.daily_appointments_report()` |
| `GET` | `/api/v1/admin/reports/wait-times/` | Admin | `audit_repo.wait_time_report()` |
| `GET` | `/api/v1/admin/audit-log/` | Admin | `audit_repo.get_audit_log()` |
| `GET` | `/api/v1/notifications/` | Auth | `notification_repo.get_for_user()` |
| `PATCH` | `/api/v1/notifications/{id}/read/` | Auth | `notification_repo.mark_as_read()` |

### Standard Response Shapes

**Success - single object**

```json
{
  "data": {
    "patient_id": 1,
    "first_name": "Karabo"
  },
  "message": "OK"
}
```

**Success - list**

```json
{
  "data": [],
  "count": 8
}
```

**Error**

```json
{
  "error": "Slot is no longer available",
  "code": "SLOT_UNAVAILABLE",
  "status": 409
}
```

---

## 10. Security Architecture

### Role-Based Access Control

| Role | Access |
|---|---|
| `PATIENT` | Own profile, own appointments, own medical records, own notifications |
| `DOCTOR` | Assigned appointments, queue board, records for their own patients |
| `NURSE` / `STAFF` | Queue operations and operational clinic views |
| `ADMIN` | Full access to records, reports, audit logs, departments, and staff management |

### JWT Authentication

The backend issues JWTs after successful login. The token carries the user's role and owner identifiers so the API can enforce access rules without repeated lookups for every standard request.

Sensitive operations still verify the account against `USER_ACCOUNT`, especially when viewing medical records, accessing audit logs, or performing admin actions.

### Audit Trail

Every sensitive database action writes to `AUDIT_LOG`:

```sql
INSERT INTO AUDIT_LOG
    (user_id, action, table_affected, record_affected_id, ip_address)
VALUES
    (:1, :2, :3, :4, :5);
```

This supports POPIA traceability by recording who accessed or changed data, what was affected, when it happened, and where the request came from.

### SQL Injection Prevention

All SQL in `backend/db/*_repo.py` must use `cx_Oracle` bind variables:

```python
cursor.execute(
    "SELECT * FROM USER_ACCOUNT WHERE username = :1",
    [username],
)
```

String interpolation, concatenation, or f-strings inside SQL statements are not allowed.

### Password Security

Passwords are never stored in plain text. The backend stores password hashes only. Authentication compares the supplied password against the stored hash.

### QR Token Security

| Property | Detail |
|---|---|
| Token generation | Unique token generated when an appointment is created |
| Expiry | Token expires after the appointment check-in window |
| Validation | Check-in validates token existence, appointment ownership, and expiry |
| Failure response | Invalid or expired tokens return a standard `401` error |

---

## 11. SQL Files Reference

### `00_RUN_ALL.sql`

Master script. Run with F5 in Oracle SQL Developer. It calls all SQL files in the correct order and ends with verification queries.

### `01_create_tables.sql`

Creates all 12 tables in FK dependency order. Every table must use:

- Oracle-standard data types
- Named constraints
- `NUMBER GENERATED ALWAYS AS IDENTITY` primary keys where appropriate
- FK, `UNIQUE`, `CHECK`, `NOT NULL`, and default constraints
- Safe rerun setup with `DROP TABLE ... CASCADE CONSTRAINTS PURGE`

### `02_create_indexes.sql`

Creates performance indexes for high-use lookup patterns, including appointment history, doctor schedules, queue board filtering, medical record history, notification lookup, and audit reporting.

### `03_create_views.sql`

Creates reporting and dashboard views using `CREATE OR REPLACE VIEW`. Each view should include a header comment explaining its business purpose and the UI or report that uses it.

### `04_insert_data.sql`

Loads realistic South African clinic seed data. Insert order must follow the FK dependency graph. The file ends with `COMMIT` and row-count verification queries.

### `05_queries.sql`

Contains all rubric query categories. Each query block starts with a clear comment explaining:

- The query category
- The business question being answered
- The tables involved
- Any notable Oracle SQL feature used

This file is designed for one-query-at-a-time F9 execution during the demo video.

---

## 12. Module Ownership

| Module | Owner | SQL Files | Backend Files |
|---|---|---|---|
| **Oracle Schema** | S1 | All files in `sql/` | `backend/db/oracle_connection.py` |
| **Auth** | B1 | None | `api/auth.py` - `services/auth_service.py` - `db/user_account_repo.py` |
| **Patients** | B2 | None | `db/patient_repo.py` - `api/patients.py` - `services/patient_service.py` |
| **Appointments & Queue** | B3 | None | `db/appointment_repo.py` - `db/queue_repo.py` - `api/appointments.py` - `api/queue.py` |
| **Admin & Reporting** | B4 | None | `db/audit_repo.py` - `api/admin_reporting.py` - reporting tests |
| **Notifications** | B4 / shared | None | `db/notification_repo.py` - `api/notifications.py` |
| **Frontend Shell** | F1 | None | Auth context, routing, shared layout, reusable components |
| **Patient UI** | F2 | None | Patient dashboard, profile, appointment history, medical history |
| **Doctor UI** | F3 | None | Doctor dashboard, booking form, queue board |
| **Admin UI** | F4 | None | Reports, audit log, notifications panel |

### S1 Authority

S1 owns the database direction and must review any change that affects:

- SQL table structure
- FK relationships
- Constraint names or rules
- Index strategy
- Views
- Seed data assumptions
- Repository SQL that changes database behavior
- CI checks for SQL files

---

## 13. Design Decisions Log

| Decision | Chosen | Rejected | Reason |
|---|---|---|---|
| **Database** | Oracle XE 21c | PostgreSQL | Rubric requires Oracle SQL Developer demonstration |
| **DB access pattern** | SQL Repository Pattern | Django ORM | ORM hides SQL; repository pattern keeps SQL visible and auditable |
| **SQL organisation** | Separate `.sql` files by purpose | Single SQL dump file | Easier marking, review, reruns, and demo recording |
| **Primary key strategy** | `GENERATED ALWAYS AS IDENTITY` | Manual sequences | Cleaner Oracle 12c+ syntax and less boilerplate |
| **Doctor design** | Subtype table with PK as FK to `STAFF` | Nullable doctor columns on `STAFF` | 3NF compliance and cleaner staff model |
| **Double-booking prevention** | `UNIQUE(slot_id)` + `SELECT FOR UPDATE` | Application-level check only | Database constraints cannot be bypassed |
| **Migration strategy** | Manual Oracle DDL scripts | Django migrations | Rubric requires hand-written Oracle DDL |
| **Bind variables** | `cx_Oracle` `:1`, `:2` syntax | String interpolation | Prevents SQL injection and supports Oracle execution plan caching |
| **View strategy** | Purpose-specific views | One large mega-view | Each view maps to a clear UI/reporting need |
| **Audit strategy** | Append-only `AUDIT_LOG` | Informal app logging only | Database-backed traceability supports POPIA |
| **Frontend coupling** | Frontend calls `/api/v1/` only | Frontend aware of database schema | Keeps the database behind the API boundary |
| **S1 control point** | S1 reviews database-impacting changes | Everyone edits schema independently | Prevents FK, seed data, and integration conflicts |

---

*Ubuntu Campus Clinic - Appointment System - Group 19 - CMPG 311 - DBMS Module*

*Document lives at `docs/SYSTEM_DESIGN.md` and is referenced from `README.md`.*
