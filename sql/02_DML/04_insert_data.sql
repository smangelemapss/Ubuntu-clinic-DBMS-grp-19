-- =============================================================================
-- UBUNTU CAMPUS CLINIC â€” APPOINTMENT SYSTEM
-- Group 19 | CMPG 311 | DBMS Module | Physical Design
-- File: 04_insert_data.sql
-- Purpose: Populate all 12 tables with realistic South African clinic seed data
-- Database: Oracle SQL Developer
-- Run order: AFTER 01_create_tables.sql, 02_create_indexes.sql, 03_create_views.sql
-- =============================================================================

-- =============================================================================
-- DEPARTMENT â€” 5 rows
-- head_staff_id set to NULL here; updated after STAFF rows are inserted
-- =============================================================================
INSERT INTO DEPARTMENT (department_name, head_staff_id) VALUES ('Medical',        NULL);
INSERT INTO DEPARTMENT (department_name, head_staff_id) VALUES ('Nursing',        NULL);
INSERT INTO DEPARTMENT (department_name, head_staff_id) VALUES ('Pharmacy',       NULL);
INSERT INTO DEPARTMENT (department_name, head_staff_id) VALUES ('Laboratory',     NULL);
INSERT INTO DEPARTMENT (department_name, head_staff_id) VALUES ('Administration', NULL);

-- =============================================================================
-- STAFF â€” 6 rows (3 doctors, 2 nurses, 1 admin)
-- =============================================================================
INSERT INTO STAFF (department_id, first_name, last_name, role, email, contact_number, working_hours_start, working_hours_end)
VALUES (1, 'Naledi', 'Mokoena', 'DOCTOR', 'dr.naledi.mokoena@ubuntuclinic.ac.za', '0721234567', '08:00', '16:00');

INSERT INTO STAFF (department_id, first_name, last_name, role, email, contact_number, working_hours_start, working_hours_end)
VALUES (1, 'Thabo', 'Dlamini', 'DOCTOR', 'dr.thabo.dlamini@ubuntuclinic.ac.za', '0732345678', '08:00', '16:00');

INSERT INTO STAFF (department_id, first_name, last_name, role, email, contact_number, working_hours_start, working_hours_end)
VALUES (1, 'Aisha', 'Patel', 'DOCTOR', 'dr.aisha.patel@ubuntuclinic.ac.za', '0743456789', '09:00', '17:00');

INSERT INTO STAFF (department_id, first_name, last_name, role, email, contact_number, working_hours_start, working_hours_end)
VALUES (2, 'Lerato', 'Molefe', 'NURSE', 'nurse.lerato.molefe@ubuntuclinic.ac.za', '0754567890', '07:30', '15:30');

INSERT INTO STAFF (department_id, first_name, last_name, role, email, contact_number, working_hours_start, working_hours_end)
VALUES (2, 'Sipho', 'Khumalo', 'NURSE', 'nurse.sipho.khumalo@ubuntuclinic.ac.za', '0765678901', '10:00', '18:00');

INSERT INTO STAFF (department_id, first_name, last_name, role, email, contact_number, working_hours_start, working_hours_end)
VALUES (5, 'Nomsa', 'Ndlovu', 'ADMIN', 'admin.nomsa.ndlovu@ubuntuclinic.ac.za', '0776789012', '08:00', '16:00');

-- Assign department heads now that STAFF rows exist
-- IDENTITY generates: Mokoena=1, Dlamini=2, Patel=3, Molefe=4, Khumalo=5, Ndlovu=6
UPDATE DEPARTMENT SET head_staff_id = 1 WHERE department_name = 'Medical';
UPDATE DEPARTMENT SET head_staff_id = 4 WHERE department_name = 'Nursing';
UPDATE DEPARTMENT SET head_staff_id = 6 WHERE department_name = 'Administration';

-- =============================================================================
-- DOCTOR â€” 3 rows (only STAFF members with role = 'DOCTOR' get a DOCTOR row)
-- =============================================================================
INSERT INTO DOCTOR (staff_id, license_number, specialisation) VALUES (1, 'HPCSA-MP-10001', 'General Practice');
INSERT INTO DOCTOR (staff_id, license_number, specialisation) VALUES (2, 'HPCSA-MP-10002', 'Primary Care');
INSERT INTO DOCTOR (staff_id, license_number, specialisation) VALUES (3, 'HPCSA-MP-10003', 'Mental Health');

