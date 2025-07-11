CREATE OR REPLACE PACKAGE data_pre_processor AS
    PROCEDURE clean_staging_employee;
    PROCEDURE clean_staging_training_attendance;
    PROCEDURE clean_staging_absences;
    PROCEDURE clean_staging_exam_absence;

    PROCEDURE run_pre_processing;
END data_pre_processor;
/

CREATE OR REPLACE PACKAGE BODY data_pre_processor AS
    PROCEDURE clean_staging_employee IS
    BEGIN
        UPDATE stg_employee
        SET employee_email = TRIM(LOWER(employee_email))
        WHERE employee_email IS NOT NULL
        AND process_status IN ('PENDING');

        DBMS_OUTPUT.PUT_LINE('Staging employee table cleaned.');
    END clean_staging_employee;

    PROCEDURE clean_staging_training_attendance IS
    BEGIN
        UPDATE stg_training_attendance
        SET employee_name = TRIM(employee_name),
            first_join = TRIM(first_join),
            last_leave = TRIM(last_leave),
            email = TRIM(LOWER(email)),
            training_name = TRIM(training_name),
            training_role = TRIM(training_role)
        WHERE process_status IN ('PENDING');

        DBMS_OUTPUT.PUT_LINE('Staging training attendance table cleaned.');
    END clean_staging_training_attendance;
    
    PROCEDURE clean_staging_absences IS
    BEGIN
        UPDATE stg_absences
        SET absence_type = TRIM(LOWER(absence_type))
        WHERE process_status IN ('PENDING');

        DBMS_OUTPUT.PUT_LINE('Staging absences table cleaned.');
    END clean_staging_absences;

    PROCEDURE clean_staging_exam_absence IS
    BEGIN
        UPDATE stg_exam_absence
        SET email = TRIM(LOWER(email)),
            monday = TRIM(LOWER(monday)),
            tuesday = TRIM(LOWER(tuesday)),
            wednesday = TRIM(LOWER(wednesday)),
            thursday = TRIM(LOWER(thursday)),
            friday = TRIM(LOWER(friday))
        WHERE email IS NOT NULL
        AND process_status IN ('PENDING');

        DBMS_OUTPUT.PUT_LINE('Staging exam absence table cleaned.');
    END clean_staging_exam_absence;

    PROCEDURE run_pre_processing IS
    BEGIN
        DBMS_OUTPUT.PUT_LINE('Starting pre-processing...');

        clean_staging_employee;
        clean_staging_training_attendance;
        clean_staging_absences;
        clean_staging_exam_absence;

        DBMS_OUTPUT.PUT_LINE('All staging tables pre-processed successfully.');
        DBMS_OUTPUT.PUT_LINE('----------------------------------------');
    END run_pre_processing;
END data_pre_processor;
/