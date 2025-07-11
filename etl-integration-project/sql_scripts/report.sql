-----------------------------------111111111111111111111111111111111-----------------------------
-- Rezolvat prima chestie
CREATE OR REPLACE PROCEDURE employee_at_day(p_name IN VARCHAR2, p_date IN DATE)
IS
BEGIN
    EXECUTE IMMEDIATE 'SELECT e.employee_name, d.full_date, f.activity_type, f.hours
    FROM tgt_fact_employee_activity f
    JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
    JOIN tgt_dim_date d ON f.date_id = d.date_id
    WHERE e.employee_name = :p_name AND
        d.full_date = :p_date'
    USING p_name, p_date;
END employee_at_day;

SELECT e.employee_name, d.full_date, f.activity_type, f.hours
    FROM tgt_fact_employee_activity f
    JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
    JOIN tgt_dim_date d ON f.date_id = d.date_id
    WHERE e.employee_name = 'Alin Avram' AND
        d.full_date = TO_DATE('2025-06-26', 'YYYY-MM-DD');

EXEC employee_at_day('Alin Avram', TO_DATE('2025-06-26', 'YYYY-MM-DD'));

--activități multiple în aceeași zi 
SELECT
  e.employee_name,
  d.full_date,
  MAX(CASE WHEN f.activity_type = 'absence' THEN 1 ELSE 0 END) AS has_absence,
  MAX(CASE WHEN f.activity_type = 'training' THEN 1 ELSE 0 END) AS has_training,
  MAX(CASE WHEN f.activity_type = 'work' THEN 1 ELSE 0 END) AS has_work,
  CASE
    WHEN COUNT(*) > 1 THEN 'MULTIPLE_ACTIVITIES'
    ELSE NULL
  END AS conflict_flag
FROM tgt_fact_employee_activity f
JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
JOIN tgt_dim_date d ON f.date_id = d.date_id
GROUP BY e.employee_name, d.full_date
HAVING COUNT(*) > 1;


--Total ore de muncă per lună, per angajat
SELECT
  e.employee_name,
  d.year_num,
  d.month_num,
  SUM(f.hours) AS total_work_hours
FROM tgt_fact_employee_activity f
JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
JOIN tgt_dim_date d ON f.date_id = d.date_id
WHERE f.activity_type = 'work'
GROUP BY e.employee_name, d.year_num, d.month_num
ORDER BY d.year_num, d.month_num, e.employee_name;


--Raport lunar comparativ: work vs training vs absence

SELECT
  e.employee_name,
  d.year_num,
  d.month_num,
  SUM(CASE WHEN f.activity_type = 'work' THEN f.hours ELSE 0 END) AS work_hours,
  SUM(CASE WHEN f.activity_type = 'training' THEN f.hours ELSE 0 END) AS training_hours,
  SUM(CASE WHEN f.activity_type = 'absence' THEN f.hours ELSE 0 END) AS absence_hours,
  SUM(CASE WHEN f.activity_type IN ('work', 'training', 'absence') THEN f.hours ELSE 0 END) AS total_hours
FROM tgt_fact_employee_activity f
JOIN tgt_dim_employee e ON f.employee_id = e.employee_id
JOIN tgt_dim_date d ON f.date_id = d.date_id
GROUP BY e.employee_name, d.year_num, d.month_num
ORDER BY d.year_num, d.month_num, e.employee_name;