-- =============================================================================
-- PATIENT â€” 8 rows (realistic NWU student data)
-- =============================================================================
INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given)
VALUES ('10012345', 'Karabo',      'Mabena',   '10012345@mynwu.ac.za', '0781234567', DATE '2002-03-12', '12 Steve Biko Drive',     'Potchefstroom',  '2531', 1);

INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given)
VALUES ('10023456', 'Boitumelo',   'Maseko',   '10023456@mynwu.ac.za', '0782345678', DATE '2001-07-24', '45 Albert Luthuli Avenue', 'Mahikeng',       '2745', 1);

INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given)
VALUES ('10034567', 'Minenhle',    'Nkosi',    '10034567@mynwu.ac.za', '0783456789', DATE '2003-01-05', '8 Nelson Mandela Drive',   'Vanderbijlpark', '1900', 1);

INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given)
VALUES ('10045678', 'Tshegofatso', 'Radebe',   '10045678@mynwu.ac.za', '0784567890', DATE '2000-11-18', '21 Beyers Naude Avenue',   'Potchefstroom',  '2531', 1);

INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given)
VALUES ('10056789', 'Anathi',      'Mthembu',  '10056789@mynwu.ac.za', '0785678901', DATE '2002-09-02', '6 University Road',        'Mahikeng',       '2745', 1);

INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given)
VALUES ('10067890', 'Lehlohonolo', 'Sithole',  '10067890@mynwu.ac.za', '0786789012', DATE '2001-04-16', '33 Pitso Street',          'Mahikeng',       '2745', 0);

INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given)
VALUES ('10078901', 'Zanele',      'Dube',     '10078901@mynwu.ac.za', '0787890123', DATE '2003-06-28', '19 Freedom Square',        'Potchefstroom',  '2531', 1);

INSERT INTO PATIENT (student_number, first_name, last_name, email, contact_number, date_of_birth, street, city, postal_code, consent_given)
VALUES ('10089012', 'Sibusiso',    'Zwane',    '10089012@mynwu.ac.za', '0788901234', DATE '2000-12-03', '7 Tlokwe Avenue',          'Vanderbijlpark', '1900', 1);

-- =============================================================================
-- PATIENT_CONTACT â€” 8 rows (one next-of-kin per patient)
-- =============================================================================
INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship) VALUES (1, 'Grace Mabena',     '0821234567', 'Mother');
INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship) VALUES (2, 'Sibusiso Maseko',  '0822345678', 'Father');
INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship) VALUES (3, 'Nokuthula Nkosi',  '0823456789', 'Aunt');
INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship) VALUES (4, 'Refilwe Radebe',   '0824567890', 'Sister');
INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship) VALUES (5, 'Zanele Mthembu',   '0825678901', 'Guardian');
INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship) VALUES (6, 'Kgomotso Sithole', '0826789012', 'Mother');
INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship) VALUES (7, 'Mandla Dube',      '0827890123', 'Brother');
INSERT INTO PATIENT_CONTACT (patient_id, contact_name, phone_number, relationship) VALUES (8, 'Thandi Zwane',     '0828901234', 'Mother');

