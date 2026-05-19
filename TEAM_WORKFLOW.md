# Ubuntu Campus Clinic — Team Workflow
## Operational Guide · Group 19 · Phase 3 · Oracle SQL Migration

> This is the operational guide — not the rules document. CONTRIBUTING.md covers the rules. This document covers exactly how each role works day to day, how git works in practice, and what to do when things break.

---

## Table of Contents

1. [Daily Workflow Loop](#1-daily-workflow-loop)
2. [Git in Practice](#2-git-in-practice)
3. [S1 — DB Lead & DevOps](#3-s1--db-lead--devops)
4. [B1 B2 B3 B4 — Backend Team](#4-b1-b2-b3-b4--backend-team)
5. [F1 F2 F3 F4 — Frontend Team](#5-f1-f2-f3-f4--frontend-team)
6. [Cross-Team Collaboration](#6-cross-team-collaboration)
7. [Pull Request Workflow](#7-pull-request-workflow-on-github)
8. [When Things Go Wrong](#8-when-things-go-wrong)
9. [Sprint Timeline](#9-sprint-timeline)

---

## 1. Daily Workflow Loop

Every team member follows this sequence every working day.

### Before Writing Any Code

```bash
# Confirm which branch you are on
git branch
# If you see * dev or * main — STOP. You should be on your feature branch.

# Update dev with everyone's latest merged work
git checkout dev
git pull origin dev

# Switch back to your feature branch
git checkout feature/your-branch

# Bring dev into your branch so you stay current
git merge dev
# Resolve any conflicts before continuing — see Section 8
```

### While Coding

```bash
git status
git diff
git add sql/04_queries/05_queries.sql
git commit -m "feat(s1): add GROUP BY and HAVING queries for appointments"
git push origin feature/5-oracle-raw-sql-migration
```

### Before Closing the Laptop

```bash
git status        # check for uncommitted work
git add .
git commit -m "wip(b2): patient_repo get and create functions in progress"
git push origin feature/b2-patient-api
```

Push every session. Never lose work.

---

## 2. Git in Practice

### How to Read the Branch Graph

```bash
git log --oneline --graph --all

# Example output:
# * f3a1c2d (HEAD -> feature/b2-patient-api) feat(b2): add patient_repo functions
# * 8b2e4a1 feat(b2): add oracle_connection import
# | * 2a8c1b4 (dev) feat(s1): add Oracle DDL 12-table schema
# |/
# * 1e4f9d3 chore(s1): initial project scaffold
```

### How to Undo Things Safely

**Changed a file but not staged:**
```bash
git restore sql/04_queries/05_queries.sql
# WARNING: permanent
```

**Staged but not committed:**
```bash
git restore --staged sql/04_queries/05_queries.sql
```

**Committed but not pushed:**
```bash
git reset --soft HEAD~1
# Changes go back to staged
```

**Committed and pushed:**
```bash
git revert HEAD
# Creates a new undo commit — history preserved
```

### Handling a Merge Conflict

```bash
git status
# Files under "both modified" have conflicts

# Edit the file — remove ALL Git markers:
<<<<<<< HEAD
    your version
=======
    incoming version
>>>>>>> dev

git add sql/04_queries/05_queries.sql
git commit -m "merge: resolve conflict in queries file"
git push origin feature/your-branch
```

---

## 3. S1 — DB Lead & DevOps

S1 owns the entire Oracle SQL layer. This is the primary exam deliverable. Every team member depends on S1 completing the database setup before they can build anything.

### Phase 3 Migration — What S1 Does First (Issue #5)

S1 created Issue #5 and branch `feature/5-oracle-raw-sql-migration`. The work is:

**Step 1 — Write `sql/01_DDL/01_create_tables.sql`**

12 tables in FK dependency order. Every table must have:
- Oracle data types (`VARCHAR2`, `NUMBER`, `DATE`, `TIMESTAMP`)
- `GENERATED ALWAYS AS IDENTITY` primary keys
- Named `CONSTRAINT` clauses for every PK, FK, UNIQUE, and CHECK
- Correct `ON DELETE` behaviour on all FKs

Dependency order:
```
Level 1: PATIENT · TIMESLOT · DEPARTMENT
Level 2: PATIENT_CONTACT · STAFF
Level 3: DOCTOR · USER_ACCOUNT
Level 4: APPOINTMENT · AUDIT_LOG
Level 5: QUEUE_ENTRY · MEDICAL_RECORD · NOTIFICATION
```

```bash
git add sql/01_DDL/01_create_tables.sql
git commit -m "feat(s1): add Oracle 12-table DDL schema with all constraints"
```

**Step 2 — Write `sql/01_DDL/02_create_indexes.sql`**

At minimum:
- `idx_timeslot_date` — slot availability queries
- `idx_timeslot_date_avail` — composite, most frequent query
- `idx_appt_patient`, `idx_appt_staff`, `idx_appt_status`
- `idx_queue_appt`, `idx_mr_patient`, `idx_audit_timestamp`

```bash
git commit -m "feat(s1): add 12 performance indexes"
```

**Step 3 — Write `sql/01_DDL/03_create_views.sql`**

4 views:
- `vw_patient_appointments` — patient dashboard
- `vw_daily_queue_board` — nurse/admin live queue
- `vw_doctor_schedule` — doctor's daily schedule
- `vw_audit_trail_summary` — POPIA compliance report

```bash
git commit -m "feat(s1): add 4 reporting views"
```

**Step 4 — Write `sql/02_DML/04_insert_data.sql`**

Realistic South African clinic data across all 12 tables:
- 5 departments, 6 staff (3 doctors, 2 nurses, 1 admin)
- 8 patients with student numbers, contacts
- 12 timeslots (past + future), 8 appointments
- Queue entries, medical records, notifications, audit logs

```bash
git commit -m "feat(s1): add seed data INSERT scripts for all 12 tables"
```

**Step 5 — Write `sql/04_queries/05_queries.sql`**

All 11 rubric categories. Multiple examples per category. Clear comments above every query block.

```bash
git commit -m "feat(s1): implement all 11 rubric query categories"
```

**Step 6 — Write `sql/00_RUN_ALL.sql`**

Master script using `@@` to call all files in order. Add verification queries at the end.

```bash
git commit -m "feat(s1): add master run script with verification checks"
```

**Step 7 — Write `backend/db/oracle_connection.py`**

```python
import cx_Oracle

def get_connection():
    return cx_Oracle.connect(
        user="system",
        password="your_password",
        dsn="localhost:1521/XE"
    )
```

```bash
git commit -m "feat(s1): add Oracle connection factory"
```

**Step 8 — Push, open PR, merge to dev**

```bash
git push origin feature/5-oracle-raw-sql-migration
# Open PR on GitHub targeting dev
# Title: feat(s1): Oracle raw SQL migration — 12 tables, indexes, views, queries
# Body: Closes #5
```

Post in group chat:
> **"Issue #5 Oracle migration is live on dev. sql/ folder has everything. All backend devs: pull dev now and start your repo files. Oracle connection factory is in backend/db/oracle_connection.py."**

---

### S1 Ongoing Responsibilities

**Schema change governance:**

When anyone needs to change the schema:
1. They post: `"[SCHEMA REQUEST] B2 — adding allergies VARCHAR2(500) to PATIENT"`
2. S1 checks impact on all views and repo queries
3. S1 updates `01_create_tables.sql` and the relevant view/query files
4. S1 commits and opens a `db/` PR

**Backend oracle_connection.py:**

S1 owns this file. If the Oracle credentials or DSN change, S1 updates it and notifies everyone immediately.

**Deployment:**

S1 manages the live demo environment used in the video. Every SQL file must run cleanly in a fresh Oracle XE schema before submission.

---

## 4. B1 B2 B3 B4 — Backend Team

### What Each Backend Developer Builds

| Role | Module | What to Build |
|---|---|---|
| **B1** | Auth | JWT login/register/refresh/logout · `user_account_repo.py` · permission middleware · route protection |
| **B2** | Patients | `patient_repo.py` for `PATIENT`, `PATIENT_CONTACT`, and `MEDICAL_RECORD` · Patient API routes |
| **B3** | Bookings & Queue | `appointment_repo.py` · `queue_repo.py` · Booking endpoint with slot locking · QR generation · queue check-in flow |
| **B4** | Admin & Reporting | `audit_repo.py` · reporting endpoints · full pytest suite for all backend modules |

### Getting Started

```bash
git checkout dev
git pull origin dev
git checkout -b feature/b2-patient-api   # your assigned branch

# Verify oracle_connection.py is there (S1 must merge first)
cat backend/db/oracle_connection.py
```

### Build Order — Follow This Exactly

```
Step 1 — Import get_connection from oracle_connection.py
Step 2 — Write the repo functions (SELECT, INSERT, UPDATE)
Step 3 — Write the service layer (calls repo)
Step 4 — Write the API routes (calls service)
Step 5 — Write tests
Step 6 — Commit each step separately
```

**Example — B2 writing patient_repo.py:**

```python
# backend/db/patient_repo.py
from db.oracle_connection import get_connection

def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT patient_id, student_number, first_name, last_name, "
        "email, city, consent_given "
        "FROM PATIENT ORDER BY last_name"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_patient_by_id(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM PATIENT WHERE patient_id = :1",
        [patient_id]
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def create_patient(student_number, first_name, last_name, email,
                   contact_number, dob, street, city, postal_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO PATIENT "
        "(student_number, first_name, last_name, email, contact_number, "
        "date_of_birth, street, city, postal_code, consent_given) "
        "VALUES (:1, :2, :3, :4, :5, TO_DATE(:6,'YYYY-MM-DD'), :7, :8, :9, 1)",
        [student_number, first_name, last_name, email,
         contact_number, dob, street, city, postal_code]
    )
    conn.commit()
    cursor.close()
    conn.close()
```

Commit each function group separately:

```bash
git commit -m "feat(b2): add get_all_patients and get_patient_by_id to patient_repo"
git commit -m "feat(b2): add create_patient INSERT function with bind variables"
git commit -m "feat(b2): add Patient API GET and POST routes"
git commit -m "test(b2): add patient repo and API endpoint tests"
```

### Testing Your Endpoints

```bash
# Start backend
python app.py

# Get JWT
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student_10012345", "password": "testpass"}'

# Call endpoint
curl -X GET http://localhost:8000/api/v1/patients/ \
  -H "Authorization: Bearer <your_access_token>"
```

Also verify directly in Oracle SQL Developer:
```sql
SELECT * FROM PATIENT;
```

Post in group chat when ready:
> **"B2 patient endpoints live on dev. /api/v1/patients/ working. F2 can connect."**

---

## 5. F1 F2 F3 F4 — Frontend Team

### What Each Frontend Developer Builds

| Role | Module | What to Build |
|---|---|---|
| **F1** | Layout, Auth & Routing | `App.jsx` · `AuthContext` · JWT storage · login + register pages · shared components · axios interceptor |
| **F2** | Patient & Medical Pages | Patient profile · medical history · emergency contacts · appointment list |
| **F3** | Doctor Dashboard & Booking | Doctor dashboard · timeslot availability · booking form · QR display · queue board |
| **F4** | Admin UI & Notifications | Admin reports dashboard · audit log table · notification history |

### The Core Rule

React never calls the database. React never calls axios directly in a component.

```javascript
// ❌ Wrong
const res = await fetch('http://localhost:8000/api/v1/patients/');

// ✅ Correct
import { getPatients } from '../services/patientService';
const patients = await getPatients();
```

### Working Before Backend Endpoints Are Ready — Mocking

```javascript
// src/services/patientService.js

// Mock — use until B2 merges
export const getPatient = async (id) => {
  return { patient_id: 1, first_name: "Karabo", email: "10012345@student.nwu.ac.za" };
};

// Real — swap in when B2 endpoint is live
export const getPatient = async (id) => {
  const response = await api.get(`/api/v1/patients/${id}/`);
  return response.data;
};
```

---

## 6. Cross-Team Collaboration

### Dependency Map

```
S1 — Issue #5 Oracle migration merged to dev
         │
         ▼
B1 — oracle_connection.py + JWT auth merged
         │
    ┌────┴────────────────┐
    ▼                     ▼
  B2 — patient_repo    B3 — appointment_repo + queue_repo
    │                     │
    └────────┬────────────┘
             ▼
    B4 — audit_repo + tests
             │
             ▼
    F1 — AuthContext + shell merged
         │
    ┌────┼────┬────┐
    ▼    ▼    ▼    ▼
   F2   F3   F4  (connect to real endpoints as they merge)
```

### Communication Protocol

Post in group chat at these moments:

| When | What to Post |
|---|---|
| Starting work | `"Starting feature/b2-patient-api — building patient_repo.py today"` |
| Endpoint ready | `"B2 endpoints live on dev — /api/v1/patients/ working. F2 can connect."` |
| Schema question | `"[SCHEMA REQUEST] B2 — do we have an allergies field on PATIENT or do I add it?"` |
| PR open | `"PR open — feature/b2-patient-api. Please review."` |
| Blocked | `"Blocked on B1 — need JWT middleware before I can protect my routes"` |

---

## 7. Pull Request Workflow on GitHub

### Opening a PR

1. Push your branch: `git push origin feature/your-branch`
2. Go to GitHub — click **"Compare & pull request"**
3. **Set base branch to `dev`** — never `main`
4. Fill in the PR description completely
5. Assign 2 reviewers
6. Tag S1 if any file in `sql/01_DDL/` is modified
7. Link the issue: `Closes #5`

### Responding to Review Comments

```bash
git add backend/db/patient_repo.py
git commit -m "fix(b2): add missing cursor.close() in get_patient_by_id"
git push origin feature/b2-patient-api
# Reply on GitHub: "Fixed in commit abc1234"
# Click Resolve conversation
# Click Re-request review
```

### After Merge

```bash
git checkout dev
git pull origin dev
git branch -d feature/b2-patient-api
```

Post in group chat: **"B2 merged — Patient CRUD live on dev"**

---

## 8. When Things Go Wrong

### Oracle Connection Error

**Symptom:** `cx_Oracle.DatabaseError: ORA-12541: TNS:no listener`

**Fix:**
1. Confirm Oracle XE is running: open Services (Windows) or check `lsnrctl status` (Mac/Linux)
2. Verify `backend/db/oracle_connection.py` has correct DSN, username, password
3. Test connection in SQL Developer first — if SQL Developer connects, the Python code will too

### ORA-00001: Unique Constraint Violated

**Symptom:** INSERT fails with `ORA-00001`

**Fix:**
1. Open SQL Developer
2. Run: `SELECT * FROM PATIENT WHERE student_number = '10012345';`
3. The row already exists — either truncate test data or use a different value
4. For the seed script: add `DELETE FROM TABLE_NAME;` before INSERT blocks

### ORA-02291: Integrity Constraint Violated (FK)

**Symptom:** INSERT on a child table fails because the parent row doesn't exist

**Fix:** Check your insert order. Parent must exist before child. Refer to the dependency order in Section 3.

### SQL File Won't Run (F5 in SQL Developer)

**Symptom:** Script Output shows errors partway through

**Fix:**
1. Check the exact Oracle error line number
2. Look for `DROP TABLE` errors — add `CASCADE CONSTRAINTS PURGE` to every DROP
3. Check for table creation order — create parent before child

### Your Branch Is Behind Dev

```bash
git checkout dev
git pull origin dev
git checkout feature/your-branch
git merge dev
# Resolve conflicts
git push origin feature/your-branch
```

---

## 9. Sprint Timeline

| Day | Date | S1 | B1 | B2 | B3 | B4 | F1 | F2 | F3 | F4 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Now | Issue #5 · Oracle DDL · indexes · views · seed data | Clone · plan | Clone · plan | Clone · plan | Clone · plan | Clone · plan | Clone · plan | Clone · plan | Clone · plan |
| 2 | +1 | All SQL files committed · master run script | user_account_repo.py · JWT login | patient_repo skeleton | appointment_repo skeleton | audit_repo skeleton | AuthContext · axios | Mock patient service | Mock doctor service | Mock admin service |
| 3 | +2 | Support backend team · schema questions | JWT refresh + logout · route protection | Patient API routes | Appointment + Queue endpoints | Raw SQL report endpoints | Login + register pages | Patient profile page | Doctor dashboard | Reports page |
| 4 | +3 | Review Issue #5 PR · merge to dev | **B1 PR → merge** | Patient tests | QR generation | pytest suite | Protected routes | Medical history page | Booking form | Audit log table |
| 5 | +4 | Support all · schema governance | Support F1 wiring | B2 PR open | Queue status flow | B4 PR open | Wire auth to B1 | Wire patient to B2 | Wire booking to B3 | Wire reports to B4 |
| 6 | +5 | Review all PRs | Done | **B2 PR → merge** | B3 PR open | **B4 PR → merge** | Done | Done | Queue board | Notifications |
| 7 | +6 | Verify seed data on Oracle · video demo prep | — | Done | **B3 PR → merge** | Done | Done | Done | **F3 PR → merge** | **F4 PR → merge** |
| 8 | +7 | All PRs reviewed | — | — | Done | Done | **F1 PR → merge** | **F2 PR → merge** | Done | Done |
| 9 | +8 | Final Oracle SQL demo verification | All | All | All | All | All | All | All | All |
| **Sub** | | **Submit GitHub repo link + video demo** | | | | | | | | |

### The Two Non-Negotiable Gates

```
GATE 1
S1 merges Issue #5 to dev
Oracle schema running · seed data loaded
Everyone blocks until this is green

GATE 2
B1 merges JWT auth to dev
Route protection working
All API endpoints block until this is green
```

---

*Ubuntu Campus Clinic — Appointment System · Group 19 · CMPG 311 · DBMS Module*
*`TEAM_WORKFLOW.md` · referenced from `README.md` and `CONTRIBUTING.md`*
