# Contributing to Ubuntu Campus Clinic — Appointment System

Welcome to the team. 🎉

This is a CMPG 311 DBMS module project. The goal is to build a production-grade Clinic Appointment System while practising real-world software engineering — git workflows, Oracle database design, code reviews, and API development.

Read this document once before writing any code. Reference it whenever you are unsure about a process.

---

## The Golden Rules

1. **The Oracle database is sacred.** The SQL schema is the primary exam deliverable. No column renames, table renames, or structural changes without S1's written sign-off first.
2. **SQL has two approved homes.** Exam/demo SQL lives in the `sql/` folder. Runtime backend SQL lives only in `backend/db/*_repo.py`. No SQL strings are allowed in API routes, controllers, or service files.
3. **Be kind.** Constructive feedback is a gift — give it respectfully and receive it gracefully. Everyone is learning.
4. **Code is read more than written.** Write clean, self-documenting SQL and Python. Name your queries clearly. Add a comment above every SQL block explaining what business question it answers.
5. **One concern per branch.** A branch that mixes two modules makes review impossible and rollback destructive.

---

## Branch Model

Three types of branches. Never work directly on `main` or `dev`.

| Branch | Purpose | Who Touches It |
|---|---|---|
| `main` | Production-ready only · examiner accesses live URL from here | S1 merges `dev` into `main` at sprint end |
| `dev` | Integration branch · all PRs target here | Everyone via PR only |
| `feature/your-branch` | Your working branch · one per module or concern | The person who owns that module |

---

## Branch Naming Convention

| Branch | Owner | Purpose |
|---|---|---|
| `feature/5-oracle-raw-sql-migration` | S1 | Oracle schema · all 12 tables · indexes · views · seed data |
| `feature/b1-auth-api` | B1 | JWT endpoints · oracle_connection.py · permission logic |
| `feature/b2-patient-api` | B2 | patient_repo.py · Patient + Contact + MedicalRecord API |
| `feature/b3-booking-api` | B3 | appointment_repo.py · queue_repo.py · QR generation |
| `feature/b4-admin-api` | B4 | audit_repo.py · reporting endpoints · test suite |
| `feature/f1-design-system` | F1 | App shell · AuthContext · shared components · routing |
| `feature/f2-patient-module` | F2 | Patient profile · medical history · appointment list |
| `feature/f3-doctor-module` | F3 | Doctor dashboard · booking form · queue board |
| `feature/f4-admin-module` | F4 | Reports dashboard · audit log · notifications panel |

**Additional branches for fixes and maintenance:**

```
fix/short-description          → bug fix
db/short-description           → SQL schema change
docs/short-description         → documentation update
chore/short-description        → dependency or config update
```

---

## Commits

Follow **Conventional Commits**. Format: `type(scope): description`. Keep it lowercase and imperative.

```bash
# ✅ Correct
feat(s1): add Oracle 12-table DDL schema with all constraints
feat(s1): add seed data INSERT scripts for all 12 tables
feat(s1): implement all 11 rubric query categories
feat(b1): add JWT login endpoint using patient_repo
feat(b2): add patient_repo with SELECT, INSERT, UPDATE queries
fix(b3): resolve double-booking constraint error on slot_id
test(b4): add audit log and reporting endpoint tests
db(s1): add composite index on TIMESLOT slot_date and is_available
docs(readme): update architecture diagram for Oracle SQL migration
chore(deps): add cx_Oracle to requirements.txt

# ❌ Wrong
git commit -m "done"
git commit -m "fixed stuff"
git commit -m "wip"
git commit -m "changes"
```

Commit after every meaningful unit of work — one table created, one repo function written, one query implemented, one test written. The examiner reads git history.

---

## SQL & Schema Rules

The SQL schema is the primary exam deliverable. These rules protect it.

**Schema ownership — S1 only:**
- S1 writes and owns all files in `sql/01_DDL/`
- No one modifies `01_create_tables.sql` without S1's written sign-off
- No column renames, type changes, or constraint modifications without a posted proposal

**SQL file rules:**
- All DDL (CREATE TABLE, CREATE INDEX, CREATE VIEW) lives in `sql/01_DDL/`
- All DML (INSERT, UPDATE) lives in `sql/02_DML/`
- All SELECT queries live in `sql/04_queries/`
- SQL in the backend lives **only** in `backend/db/*_repo.py` files
- No raw SQL strings in `api/`, `services/`, or any other folder

**Before changing the schema:**
1. Post in the group chat with the exact change and reason
2. Wait for S1 to confirm no impact on other tables or queries
3. S1 updates the `.sql` file and tags everyone in the PR

---

## Repository Pattern — The ORM Replacement

There is no ORM in this project. All database access goes through repository files.

**Every table has exactly one repo file:**

```
backend/db/
├── oracle_connection.py    ← shared connection — used by all repos
├── user_account_repo.py    ← all SQL touching USER_ACCOUNT table
├── patient_repo.py         ← all SQL touching PATIENT + PATIENT_CONTACT + MEDICAL_RECORD
├── appointment_repo.py     ← all SQL touching APPOINTMENT + TIMESLOT
├── doctor_repo.py          ← all SQL touching STAFF + DOCTOR + DEPARTMENT
├── queue_repo.py           ← all SQL touching QUEUE_ENTRY table
├── notification_repo.py    ← all SQL touching NOTIFICATION table
└── audit_repo.py           ← all SQL touching AUDIT_LOG table
```