-- =============================================================================
-- USER_ACCOUNT â€” 12 rows (8 patients + 3 doctors + 1 admin)
-- =============================================================================
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('student_10012345', 'pbkdf2_sha256$600000$salt1$hash1',   1, NULL, 'PATIENT', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('student_10023456', 'pbkdf2_sha256$600000$salt2$hash2',   2, NULL, 'PATIENT', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('student_10034567', 'pbkdf2_sha256$600000$salt3$hash3',   3, NULL, 'PATIENT', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('student_10045678', 'pbkdf2_sha256$600000$salt4$hash4',   4, NULL, 'PATIENT', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('student_10056789', 'pbkdf2_sha256$600000$salt5$hash5',   5, NULL, 'PATIENT', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('student_10067890', 'pbkdf2_sha256$600000$salt6$hash6',   6, NULL, 'PATIENT', 'LOCKED');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('student_10078901', 'pbkdf2_sha256$600000$salt7$hash7',   7, NULL, 'PATIENT', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('student_10089012', 'pbkdf2_sha256$600000$salt8$hash8',   8, NULL, 'PATIENT', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('doctor_mokoena',   'pbkdf2_sha256$600000$salt9$hash9',   NULL, 1, 'DOCTOR', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('doctor_dlamini',   'pbkdf2_sha256$600000$salt10$hash10', NULL, 2, 'DOCTOR', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('doctor_patel',     'pbkdf2_sha256$600000$salt11$hash11', NULL, 3, 'DOCTOR', 'ACTIVE');
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('admin_ndlovu',     'pbkdf2_sha256$600000$salt12$hash12', NULL, 6, 'ADMIN',  'ACTIVE');

-- =============================================================================
-- TIMESLOT â€” 12 rows (mix of past, today-adjacent, and future slots)
-- Using TRUNC(SYSDATE) so dates stay relative when run on any day
-- =============================================================================
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) - 3, '09:00', '09:30', 0);   -- slot_id 1
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) - 3, '10:00', '10:30', 0);   -- slot_id 2
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) - 2, '09:00', '09:30', 0);   -- slot_id 3
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) - 1, '11:00', '11:30', 0);   -- slot_id 4
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) - 1, '14:00', '14:30', 0);   -- slot_id 5
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 1, '08:00', '08:30', 0);   -- slot_id 6
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 1, '09:00', '09:30', 1);   -- slot_id 7
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 1, '10:00', '10:30', 1);   -- slot_id 8
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 2, '08:30', '09:00', 1);   -- slot_id 9
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 2, '11:00', '11:30', 1);   -- slot_id 10
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 3, '09:00', '09:30', 1);   -- slot_id 11
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 7, '14:00', '14:30', 1);   -- slot_id 12

-- Today + extra windows so Book Appointment is not empty on common picks
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE), '09:00', '09:30', 1);
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE), '10:00', '10:30', 1);
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE), '11:00', '11:30', 1);
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE), '14:00', '14:30', 1);
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 1, '11:00', '11:30', 1);
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 1, '14:00', '14:30', 1);
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 2, '09:00', '09:30', 1);
INSERT INTO TIMESLOT (slot_date, start_time, end_time, is_available)
VALUES (TRUNC(SYSDATE) + 2, '14:00', '14:30', 1);

-- =============================================================================
-- APPOINTMENT â€” 8 rows (covers all status and booking_type values)
-- =============================================================================
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (1, 1, 1, 'COMPLETED',  'SICK',           'NORMAL', 'a1b2c3d4-0001-0001-0001-aabbccdd0001');
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (2, 2, 2, 'COMPLETED',  'FOLLOW_UP',      'NORMAL', 'a1b2c3d4-0002-0002-0002-aabbccdd0002');
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (3, 3, 3, 'COMPLETED',  'SICK',           'URGENT', 'a1b2c3d4-0003-0003-0003-aabbccdd0003');
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (4, 4, 1, 'NO_SHOW',    'SICK',           'NORMAL', 'a1b2c3d4-0004-0004-0004-aabbccdd0004');
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (5, 5, 2, 'CANCELLED',  'WALK_IN',        'NORMAL', 'a1b2c3d4-0005-0005-0005-aabbccdd0005');
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (6, 6, 3, 'CONFIRMED',  'SICK',           'URGENT', 'a1b2c3d4-0006-0006-0006-aabbccdd0006');
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (7, 7, 1, 'SCHEDULED',  'FOLLOW_UP',      'NORMAL', 'a1b2c3d4-0007-0007-0007-aabbccdd0007');
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (9, 8, 2, 'SCHEDULED',  'VIRTUAL_TRIAGE', 'NORMAL', 'a1b2c3d4-0008-0008-0008-aabbccdd0008');

-- karabo.mabena (patient_id=1): upcoming follow-up with Dr Mokoena (slot 8, tomorrow 10:00)
INSERT INTO APPOINTMENT (slot_id, patient_id, staff_id, status, booking_type, priority, qr_code_token)
VALUES (8, 1, 1, 'SCHEDULED', 'FOLLOW_UP', 'NORMAL', 'a1b2c3d4-karabo-upcoming-0001');

UPDATE TIMESLOT SET is_available = 0 WHERE slot_id = 8;

