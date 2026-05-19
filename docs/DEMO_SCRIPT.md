# Ubuntu Clinic — 2–3 minute demo script

Use this order for examiners or video submission.

## Before you start

1. Run `sql/00_RUN_ALL.sql` in Oracle SQL Developer (F5).
2. `cd backend && python scripts/reset_seed_passwords.py`
3. `cd backend && python scripts/verify_deploy_ready.py` (add `--http` if API is up).
4. Run `start-dev.bat` or `demo-ready.bat`.

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173/ |
| API health | http://localhost:8000/api/v1/health/ |

## Walkthrough

### 1. Health and home (30 s)

- Open http://localhost:5173/
- Point out health status on the homepage (API + database connected).

### 2. Patient journey (60 s)

- **Register** at `/register` (NWU rules: 8-digit student #, `@mynwu.ac.za`, `firstname.lastname`).
- Or **login**: `karabo.mabena` / `Clinic@123`
- **Dashboard** — stats for upcoming, past visits, pending results.
- **Book appointment** — pick doctor, date, slot.
- **Appointments** — cancel one appointment.
- **Profile** — show QR code; edit phone/address and save.

### 3. Staff (30 s)

- Log out → **Staff login** at `/staff/login`
- `dr.mokoena` / `Clinic@123`
- **Notifications** — mark one read.
- **Queue** — enter an appointment ID, **Check in**, show queue JSON.

### 4. Admin (30 s)

- Staff login: `admin.ndlovu` / `Clinic@123`
- **Overview** — summary stats.
- **Departments** — add a department.
- **Users** — change a user role (dropdown).
- **Audit** — show rows from login/booking/admin actions.

### 5. Database rubric (30 s)

- In SQL Developer, open `sql/04_queries/05_queries.sql`
- Run one query category (F9) — e.g. appointments by department.

## Demo accounts

| Username | Password | Role |
|----------|----------|------|
| karabo.mabena | Clinic@123 | PATIENT |
| dr.mokoena | Clinic@123 | DOCTOR |
| nurse.molefe | Clinic@123 | NURSE |
| admin.ndlovu | Clinic@123 | ADMIN |
