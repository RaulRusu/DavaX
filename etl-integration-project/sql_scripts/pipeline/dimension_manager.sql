CREATE or REPLACE PACKAGE dimension_manager AS
    -- Procedure to manage dimensions
    PROCEDURE manage_employee_scd2;
    PROCEDURE manage_projects;
    PROCEDURE manage_trainings;
    PROCEDURE manage_absence_types;
    PROCEDURE populate_tgt_dim_date;

    PROCEDURE run_dimension_management;
END dimension_manager;
/

CREATE OR REPLACE PACKAGE BODY dimension_manager AS

    PROCEDURE manage_employee_scd2 AS
        row_count NUMBER := 0;
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting SCD Type 2 management for employee dimension...');

        -- 1. Insert all new records from the staging table into the dimension table
        INSERT INTO tgt_dim_employee (
            employee_name, employee_email, department, manager_id, experience_level,
            original_id, valid_from, valid_to, is_current
        )
        SELECT
            s.employee_name, s.employee_email, s.department, s.manager_id, s.experience_level,
            s.employee_id, s.updated_at, NULL, 'Y'
        FROM stg_employee s
        WHERE s.process_status = 'PENDING';
        
        row_count := SQL%ROWCOUNT;

        -- Mark the staging records as processed
        UPDATE stg_employee
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'DIM-PROCESSED'
        WHERE process_status = 'PENDING';


        -- 2. Expire all but the most recent record for each employee
        -- Set valid_to to the next newer updated_at minus 1 second (for timestamp granularity)
        UPDATE tgt_dim_employee t
        SET
            t.valid_to = (
                SELECT MIN(t2.valid_from) - INTERVAL '1' SECOND
                FROM tgt_dim_employee t2
                WHERE t2.original_id = t.original_id
                AND t2.valid_from > t.valid_from
            ),
            t.is_current = 'N'
        WHERE EXISTS (
            SELECT 1 FROM tgt_dim_employee tw
            WHERE tw.original_id = t.original_id
            AND tw.valid_from > t.valid_from
        );

        -- 3. Set the latest version per employee as current, valid_to as NULL
        UPDATE tgt_dim_employee t
        SET
            t.is_current = 'Y',
            t.valid_to = NULL
        WHERE (t.original_id, t.valid_from) IN (
            SELECT original_id, MAX(valid_from)
            FROM tgt_dim_employee
            GROUP BY original_id
        );

        DBMS_OUTPUT.PUT_LINE('Finished SCD Type 2 management '|| row_count || ' records processed for employee dimension.');
    END manage_employee_scd2;

    PROCEDURE manage_projects AS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting project dimension management...');

        -- Insert new projects into the dimension table
        INSERT INTO tgt_dim_project (project_id, project_name, project_code)
        SELECT s.project_id, s.project_name, s.project_code
        FROM stg_projects s
        WHERE s.process_status = 'PENDING' AND
            NOT EXISTS (SELECT 1 FROM tgt_dim_project t
                        WHERE t.project_id = s.project_id);

        -- Mark the staging records as processed
        UPDATE stg_projects
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'DIM-PROCESSED'
        WHERE process_status = 'PENDING';

        DBMS_OUTPUT.PUT_LINE('Finished project dimension management '|| SQL%ROWCOUNT || ' records processed.');
    END manage_projects;

    PROCEDURE manage_trainings AS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting training dimension management...');

        INSERT INTO tgt_dim_training (training_name, instructor, training_duration)
        SELECT
            s.training_name,
            -- Instructor: employee with role "Organizer" (arbitrarily picks MIN if multiple organizers)
            MIN(CASE WHEN s.training_role = 'Organizer' THEN s.employee_name END) AS instructor,
            -- Duration: average difference between last_leave and first_join (in minutes)
            AVG(
                (TO_DATE(s.last_leave, 'MM/DD/YY, HH:MI:SS PM') - TO_DATE(s.first_join, 'MM/DD/YY, HH:MI:SS PM')) * 24 * 60
            ) AS training_duration_minutes
        FROM stg_training_attendance s
        WHERE s.process_status = 'PENDING'
            AND NOT EXISTS (
                SELECT 1 FROM tgt_dim_training t
                WHERE t.training_name = s.training_name
            )
        GROUP BY s.training_name;

        -- Mark the staging records as processed
        UPDATE stg_training_attendance
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'DIM-PROCESSED'
        WHERE process_status = 'PENDING';

        DBMS_OUTPUT.PUT_LINE('Finished training dimension management '|| SQL%ROWCOUNT || ' records processed.');
    END manage_trainings;

    PROCEDURE populate_tgt_dim_date IS
        v_start_date DATE := DATE '1970-01-01';
        v_end_date   DATE := DATE '2050-12-31';
        v_cur_date   DATE;
        v_date_id    NUMBER := 1;
    BEGIN
        v_cur_date := v_start_date;

        WHILE v_cur_date <= v_end_date LOOP
            INSERT INTO tgt_dim_date (
                date_id,
                full_date,
                day_of_week,
                month_num,
                year_num
            ) VALUES (
                v_date_id,
                v_cur_date,
                TO_CHAR(v_cur_date, 'Day', 'NLS_DATE_LANGUAGE=ENGLISH'),
                EXTRACT(MONTH FROM v_cur_date),
                EXTRACT(YEAR FROM v_cur_date)
            );
            v_cur_date := v_cur_date + 1;
            v_date_id  := v_date_id + 1;
        END LOOP;
    END;

    PROCEDURE manage_absence_types AS
        row_count NUMBER := 0;
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting absence type management...');
        -- Insert new absence types into the dimension table
        INSERT INTO tgt_dim_absence_type (absence_type_name)
        SELECT DISTINCT s.absence_type
        FROM stg_absences s
        WHERE s.process_status = 'PENDING' 
                AND NOT EXISTS (SELECT 1 FROM tgt_dim_absence_type t
                          WHERE t.absence_type_name = s.absence_type);
            
        row_count := SQL%ROWCOUNT;

        -- Mark the staging records as processed
        UPDATE stg_absences
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'DIM-PROCESSED'
        WHERE process_status = 'PENDING';

        INSERT INTO tgt_dim_absence_type (absence_type_name)
        SELECT DISTINCT
            unpvt.absence_type
        FROM (
            SELECT weekday_name, day_value, categorize_absence(TRIM(REGEXP_SUBSTR(day_value, '^[^|]+'))) AS absence_type
            FROM stg_exam_absence
            UNPIVOT (
                day_value FOR weekday_name IN (
                    monday     AS 'Monday',
                    tuesday    AS 'Tuesday',
                    wednesday  AS 'Wednesday',
                    thursday   AS 'Thursday',
                    friday     AS 'Friday'
                )
            )
            where process_status = 'PENDING'
        ) unpvt
        WHERE day_value IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM tgt_dim_absence_type t
            WHERE t.absence_type_name = unpvt.absence_type);
        
        -- Mark the staging records as processed
        UPDATE stg_exam_absence
        SET processed_ts = CURRENT_TIMESTAMP,
            process_status = 'DIM-PROCESSED'
        WHERE process_status = 'PENDING';

        row_count := row_count + SQL%ROWCOUNT;
        DBMS_OUTPUT.PUT_LINE('Finished absence type management '|| row_count || ' records processed for absences.');
    END manage_absence_types;

    PROCEDURE run_dimension_management AS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting dimension management...');

        -- Run all dimension management procedures
        manage_employee_scd2;
        manage_projects;
        manage_trainings;
        manage_absence_types;

        DBMS_OUTPUT.PUT_LINE('Finished dimension management.');
        DBMS_OUTPUT.PUT_LINE('----------------------------------------');
    END run_dimension_management;
END dimension_manager;