-- =============================================================================
-- QUEUE_ENTRY â€” 3 rows (one per completed appointment)
-- =============================================================================
INSERT INTO QUEUE_ENTRY (appointment_id, status, consult_start_time, consult_end_time, room_number)
VALUES (1, 'COMPLETED', '09:15', '09:45', 'Room 1');
INSERT INTO QUEUE_ENTRY (appointment_id, status, consult_start_time, consult_end_time, room_number)
VALUES (2, 'COMPLETED', '10:10', '10:40', 'Room 2');
INSERT INTO QUEUE_ENTRY (appointment_id, status, consult_start_time, consult_end_time, room_number)
VALUES (3, 'COMPLETED', '09:05', '09:50', 'Room 3');

-- =============================================================================
-- MEDICAL_RECORD â€” 3 rows (one per completed consultation)
-- =============================================================================
INSERT INTO MEDICAL_RECORD (appointment_id, patient_id, diagnosis, prescription, treatment_notes)
VALUES (1, 1,
    'Seasonal influenza',
    'Paracetamol 1g every 6 hours for 3 days. Maintain fluid intake.',
    'Rest for 48 hours. Return if fever persists beyond 72 hours.');

INSERT INTO MEDICAL_RECORD (appointment_id, patient_id, diagnosis, prescription, treatment_notes)
VALUES (2, 2,
    'Tension headache',
    'Ibuprofen 400mg as needed, maximum 3 times daily.',
    'Stress management discussed. Follow up if migraines recur.');

INSERT INTO MEDICAL_RECORD (appointment_id, patient_id, diagnosis, prescription, treatment_notes)
VALUES (3, 3,
    'Generalised anxiety disorder',
    'Referral to campus counselling centre issued.',
    'Breathing exercises demonstrated. Avoid caffeine. Weekly check-in scheduled.');

-- =============================================================================
-- NOTIFICATION â€” 8 rows (one per appointment, mix of channels and statuses)
-- =============================================================================
INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (1, NULL, 1, 'EMAIL', 'SENT',
    'Your appointment at Ubuntu Clinic on ' || TO_CHAR(TRUNC(SYSDATE) - 3, 'DD Mon YYYY') || ' at 09:00 has been completed.');
INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (2, NULL, 2, 'EMAIL', 'SENT',
    'Your appointment at Ubuntu Clinic on ' || TO_CHAR(TRUNC(SYSDATE) - 3, 'DD Mon YYYY') || ' at 10:00 has been completed.');
INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (3, NULL, 3, 'EMAIL', 'SENT',
    'Your appointment at Ubuntu Clinic on ' || TO_CHAR(TRUNC(SYSDATE) - 2, 'DD Mon YYYY') || ' at 09:00 has been completed.');
INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (4, NULL, 4, 'EMAIL', 'SENT',
    'Your appointment on ' || TO_CHAR(TRUNC(SYSDATE) - 1, 'DD Mon YYYY') || ' was marked as NO_SHOW. Please contact the clinic to rebook.');
INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (5, NULL, 5, 'EMAIL', 'SENT',
    'Your appointment on ' || TO_CHAR(TRUNC(SYSDATE) - 1, 'DD Mon YYYY') || ' has been cancelled. Please contact Ubuntu Clinic to rebook.');
INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (6, NULL, 6, 'EMAIL', 'PENDING',
    'Reminder: You have a CONFIRMED appointment at Ubuntu Clinic tomorrow. Please bring your student card.');
INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (7, NULL, 7, 'EMAIL', 'PENDING',
    'Reminder: Your appointment at Ubuntu Clinic is confirmed for ' || TO_CHAR(TRUNC(SYSDATE) + 1, 'DD Mon YYYY') || ' at 09:00.');
INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (8, NULL, 8, 'SMS', 'PENDING',
    'Ubuntu Clinic: Appt confirmed for ' || TO_CHAR(TRUNC(SYSDATE) + 2, 'DD Mon YYYY') || ' at 08:30. Reply CANCEL to cancel.');

INSERT INTO NOTIFICATION (patient_id, staff_id, appointment_id, channel, status, message)
VALUES (1, NULL, 9, 'EMAIL', 'PENDING',
    'Reminder: Your follow-up at Ubuntu Clinic is scheduled for '
    || TO_CHAR(TRUNC(SYSDATE) + 1, 'DD Mon YYYY') || ' at 10:00 with Dr Mokoena.');

