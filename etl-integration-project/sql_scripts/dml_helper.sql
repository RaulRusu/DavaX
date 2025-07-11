SELECT count(*) FROM src_employee;
SELECT count(*) FROM src_projects;
SELECT count(*) FROM src_timesheet;
SELECT count(*) FROM src_absences;

SELECT * FROM stg_employee;
SELECT * FROM stg_projects;
SELECT * FROM stg_timesheet;
SELECT * FROM stg_absences;
SELECT * FROM STG_TRAINING_ATTENDANCE;
SELECT * FROM stg_exam_absence;

select * from ETL_METADATA;

SELECT * FROM TGT_DIM_EMPLOYEE;
SELECT * FROM TGT_DIM_DATE;
SELECT * FROM TGT_DIM_PROJECT;
SELECT * FROM TGT_DIM_TRAINING;
SELECT * FROM TGT_DIM_ABSENCE_TYPE;
SELECT * FROM TGT_FACT_EMPLOYEE_ACTIVITY;

TRUNCATE TABLE src_employee;
TRUNCATE TABLE src_projects;
TRUNCATE TABLE src_timesheet;
TRUNCATE TABLE src_absences;

TRUNCATE TABLE stg_training_attendance;
TRUNCATE TABLE stg_exam_absence;

TRUNCATE TABLE stg_employee;
TRUNCATE TABLE stg_projects;
TRUNCATE TABLE stg_timesheet;
TRUNCATE TABLE stg_absences;

TRUNCATE TABLE etl_metadata;

TRUNCATE TABLE tgt_dim_employee;
TRUNCATE TABLE tgt_dim_project;
TRUNCATE TABLE tgt_dim_training;
TRUNCATE TABLE tgt_dim_absence_type;
TRUNCATE TABLE tgt_fact_employee_activity;
