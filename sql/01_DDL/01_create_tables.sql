-- =============================================================================
-- UBUNTU CAMPUS CLINIC â€” APPOINTMENT SYSTEM
-- Group 19 | CMPG 311 | DBMS Module | Physical Design
-- File: 01_create_tables.sql
-- Purpose: Create all 12 tables in FK dependency order
-- Database: Oracle SQL Developer (XE or university-provided schema)
-- =============================================================================

-- Drop tables in reverse FK order so re-runs are safe.
-- Ignore missing tables instead of failing on the first run.
DECLARE
    TYPE table_list_t IS TABLE OF VARCHAR2(30);
    tables table_list_t := table_list_t(
        'AUDIT_LOG',
        'NOTIFICATION',
        'MEDICAL_RECORD',
        'QUEUE_ENTRY',
        'APPOINTMENT',
        'USER_ACCOUNT',
        'DOCTOR',
        'PATIENT_CONTACT',
        'STAFF',
        'DEPARTMENT',
        'TIMESLOT',
        'PATIENT'
    );
BEGIN
    FOR i IN 1 .. tables.COUNT LOOP
        BEGIN
            EXECUTE IMMEDIATE 'DROP TABLE ' || tables(i) || ' CASCADE CONSTRAINTS PURGE';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -942 THEN
                    RAISE;
                END IF;
        END;
    END LOOP;
END;
/

-- =============================================================================
-- LEVEL 1 â€” No FK dependencies
-- =============================================================================

-- 1. PATIENT
--    Core entity. Stores NWU student demographic and consent data.
--    POPIA compliance enforced via consent_given CHECK constraint.
CREATE TABLE PATIENT (
    patient_id        NUMBER         GENERATED ALWAYS AS IDENTITY,
    student_number    VARCHAR2(10)   NOT NULL,
    first_name        VARCHAR2(100)  NOT NULL,
    last_name         VARCHAR2(100)  NOT NULL,
    email             VARCHAR2(254)  NOT NULL,
    contact_number    VARCHAR2(20)   NOT NULL,
    date_of_birth     DATE           NOT NULL,
    street            VARCHAR2(255)  NOT NULL,
    city              VARCHAR2(100)  NOT NULL,
    postal_code       VARCHAR2(10)   NOT NULL,
    consent_given     NUMBER(1)      DEFAULT 0 NOT NULL,
    registration_date TIMESTAMP      DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pk_patient        PRIMARY KEY (patient_id),
    CONSTRAINT uq_patient_stdnum UNIQUE      (student_number),
    CONSTRAINT uq_patient_email  UNIQUE      (email),
    CONSTRAINT chk_consent       CHECK       (consent_given IN (0, 1))
);

-- 2. TIMESLOT
--    Available appointment slots. is_available flipped to 0 when APPOINTMENT is booked.
--    end_time > start_time enforced at DB level.
CREATE TABLE TIMESLOT (
    slot_id      NUMBER       GENERATED ALWAYS AS IDENTITY,
    slot_date    DATE         NOT NULL,
    start_time   VARCHAR2(8)  NOT NULL,
    end_time     VARCHAR2(8)  NOT NULL,
    is_available NUMBER(1)    DEFAULT 1 NOT NULL,
    CONSTRAINT pk_timeslot    PRIMARY KEY (slot_id),
    CONSTRAINT chk_slot_avail CHECK       (is_available IN (0, 1)),
    CONSTRAINT chk_slot_time  CHECK       (end_time > start_time)
);

-- 3. DEPARTMENT
--    head_staff_id FK to STAFF is added after STAFF is created (ALTER TABLE below).
CREATE TABLE DEPARTMENT (
    department_id   NUMBER        GENERATED ALWAYS AS IDENTITY,
    department_name VARCHAR2(200) NOT NULL,
    head_staff_id   NUMBER,
    created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pk_department      PRIMARY KEY (department_id),
    CONSTRAINT uq_department_name UNIQUE      (department_name)
);

