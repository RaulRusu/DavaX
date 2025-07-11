CREATE or REPLACE PROCEDURE pipeline 
AS
BEGIN
    data_pre_processor.run_pre_processing;

    dimension_manager.run_dimension_management;

    DATA_PROCESSOR.run_data_processing;
END pipeline;

EXEC extract_pck.load_data_from_source;

EXEC PIPELINE;


EXEC DATA_PROCESSOR.process_timesheet;
EXEC DATA_PROCESSOR.process_training_attendance;
EXEC DATA_PROCESSOR.process_absences;
EXEC DATA_PROCESSOR.process_matrix;

SELECT count(*) FROM stg_employee;
SELECT count(*) FROM stg_projects;
SELECT count(*) FROM stg_timesheet;
SELECT count(*) FROM stg_absences;
SELECT count(*) FROM STG_TRAINING_ATTENDANCE;
SELECT count(*) FROM stg_exam_absence;

SELECT count(*) FROM TGT_DIM_EMPLOYEE;
SELECT count(*) FROM TGT_DIM_PROJECT;
SELECT count(*) FROM TGT_DIM_TRAINING;
SELECT count(*) FROM TGT_DIM_ABSENCE_TYPE;
SELECT count(*) FROM TGT_FACT_EMPLOYEE_ACTIVITY;


SELECT * FROM TGT_DIM_ABSENCE_TYPE;

SELECT * FROM TGT_FACT_EMPLOYEE_ACTIVITY;

/

SELECT * FROM stg_employee;
SELECT * FROM stg_projects;
SELECT * FROM stg_timesheet;
SELECT * FROM stg_absences;
SELECT * FROM STG_TRAINING_ATTENDANCE;
SELECT * FROM stg_exam_absence;