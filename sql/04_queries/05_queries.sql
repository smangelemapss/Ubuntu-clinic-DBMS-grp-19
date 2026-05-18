-- =============================================================================
-- UBUNTU CAMPUS CLINIC â€” APPOINTMENT SYSTEM
-- Group 19 | CMPG 311 | DBMS Module | Physical Design
-- File: 05_queries.sql
-- Purpose: All 11 rubric query categories â€” Q1 through Q11
-- Database: Oracle SQL Developer (XE 21c)
-- HOW TO RUN: Highlight ONE query block â†’ press F9 (Run Statement)
--             Do NOT use F5 for this file â€” &substitution variables need F9
-- =============================================================================


/* ============================================================================
   Q1 â€” BUSINESS INFORMATION QUERIES  (10 marks)
   Five queries that answer real operational questions for the Ubuntu Clinic
   ============================================================================ */

-- Q1.1  Full appointment schedule with patient, doctor, timeslot and priority
SELECT p.student_number,
       p.first_name || ' ' || p.last_name       AS patient_name,
       s.first_name || ' ' || s.last_name       AS doctor_name,
       d.specialisation,
       t.slot_date,
       t.start_time,
       t.end_time,
       a.status                                  AS appointment_status,
       a.booking_type,
       a.priority
FROM   APPOINTMENT  a
JOIN   PATIENT      p    ON p.patient_id   = a.patient_id
JOIN   STAFF        s    ON s.staff_id     = a.staff_id
JOIN   DOCTOR       d    ON d.staff_id     = s.staff_id
JOIN   TIMESLOT     t    ON t.slot_id      = a.slot_id
ORDER BY t.slot_date, t.start_time;

-- Q1.2  Patients who have had COMPLETED appointments with visit count
SELECT p.patient_id,
       p.student_number,
       p.first_name || ' ' || p.last_name       AS patient_name,
       p.email,
       COUNT(a.appointment_id)                   AS completed_visits
FROM   PATIENT      p
JOIN   APPOINTMENT  a ON a.patient_id = p.patient_id
WHERE  a.status = 'COMPLETED'
GROUP BY p.patient_id, p.student_number, p.first_name, p.last_name, p.email
ORDER BY completed_visits DESC;

-- Q1.3  Upcoming SCHEDULED or CONFIRMED appointments in the next 7 days
SELECT p.student_number,
       p.first_name || ' ' || p.last_name       AS patient_name,
       p.contact_number,
       s.first_name || ' ' || s.last_name       AS assigned_doctor,
       t.slot_date                               AS appointment_date,
       t.start_time,
       a.booking_type,
       a.priority
FROM   APPOINTMENT  a
JOIN   PATIENT      p ON p.patient_id = a.patient_id
JOIN   STAFF        s ON s.staff_id   = a.staff_id
JOIN   TIMESLOT     t ON t.slot_id    = a.slot_id
WHERE  a.status IN ('SCHEDULED', 'CONFIRMED')
  AND  t.slot_date BETWEEN TRUNC(SYSDATE) AND TRUNC(SYSDATE) + 7
ORDER BY t.slot_date, t.start_time;

-- Q1.4  Doctor workload report: appointment count per doctor per status
SELECT s.first_name || ' ' || s.last_name       AS doctor_name,
       d.specialisation,
       dept.department_name,
       a.status,
       COUNT(a.appointment_id)                   AS appointment_count
FROM   STAFF        s
JOIN   DOCTOR       d    ON d.staff_id         = s.staff_id
JOIN   DEPARTMENT   dept ON dept.department_id  = s.department_id
JOIN   APPOINTMENT  a    ON a.staff_id         = s.staff_id
GROUP BY s.first_name, s.last_name, d.specialisation, dept.department_name, a.status
ORDER BY doctor_name, a.status;