-- =============================================================================
-- LEVEL 2 â€” Depends on Level 1
-- =============================================================================

-- 4. PATIENT_CONTACT
--    Emergency / next-of-kin contacts. Cascades on patient delete.
CREATE TABLE PATIENT_CONTACT (
    patient_contact_id NUMBER        GENERATED ALWAYS AS IDENTITY,
    patient_id         NUMBER        NOT NULL,
    contact_name       VARCHAR2(150) NOT NULL,
    phone_number       VARCHAR2(20)  NOT NULL,
    relationship       VARCHAR2(100),
    CONSTRAINT pk_patient_contact PRIMARY KEY (patient_contact_id),
    CONSTRAINT fk_pc_patient      FOREIGN KEY (patient_id)
        REFERENCES PATIENT (patient_id) ON DELETE CASCADE
);

-- 5. STAFF
--    All clinic personnel (DOCTOR, NURSE, ADMIN). Subtype DOCTOR extends this table.
CREATE TABLE STAFF (
    staff_id            NUMBER        GENERATED ALWAYS AS IDENTITY,
    department_id       NUMBER,
    first_name          VARCHAR2(100) NOT NULL,
    last_name           VARCHAR2(100) NOT NULL,
    role                VARCHAR2(20)  NOT NULL,
    email               VARCHAR2(254) NOT NULL,
    contact_number      VARCHAR2(20)  NOT NULL,
    working_hours_start VARCHAR2(8)   NOT NULL,
    working_hours_end   VARCHAR2(8)   NOT NULL,
    CONSTRAINT pk_staff       PRIMARY KEY (staff_id),
    CONSTRAINT uq_staff_email UNIQUE      (email),
    CONSTRAINT chk_staff_role CHECK       (role IN ('DOCTOR', 'NURSE', 'ADMIN')),
    CONSTRAINT fk_staff_dept  FOREIGN KEY (department_id)
        REFERENCES DEPARTMENT (department_id) ON DELETE SET NULL
);

-- Resolve the circular FK: DEPARTMENT.head_staff_id â†’ STAFF
ALTER TABLE DEPARTMENT
    ADD CONSTRAINT fk_dept_head
    FOREIGN KEY (head_staff_id)
    REFERENCES STAFF (staff_id) ON DELETE SET NULL;

-- =============================================================================
-- LEVEL 3 â€” Depends on Level 2
-- =============================================================================

-- 6. DOCTOR
--    Supertype/subtype pattern. PK is also FK to STAFF â€” one-to-one relationship.
--    Only STAFF rows with role = 'DOCTOR' will have a matching DOCTOR row.
CREATE TABLE DOCTOR (
    staff_id       NUMBER        NOT NULL,
    license_number VARCHAR2(50)  NOT NULL,
    specialisation VARCHAR2(150) NOT NULL,
    CONSTRAINT pk_doctor         PRIMARY KEY (staff_id),
    CONSTRAINT uq_doctor_license UNIQUE      (license_number),
    CONSTRAINT fk_doctor_staff   FOREIGN KEY (staff_id)
        REFERENCES STAFF (staff_id) ON DELETE CASCADE
);

