CREATE OR REPLACE PACKAGE extract_pck AS
    -- Procedure to load employee data
    PROCEDURE load_employee;

    -- Procedure to load timesheet data
    PROCEDURE load_timesheet;

    -- Procedure to load project data
    PROCEDURE load_projects;

    -- Procedure to load absence data
    PROCEDURE load_absences;

    -- Procedure to load data from source tables into staging tables
    -- This procedure will call the individual load procedures for each staging table
    PROCEDURE load_data_from_source;
END extract_pck;
/

CREATE OR REPLACE PACKAGE BODY extract_pck AS
    PROCEDURE load_employee AS
    BEGIN
        INSERT INTO stg_employee (employee_id, employee_name, employee_email, department, experience_level, employee_location, manager_id, updated_at, process_status)
        SELECT employee_id, employee_name, employee_email, department, experience_level, employee_location, manager_id, updated_at, 'PENDING'
        FROM src_employee
        WHERE updated_at > etl_metadata_pck.get_last_load_timestamp('stg_employee');

        etl_metadata_pck.update_last_load_processed_timestamp('stg_employee', CURRENT_TIMESTAMP);
    END load_employee;


    PROCEDURE load_timesheet AS
    BEGIN
        INSERT INTO stg_timesheet (entry_id, employee_id, project_id, entry_date, hours_worked, updated_at, process_status)
        SELECT entry_id, employee_id, project_id, entry_date, hours_worked, updated_at, 'PENDING'
        FROM src_timesheet
        WHERE updated_at > etl_metadata_pck.get_last_load_timestamp('stg_timesheet');

        etl_metadata_pck.update_last_load_processed_timestamp('stg_timesheet', CURRENT_TIMESTAMP);
    END load_timesheet;


    PROCEDURE load_projects AS
    BEGIN
        INSERT INTO stg_projects (project_id, project_name, project_code, updated_at, process_status)
        SELECT project_id, project_name, project_code, updated_at, 'PENDING'
        FROM src_projects
        WHERE updated_at > etl_metadata_pck.get_last_load_timestamp('stg_projects');

        etl_metadata_pck.update_last_load_processed_timestamp('stg_projects', CURRENT_TIMESTAMP);
    END load_projects;

    PROCEDURE load_absences AS
    BEGIN
        INSERT INTO stg_absences (absence_id, employee_id, absence_type, start_date, end_date, updated_at, process_status)
        SELECT absence_id, employee_id, absence_type, start_date, end_date, updated_at, 'PENDING'
        FROM src_absences
        WHERE updated_at > etl_metadata_pck.get_last_load_timestamp('stg_absences');

        etl_metadata_pck.update_last_load_processed_timestamp('stg_absences', CURRENT_TIMESTAMP);
    END load_absences;

    PROCEDURE load_data_from_source AS
    BEGIN
        load_employee;
        load_timesheet;
        load_projects;
        load_absences;
        DBMS_OUTPUT.PUT_LINE('Data loaded successfully from source tables into staging tables.');
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Error occurred while loading data from source: ' || SQLERRM);
            RAISE;
    END load_data_from_source;

END extract_pck;