-- Q1.5  Patients with emergency contacts on file and their latest diagnosis
SELECT p.student_number,
       p.first_name || ' ' || p.last_name       AS patient_name,
       pc.contact_name                           AS emergency_contact,
       pc.phone_number                           AS emergency_phone,
       pc.relationship,
       mr.diagnosis,
       mr.created_at                             AS record_date
FROM   PATIENT           p
JOIN   PATIENT_CONTACT   pc ON pc.patient_id    = p.patient_id
LEFT JOIN MEDICAL_RECORD mr ON mr.patient_id    = p.patient_id
ORDER BY p.student_number, mr.created_at DESC;


/* ============================================================================
   Q2 â€” QUERY LIMITATIONS: ROWS AND COLUMNS  (4 marks)
   Demonstrate FETCH FIRST, ROWNUM, column projection, and pagination
   ============================================================================ */

-- Q2.1  Top 3 most recent appointments â€” FETCH FIRST (Oracle 12c+ standard syntax)
SELECT appointment_id,
       patient_id,
       staff_id,
       status,
       booking_type
FROM   APPOINTMENT
ORDER BY appointment_id DESC
FETCH FIRST 3 ROWS ONLY;

-- Q2.2  First 5 patients â€” ROWNUM (classic Oracle pre-12c compatible syntax)
SELECT student_number,
       first_name,
       last_name,
       email
FROM (
    SELECT student_number, first_name, last_name, email
    FROM   PATIENT
    ORDER BY student_number
) top_patients
WHERE  ROWNUM <= 5;

-- Q2.3  Column projection: only 4 columns from STAFF (no sensitive data exposed)
SELECT first_name,
       last_name,
       role,
       email
FROM   STAFF;

-- Q2.4  Pagination â€” rows 4 to 6 using inline ROWNUM view
SELECT appointment_id,
       patient_id,
       status,
       booking_type,
       priority
FROM (
    SELECT a.*, ROWNUM AS rn
    FROM   APPOINTMENT a
    ORDER  BY appointment_id
) appt_page
WHERE  rn BETWEEN 4 AND 6;


/* ============================================================================
   Q3 â€” SORTING OPERATIONS  (4 marks)
   ============================================================================ */

-- Q3.1  Patients sorted ascending by last_name then first_name (multi-column ASC)
SELECT student_number,
       first_name,
       last_name,
       city,
       date_of_birth
FROM   PATIENT
ORDER BY last_name ASC, first_name ASC;

-- Q3.2  Most recent audit log entries first (DESC on timestamp)
SELECT audit_log_id,
       user_id,
       action,
       table_affected,
       log_timestamp
FROM   AUDIT_LOG
ORDER BY log_timestamp DESC;

-- Q3.3  Timeslots sorted by date ASC then start_time ASC (multi-column sort)
SELECT slot_id,
       slot_date,
       start_time,
       end_time,
       is_available
FROM   TIMESLOT
ORDER BY slot_date ASC, start_time ASC;

-- Q3.4  Appointments sorted priority DESC (URGENT first), booking_type ASC
SELECT appointment_id,
       patient_id,
       staff_id,
       priority,
       booking_type,
       status
FROM   APPOINTMENT
ORDER BY priority DESC, booking_type ASC;


/* ============================================================================
   Q4 â€” LIKE, AND, OR OPERATORS  (4 marks)
   ============================================================================ */

-- Q4.1  LIKE: patients whose email is an NWU student address (@mynwu.ac.za)
SELECT student_number,
       first_name || ' ' || last_name    AS patient_name,
       email
FROM   PATIENT
WHERE  email LIKE '%@mynwu.ac.za';

-- Q4.2  AND: staff who are DOCTORS assigned to department 1
SELECT staff_id,
       first_name || ' ' || last_name    AS staff_name,
       role,
       email
FROM   STAFF
WHERE  role = 'DOCTOR'
  AND  department_id = 1;

-- Q4.3  OR: appointments that are CANCELLED or NO_SHOW
SELECT appointment_id,
       patient_id,
       staff_id,
       status,
       booking_type