-- 7. USER_ACCOUNT
--    Authentication table. A user is either a patient or a staff member (never both null).
CREATE TABLE USER_ACCOUNT (
    user_account_id NUMBER        GENERATED ALWAYS AS IDENTITY,
    username        VARCHAR2(150) NOT NULL,
    password_hash   VARCHAR2(255) NOT NULL,
    patient_id      NUMBER,
    staff_id        NUMBER,
    role            VARCHAR2(20)  NOT NULL,
    status          VARCHAR2(20)  DEFAULT 'ACTIVE' NOT NULL,
    date_joined     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pk_user_account           PRIMARY KEY (user_account_id),
    CONSTRAINT uq_username               UNIQUE      (username),
    CONSTRAINT chk_user_role             CHECK       (role IN ('PATIENT','DOCTOR','NURSE','ADMIN','RECEPTIONIST')),
    CONSTRAINT chk_user_status           CHECK       (status IN ('ACTIVE','LOCKED','DISABLED')),
    CONSTRAINT chk_user_patient_or_staff CHECK       (patient_id IS NOT NULL OR staff_id IS NOT NULL),
    CONSTRAINT fk_user_patient           FOREIGN KEY (patient_id)
        REFERENCES PATIENT (patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_staff             FOREIGN KEY (staff_id)
        REFERENCES STAFF (staff_id) ON DELETE CASCADE
);

-- =============================================================================
-- LEVEL 4 â€” Depends on Level 3
-- =============================================================================

-- 8. APPOINTMENT
--    Central booking record. UNIQUE on slot_id prevents double-booking at DB level.
--    QR code token supports mobile check-in flows.
CREATE TABLE APPOINTMENT (
    appointment_id NUMBER        GENERATED ALWAYS AS IDENTITY,
    slot_id        NUMBER        NOT NULL,
    patient_id     NUMBER        NOT NULL,
    staff_id       NUMBER        NOT NULL,
    status         VARCHAR2(20)  DEFAULT 'SCHEDULED' NOT NULL,
    booking_type   VARCHAR2(20)  DEFAULT 'SICK'      NOT NULL,
    priority       VARCHAR2(10)  DEFAULT 'NORMAL'    NOT NULL,
    qr_code_token  VARCHAR2(36),
    CONSTRAINT pk_appointment      PRIMARY KEY (appointment_id),
    CONSTRAINT uq_appointment_slot UNIQUE      (slot_id),
    CONSTRAINT uq_appt_qr_token    UNIQUE      (qr_code_token),
    CONSTRAINT chk_appt_status     CHECK       (status   IN ('SCHEDULED','CONFIRMED','COMPLETED','CANCELLED','NO_SHOW')),
    CONSTRAINT chk_appt_type       CHECK       (booking_type IN ('SICK','FOLLOW_UP','WALK_IN','VIRTUAL_TRIAGE')),
    CONSTRAINT chk_appt_priority   CHECK       (priority IN ('NORMAL','URGENT')),
    CONSTRAINT fk_appt_slot        FOREIGN KEY (slot_id)
        REFERENCES TIMESLOT (slot_id),
    CONSTRAINT fk_appt_patient     FOREIGN KEY (patient_id)
        REFERENCES PATIENT (patient_id),
    CONSTRAINT fk_appt_staff       FOREIGN KEY (staff_id)
        REFERENCES STAFF (staff_id)
);

-- 9. AUDIT_LOG
--    POPIA-compliant action tracking. Every CREATE/READ/UPDATE/DELETE on sensitive tables.
CREATE TABLE AUDIT_LOG (
    audit_log_id       NUMBER        GENERATED ALWAYS AS IDENTITY,
    user_id            NUMBER        NOT NULL,
    action             VARCHAR2(10)  NOT NULL,
    table_affected     VARCHAR2(100) NOT NULL,
    record_affected_id NUMBER        NOT NULL,
    log_timestamp      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ip_address         VARCHAR2(45),
    CONSTRAINT pk_audit_log    PRIMARY KEY (audit_log_id),
    CONSTRAINT chk_audit_action CHECK       (action IN ('CREATE','READ','UPDATE','DELETE')),
    CONSTRAINT fk_audit_user   FOREIGN KEY (user_id)
        REFERENCES USER_ACCOUNT (user_account_id)
);

-- =============================================================================
-- LEVEL 5 â€” Depends on Level 4
-- =============================================================================

-- 10. QUEUE_ENTRY
--     Live waiting-room queue. One entry per appointment (UNIQUE on appointment_id).
CREATE TABLE QUEUE_ENTRY (
    queue_entry_id     NUMBER      GENERATED ALWAYS AS IDENTITY,
    appointment_id     NUMBER      NOT NULL,
    status             VARCHAR2(20) DEFAULT 'WAITING' NOT NULL,
    checked_in_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP NOT NULL,
    consult_start_time VARCHAR2(8),
    consult_end_time   VARCHAR2(8),
    room_number        VARCHAR2(50),
    CONSTRAINT pk_queue_entry   PRIMARY KEY (queue_entry_id),
    CONSTRAINT uq_queue_appt    UNIQUE      (appointment_id),
    CONSTRAINT chk_queue_status CHECK       (status IN ('WAITING','IN_PROGRESS','COMPLETED','LEFT_WITHOUT_SEEN')),
    CONSTRAINT fk_queue_appt    FOREIGN KEY (appointment_id)
        REFERENCES APPOINTMENT (appointment_id)
);

-- 11. MEDICAL_RECORD
--     Clinical notes created after a completed consultation.
CREATE TABLE MEDICAL_RECORD (
    medical_record_id NUMBER        GENERATED ALWAYS AS IDENTITY,
    appointment_id    NUMBER        NOT NULL,
    patient_id        NUMBER        NOT NULL,
    diagnosis         VARCHAR2(4000),
    prescription      VARCHAR2(4000),
    treatment_notes   VARCHAR2(4000),
    created_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pk_medical_record PRIMARY KEY (medical_record_id),
    CONSTRAINT fk_mr_appointment FOREIGN KEY (appointment_id)
        REFERENCES APPOINTMENT (appointment_id),
    CONSTRAINT fk_mr_patient     FOREIGN KEY (patient_id)
        REFERENCES PATIENT (patient_id)
);

-- 12. NOTIFICATION
--     Email / SMS delivery records. Either patient_id or staff_id must be set.
CREATE TABLE NOTIFICATION (
    notification_id NUMBER        GENERATED ALWAYS AS IDENTITY,
    patient_id      NUMBER,
    staff_id        NUMBER,
    appointment_id  NUMBER        NOT NULL,
    channel         VARCHAR2(10)  NOT NULL,
    status          VARCHAR2(10)  DEFAULT 'PENDING' NOT NULL,
    message         VARCHAR2(4000) NOT NULL,
    created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP NOT NULL,
    sent_at         TIMESTAMP,
    error_message   VARCHAR2(4000),
    CONSTRAINT pk_notification     PRIMARY KEY (notification_id),
    CONSTRAINT chk_notif_channel   CHECK       (channel IN ('EMAIL','SMS')),
    CONSTRAINT chk_notif_status    CHECK       (status  IN ('PENDING','SENT','FAILED')),
    CONSTRAINT chk_notif_recipient CHECK       (patient_id IS NOT NULL OR staff_id IS NOT NULL),
    CONSTRAINT fk_notif_patient    FOREIGN KEY (patient_id)
        REFERENCES PATIENT (patient_id) ON DELETE SET NULL,
    CONSTRAINT fk_notif_staff      FOREIGN KEY (staff_id)
        REFERENCES STAFF (staff_id) ON DELETE SET NULL,
    CONSTRAINT fk_notif_appt       FOREIGN KEY (appointment_id)
        REFERENCES APPOINTMENT (appointment_id) ON DELETE CASCADE
);

-- =============================================================================
-- Verification â€” confirm all 12 tables exist
-- =============================================================================
SELECT table_name
FROM   user_tables
WHERE  table_name IN (
           'PATIENT','PATIENT_CONTACT','TIMESLOT','DEPARTMENT',
           'STAFF','DOCTOR','USER_ACCOUNT','APPOINTMENT',
           'AUDIT_LOG','QUEUE_ENTRY','MEDICAL_RECORD','NOTIFICATION'
       )
ORDER BY table_name;
