-- =============================================================================
-- UBUNTU CAMPUS CLINIC â€” APPOINTMENT SYSTEM
-- Group 19 | CMPG 311 | DBMS Module | Physical Design
-- File: 03_create_views.sql
-- Purpose: Create 4 reporting views used by the clinic application
-- Database: Oracle SQL Developer
-- Note: ORDER BY is intentionally omitted from view bodies (Oracle disallows it).
--       Callers may add ORDER BY when querying the view.
-- =============================================================================

-- =============================================================================
-- VIEW 1: vw_patient_appointments
-- Purpose: Complete appointment history per patient.
--          Used by the patient dashboard and receptionist booking lookup.
-- =============================================================================
CREATE OR REPLACE VIEW vw_patient_appointments AS
SELECT
    p.patient_id,
    p.student_number,
    p.first_name  || ' ' || p.last_name    AS patient_name,
    p.email                                 AS patient_email,
    p.city                                  AS patient_city,
    a.appointment_id,
    a.status                                AS appointment_status,
    a.booking_type,
    a.priority,
    t.slot_date,
    t.start_time,
    t.end_time,
    s.first_name  || ' ' || s.last_name    AS doctor_name,
    s.role                                  AS staff_role
FROM   PATIENT      p
JOIN   APPOINTMENT  a ON a.patient_id = p.patient_id
JOIN   TIMESLOT     t ON t.slot_id    = a.slot_id
JOIN   STAFF        s ON s.staff_id   = a.staff_id;

-- =============================================================================
-- VIEW 2: vw_daily_queue_board
-- Purpose: Live queue for today.
--          Used by nurses and admin to manage the waiting room in real time.
-- =============================================================================
CREATE OR REPLACE VIEW vw_daily_queue_board AS
SELECT
    q.queue_entry_id,
    q.status                                AS queue_status,
    q.checked_in_at,
    q.consult_start_time,
    q.consult_end_time,
    q.room_number,
    p.student_number,
    p.first_name  || ' ' || p.last_name    AS patient_name,
    a.appointment_id,
    a.priority,
    a.booking_type,
    t.slot_date,
    t.start_time,
    s.first_name  || ' ' || s.last_name    AS doctor_name
FROM   QUEUE_ENTRY  q
JOIN   APPOINTMENT  a ON a.appointment_id = q.appointment_id
JOIN   PATIENT      p ON p.patient_id     = a.patient_id
JOIN   TIMESLOT     t ON t.slot_id        = a.slot_id
JOIN   STAFF        s ON s.staff_id       = a.staff_id
WHERE  t.slot_date = TRUNC(SYSDATE);

-- =============================================================================
-- VIEW 3: vw_doctor_schedule
-- Purpose: Each doctor's schedule with patient and slot details.
--          Used by doctors to review their upcoming consultations.
-- =============================================================================
CREATE OR REPLACE VIEW vw_doctor_schedule AS
SELECT
    s.staff_id,
    s.first_name  || ' ' || s.last_name    AS doctor_name,
    s.email                                 AS doctor_email,
    d.specialisation,
    d.license_number,
    dept.department_name,
    a.appointment_id,
    a.status,
    a.priority,
    a.booking_type,
    t.slot_date,
    t.start_time,
    t.end_time,
    p.student_number,
    p.first_name  || ' ' || p.last_name    AS patient_name,
    p.contact_number                        AS patient_contact
FROM   STAFF        s
JOIN   DOCTOR       d    ON d.staff_id        = s.staff_id
JOIN   DEPARTMENT   dept ON dept.department_id = s.department_id
JOIN   APPOINTMENT  a    ON a.staff_id        = s.staff_id
JOIN   TIMESLOT     t    ON t.slot_id         = a.slot_id
JOIN   PATIENT      p    ON p.patient_id      = a.patient_id
WHERE  a.status NOT IN ('CANCELLED', 'NO_SHOW');

-- =============================================================================
-- VIEW 4: vw_audit_trail_summary
-- Purpose: Human-readable audit log for POPIA compliance reporting.
--          Shows who did what, to which record, and when.
-- =============================================================================
CREATE OR REPLACE VIEW vw_audit_trail_summary AS
SELECT
    al.audit_log_id,
    al.log_timestamp,
    ua.username,
    ua.role                                 AS user_role,
    al.action,
    al.table_affected,
    al.record_affected_id,
    al.ip_address,
    p.first_name  || ' ' || p.last_name    AS patient_name,
    p.student_number
FROM   AUDIT_LOG    al
JOIN   USER_ACCOUNT ua ON ua.user_account_id = al.user_id
LEFT JOIN PATIENT   p  ON p.patient_id       = ua.patient_id;

-- =============================================================================
-- Verification â€” confirm all 4 views exist
-- =============================================================================
SELECT view_name
FROM   user_views
WHERE  view_name IN (
           'VW_PATIENT_APPOINTMENTS',
           'VW_DAILY_QUEUE_BOARD',
           'VW_DOCTOR_SCHEDULE',
           'VW_AUDIT_TRAIL_SUMMARY'
       )
ORDER BY view_name;