FROM   APPOINTMENT
WHERE  status = 'CANCELLED'
   OR  status = 'NO_SHOW';

-- Q4.4  LIKE + AND: PENDING notifications sent via EMAIL channel
SELECT notification_id,
       patient_id,
       appointment_id,
       channel,
       status,
       SUBSTR(message, 1, 60) || '...'  AS message_preview
FROM   NOTIFICATION
WHERE  status  = 'PENDING'
  AND  channel LIKE 'EMAIL%';

-- Q4.5  OR + AND combined: consenting patients from Potchefstroom OR Mahikeng
SELECT student_number,
       first_name || ' ' || last_name    AS patient_name,
       city,
       consent_given
FROM   PATIENT
WHERE  (city = 'Potchefstroom' OR city = 'Mahikeng')
  AND  consent_given = 1;


/* ============================================================================
   Q5 â€” VARIABLES AND CHARACTER FUNCTIONS  (4 marks)
   ============================================================================ */

-- Q5.1  UPPER, LOWER, INITCAP: normalise patient name casing
SELECT student_number,
       UPPER(first_name)                              AS first_name_upper,
       LOWER(last_name)                               AS last_name_lower,
       INITCAP(first_name || ' ' || last_name)        AS full_name_proper
FROM   PATIENT;

-- Q5.2  SUBSTR, LENGTH, INSTR: inspect and extract parts of string fields
SELECT student_number,
       SUBSTR(student_number, 1, 4)                   AS year_prefix,
       LENGTH(student_number)                          AS id_length,
       SUBSTR(email, 1, INSTR(email, '@') - 1)         AS email_local_part
FROM   PATIENT;

-- Q5.3  CONCAT and TRIM: build formatted contact display strings
SELECT CONCAT(CONCAT(first_name, ' '), last_name)      AS full_name,
       TRIM(contact_number)                             AS phone_trimmed,
       TRIM(' ' FROM city)                              AS city_clean
FROM   PATIENT;

-- Q5.4  LPAD and RPAD: format queue position numbers for display board
SELECT queue_entry_id,
       LPAD(TO_CHAR(queue_entry_id), 4, '0')           AS ticket_number,
       RPAD(status, 20, '.')                            AS status_padded,
       room_number
FROM   QUEUE_ENTRY;

-- Q5.5  REPLACE and INSTR: partial masking of contact number (data privacy display)
SELECT patient_id,
       contact_number,
       REPLACE(contact_number,
               SUBSTR(contact_number, 4, 4), '****')   AS masked_number,
       INSTR(email, '@')                                AS at_sign_position
FROM   PATIENT;

-- Q5.6  Substitution variable: search a patient by student number
--       SQL Developer will display an input dialog when this query is run
SELECT patient_id,
       student_number,
       first_name || ' ' || last_name    AS patient_name,
       email,
       city
FROM   PATIENT
WHERE  student_number = '&enter_student_number';


/* ============================================================================
   Q6 â€” ROUNDING AND TRUNCATION  (4 marks)
   ============================================================================ */

-- Q6.1  ROUND: patient age rounded to nearest whole year and to 1 decimal
SELECT student_number,
       first_name || ' ' || last_name                           AS patient_name,
       date_of_birth,
       ROUND(MONTHS_BETWEEN(SYSDATE, date_of_birth) / 12, 0)   AS age_years_rounded,
       ROUND(MONTHS_BETWEEN(SYSDATE, date_of_birth), 1)         AS months_old_rounded
FROM   PATIENT
ORDER BY date_of_birth;

-- Q6.2  TRUNC: truncate fractional age to integer (no rounding) + truncate to month
SELECT student_number,
       first_name || ' ' || last_name                           AS patient_name,
       TRUNC(MONTHS_BETWEEN(SYSDATE, date_of_birth) / 12)      AS age_years_truncated,
       TRUNC(SYSDATE, 'MM')                                     AS first_of_current_month
FROM   PATIENT;

