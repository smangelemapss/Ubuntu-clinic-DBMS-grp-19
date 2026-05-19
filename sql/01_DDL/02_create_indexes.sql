-- =============================================================================
-- UBUNTU CAMPUS CLINIC â€” APPOINTMENT SYSTEM
-- Group 19 | CMPG 311 | DBMS Module | Physical Design
-- File: 02_create_indexes.sql
-- Purpose: Create all performance and query-support indexes
-- Database: Oracle SQL Developer
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TIMESLOT indexes
-- Slot availability lookup by date is the most frequent read in the system
-- -----------------------------------------------------------------------------
CREATE INDEX idx_timeslot_date
    ON TIMESLOT (slot_date);

-- Composite index: available slots on a specific date (covers the availability query)
CREATE INDEX idx_timeslot_date_avail
    ON TIMESLOT (slot_date, is_available);

-- -----------------------------------------------------------------------------
-- APPOINTMENT indexes
-- -----------------------------------------------------------------------------

-- Patient appointment history (patient portal, receptionist lookup)
CREATE INDEX idx_appt_patient
    ON APPOINTMENT (patient_id);

-- Doctor/staff schedule queries
CREATE INDEX idx_appt_staff
    ON APPOINTMENT (staff_id);

-- Status filtering â€” e.g. all CONFIRMED appointments for today's queue
CREATE INDEX idx_appt_status
    ON APPOINTMENT (status);

-- -----------------------------------------------------------------------------
-- QUEUE_ENTRY indexes
-- -----------------------------------------------------------------------------

-- Check-in lookup by appointment (foreign key navigation)
-- This column already has an index from the unique constraint on appointment_id.
-- No separate index is required and creating one would raise ORA-01408.
--CREATE INDEX idx_queue_appt
--    ON QUEUE_ENTRY (appointment_id);

-- Live queue board filtered by status (WAITING / IN_PROGRESS)
CREATE INDEX idx_queue_status
    ON QUEUE_ENTRY (status);

-- -----------------------------------------------------------------------------
-- MEDICAL_RECORD indexes
-- -----------------------------------------------------------------------------

-- Full patient medical history lookup
CREATE INDEX idx_mr_patient
    ON MEDICAL_RECORD (patient_id);

-- Records per appointment (one-to-one in practice, but indexed for joins)
CREATE INDEX idx_mr_appt
    ON MEDICAL_RECORD (appointment_id);

-- -----------------------------------------------------------------------------
-- NOTIFICATION indexes
-- -----------------------------------------------------------------------------

-- Notification lookup per appointment (delivery tracking)
CREATE INDEX idx_notif_appt
    ON NOTIFICATION (appointment_id);

-- Inbox queries by recipient (patient/staff notification lists)
CREATE INDEX idx_notif_patient
    ON NOTIFICATION (patient_id);

CREATE INDEX idx_notif_staff
    ON NOTIFICATION (staff_id);

-- -----------------------------------------------------------------------------
-- USER_ACCOUNT indexes
-- Join from USER_ACCOUNT to PATIENT for profile and notification routing
-- -----------------------------------------------------------------------------
CREATE INDEX idx_user_patient
    ON USER_ACCOUNT (patient_id);

CREATE INDEX idx_user_staff
    ON USER_ACCOUNT (staff_id);

-- -----------------------------------------------------------------------------
-- AUDIT_LOG indexes
-- -----------------------------------------------------------------------------

-- Date-range filtering for admin compliance reports
CREATE INDEX idx_audit_timestamp
    ON AUDIT_LOG (log_timestamp);

-- Per-user activity history
CREATE INDEX idx_audit_user
    ON AUDIT_LOG (user_id);

-- =============================================================================
-- Verification â€” list all indexes created by this script
-- =============================================================================
SELECT index_name,
       table_name,
       uniqueness
FROM   user_indexes
WHERE  index_name IN (
           'IDX_TIMESLOT_DATE',
           'IDX_TIMESLOT_DATE_AVAIL',
           'IDX_APPT_PATIENT',
           'IDX_APPT_STAFF',
           'IDX_APPT_STATUS',
           'IDX_QUEUE_STATUS',
           'IDX_MR_PATIENT',
           'IDX_MR_APPT',
           'IDX_NOTIF_APPT',
           'IDX_NOTIF_PATIENT',
           'IDX_NOTIF_STAFF',
           'IDX_USER_PATIENT',
           'IDX_USER_STAFF',
           'IDX_AUDIT_TIMESTAMP',
           'IDX_AUDIT_USER'
       )
ORDER BY table_name, index_name;
