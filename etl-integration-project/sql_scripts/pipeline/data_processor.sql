-- ==============================================
-- PACKAGE SPECIFICATION: DATA_PROCESSOR
-- ==============================================
CREATE OR REPLACE PACKAGE data_processor AS
    PROCEDURE process_timesheet;
    PROCEDURE process_training_attendance;
    PROCEDURE process_absences;
    PROCEDURE process_matrix;

    PROCEDURE run_data_processing;
END data_processor;
/

-- ==============================================
-- PACKAGE BODY: DATA_PROCESSOR
-- ==============================================
CREATE OR REPLACE PACKAGE BODY data_processor AS
    -------------------------------------------------
    --process_timesheet
    -- stg_timesheet --> tgt_fact_employee_activity
    --employee_id din staging → dim_employee
    --project_id → dim_project
    --entry_date → dim_date
    PROCEDURE process_timesheet IS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting timesheet processing...');

        INSERT INTO tgt_fact_employee_activity (
            date_id, employee_id, project_id,
            training_id, absence_type_id,
            hours, activity_type, activity_description
        )
        SELECT
            d.date_id,
            e.employee_id,
            p.project_id,
            NULL,
            NULL,
            t.hours_worked,
            'work',
            'project work'
        FROM stg_timesheet t
        JOIN tgt_dim_project p ON t.project_id = p.project_id
        JOIN tgt_dim_date d ON t.entry_date = d.full_date
        JOIN tgt_dim_employee e
            ON t.employee_id = e.original_id
            AND d.full_date BETWEEN e.valid_from AND NVL(e.valid_to, TIMESTAMP '9999-12-31 23:59:59.999999999')
        WHERE t.process_status = 'PENDING' OR t.process_status = 'DIM-PROCESSED';

        DBMS_OUTPUT.PUT_LINE('Finished timesheet processing ' || SQL%ROWCOUNT || ' records processed.');

        UPDATE stg_timesheet
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'PROCESSED'
        WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED';
    END process_timesheet;
 
    -------------------------------------------------
    --process_training_attendance
    -- training_name --> dim_training
    -- employee_email --> dim_employee
    PROCEDURE process_training_attendance IS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting training attendance processing...');

        INSERT INTO tgt_fact_employee_activity (
            date_id, employee_id, project_id,
        training_id, absence_type_id,
        hours, activity_type, activity_description
        )
        SELECT 
            dim_date.date_id,
            dim_employee.employee_id,
            NULL,
            dim_training.training_id,
            NULL,
            ROUND((TO_DATE(attendace.last_leave, 'MM/DD/YY, HH:MI:SS PM') - TO_DATE(attendace.first_join, 'MM/DD/YY, HH:MI:SS PM')) * 24, 2),
            'training',
            'training attendance'
        FROM STG_TRAINING_ATTENDANCE attendace
        JOIN tgt_dim_training dim_training ON attendace.training_name = dim_training.training_name
        JOIN tgt_dim_date dim_date ON TRUNC(TO_DATE(attendace.first_join, 'MM/DD/YY, HH:MI:SS PM')) = dim_date.full_date
        JOIN tgt_dim_employee dim_employee 
            ON attendace.email = dim_employee.employee_email
            AND dim_date.full_date BETWEEN dim_employee.valid_from AND NVL(dim_employee.valid_to, TIMESTAMP '9999-12-31 23:59:59.999999999')
        WHERE attendace.process_status = 'PENDING' OR attendace.process_status = 'DIM-PROCESSED';
        
        DBMS_OUTPUT.PUT_LINE('Finished training attendance processing ' || SQL%ROWCOUNT || ' records processed.');

        UPDATE stg_training_attendance
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'PROCESSED'
        WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED';
    END process_training_attendance;
 
    -------------------------------------------------
    --process_absences
    PROCEDURE process_absences IS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting absence processing...');

        INSERT INTO tgt_fact_employee_activity (
            date_id, employee_id, project_id,
            training_id, absence_type_id,
            hours, activity_type, activity_description
            )
        SELECT
            dim_date.date_id,
            dim_emp.employee_id,
            NULL,
            NULL,
            dim_abs.absence_type_id,
            8,
            'absence',
            'absence - ' || dim_abs.absence_type_name
        FROM (
        SELECT
            employee_id,
            TRUNC(absences.start_date + LEVEL - 1) AS absence_date,
            absences.absence_type
            FROM stg_absences absences
            WHERE absences.process_status = 'PENDING' OR absences.process_status = 'DIM-PROCESSED'
            CONNECT BY LEVEL <= (TRUNC(absences.end_date) - TRUNC(absences.start_date)) + 1  --genereaza câte o zi per înregistrare (interval)
            AND PRIOR absences.absence_id = absences.absence_id
            AND PRIOR DBMS_RANDOM.VALUE IS NOT NULL
        ) absence_exp
        JOIN tgt_dim_absence_type dim_abs ON absence_exp.absence_type = dim_abs.absence_type_name
        JOIN tgt_dim_date dim_date ON absence_exp.absence_date = dim_date.full_date
        JOIN tgt_dim_employee dim_emp
            ON absence_exp.employee_id = dim_emp.original_id
            AND dim_date.full_date BETWEEN dim_emp.valid_from AND NVL(dim_emp.valid_to, TIMESTAMP '9999-12-31 23:59:59.999999999');

        DBMS_OUTPUT.PUT_LINE('Finished absence processing ' || SQL%ROWCOUNT || ' records processed.');

        UPDATE stg_absences
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'PROCESSED'
        WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED';
    END process_absences;
 
    -------------------------------------------------
    --process_matrix
    --Unpivotarea monday → friday,absence_date
    PROCEDURE process_matrix IS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting matrix processing...');

        INSERT INTO tgt_fact_employee_activity (
            date_id, employee_id, project_id,
            training_id, absence_type_id,
            hours, activity_type, activity_description
        )
        WITH normalized_matrix AS (
        SELECT
            email,
            employee_name,
            week_start_date + day_offset AS absence_date,
            categorize_absence(TRIM(REGEXP_SUBSTR(cell_value, '^[^|]+'))) AS absence_type,
            TO_NUMBER(TRIM(REGEXP_SUBSTR(cell_value, '[^|]+$', 1, 1))) AS hours
        FROM (
            SELECT email, employee_name, week_start_date, monday AS cell_value, 0 AS day_offset FROM stg_exam_absence
            WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED'
            UNION ALL SELECT email, employee_name, week_start_date, tuesday, 1 FROM stg_exam_absence
            WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED'
            UNION ALL SELECT email, employee_name, week_start_date, wednesday, 2 FROM stg_exam_absence
            WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED'
            UNION ALL SELECT email, employee_name, week_start_date, thursday, 3 FROM stg_exam_absence
            WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED'
            UNION ALL SELECT email, employee_name, week_start_date, friday, 4 FROM stg_exam_absence
            WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED'
        ) unpvt
        WHERE cell_value IS NOT NULL
        )
        SELECT
            dim_date.date_id,
            dim_emp.employee_id,
            NULL,
            NULL,
            dim_abs.absence_type_id,
            matrix.hours,
            'absence',
            'absence - ' || dim_abs.absence_type_name
        FROM normalized_matrix matrix
        JOIN tgt_dim_absence_type dim_abs ON matrix.absence_type = dim_abs.absence_type_name
        JOIN tgt_dim_date dim_date ON matrix.absence_date = dim_date.full_date
        JOIN tgt_dim_employee dim_emp
            ON matrix.email = dim_emp.employee_email
            AND dim_date.full_date BETWEEN dim_emp.valid_from AND NVL(dim_emp.valid_to, TIMESTAMP '9999-12-31 23:59:59.999999999');

        DBMS_OUTPUT.PUT_LINE('Finished matrix processing ' || SQL%ROWCOUNT || ' records processed.');
        
        UPDATE stg_exam_absence
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'PROCESSED'
        WHERE process_status = 'PENDING' OR process_status = 'DIM-PROCESSED';
    END process_matrix;

    PROCEDURE run_data_processing IS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Running data processor procedures...');

        process_timesheet;
        process_training_attendance;
        process_absences;
        process_matrix;

        DBMS_OUTPUT.PUT_LINE('Data processor procedures completed.');
        DBMS_OUTPUT.PUT_LINE('----------------------------------------');
    END run_data_processing;

END data_processor;
/