-- Q6.3  CEIL: ceiling on months of system operation
SELECT staff_id,
       first_name || ' ' || last_name                           AS staff_name,
       role,
       CEIL(MONTHS_BETWEEN(SYSDATE, DATE '2024-01-15'))         AS months_service_ceil
FROM   STAFF;

-- Q6.4  FLOOR: floor division â€” full complete years since a patient registered
SELECT patient_id,
       student_number,
       first_name || ' ' || last_name                           AS patient_name,
       FLOOR(MONTHS_BETWEEN(SYSDATE, registration_date) / 12)  AS full_years_registered,
       ROUND(MONTHS_BETWEEN(SYSDATE, registration_date), 2)     AS exact_months_registered
FROM   PATIENT
ORDER BY registration_date;


/* ============================================================================
   Q7 â€” DATE FUNCTIONS  (4 marks)
   ============================================================================ */

-- Q7.1  SYSDATE and TRUNC: current server datetime at different granularities
SELECT SYSDATE                            AS current_datetime,
       TRUNC(SYSDATE)                     AS today_date_only,
       TRUNC(SYSDATE, 'MM')              AS first_of_this_month,
       TRUNC(SYSDATE, 'YYYY')            AS first_of_this_year
FROM   DUAL;

-- Q7.2  TO_CHAR: format appointment slot dates for human-readable reporting
SELECT a.appointment_id,
       t.slot_date,
       TO_CHAR(t.slot_date, 'DD Month YYYY')     AS formatted_date,
       TO_CHAR(t.slot_date, 'Day')               AS day_of_week,
       TO_CHAR(t.slot_date, 'WW')                AS week_number,
       t.start_time
FROM   APPOINTMENT  a
JOIN   TIMESLOT     t ON t.slot_id = a.slot_id
ORDER BY t.slot_date;

-- Q7.3  TO_DATE: parse a string literal and filter patients born after a date
SELECT patient_id,
       student_number,
       first_name || ' ' || last_name    AS patient_name,
       date_of_birth,
       TO_DATE('2000-01-01', 'YYYY-MM-DD') AS cutoff_date
FROM   PATIENT
WHERE  date_of_birth > TO_DATE('2000-01-01', 'YYYY-MM-DD')
ORDER BY date_of_birth;

-- Q7.4  MONTHS_BETWEEN and ADD_MONTHS: patient age + 6-month follow-up projection
SELECT p.student_number,
       p.first_name || ' ' || p.last_name             AS patient_name,
       p.date_of_birth,
       ROUND(MONTHS_BETWEEN(SYSDATE, p.date_of_birth) / 12, 1) AS age_years,
       t.slot_date                                     AS consultation_date,
       ADD_MONTHS(t.slot_date, 6)                      AS six_month_followup_due
FROM   PATIENT      p
JOIN   APPOINTMENT  a ON a.patient_id = p.patient_id
JOIN   TIMESLOT     t ON t.slot_id    = a.slot_id
WHERE  a.status = 'COMPLETED';

-- Q7.5  LAST_DAY and NEXT_DAY: scheduling boundary helpers
SELECT SYSDATE                                AS today,
       LAST_DAY(SYSDATE)                     AS last_day_of_month,
       NEXT_DAY(SYSDATE, 'MONDAY')           AS next_monday,
       NEXT_DAY(SYSDATE, 'FRIDAY')           AS next_friday,
       ADD_MONTHS(LAST_DAY(SYSDATE), 1) + 1  AS first_of_next_month
FROM   DUAL;

-- Q7.6  Date arithmetic: days until each upcoming appointment
SELECT p.student_number,
       p.first_name || ' ' || p.last_name         AS patient_name,
       t.slot_date,
       t.slot_date - TRUNC(SYSDATE)               AS days_until_appointment,
       TO_CHAR(t.slot_date, 'Dy DD-Mon-YYYY')     AS formatted_appointment_date
