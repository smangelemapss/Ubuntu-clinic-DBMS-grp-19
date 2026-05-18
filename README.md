# 🏥 Ubuntu Campus Clinic — Appointment System

<div align="center">

![Status](https://img.shields.io/badge/Status-Active%20Development-teal?style=for-the-badge)
![Phase](https://img.shields.io/badge/Phase-3%20Physical%20Design-0D1B2A?style=for-the-badge)
![DB](https://img.shields.io/badge/Database-Oracle%20SQL-F80000?style=for-the-badge&logo=oracle&logoColor=white)
![Tool](https://img.shields.io/badge/Tool-SQL%20Developer-F80000?style=for-the-badge&logo=oracle&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-React%2018-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

**Group 19 · CMPG 311 · DBMS Module · Phase 3**

*Replacing manual paper-based clinic scheduling with a production-grade digital system —
built database-first on Oracle SQL, designed to scale.*

[Getting Started](#-getting-started) · [Architecture](#-architecture) · [Database Schema](#-database-schema) · [SQL Files](#-sql-files) · [Team](#-team) · [Docs](#-documentation)

</div>

---

## What Is This?

Ubuntu Campus Clinic runs on paper. Students wait days for appointments. Records get lost. Staff have no visibility into capacity or performance. After hours — the system stops entirely.

This changes that.

The **Ubuntu Campus Clinic Appointment System** is a full-stack web application that digitizes the complete patient lifecycle — registration, booking, queue management, consultation, medical records, and automated notifications — in one centralized platform accessible 24/7 from any browser.

> **The primary exam deliverable is the Oracle SQL database** — schema design, data integrity enforcement, indexes, views, and a full suite of raw SQL queries demonstrated in Oracle SQL Developer. The backend API and React 18 frontend exist to demonstrate the database working end-to-end as a complete, live system.

---

## 🛠 Tech Stack

| Layer | Technology | Why We Chose It |
|---|---|---|
| **Database** | Oracle SQL | ACID compliance · industry-standard · primary exam deliverable · Oracle SQL Developer tooling |
| **DB Tool** | Oracle SQL Developer | Official Oracle GUI · required for rubric demonstration video |
| **Backend** | Python + SQL Repository Layer | Raw SQL via cx_Oracle · no ORM — direct Oracle DB access |
| **Auth** | JWT (PyJWT) | Stateless · role encoded in payload · scales horizontally |
| **Frontend** | React 18 + Tailwind CSS | Component-based · responsive · browser + mobile |
| **CI** | GitHub Actions | Full test suite on every PR to `dev` — broken code never merges |

---

## ⚙️ Prerequisites

| Tool | Version | Download |
|---|---|---|
| Oracle Database XE | 21c | [oracle.com/database/technologies/xe-downloads.html](https://www.oracle.com/database/technologies/xe-downloads.html) |
| Oracle SQL Developer | Latest | [oracle.com/tools/downloads/sqldev-downloads.html](https://www.oracle.com/tools/downloads/sqldev-downloads.html) |
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Git | Latest | [git-scm.com](https://git-scm.com/) |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/smangelemapss/Ubuntu-clinic-DBMS-grp-19.git
cd Ubuntu-clinic-DBMS-grp-19
```

> ⚠️ **Team members:** Always clone from `dev`, never from `main`. Read [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) before writing any code.

### 2. Set Up Oracle Database

1. Install **Oracle Database XE 21c**
2. Open **Oracle SQL Developer**
3. Create a new connection:
   - **Connection Name:** `ubuntu_clinic`
   - **Username:** `system` (or your schema user)
   - **Password:** your Oracle password
   - **Hostname:** `localhost`
   - **Port:** `1521`
   - **SID:** `XE`
4. Click **Test** → should say *Status: Success*
5. Click **Connect**

### 3. Run the Database Setup Script

In Oracle SQL Developer:

1. Go to **File > Open**
2. Open `sql/00_RUN_ALL.sql`
3. Press **F5** (Run Script — not F9)
4. Watch the Script Output panel — all 12 tables, indexes, views, and seed data will be created

### 4. Verify Setup

After the script completes, run this verification query:

```sql
SELECT table_name FROM user_tables
WHERE table_name IN (
    'PATIENT','PATIENT_CONTACT','TIMESLOT','DEPARTMENT',
    'STAFF','DOCTOR','USER_ACCOUNT','APPOINTMENT',
    'AUDIT_LOG','QUEUE_ENTRY','MEDICAL_RECORD','NOTIFICATION'
)
ORDER BY table_name;
```

You should see all 12 table names returned.

### 5. Run the Queries (for Demo / Video)

1. Open `sql/04_queries/05_queries.sql`
2. Highlight a single query block
3. Press **F9** (Run Statement)
4. Results appear in the Query Result tab

### 6. Backend Setup (Optional — API Layer)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
cp .env.example .env
# Fill in Oracle credentials in .env
python app.py
```

### 7. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

| Service | URL |
|---|---|
| React App | `http://localhost:5173/` |
| Backend API | `http://localhost:8000/api/v1/` |

### 8. Verify demo readiness (examiners)

After Oracle seed + `backend/.env`:

```bash
cd backend
python scripts/reset_seed_passwords.py
python scripts/verify_deploy_ready.py
```

With API already running, add `--http` to probe health endpoints.

From repo root, start both servers:

```bat
start-dev.bat
```

Or pre-flight then start:

```bat
demo-ready.bat
```

### Demo login accounts

| Portal | Username | Password | Role |
|--------|----------|----------|------|
| Patient | `karabo.mabena` | `Clinic@123` | PATIENT |
| Staff | `dr.mokoena` | `Clinic@123` | DOCTOR |
| Staff | `nurse.molefe` | `Clinic@123` | NURSE |
| Admin | `admin.ndlovu` | `Clinic@123` | ADMIN |

See [docs/DEMO_SCRIPT.md](./docs/DEMO_SCRIPT.md) for a 2–3 minute presentation walkthrough.

---

## 🏗 Architecture

The system is built on a four-layer architecture. Each layer has one responsibility and communicates only with the layer directly below it.

```
┌───────────────────────────────────────────────┐
│           PRESENTATION LAYER                  │
│   React 18 · React Router · Tailwind · axios  │
│   Renders UI · never calls DB directly        │
└──────────────────┬────────────────────────────┘
                   │  HTTP/JSON · /api/v1/
┌──────────────────▼────────────────────────────┐
│           APPLICATION LAYER                   │
│   Python REST API · PyJWT · permission logic  │
│   Enforces rules · validates · authorizes     │
└──────────────────┬────────────────────────────┘
                   │  Raw SQL via cx_Oracle
┌──────────────────▼────────────────────────────┐
│           SQL REPOSITORY LAYER                │
│   *_repo.py files · oracle_connection.py      │
│   Executes raw SQL · returns results to API   │
└──────────────────┬────────────────────────────┘
                   │  Oracle SQL
┌──────────────────▼────────────────────────────┐
│           DATABASE LAYER                      │
│   Oracle XE · FK · UNIQUE · CHECK · Indexes   │
│   Stores data · enforces integrity · ACID     │
│        PRIMARY EXAM DELIVERABLE               │
└───────────────────────────────────────────────┘
```

**The Repository Rule:** The backend never builds SQL strings in views or controllers. All SQL lives in `backend/db/*_repo.py` files only. The API layer calls repository functions and returns results.

Full architecture detail in [docs/SYSTEM_DESIGN.md](./docs/SYSTEM_DESIGN.md).

---

## 🗄 Database Schema

The schema covers 12 tables across 4 domains. All tables created using Oracle DDL (`CREATE TABLE`) with explicit constraints.

These 12 tables are the approved core entities. Backend repository files may group related tables together, but the Oracle schema should not gain extra core tables without S1 approval.

| Domain | Table | Key Constraint |
|---|---|---|
| Identity | `PATIENT` | `UNIQUE(student_number)` · `UNIQUE(email)` · `CHECK(consent IN (0,1))` |
| Identity | `PATIENT_CONTACT` | `FK → PATIENT` ON DELETE CASCADE |
| Identity | `USER_ACCOUNT` | `CHECK(patient OR staff NOT NULL)` · `UNIQUE(username)` |
| Staff | `DEPARTMENT` | `UNIQUE(department_name)` · `FK → STAFF` nullable head |
| Staff | `STAFF` | `UNIQUE(email)` · `FK → DEPARTMENT` |
| Staff | `DOCTOR` | `PK = FK → STAFF` · `UNIQUE(license_number)` |
| Scheduling | `TIMESLOT` | `CHECK(is_available IN (0,1))` · `CHECK(end > start)` |
| Scheduling | `APPOINTMENT` | `UNIQUE(slot_id)` — prevents double-booking at DB level |
| Operations | `QUEUE_ENTRY` | `UNIQUE(appointment_id)` · CHECK on status lifecycle |
| Operations | `MEDICAL_RECORD` | `FK → APPOINTMENT + PATIENT` |
| System | `NOTIFICATION` | `CHECK(patient OR staff NOT NULL)` |
| System | `AUDIT_LOG` | `FK → USER_ACCOUNT` · auto-timestamp |

**Creation order (FK dependency):**
Level 1 → `PATIENT · TIMESLOT · DEPARTMENT` →
Level 2 → `PATIENT_CONTACT · STAFF` →
Level 3 → `DOCTOR · USER_ACCOUNT` →
Level 4 → `APPOINTMENT · AUDIT_LOG` →
Level 5 → `QUEUE_ENTRY · MEDICAL_RECORD · NOTIFICATION`

---

## 📂 SQL Files

```
sql/
├── 00_RUN_ALL.sql                  ← START HERE — runs everything in order (F5)
│
├── 01_DDL/
│   ├── 01_create_tables.sql        ← 12 tables, all constraints
│   ├── 02_create_indexes.sql       ← 12 performance indexes
│   └── 03_create_views.sql         ← 4 reporting views
│
├── 02_DML/
│   └── 04_insert_data.sql          ← Seed data for all 12 tables
│
└── 04_queries/
    └── 05_queries.sql              ← All 11 rubric query categories
```

### Query Categories in `05_queries.sql`

| Category | Queries | Oracle Features Used |
|---|---|---|
| Q1 — Business queries | Q1.1–Q1.5 | Multi-table joins, WHERE, ORDER BY |
| Q2 — Row/column limits | Q2.1–Q2.4 | FETCH FIRST, ROWNUM, column selection |
| Q3 — Sorting | Q3.1–Q3.4 | ORDER BY ASC/DESC, multi-column sort |
| Q4 — LIKE, AND, OR | Q4.1–Q4.5 | LIKE '%', AND, OR combinations |
| Q5 — Character functions | Q5.1–Q5.6 | UPPER, LOWER, SUBSTR, LENGTH, INITCAP, CONCAT, TRIM, substitution variable |
| Q6 — Rounding/truncation | Q6.1–Q6.4 | ROUND, TRUNC, CEIL, FLOOR |
| Q7 — Date functions | Q7.1–Q7.6 | SYSDATE, ADD_MONTHS, MONTHS_BETWEEN, TO_CHAR, TO_DATE, LAST_DAY, NEXT_DAY |
| Q8 — Aggregates | Q8.1–Q8.6 | COUNT, AVG, MAX, MIN, COUNT DISTINCT |
| Q9 — GROUP BY / HAVING | Q9.1–Q9.5 | GROUP BY, HAVING, multi-column grouping |
| Q10 — Joins | Q10.1–Q10.6 | INNER JOIN, LEFT JOIN, 5-table joins, self join |
| Q11 — Sub-queries | Q11.1–Q11.6 | IN, NOT IN, scalar, correlated, EXISTS, inline view, RANK() |

---

## 📂 Project Structure

```
Ubuntu-clinic-DBMS-grp-19/
│
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI
│
├── sql/                         ← PRIMARY EXAM DELIVERABLE
│   ├── 00_RUN_ALL.sql           # Master script — run this in SQL Developer
│   ├── 01_DDL/
│   │   ├── 01_create_tables.sql
│   │   ├── 02_create_indexes.sql
│   │   └── 03_create_views.sql
│   ├── 02_DML/
│   │   └── 04_insert_data.sql
│   └── 04_queries/
│       └── 05_queries.sql
│
├── backend/
│   ├── app.py
│   ├── api/                     # Route handlers — HTTP request/response only
│   ├── services/                # Business logic layer
│   ├── db/
│   │   ├── oracle_connection.py # cx_Oracle connection factory
│   │   ├── user_account_repo.py # All USER_ACCOUNT auth queries
│   │   ├── patient_repo.py      # PATIENT · PATIENT_CONTACT · MEDICAL_RECORD
│   │   ├── appointment_repo.py  # APPOINTMENT · TIMESLOT
│   │   ├── doctor_repo.py       # STAFF · DOCTOR · DEPARTMENT
│   │   ├── queue_repo.py        # All QUEUE_ENTRY SQL queries
│   │   ├── notification_repo.py # All NOTIFICATION SQL queries
│   │   └── audit_repo.py        # All AUDIT_LOG SQL queries
│   ├── utils/                   # JWT helpers, error handlers
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── README.md
│   └── src/
│       ├── routes/
│       ├── context/             # AuthContext · JWT · role
│       ├── services/            # All axios calls — one file per backend app
│       ├── pages/
│       │   ├── auth/
│       │   ├── patient/
│       │   ├── doctor/
│       │   └── admin/
│       ├── components/
│       └── utils/
│
├── docs/
│   └── SYSTEM_DESIGN.md
│
├── README.md
├── CONTRIBUTING.md
└── TEAM_WORKFLOW.md
```

---

## 🌐 API Reference

All endpoints versioned at `/api/v1/`. Protected routes require `Authorization: Bearer <token>`. All SQL executed via repository layer — no ORM, no query builders.

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/login/` | Public | Returns JWT access + refresh tokens |
| `POST` | `/api/v1/auth/register/` | Public | Creates `USER_ACCOUNT` |
| `POST` | `/api/v1/auth/refresh/` | Public | Returns new access token |
| `POST` | `/api/v1/auth/logout/` | Protected | Invalidates refresh token |
| `GET/POST` | `/api/v1/patients/` | Auth | List or register patients |
| `GET/PATCH` | `/api/v1/patients/{id}/` | Patient · Admin | Profile view and update |
| `GET` | `/api/v1/patients/{id}/records/` | Doctor · Patient | Full medical history |
| `GET` | `/api/v1/timeslots/?date=YYYY-MM-DD&available=true` | Auth | Available slots for a date |
| `GET/POST` | `/api/v1/appointments/` | Auth | List or book appointments |
| `PATCH` | `/api/v1/appointments/{id}/cancel/` | Patient · Admin | Cancel appointment |
| `POST` | `/api/v1/queue/check-in/` | Patient | Check in via QR token |
| `PATCH` | `/api/v1/queue/{id}/status/` | Doctor · Admin | `WAITING → IN_PROGRESS → COMPLETED` |
| `GET` | `/api/v1/admin/reports/daily/` | Admin | Appointments per day |
| `GET` | `/api/v1/admin/reports/wait-times/` | Admin | Average wait time per doctor |
| `GET` | `/api/v1/admin/audit-log/` | Admin | Full audit trail |
| `GET` | `/api/v1/notifications/` | Auth | Notification history |

**Standard error shape — every endpoint:**
```json
{ "error": "Slot is no longer available", "code": "SLOT_UNAVAILABLE", "status": 409 }
```

---

## 👥 Team

| Role | Code | Deliverables |
|---|---|---|
| **DB Lead + DevOps** | S1 | All SQL files · Oracle schema · seed data · CI · deployment |
| **Backend Lead — Auth** | B1 | JWT endpoints · permission logic · oracle_connection.py |
| **Backend — Patients** | B2 | patient_repo.py · Patient API endpoints |
| **Backend — Bookings & Queue** | B3 | appointment_repo.py · queue_repo.py · QR generation |
| **Backend — Admin & Reporting** | B4 | audit_repo.py · report endpoints · test suite |
| **Frontend Lead** | F1 | App shell · AuthContext · routing · shared components |
| **Frontend — Patient** | F2 | Patient profile · medical history · appointment list |
| **Frontend — Doctor** | F3 | Doctor dashboard · booking form · queue board |
| **Frontend — Admin** | F4 | Reports dashboard · audit log · notifications panel |

---

## 📖 Documentation

| Document | What It Covers |
|---|---|
| [docs/SYSTEM_DESIGN.md](./docs/SYSTEM_DESIGN.md) | Full architecture · Oracle schema · repository pattern · security · design decisions |
| [docs/UBUNTU_CLINIC_API_CONTRACT_v1_2.md](./docs/UBUNTU_CLINIC_API_CONTRACT_v1_2.md) | Frontend-to-backend mock API contract · request/response shapes · roles · error codes |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Engineering standards · branch naming · commit format · PR process · The Laws |
| [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) | Day-to-day git workflow · role responsibilities · sprint timeline · recovery steps |

---

## 📚 Resources

| Resource | Link |
|---|---|
| Oracle SQL Developer Downloads | [oracle.com/tools/downloads/sqldev-downloads.html](https://www.oracle.com/tools/downloads/sqldev-downloads.html) |
| Oracle Database XE | [oracle.com/database/technologies/xe-downloads.html](https://www.oracle.com/database/technologies/xe-downloads.html) |
| Oracle SQL Reference | [docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf](https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/) |
| cx_Oracle (Python driver) | [cx-oracle.readthedocs.io](https://cx-oracle.readthedocs.io/) |
| React Documentation | [react.dev](https://react.dev/) |

---

<div align="center">

*Ubuntu Campus Clinic — Appointment System · Group 19 · CMPG 311 · DBMS Module*

*Built database-first on Oracle SQL. Engineered as a team.*

</div>
