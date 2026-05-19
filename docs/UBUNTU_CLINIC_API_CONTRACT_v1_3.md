# Ubuntu Clinic API Contract v1.3

| Field | Value |
|---|---|
| **Document ID** | UBUNTU-CBS-API-CONTRACT-v1.3 |
| **Status** | **APPROVED** — aligned with Flask + React implementation |
| **Version** | 1.3.0 |
| **Date** | 2026-05-17 |
| **Base URL** | `/api/v1/` (trailing slashes required) |
| **Auth** | JWT Bearer · refresh at `POST /api/v1/auth/token/refresh/` |

> Supersedes [v1.2](./UBUNTU_CLINIC_API_CONTRACT_v1_2.md) for route paths and implementation status.

## Global rules

- Header: `Authorization: Bearer <access_token>`
- Token refresh: `POST /api/v1/auth/token/refresh/` body `{ "refresh": "..." }`
- Error envelope: `{ "error": "message", "code": "CODE" }`
- Success envelope: JSON body (array or object) at top level

## Endpoint index

| Method | Path | Roles | Status |
|--------|------|-------|--------|
| GET | `/health/` | public | Implemented |
| POST | `/auth/login/` | public | Implemented |
| POST | `/auth/register/` | public | Implemented |
| POST | `/auth/logout/` | authenticated | Implemented |
| GET | `/auth/me/` | authenticated | Implemented |
| POST | `/auth/token/refresh/` | public (refresh token) | Implemented |
| GET | `/patient/profile/` | PATIENT | Implemented |
| PATCH | `/patient/profile/` | PATIENT | Implemented |
| GET | `/patient/dashboard/` | PATIENT | Implemented |
| GET | `/patient/qr-code/` | PATIENT | Implemented |
| GET | `/medical/records/` | PATIENT | Implemented |
| GET | `/medical/records/<id>/` | PATIENT | Implemented |
| GET/POST | `/emergency-contacts/` | PATIENT | Implemented |
| PATCH/DELETE | `/emergency-contacts/<id>/` | PATIENT | Implemented |
| GET | `/appointments/upcoming/` | PATIENT | Implemented |
| GET | `/appointments/history/` | PATIENT | Implemented |
| GET | `/appointments/pending-results/` | PATIENT | Implemented |
| POST | `/appointments/book/` | PATIENT | Implemented |
| PATCH | `/appointments/<id>/cancel/` | PATIENT | Implemented |
| GET | `/doctors/` | PATIENT | Implemented |
| GET | `/timeslots/?date=&doctor_id=` | PATIENT | Implemented |
| POST | `/queue/check-in/` | authenticated | Implemented |
| GET | `/queue/<appointment_id>/` | authenticated | Implemented |
| GET | `/notifications/` | authenticated | Implemented |
| PATCH | `/notifications/<id>/read/` | authenticated | Implemented |
| PATCH | `/notifications/read-all/` | authenticated | Implemented |
| DELETE | `/notifications/<id>/` | ADMIN | Implemented |
| GET | `/admin/reports/summary/` | ADMIN | Implemented |
| GET | `/admin/reports/appointments/` | ADMIN | Implemented |
| GET | `/admin/reports/daily-counts/` | ADMIN | Implemented |
| GET | `/admin/audit-log/` | ADMIN | Implemented |
| GET/POST | `/admin/departments/` | ADMIN | Implemented |
| PATCH/DELETE | `/admin/departments/<id>/` | ADMIN | Implemented |
| GET | `/admin/users/` | ADMIN | Implemented |
| PATCH | `/admin/users/<id>/` | ADMIN | Implemented |

## v1.2 → v1.3 corrections

| v1.2 (incorrect) | v1.3 (actual) |
|------------------|---------------|
| `POST /auth/refresh` | `POST /auth/token/refresh/` |
| Generic `/patients` | `/patient/profile/`, `/patient/dashboard/` |
| (missing) | `GET /health/`, `PATCH /appointments/<id>/cancel/`, queue routes |

## Audit actions (written on mutation)

`LOGIN`, `REGISTER`, `BOOK_APPOINTMENT`, `CANCEL_APPOINTMENT`, `UPDATE_PROFILE`, `CREATE_DEPARTMENT`, `UPDATE_DEPARTMENT`, `DELETE_DEPARTMENT`, `UPDATE_USER`

## Environment

| Variable | Layer |
|----------|-------|
| `ORA_USER`, `ORA_PASSWORD`, `ORA_HOST`, `ORA_PORT`, `ORA_SID` | Backend |
| `JWT_SECRET`, `FLASK_ENV`, `CORS_ORIGINS` | Backend |
| `VITE_API_URL` | Frontend (`http://localhost:8000`) |
| `VITE_USE_MOCK` | Frontend (`false` for demo) |