FROM   APPOINTMENT  a
JOIN   PATIENT      p ON p.patient_id = a.patient_id
JOIN   TIMESLOT     t ON t.slot_id    = a.slot_id
WHERE  a.status IN ('SCHEDULED', 'CONFIRMED')
  AND  t.slot_date >= TRUNC(SYSDATE)
ORDER BY t.slot_date;


/* ============================================================================
   Q8 â€” AGGREGATE FUNCTIONS  (4 marks)
   ============================================================================ */

-- Q8.1  COUNT with conditional aggregation: consent breakdown across all patients
SELECT COUNT(*)                                           AS total_patients,
       COUNT(CASE WHEN consent_given = 1 THEN 1 END)     AS patients_consented,
       COUNT(CASE WHEN consent_given = 0 THEN 1 END)     AS patients_not_consented
FROM   PATIENT;

-- Q8.2  AVG, MIN, MAX: patient age statistics
SELECT ROUND(AVG(MONTHS_BETWEEN(SYSDATE, date_of_birth) / 12), 1) AS avg_age_years,
       ROUND(MIN(MONTHS_BETWEEN(SYSDATE, date_of_birth) / 12), 1) AS youngest_years,
       ROUND(MAX(MONTHS_BETWEEN(SYSDATE, date_of_birth) / 12), 1) AS oldest_years
FROM   PATIENT;

-- Q8.3  MAX, MIN, COUNT, SUM on TIMESLOT: availability summary
SELECT MIN(slot_date)                                             AS earliest_slot,
       MAX(slot_date)                                             AS latest_slot,
       COUNT(slot_id)                                             AS total_slots,
       SUM(CASE WHEN is_available = 1 THEN 1 ELSE 0 END)         AS slots_available,
       SUM(CASE WHEN is_available = 0 THEN 1 ELSE 0 END)         AS slots_booked
FROM   TIMESLOT;

-- Q8.4  COUNT DISTINCT: unique patients booked and unique doctors assigned
SELECT COUNT(DISTINCT patient_id)    AS unique_patients_with_bookings,
       COUNT(appointment_id)         AS total_appointments,
       COUNT(DISTINCT staff_id)      AS unique_doctors_assigned
FROM   APPOINTMENT;

-- Q8.5  Aggregate on NOTIFICATION: delivery statistics per channel
SELECT channel,
       COUNT(*)                                              AS total_notifications,
       COUNT(CASE WHEN status = 'SENT'    THEN 1 END)       AS delivered,
       COUNT(CASE WHEN status = 'PENDING' THEN 1 END)       AS pending,
       COUNT(CASE WHEN status = 'FAILED'  THEN 1 END)       AS failed
FROM   NOTIFICATION
GROUP BY channel;

-- Q8.6  Audit log: occurrence count and time range per action type
SELECT action,
       COUNT(*)              AS occurrences,
       MIN(log_timestamp)    AS first_occurrence,
       MAX(log_timestamp)    AS latest_occurrence
FROM   AUDIT_LOG
GROUP BY action
ORDER BY occurrences DESC;


/* ============================================================================
   Q9 â€” GROUP BY AND HAVING CLAUSES  (4 marks)
   ============================================================================ */

-- Q9.1  GROUP BY single column: appointment count by status
SELECT status,
       COUNT(*) AS total_appointments
FROM   APPOINTMENT
GROUP BY status
ORDER BY total_appointments DESC;

-- Q9.2  HAVING: departments with MORE than 1 staff member
SELECT d.department_name,
       COUNT(s.staff_id)                                       AS staff_count,
       LISTAGG(s.role, ', ') WITHIN GROUP (ORDER BY s.role)   AS roles_present
FROM   DEPARTMENT   d
JOIN   STAFF        s ON s.department_id = d.department_id
GROUP BY d.department_name
HAVING COUNT(s.staff_id) > 1
ORDER BY staff_count DESC;

