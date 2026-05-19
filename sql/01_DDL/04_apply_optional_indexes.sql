-- =============================================================================
-- Apply performance indexes added after initial deployment (idempotent).
-- Safe to run on an existing schema — skips indexes that already exist.
-- Run in SQL Developer with F5 after 01_create_tables.sql is in place.
-- =============================================================================

DECLARE
    PROCEDURE create_index_if_missing(p_name VARCHAR2, p_sql VARCHAR2) IS
    BEGIN
        EXECUTE IMMEDIATE p_sql;
        DBMS_OUTPUT.PUT_LINE('Created ' || p_name);
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLCODE = -955 THEN
                DBMS_OUTPUT.PUT_LINE('Skipped ' || p_name || ' (already exists)');
            ELSE
                RAISE;
            END IF;
    END;
BEGIN
    create_index_if_missing(
        'IDX_NOTIF_PATIENT',
        'CREATE INDEX idx_notif_patient ON NOTIFICATION (patient_id)'
    );
    create_index_if_missing(
        'IDX_NOTIF_STAFF',
        'CREATE INDEX idx_notif_staff ON NOTIFICATION (staff_id)'
    );
    create_index_if_missing(
        'IDX_USER_PATIENT',
        'CREATE INDEX idx_user_patient ON USER_ACCOUNT (patient_id)'
    );
    create_index_if_missing(
        'IDX_USER_STAFF',
        'CREATE INDEX idx_user_staff ON USER_ACCOUNT (staff_id)'
    );
END;
/

SELECT index_name, table_name
FROM   user_indexes
WHERE  index_name IN (
           'IDX_NOTIF_PATIENT', 'IDX_NOTIF_STAFF',
           'IDX_USER_PATIENT', 'IDX_USER_STAFF'
       )
ORDER BY index_name;