-- =============================================================================
-- AUDIT_LOG â€” 10 rows (realistic action history by admin and doctors)
-- user_id references: 9=doctor_mokoena, 10=doctor_dlamini, 11=doctor_patel, 12=admin_ndlovu
-- =============================================================================
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (12, 'CREATE', 'PATIENT',       1, '192.168.1.10');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (12, 'CREATE', 'PATIENT',       2, '192.168.1.10');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (12, 'CREATE', 'PATIENT',       3, '192.168.1.10');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (9,  'CREATE', 'APPOINTMENT',   1, '10.0.0.5');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (10, 'CREATE', 'APPOINTMENT',   2, '10.0.0.6');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (11, 'CREATE', 'APPOINTMENT',   3, '10.0.0.7');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (9,  'UPDATE', 'APPOINTMENT',   1, '10.0.0.5');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (12, 'READ',   'MEDICAL_RECORD',1, '192.168.1.10');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (9,  'READ',   'MEDICAL_RECORD',1, '10.0.0.5');
INSERT INTO AUDIT_LOG (user_id, action, table_affected, record_affected_id, ip_address)
VALUES (12, 'UPDATE', 'USER_ACCOUNT',  6, '192.168.1.10');

COMMIT;

-- =============================================================================
-- Verification â€” expected row counts per table
-- =============================================================================
-- =============================================================================
-- USER_ACCOUNT seed rows (one per role — named accounts for easy testing)
-- Password for all: Clinic@123
-- Run backend/scripts/reset_seed_passwords.py after schema setup to set real
-- werkzeug-compatible password hashes (replaces the 'CHANGEME' placeholder).
-- =============================================================================

-- Patient account linked to patient_id=1 (Karabo Mabena, student 10012345, 10012345@mynwu.ac.za)
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('karabo.mabena', 'CHANGEME', 1, NULL, 'PATIENT', 'ACTIVE');

-- Doctor account linked to staff_id=1 (Dr. Naledi Mokoena)
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('dr.mokoena', 'CHANGEME', NULL, 1, 'DOCTOR', 'ACTIVE');

-- Nurse account linked to staff_id=4 (Lerato Molefe)
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('nurse.molefe', 'CHANGEME', NULL, 4, 'NURSE', 'ACTIVE');

-- Admin account linked to staff_id=6 (Nomsa Ndlovu)
INSERT INTO USER_ACCOUNT (username, password_hash, patient_id, staff_id, role, status)
VALUES ('admin.ndlovu', 'CHANGEME', NULL, 6, 'ADMIN', 'ACTIVE');

COMMIT;

-- =============================================================================
-- Verification — expected row counts per table
-- =============================================================================
SELECT 'DEPARTMENT'     AS table_name, COUNT(*) AS row_count FROM DEPARTMENT     UNION ALL
SELECT 'STAFF',                        COUNT(*)              FROM STAFF           UNION ALL
SELECT 'DOCTOR',                       COUNT(*)              FROM DOCTOR          UNION ALL
SELECT 'PATIENT',                      COUNT(*)              FROM PATIENT         UNION ALL
SELECT 'PATIENT_CONTACT',              COUNT(*)              FROM PATIENT_CONTACT UNION ALL
SELECT 'USER_ACCOUNT',                 COUNT(*)              FROM USER_ACCOUNT    UNION ALL
SELECT 'TIMESLOT',                     COUNT(*)              FROM TIMESLOT        UNION ALL
SELECT 'APPOINTMENT',                  COUNT(*)              FROM APPOINTMENT     UNION ALL  -- expect 9 after karabo upcoming row
SELECT 'QUEUE_ENTRY',                  COUNT(*)              FROM QUEUE_ENTRY     UNION ALL
SELECT 'MEDICAL_RECORD',              COUNT(*)              FROM MEDICAL_RECORD  UNION ALL
SELECT 'NOTIFICATION',                COUNT(*)              FROM NOTIFICATION    UNION ALL
SELECT 'AUDIT_LOG',                   COUNT(*)              FROM AUDIT_LOG
ORDER BY 1;