-- Q9.3  Multi-column GROUP BY: appointment count per doctor per booking type
SELECT s.first_name || ' ' || s.last_name    AS doctor_name,
       a.booking_type,
       COUNT(a.appointment_id)               AS appointment_count
FROM   APPOINTMENT  a
JOIN   STAFF        s ON s.staff_id = a.staff_id
GROUP BY s.first_name, s.last_name, a.booking_type
ORDER BY doctor_name, appointment_count DESC;

-- Q9.4  GROUP BY city with HAVING: cities where more than 1 appointment was made
SELECT p.city,
       COUNT(DISTINCT p.patient_id)     AS patient_count,
       COUNT(a.appointment_id)          AS total_appointments
FROM   PATIENT      p
LEFT JOIN APPOINTMENT a ON a.patient_id = p.patient_id
GROUP BY p.city
HAVING COUNT(a.appointment_id) > 1
ORDER BY total_appointments DESC;

-- Q9.5  Multi-column GROUP BY with HAVING on NOTIFICATION
SELECT n.patient_id,
       p.first_name || ' ' || p.last_name    AS patient_name,
       n.channel,
       COUNT(*)                               AS notification_count
FROM   NOTIFICATION n
JOIN   PATIENT      p ON p.patient_id = n.patient_id
GROUP BY n.patient_id, p.first_name, p.last_name, n.channel
HAVING COUNT(*) >= 1
ORDER BY notification_count DESC;


/* ============================================================================
   Q10 â€” JOINS  (5 marks)
   ============================================================================ */

-- Q10.1  INNER JOIN (2 tables): patients and their appointments
SELECT p.student_number,
       p.first_name || ' ' || p.last_name    AS patient_name,
       a.appointment_id,
       a.status,
       a.booking_type
FROM   PATIENT      p
INNER JOIN APPOINTMENT a ON a.patient_id = p.patient_id;

-- Q10.2  LEFT JOIN: ALL patients, including those who have not yet booked
SELECT p.student_number,
       p.first_name || ' ' || p.last_name    AS patient_name,
       p.city,
       a.appointment_id,
       a.status
FROM   PATIENT      p
LEFT JOIN APPOINTMENT a ON a.patient_id = p.patient_id
ORDER BY p.student_number;

-- Q10.3  3-table INNER JOIN: appointments with full patient and timeslot detail
SELECT a.appointment_id,
       p.student_number,
       p.first_name || ' ' || p.last_name    AS patient_name,
       s.first_name || ' ' || s.last_name    AS doctor_name,
       t.slot_date,
       t.start_time,
       a.status
FROM   APPOINTMENT  a
JOIN   PATIENT      p ON p.patient_id = a.patient_id
JOIN   TIMESLOT     t ON t.slot_id    = a.slot_id
JOIN   STAFF        s ON s.staff_id   = a.staff_id;

-- Q10.4  5-table JOIN: complete clinical record â€” patient, doctor, slot, queue, diagnosis
SELECT p.student_number,
       p.first_name || ' ' || p.last_name    AS patient_name,
       s.first_name || ' ' || s.last_name    AS doctor_name,
       t.slot_date,
       q.status                               AS queue_status,
       q.room_number,
       mr.diagnosis,
       mr.prescription
FROM   APPOINTMENT     a
JOIN   PATIENT         p   ON p.patient_id      = a.patient_id
JOIN   TIMESLOT        t   ON t.slot_id         = a.slot_id
JOIN   STAFF           s   ON s.staff_id        = a.staff_id
JOIN   QUEUE_ENTRY     q   ON q.appointment_id  = a.appointment_id
JOIN   MEDICAL_RECORD  mr  ON mr.appointment_id = a.appointment_id;

-- Q10.5  LEFT JOIN + GROUP BY: all doctors with department and appointment totals
SELECT s.first_name || ' ' || s.last_name    AS doctor_name,
       d.specialisation,
       dept.department_name,
       COUNT(a.appointment_id)               AS total_appointments
