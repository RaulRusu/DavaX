--  View: toate activitățile unui angajat într-o zi
CREATE OR REPLACE VIEW vw_employee_at_day AS
SELECT 
  e.employee_name,
  TO_CHAR(d.full_date, 'YYYY-MM-DD') AS activity_date,
  f.activity_type,
  f.hours
FROM tgt_fact_employee_activity f
JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
JOIN tgt_dim_date d ON f.date_id = d.date_id;
   

--  View: toti angajatii intr-o luna
CREATE OR REPLACE VIEW vw_monthly_summary AS
SELECT
    e.employee_name,
    e.employee_email,
    d.year_num,
    d.month_num,
    SUM(CASE WHEN f.activity_type = 'work' THEN f.hours ELSE 0 END) AS total_work_hours,
    SUM(CASE WHEN f.activity_type = 'training' THEN f.hours ELSE 0 END) AS total_training_hours,
    COUNT(DISTINCT CASE WHEN f.activity_type = 'absence' THEN d.full_date END) AS total_absence_days,
    SUM(CASE WHEN f.activity_type IN ('work', 'training') THEN f.hours ELSE 0 END) AS total_activity_hours
FROM tgt_fact_employee_activity f
JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
JOIN tgt_dim_date d ON f.date_id = d.date_id
GROUP BY e.employee_name, e.employee_email, d.year_num, d.month_num;


-- View:  mai mult de 12h intr-o zi
CREATE OR REPLACE VIEW vw_over_legal_hours AS
SELECT 
  e.employee_name,
  TO_CHAR(d.full_date, 'YYYY-MM-DD') AS conflict_date,
  SUM(CASE WHEN f.activity_type = 'work' THEN f.hours ELSE 0 END) AS work_hours,
  SUM(CASE WHEN f.activity_type = 'training' THEN f.hours ELSE 0 END) AS training_hours,
  SUM(f.hours) AS total_hours
FROM tgt_fact_employee_activity f
JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
JOIN tgt_dim_date d ON f.date_id = d.date_id
WHERE f.activity_type IN ('work', 'training')
GROUP BY e.employee_name, d.full_date
HAVING SUM(f.hours) > 12;

-- View: angajați care au 8h absență + activitate în aceeași zi
CREATE OR REPLACE VIEW vw_absence_conflict AS
SELECT 
  e.employee_name,
  TO_CHAR(d.full_date, 'YYYY-MM-DD') AS conflict_date,
  SUM(CASE WHEN f.activity_type = 'absence' THEN f.hours ELSE 0 END) AS absence_hours,
  SUM(CASE WHEN f.activity_type = 'work' THEN f.hours ELSE 0 END) AS work_hours,
  SUM(CASE WHEN f.activity_type = 'training' THEN f.hours ELSE 0 END) AS training_hours,
  SUM(f.hours) AS total_hours
FROM tgt_fact_employee_activity f
JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
JOIN tgt_dim_date d ON f.date_id = d.date_id
GROUP BY e.employee_name, d.full_date
HAVING SUM(CASE WHEN f.activity_type = 'absence' THEN f.hours ELSE 0 END) >= 8
   AND SUM(CASE WHEN f.activity_type IN ('work', 'training') THEN f.hours ELSE 0 END) > 0;


