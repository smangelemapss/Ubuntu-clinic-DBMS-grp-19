# Ubuntu Clinic API Contract

## Frontend <-> Backend Agreement Layer

> Markdown rendering of the frontend handoff document. The original Word file remains available at [`UBUNTU_CLINIC_API_CONTRACT_v1_2.docx`](./UBUNTU_CLINIC_API_CONTRACT_v1_2.docx).

| Field | Value |
|---|---|
| **Document ID** | UBUNTU-CBS-API-CONTRACT-v1.2 |
| **Status** | Superseded — see [v1.3](./UBUNTU_CLINIC_API_CONTRACT_v1_3.md) (APPROVED) |
| **Version** | 1.2.0 - F4 Admin module added; F1-F2-F3-F4 complete |
| **Date Issued** | 2026-05-14 |
| **Prepared by** | Frontend Teams F1 - F2 - F3 - F4 |
| **Sent to** | Backend Team (B1 - B2 - B3 - B4) - S1 |
| **Stack** | React (axios) - Flask 3.0 - cx_Oracle 8.3 - Oracle XE 21c |
| **Auth scheme** | JWT Bearer tokens - Authorization header (PyJWT HS256) |
| **Base URL** | /api/v1/ - ALL routes (trailing slashes enforced) |
| **Classification** | CONFIDENTIAL - INTERNAL USE ONLY |

## Table of Contents