FROM   STAFF        s
JOIN   DOCTOR       d    ON d.staff_id         = s.staff_id
LEFT JOIN DEPARTMENT dept ON dept.department_id  = s.department_id
LEFT JOIN APPOINTMENT a   ON a.staff_id         = s.staff_id
GROUP BY s.first_name, s.last_name, d.specialisation, dept.department_name
ORDER BY total_appointments DESC;

-- Q10.6  SELF JOIN on PATIENT: find pairs of patients who share the same city
SELECT p1.first_name || ' ' || p1.last_name    AS patient_a,
       p2.first_name || ' ' || p2.last_name    AS patient_b,
       p1.city                                  AS shared_city
FROM   PATIENT  p1
JOIN   PATIENT  p2 ON  p1.city       = p2.city
                   AND p1.patient_id < p2.patient_id
ORDER BY p1.city, patient_a;


/* ============================================================================
   Q11 â€” SUB-QUERIES  (5 marks)
   ============================================================================ */

-- Q11.1  IN sub-query: patients who have at least one appointment on record
SELECT student_number,
       first_name || ' ' || last_name    AS patient_name,
       email,
       city
FROM   PATIENT
WHERE  patient_id IN (
    SELECT DISTINCT patient_id
    FROM   APPOINTMENT
)
ORDER BY student_number;

-- Q11.2  NOT IN sub-query: patients who have NEVER had a COMPLETED appointment
SELECT student_number,
       first_name || ' ' || last_name    AS patient_name,
       email
FROM   PATIENT
WHERE  patient_id NOT IN (
    SELECT DISTINCT patient_id
    FROM   APPOINTMENT
    WHERE  status     = 'COMPLETED'
      AND  patient_id IS NOT NULL
);

-- Q11.3  Scalar sub-query in SELECT: each appointment + total bookings for that doctor
SELECT a.appointment_id,
       a.patient_id,
       a.staff_id,
       a.status,
       (SELECT COUNT(*)
        FROM   APPOINTMENT a2
        WHERE  a2.staff_id = a.staff_id)   AS total_appts_for_this_doctor
FROM   APPOINTMENT a
ORDER BY a.staff_id, a.appointment_id;

-- Q11.4  Correlated sub-query in WHERE: patients older than the clinic average age
SELECT patient_id,
       student_number,
       first_name || ' ' || last_name                                AS patient_name,
       ROUND(MONTHS_BETWEEN(SYSDATE, date_of_birth)/12, 1)          AS age_years
FROM   PATIENT p
WHERE  MONTHS_BETWEEN(SYSDATE, date_of_birth) > (
    SELECT AVG(MONTHS_BETWEEN(SYSDATE, date_of_birth))
    FROM   PATIENT
)
ORDER BY age_years DESC;

-- Q11.5  EXISTS sub-query: doctors who have at least one COMPLETED appointment
SELECT s.staff_id,
       s.first_name || ' ' || s.last_name    AS doctor_name,
       d.specialisation
FROM   STAFF    s
JOIN   DOCTOR   d ON d.staff_id = s.staff_id
WHERE  EXISTS (
    SELECT 1
    FROM   APPOINTMENT a
    WHERE  a.staff_id = s.staff_id
      AND  a.status   = 'COMPLETED'
)
ORDER BY doctor_name;

-- Q11.6  Inline view + RANK() window function: rank doctors by total appointment load
SELECT doctor_name,
       specialisation,
       appointment_count,
       RANK() OVER (ORDER BY appointment_count DESC)   AS workload_rank
FROM (
    SELECT s.first_name || ' ' || s.last_name    AS doctor_name,
           d.specialisation,
           COUNT(a.appointment_id)               AS appointment_count
    FROM   STAFF        s
    JOIN   DOCTOR       d ON d.staff_id = s.staff_id
    LEFT JOIN APPOINTMENT a ON a.staff_id = s.staff_id
    GROUP BY s.first_name, s.last_name, d.specialisation
) doctor_workload
ORDER BY workload_rank;