The database still has exactly 12 core tables. Repo files are allowed to group related tables; they are not separate database entities.

**A repo function looks like this:**

```python
# backend/db/patient_repo.py

def get_patient_by_id(conn, patient_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT patient_id, student_number, first_name, last_name, email "
        "FROM PATIENT WHERE patient_id = :1",
        [patient_id]
    )
    row = cursor.fetchone()
    cursor.close()
    return row

def get_all_patients(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PATIENT ORDER BY last_name")
    rows = cursor.fetchall()
    cursor.close()
    return rows

def create_patient(conn, student_number, first_name, last_name, email,
                   contact_number, date_of_birth, street, city, postal_code):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO PATIENT (student_number, first_name, last_name, email, "
        "contact_number, date_of_birth, street, city, postal_code, consent_given) "
        "VALUES (:1, :2, :3, :4, :5, TO_DATE(:6,'YYYY-MM-DD'), :7, :8, :9, 1)",
        [student_number, first_name, last_name, email,
         contact_number, date_of_birth, street, city, postal_code]
    )
    conn.commit()
    cursor.close()
```

**A service layer calls the repo:**

```python
# backend/services/patient_service.py
from db.oracle_connection import get_connection
from db import patient_repo

def fetch_patient(patient_id):
    conn = get_connection()
    return patient_repo.get_patient_by_id(conn, patient_id)
```

**An API route calls the service:**

```python
# backend/api/patients.py
from services import patient_service

@app.route('/api/v1/patients/<int:patient_id>', methods=['GET'])
@require_auth
def get_patient(patient_id):
    patient = patient_service.fetch_patient(patient_id)
    if not patient:
        return {'error': 'Not found', 'status': 404}, 404
    return {'data': patient}, 200
```

This is the only permitted flow. SQL never appears in `api/` or `services/`.

---

## Pull Requests

### Before Opening a PR — Self-Review Checklist

```
[ ] Branch named correctly per the convention above
[ ] Conventional commit messages throughout
[ ] No print() or console.log statements left in code
[ ] No commented-out code blocks
[ ] No SQL strings outside backend/db/*_repo.py
[ ] All SQL uses bind variables (:1, :2) — no string concatenation
[ ] JWT permission check applied on all protected API routes
[ ] If schema change present — S1 has reviewed and approved
[ ] Tests written and passing locally
[ ] PR description filled out completely
[ ] Minimum 2 reviewers assigned
[ ] Linked to the GitHub issue (e.g. Closes #5)
```

### PR Description Template

```
Title: feat(b2): add patient_repo and Patient API endpoints

What changed:
  Added patient_repo.py with get, create, update functions.
  Added Patient API routes at /api/v1/patients/.
  All SQL uses Oracle bind variables.

Why it changed:
  Implements B2 spec — patients need to register and manage profiles.

How to test:
  1. Run sql/00_RUN_ALL.sql in Oracle SQL Developer
  2. Start backend: python app.py
  3. POST /api/v1/patients/ with valid data → expect 201
  4. GET /api/v1/patients/ with admin JWT → expect list
  5. SELECT * FROM PATIENT in SQL Developer to verify DB record

Linked issue: Closes #5
```

### The Rule of Two

Every PR requires 2 approvals before merging. S1 approval mandatory when any file in `sql/01_DDL/` is modified.

### Merge Method

Always use **Squash and merge**. Edit the squash message to be a clean conventional commit.

---

## Coding Standards

### Backend — Python / SQL

**Use bind variables. Always. No exceptions.**

```python
# ❌ Wrong — SQL injection risk, Oracle will reject it
cursor.execute(f"SELECT * FROM PATIENT WHERE student_number = '{student_number}'")

# ✅ Correct — bind variable
cursor.execute("SELECT * FROM PATIENT WHERE student_number = :1", [student_number])
```

**Commit after every INSERT block.**

```python
# ✅ Always commit after DML
conn.commit()
```

**Close cursors.**

```python
# ✅ Always close
cursor = conn.cursor()
cursor.execute(...)
result = cursor.fetchall()
cursor.close()   # ← required
return result
```

### Frontend — React

**React never calls the database. React never calls axios directly inside a component.**

```javascript
// ❌ Wrong
const res = await fetch('http://localhost:8000/api/v1/patients/');

// ✅ Correct
import { getPatients } from '../services/patientService';
const patients = await getPatients();
```

All API calls live in `src/services/`. No component imports axios directly.

---

## Bug Reports

Open a GitHub Issue and include:

- Steps to reproduce
- Expected behaviour
- Actual behaviour
- Full error message or Oracle error code (e.g. `ORA-00001: unique constraint violated`)
- Which SQL file or repo function is affected

*"It doesn't work"* is not a bug report.

---

**Write clean SQL. Protect the schema. Review each other's work.** 🚀