- [Purpose and Scope](#purpose-and-scope)
- [Global Rules and Auth](#global-rules-and-auth)
- [Endpoint Contracts](#endpoint-contracts)
- [Error Code Reference](#error-code-reference)
- [Conflicts and Resolutions](#conflicts-and-resolutions)
- [Governance Rules](#governance-rules)
- [Backend Assignment Map](#backend-assignment-map)
- [Backend Implementation Notes](#backend-implementation-notes)
- [Sign-off and Version Control](#sign-off-and-version-control)

## Purpose and Scope

This document is the official API Contract between the Ubuntu Clinic frontend teams (F1, F2, F3, F4) and the backend team. It formalises the request/response shapes, authentication rules, error codes, and governance rules that both sides must honour.

Version 1.2 adds the F4 Admin module (Sections 3.8-3.11) which was absent from v1.1. The contract is now complete across all four frontend roles.

Backend is the source of truth. Where F2 mock shapes conflict with F1/F3/F4 versioned shapes, this document records the conflict and the resolution. Backend reviews all items in Section 5 (Conflicts) before implementation begins.

## Global Rules and Auth

**AUTH NOTE - applies to ALL protected endpoints**

- **Header:** `Authorization: Bearer <access_token>`
- **Base URL:** `/api/v1/`
- **Trailing slashes:** Required on all routes.
- **Token refresh:** `POST /api/v1/auth/token/refresh/`
- **Token handling:** The frontend axios interceptor attaches the Bearer token automatically.
- **401 handling:** Frontend clears token and redirects to `/login`.

Handled automatically by the axios interceptor (axiosInstance). Frontend teams do not manually attach this header per request.

All routes use trailing slashes (Flask convention enforced). Token refresh: POST /api/v1/auth/token/refresh/ - implemented via PyJWT in backend/utils/jwt_helper.py. Token lifespan: backend decides - frontend handles 401 globally.

## Endpoint Contracts

### 3.1 Authentication (F1)

#### `POST /api/v1/auth/login/`

| Field | Value |
|---|---|
| **Description** | Authenticates a user and returns JWT access + refresh tokens along with role and user info. |
| **Auth required** | None - public endpoint |
| **Roles allowed** | All roles (unauthenticated) |

**Request body:**

```jsonc
{ "username": "string", "password": "string" }
```

**Response body:**

```jsonc
{ "access": "string", "refresh": "string", "role": "PATIENT|DOCTOR|NURSE|RECEPTIONIST|ADMIN", "user": { "id": int, "username": "string", "email": "string" } }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Invalid credentials |
| `400` | Validation error on field |

#### `POST /api/v1/auth/register/`

| Field | Value |
|---|---|
| **Description** | Registers a new patient account. Role defaults to PATIENT on the backend. |
| **Auth required** | None - public endpoint |
| **Roles allowed** | Unauthenticated only |

**Request body:**

```jsonc
{
  "username": "string",       // firstname.lastname (e.g. karabo.mabena)
  "student_number": "string", // exactly 8 digits (e.g. 48277444)
  "email": "string",          // {student_number}@mynwu.ac.za (e.g. 48277444@mynwu.ac.za)
  "password": "string"        // min 8 chars, at least one letter and one number
}
```

**Validation rules (enforced on API and register UI):**

| Field | Rule |
|---|---|
| `student_number` | Required, exactly 8 digits |
| `email` | Required, must match `{student_number}@mynwu.ac.za` |
| `username` | Required, must contain `.` (firstname.lastname) |
| `password` | Min 8 characters, at least one letter and one digit |

**Response body:**

```jsonc
{
  "message": "string",
  "user": {
    "id": int,
    "username": "string",
    "email": "string",
    "role": "PATIENT",
    "student_number": "string"
  }
}
```

**Error codes:**

| Code | Meaning |
|---|---|
| `400` | Field validation errors (`STUDENT_NUMBER_INVALID`, `EMAIL_INVALID`, `PASSWORD_WEAK`, etc.) |
| `409` | Username, student number, or email already exists |

#### `POST /api/v1/auth/logout/`

| Field | Value |
|---|---|
| **Description** | Blacklists the refresh token, ending the session. |
| **Auth required** | Bearer token required |
| **Roles allowed** | All authenticated roles |

**Request body:**

```jsonc
{ "refresh": "string" }
```

**Response body:**

```jsonc
{ "message": "Logged out successfully" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | No/expired token -> frontend redirects to /login |

#### `GET /api/v1/auth/me/`

| Field | Value |
|---|---|
| **Description** | Returns the profile of the currently authenticated user. |
| **Auth required** | Bearer token required |
| **Roles allowed** | All authenticated roles |

**Request body:** _None - identity inferred from JWT._

**Response body:**

```jsonc
{ "id": int, "username": "string", "email": "string", "role": "string" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Clear token + redirect to /login |

### 3.2 Patient Module (F2 + F3)

#### `GET /api/v1/patient/dashboard/`

| Field | Value |
|---|---|
| **Description** | Returns summary counts for the patient dashboard: upcoming, past, pending results, cancelled. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None._

**Response body:**

```jsonc
{ "upcomingCount": int, "pastVisitsCount": int, "pendingResultsCount": int, "cancelledCount": int }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Not a patient |
| `500` | Server error |

#### `GET /api/v1/patient/qr-code/`

| Field | Value |
|---|---|
| **Description** | Generates (or retrieves cached) a QR code token for patient check-in. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None._

**Response body:**

```jsonc
{ "qr_data": "string", "patient_id": int, "expires_at": "ISO8601 datetime" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `500` | Unable to generate QR code |

### 3.3 Appointments

#### `GET /api/v1/appointments/upcoming/`

| Field | Value |
|---|---|
| **Description** | Returns all upcoming (future, confirmed) appointments for the authenticated patient. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None._

**Response body:**

```jsonc
[ { "id": int, "date": "string", "time": "string", "doctor": "string", "doctor_id": int, "type": "string", "status": "upcoming", "department": "string" } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `500` | Unable to load appointments |

#### `GET /api/v1/appointments/history/`

| Field | Value |
|---|---|
| **Description** | Returns past (completed or cancelled) appointments for the authenticated patient. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None._

**Response body:**

```jsonc
[ { "id": int, "date": "string", "time": "string", "doctor": "string", "department": "string", "diagnosis": "string", "status": "Completed|Cancelled" } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `500` | Unable to load visit history |

#### `GET /api/v1/appointments/pending-results/`

| Field | Value |
|---|---|
| **Description** | Returns appointments where lab/test results have not yet been released. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None._

**Response body:**

```jsonc
[ { "id": int, "date": "string", "test": "string", "status": "string" } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `500` | Unable to load pending results |

#### `POST /api/v1/appointments/book/`

| Field | Value |
|---|---|
| **Description** | Books a new appointment for the patient. Slot is locked via SELECT FOR UPDATE. 409 returned if already taken. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:**

```jsonc
{ "doctor_id": int, "date": "YYYY-MM-DD", "time_slot": "HH:MM", "reason": "string", "type": "in-person|virtual" }
```

**Response body:**

```jsonc
{ "id": int, "appointment_date": "string", "time": "string", "doctor_name": "string", "status": "confirmed", "qr_code_token": "string" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `400` | Validation error |
| `401` | Redirect to login |
| `409` | Slot already booked |
| `500` | Failed to book |

### 3.4 Doctors & Timeslots

#### `GET /api/v1/doctors/`

| Field | Value |
|---|---|
| **Description** | Returns list of all doctors available for appointment booking. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None._

**Response body:**

```jsonc
[ { "id": int, "name": "string", "specialization": "string", "available": boolean } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `500` | Server error |

#### `GET /api/v1/timeslots/?date={YYYY-MM-DD}`

| Field | Value |
|---|---|
| **Description** | Returns available timeslots for a given doctor on a given date. Query param 'date' required. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:**

```text
Query param: date=YYYY-MM-DD (required). Optional: doctor_id=int
```

**Response body:**

```jsonc
[ { "id": int, "time": "HH:MM", "is_available": boolean } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `400` | Missing date param |
| `401` | Redirect to login |
| `500` | Server error |

### 3.5 Medical Records

#### `GET /api/v1/medical/records/`

| Field | Value |
|---|---|
| **Description** | Returns all medical records (visit history) for the authenticated patient. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None._

**Response body:**

```jsonc
[ { "id": int, "date": "YYYY-MM-DD", "doctor": "string", "diagnosis": "string", "department": "string" } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `404` | No records found |
| `500` | Unable to load history |

#### `GET /api/v1/medical/records/{id}/`

| Field | Value |
|---|---|
| **Description** | Returns full detail of a single medical record including prescription and symptoms. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None - ID in URL path._

**Response body:**

```jsonc
{ "id": int, "date": "YYYY-MM-DD", "doctor": "string", "diagnosis": "string", "symptoms": "string", "prescription": "string", "department": "string" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Not your record |
| `404` | Not found |
| `500` | Server error |

### 3.6 Emergency Contacts

#### `GET /api/v1/emergency-contacts/`

| Field | Value |
|---|---|
| **Description** | Returns all emergency contacts for the authenticated patient. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None._

**Response body:**

```jsonc
[ { "id": int, "name": "string", "relationship": "string", "phone": "string", "label": "Emergency|Home|Work" } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `500` | Unable to load contacts |

#### `POST /api/v1/emergency-contacts/`

| Field | Value |
|---|---|
| **Description** | Adds a new emergency contact for the authenticated patient. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:**

```jsonc
{ "name": "string", "relationship": "string", "phone": "string", "label": "string" }
```

**Response body:**

```jsonc
{ "id": int, "name": "string", "relationship": "string", "phone": "string", "label": "string" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `400` | Validation errors |
| `401` | Redirect to login |
| `500` | Failed to add contact |

#### `PATCH /api/v1/emergency-contacts/{id}/`

| Field | Value |
|---|---|
| **Description** | Partially updates an emergency contact. All fields optional. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:**

```jsonc
{ "name": "string (opt)", "relationship": "string (opt)", "phone": "string (opt)", "label": "string (opt)" }
```

**Response body:**

```jsonc
{ "id": int, "name": "string", "relationship": "string", "phone": "string", "label": "string" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `400` | Validation error |
| `401` | Redirect to login |
| `404` | Contact not found |
| `500` | Failed to update |

#### `DELETE /api/v1/emergency-contacts/{id}/`

| Field | Value |
|---|---|
| **Description** | Deletes the specified emergency contact belonging to the authenticated patient. |
| **Auth required** | Bearer token required |
| **Roles allowed** | PATIENT |

**Request body:** _None - ID in URL path._

**Response body:**

```jsonc
{ "message": "Contact deleted successfully", "deleted_id": int }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `404` | Contact not found |
| `500` | Failed to delete |

### 3.7 Notifications (All Roles)

#### `GET /api/v1/notifications/`

| Field | Value |
|---|---|
| **Description** | Returns all notifications for the authenticated user, ordered by most recent first. |
| **Auth required** | Bearer token required |
| **Roles allowed** | All authenticated roles |

**Request body:** _None._

**Response body:**

```jsonc
[ { "id": int, "title": "string", "text": "string", "time": "ISO8601 datetime", "read": boolean } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `500` | Unable to load notifications |

#### `PATCH /api/v1/notifications/{id}/read/`

| Field | Value |
|---|---|
| **Description** | Marks a single notification as read. Called when the user clicks a notification item in the panel. |
| **Auth required** | Bearer token required |
| **Roles allowed** | All authenticated roles |

**Request body:**

```jsonc
{ "read": true }
```

**Response body:**

```jsonc
{ "id": int, "read": true }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `404` | Notification not found |
| `500` | Failed to mark as read |

#### `PATCH /api/v1/notifications/read-all/`

| Field | Value |
|---|---|
| **Description** | Marks all notifications for the current user as read in one call. |
| **Auth required** | Bearer token required |
| **Roles allowed** | All authenticated roles |

**Request body:** _None._

**Response body:**

```jsonc
{ "message": "All notifications marked as read", "updated_count": int }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `500` | Failed to mark all as read |

#### `DELETE /api/v1/notifications/{id}/`

| Field | Value |
|---|---|
| **Description** | Deletes a single notification. Admin only - other roles receive 403. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:** _None - ID in URL path._

**Response body:**

```jsonc
{ "message": "string", "deleted_id": int }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Access denied |
| `404` | Not found |
| `500` | Failed to delete |

### 3.8 Admin Reports Dashboard (F4 - NEW)

> All /api/v1/admin/* endpoints require role: ADMIN. Flask @require_auth rejects non-admin tokens with 403 before any DB interaction.

#### `GET /api/v1/admin/reports/summary/`

| Field | Value |
|---|---|
| **Description** | Returns top-level summary cards for the admin dashboard: total patients, doctors, appointments today, cancellation rate. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:** _None._

**Response body:**

```jsonc
{ "total_patients": int, "total_doctors": int, "appointments_today": int, "cancellation_rate": float }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Admins only |
| `500` | Unable to load summary stats |

#### `GET /api/v1/admin/reports/appointments/`

| Field | Value |
|---|---|
| **Description** | Returns appointment count grouped by doctor. Response is Chart.js-ready: labels array + data array for bar chart rendering. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:** _None._

**Response body:**

```jsonc
{ "labels": ["Dr. Nkosi", "Dr. Sithole", "..."], "data": [24, 17, 31] }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Admins only |
| `500` | Unable to load appointment report |

#### `GET /api/v1/admin/reports/daily-counts/`

| Field | Value |
|---|---|
| **Description** | Returns appointment counts per day for the past 30 days. Response is Chart.js-ready for line chart rendering. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:** _None._

**Response body:**

```jsonc
{ "labels": ["2026-04-15", "2026-04-16", "..."], "data": [4, 7, 3, 9, "..."] }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Admins only |
| `500` | Unable to load daily counts |

### 3.9 Admin Audit Log (F4 - NEW)

#### `GET /api/v1/admin/audit-log/`

| Field | Value |
|---|---|
| **Description** | Returns paginated audit log entries. Supports optional query filters: ?user= &action= &date_from= &date_to=. Ordered by most recent first. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:** _None - filters via query params. Example: ?user=johndoe&date_from=2026-05-01._

**Response body:**

```jsonc
{ "count": int, "next": "string|null", "previous": "string|null", "results": [ { "id": int, "user": "string", "action": "string", "timestamp": "ISO8601", "ip_address": "string", "detail": "string" } ] }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Admins only |
| `500` | Unable to load audit log |

### 3.10 Admin Department Management (F4 - NEW)

#### `GET /api/v1/admin/departments/`

| Field | Value |
|---|---|
| **Description** | Returns the full list of departments for the department management table. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:** _None._

**Response body:**

```jsonc
[ { "id": int, "name": "string", "head_doctor": "string", "staff_count": int, "created_at": "ISO8601" } ]
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Admins only |
| `500` | Unable to load departments |

#### `POST /api/v1/admin/departments/`

| Field | Value |
|---|---|
| **Description** | Creates a new department. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:**

```jsonc
{ "name": "string", "head_doctor_id": int }
```

**Response body:**

```jsonc
{ "id": int, "name": "string", "head_doctor": "string", "staff_count": 0, "created_at": "ISO8601" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `400` | Validation errors |
| `401` | Redirect |
| `403` | Admins only |
| `409` | Name already exists |
| `500` | Failed to create |

#### `PATCH /api/v1/admin/departments/{id}/`

| Field | Value |
|---|---|
| **Description** | Partially updates an existing department. All fields optional. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:**

```jsonc
{ "name": "string (opt)", "head_doctor_id": int (opt) }
```

**Response body:**

```jsonc
{ "id": int, "name": "string", "head_doctor": "string", "staff_count": int, "created_at": "ISO8601" }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `400` | Validation errors |
| `401` | Redirect |
| `403` | Admins only |
| `404` | Not found |
| `500` | Failed to update |

#### `DELETE /api/v1/admin/departments/{id}/`

| Field | Value |
|---|---|
| **Description** | Deletes a department. Frontend must show a confirmation dialog first. Returns 409 if department has active staff. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:** _None - ID in URL path._

**Response body:**

```jsonc
{ "message": "string", "deleted_id": int }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect |
| `403` | Admins only |
| `404` | Not found |
| `409` | Has active staff |
| `500` | Failed to delete |

### 3.11 Admin User Management (F4 - NEW)

#### `GET /api/v1/admin/users/`

| Field | Value |
|---|---|
| **Description** | Returns a paginated list of all user accounts. Supports optional filter: ?role=PATIENT\|DOCTOR\|ADMIN\|etc. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:** _None - optional ?role= query param._

**Response body:**

```jsonc
{ "count": int, "next": "string|null", "previous": "string|null", "results": [ { "id": int, "username": "string", "email": "string", "role": "string", "is_active": boolean, "date_joined": "ISO8601" } ] }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `401` | Redirect to login |
| `403` | Admins only |
| `500` | Unable to load users |

#### `PATCH /api/v1/admin/users/{id}/`

| Field | Value |
|---|---|
| **Description** | Updates a user account - typically used to change role or deactivate account. |
| **Auth required** | Bearer token required |
| **Roles allowed** | ADMIN |

**Request body:**

```jsonc
{ "role": "string (opt)", "is_active": boolean (opt) }
```

**Response body:**

```jsonc
{ "id": int, "username": "string", "email": "string", "role": "string", "is_active": boolean }
```

**Error codes:**

| Code | Meaning |
|---|---|
| `400` | Validation errors |
| `401` | Redirect |
| `403` | Admins only |
| `404` | User not found |
| `500` | Failed to update |

## Error Code Reference

All error responses follow the standard envelope:

```json
{ "error": "Human-readable message", "code": "MACHINE_CODE" }
```

| Code | Name | Meaning | Applies To |
|---|---|---|---|
| `200` | OK | GET successful | All GET endpoints |
| `201` | Created | Resource created successfully | POST (booking, contacts, departments) |
| `204` | No Content | DELETE successful, no body | DELETE endpoints |
| `400` | Bad Request | Invalid payload / missing required fields | All POST/PATCH/PUT |
| `401` | Unauthorized | Missing, expired, or invalid JWT token | All protected endpoints |
| `403` | Forbidden | Valid token but insufficient role | Role-gated endpoints |
| `404` | Not Found | Resource does not exist | GET/PATCH/DELETE by ID |
| `409` | Conflict | Slot already booked or duplicate resource | POST /book/, POST /departments/ |
| `422` | Unprocessable Entity | Validation passed structure but failed logic | Complex business rules |
| `500` | Internal Server Error | Unhandled server error | All endpoints |

## Conflicts and Resolutions

The following inconsistencies were identified across F1, F2, F3, and F4 submissions. Backend must review each resolution before implementation. Any disagreement must be raised within 24 hours of receiving this document.

| Issue | Conflict | Resolution |
|---|---|---|
| URL prefix mismatch | F2 uses /api/ (no version). F1, F3, F4 use /api/v1/. | Backend standardises ALL routes under /api/v1/. Frontend F2 must update. |
| HTTP method: emergency contacts update | F2 documents PUT. F3 documents PATCH. | PATCH preferred (partial update semantics). F2 aligns to PATCH. |
| Appointment booking path | F2: POST /api/appointments. F3: POST /api/v1/appointments/book/. | Canonical: /api/v1/appointments/book/. F2 aligns. |
| Timeslot response format | F2 expects array of strings. F3 expects objects with id/date. | Backend uses objects: [ { id, time, is_available } ]. F2 aligns. |
| Medical records path | F2: /api/medical-records/{id}. F3: /api/v1/medical/records/. | Canonical: /api/v1/medical/records/ (list) and /api/v1/medical/records/{id}/ (detail). |
| Upcoming appointments duplicated | F2 and F3 both define GET upcoming with different shapes. | Backend uses F3 shape with additional doctor_id and department fields. |
| patient/dashboard not in F1/F3 | Only F2 defines GET /api/patient/dashboard. | Adopted as /api/v1/patient/dashboard/. Backend confirms fields. |
| Trailing slashes | F2 omits trailing slashes. F1, F3, F4 include them. | All endpoints use trailing slashes. F2 aligns. |
| Notification PATCH/DELETE - new in v1.2 | Not in F3 contract (only GET). F4 adds PATCH read + DELETE. | F4 shapes adopted as canonical. Backend implements all four notification endpoints. |
| Admin endpoints - new in v1.2 | F4 endpoints were absent from v1.1 contract entirely. | Sections 3.8-3.11 added. B4 implements admin/reports + audit-log. B1 implements admin/users. B2 handles departments (DEPARTMENT model). |

## Governance Rules

| Rule | Statement |
|---|---|
| `G-01` | No endpoint is implemented without appearing in this contract. |
| `G-02` | Backend is the source of truth. Frontend mocks must align to contract, not vice versa. |
| `G-03` | Any deviation from a response shape requires a contract amendment before code changes. |
| `G-04` | No Oracle DDL changes (CREATE/ALTER/DROP TABLE) run without S1 approval. No schema change is made locally and pushed - raise it first. |
| `G-05` | No endpoint merges to dev without passing tests (CI must be green). |
| `G-06` | All protected endpoints validate JWT in the @require_auth decorator (jwt_helper.py) - never inside the route function itself. |
| `G-07` | Role enforcement uses the roles= parameter on @require_auth. Valid roles: PATIENT, DOCTOR, NURSE, RECEPTIONIST, ADMIN. |
| `G-08` | All error responses follow the standard envelope: { error: string, code: string }. |
| `G-09` | Appointment booking uses SELECT FOR UPDATE + UNIQUE(slot_id) - double-booking is impossible. |
| `G-10` | Frontend axios interceptor attaches Bearer token to every protected request automatically. |
| `G-11` | 401 globally redirects to /login and clears the stored token on the frontend. |
| `G-12` | Contract version bumps require sign-off from both Frontend Lead and Backend Lead. |
| `G-13` | All /admin/* endpoints must verify role=ADMIN in @require_auth before any DB interaction. Never rely on frontend to hide admin routes. |

## Backend Assignment Map

Quick reference: which backend developer owns each endpoint group.

| Developer | Section | Endpoints | Notes |
|---|---|---|---|
| **B1** | 3.1 Auth | POST /login/ - /register/ - /logout/ - GET /me/ | JWT login, PyJWT, CORS, permission classes |
| **B1** | 3.11 Admin Users | GET & PATCH /admin/users/ | USER_ACCOUNT + STAFF + DOCTOR tables |
| **B2** | 3.2-3.5 Patient | /patient/* - /appointments/* - /medical/* - /doctors/ - /timeslots/ | PATIENT - MEDICAL_RECORD - TIMESLOT tables |
| **B2** | 3.10 Departments | GET-POST-PATCH-DELETE /admin/departments/ | DEPARTMENT table - already in B2 scope |
| **B3** | 3.3 Booking | POST /appointments/book/ | SELECT FOR UPDATE + QR code generation |
| **B3** | 3.7 Notifications | GET-PATCH-DELETE /notifications/* | NOTIFICATION model + create_notification() |
| **B4** | 3.6 Emergency Contacts | GET-POST-PATCH-DELETE /emergency-contacts/ | PATIENT_CONTACT model |
| **B4** | 3.8-3.9 Reports & Audit | GET /admin/reports/* - GET /admin/audit-log/ | Raw SQL reports + AUDIT_LOG model + middleware |

## Backend Implementation Notes

This section is addressed exclusively to the backend team. Frontend teams do not need to action anything here - their contract obligations are fully covered by Sections 2-6.

### 8.1 Stack - What Was Replaced

| Layer | Old (Removed) | New (Current) |
|---|---|---|
| Web framework | Django REST Framework | Flask 3.0 + flask-cors 4.0 |
| Database | PostgreSQL (psycopg2) | Oracle XE 21c (cx_Oracle 8.3) |
| ORM / Query | Django ORM + migrations | Raw SQL via cursor.execute() in *_repo.py |
| Auth | djangorestframework-simplejwt | PyJWT 2.9 - HS256, HTTP-only Bearer |
| Entry point | python manage.py runserver | python app.py (Flask dev server, port 8000) |
| Settings | backend/config/settings.py | backend/.env loaded via python-dotenv |
| Models | backend/apps/*/models.py | Oracle tables in sql/01_DDL/01_create_tables.sql |
| Migrations | python manage.py makemigrations | No migrations - DDL is in sql/00_RUN_ALL.sql |
| Tests | pytest-django | pytest + unittest.mock (Oracle mocked in CI) |

### 8.2 Backend Folder Structure

> Backend review normalization: this Markdown version follows the current project structure. `USER_ACCOUNT` SQL belongs in `user_account_repo.py`; `DEPARTMENT` SQL remains grouped under `doctor_repo.py`.

| File / Folder | Purpose |
|---|---|
| `backend/app.py` | Flask entry point - registers all blueprints |
| `backend/db/oracle_connection.py` | cx_Oracle `get_connection()` - imported by every repo file |
| `backend/db/user_account_repo.py` | All SQL for `USER_ACCOUNT` login credential lookups |
| `backend/db/patient_repo.py` | All SQL for `PATIENT`, `PATIENT_CONTACT`, `MEDICAL_RECORD` |
| `backend/db/appointment_repo.py` | All SQL for `APPOINTMENT` + `TIMESLOT`, including `SELECT FOR UPDATE` |
| `backend/db/doctor_repo.py` | All SQL for `STAFF`, `DOCTOR`, `DEPARTMENT` |
| `backend/db/queue_repo.py` | All SQL for `QUEUE_ENTRY` |
| `backend/db/notification_repo.py` | All SQL for `NOTIFICATION` |
| `backend/db/audit_repo.py` | All SQL for `AUDIT_LOG` + aggregation queries for admin reports |
| `backend/services/` | Business logic services; no SQL strings |
| `backend/api/` | Flask route handlers / blueprints; no SQL strings |
| `backend/utils/jwt_helper.py` | `@require_auth` decorator + token encode/decode |
| `backend/utils/error_handler.py` | Centralized error envelope: `{ error, code }` |
| `sql/` | Oracle DDL, indexes, views, seed data, and queries - schema source of truth |

### 8.3 Three Laws Every Repo Function Must Follow

| # | Law |
|---|---|
| 1 | Open connection -> open cursor -> execute with bind variables (`:1`, `:2`) -> fetch rows -> close cursor -> close connection -> return data. |
| 2 | Every DML function (`INSERT`, `UPDATE`, `DELETE`) calls `conn.commit()` before closing. No commit means no write. |
| 3 | SQL strings appear only inside `cursor.execute()` in `*_repo.py` files. Services and API routes never touch SQL directly. |

### 8.4 Appointment Booking - Double-Booking Defence

| Step | Mechanism | Detail |
|---|---|---|
| 1 | `SELECT FOR UPDATE` | Lock the `TIMESLOT` row before checking availability. No other transaction can read-modify-write the same slot concurrently. |
| 2 | `is_available` check | If `is_available = 0`, rollback immediately and return `409 SLOT_UNAVAILABLE`. |
| 3 | Insert + update | Insert into `APPOINTMENT`, update `TIMESLOT SET is_available = 0`, then commit. Both rows are committed together. |
| 4 | `UNIQUE(slot_id)` | Final Oracle-level backstop even if application logic fails. |

### 8.5 CI - Oracle Mocking Strategy

GitHub Actions cannot run Oracle XE. All backend tests must mock the database connection using unittest.mock. Any test that calls a repo function without mocking will fail in CI.

```python
from unittest.mock import patch, MagicMock
@patch('db.oracle_connection.get_connection')
def test_get_patient(mock_conn):
mock_cursor = MagicMock()
mock_cursor.fetchone.return_value = (1, 'S001', 'Thabo', 'Dlamini', 'thabo@nwu.ac.za')
mock_conn.return_value.cursor.return_value = mock_cursor
result = patient_repo.get_patient_by_id(1)
assert result[0] == 1
```

### 8.6 Environment Variables Required

| Variable | Example Value | Purpose |
|---|---|---|
| `ORA_USER` | `system` | Oracle DB username |
| `ORA_PASSWORD` | `clinic123` | Oracle DB password (set during XE installation) |
| `ORA_HOST` | `localhost` | Oracle host - always localhost for local dev |
| `ORA_PORT` | `1521` | Oracle listener port - default 1521 |
| `ORA_SID` | `XE` | Oracle SID - always XE for Express Edition |
| `JWT_SECRET` | `your-secret-here` | HS256 signing secret - keep out of version control |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm - do not change |
| `JWT_EXPIRY_MINUTES` | `60` | Token lifespan in minutes |
| `FLASK_ENV` | `development` | Flask mode - use production on deploy |
| `FLASK_PORT` | `8000` | Port Flask listens on |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend origins - comma-separated |

## Sign-off and Version Control

| Party | Name | Date | Signature |
|---|---|---|---|
| Frontend Lead (F1) |  |  |  |
| Frontend Lead (F2) |  |  |  |
| Frontend Lead (F3) |  |  |  |
| Frontend Lead (F4) |  |  |  |
| Backend Lead |  |  |  |
| S1 / Supervisor |  |  |  |

---

_UBUNTU CLINIC - CBS - Group 19 - CMPG 311 - API Contract v1.2.0_
