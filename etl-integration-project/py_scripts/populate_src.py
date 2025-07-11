from db.db_context import DBContext
import pandas as pd;

BASE_PATH = "resources/src_data/"
EMPLOYEE_DATA_CSV_PATH = BASE_PATH + "Employees.csv"
PROJECT_DATA_CSV_PATH = BASE_PATH + "Projects.csv"
TIMESHEET_DATA_CSV_PATH = BASE_PATH + "Timesheets.csv"
ABSENCE_DATA_CSV_PATH = BASE_PATH + "Absences.csv"

def populate_employee_data(context : DBContext):
    df = pd.read_csv(EMPLOYEE_DATA_CSV_PATH)
    cursor = context.cursor()
    print("Starting to populate employee data...")
    for index, row in df.iterrows():
        sql = f"""
        INSERT INTO src_employee (
            employee_id,
            employee_name,
            employee_email,
            department,
            experience_level,
            employee_location,
            manager_id,
            updated_at
        ) VALUES (
            {index + 1},
            '{row['Name']}', 
            '{row['Email']}', 
            '{row['Department']}', 
            '{row['Experience_level']}', 
            '{row['Location']}', 
            {'NULL' if row['Manager_ID'] == 0 else int(row['Manager_ID'])}, 
            TO_DATE('13-JUL-23', 'DD-MON-YY')
        )"""

        cursor.execute(sql)
    context.commit()
    print("Finished populating employee data.")

def populate_project_data(context : DBContext):
    df = pd.read_csv(PROJECT_DATA_CSV_PATH)
    cursor = context.cursor()
    print("Starting to populate project data...")
    cursor = context.cursor()
    for index, row in df.iterrows():
        sql = f"""
        INSERT INTO src_projects (
            project_id,
            project_name,
            project_code,
            updated_at
        ) VALUES (
            {index + 1},
            '{row['Project_Name']}',
            '{row['Project_Code']}',
            TO_DATE('13-JUL-23', 'DD-MON-YY')
        )"""

        cursor.execute(sql)
    context.commit()
    print("Finished populating project data.")

def populate_timesheet_data(context : DBContext):
    df = pd.read_csv(TIMESHEET_DATA_CSV_PATH)
    cursor = context.cursor()
    print("Starting to populate timesheet data...")
    for index, row in df.iterrows():
        sql = f"""
        INSERT INTO src_timesheet (
            entry_id,
            employee_id,
            project_id,
            entry_date,
            hours_worked,
            updated_at
        ) VALUES (
            {index + 1},
            {row['Employee_ID']},
            {row['Project_ID']},
            TO_DATE('{row['Entry_Date']}', 'YYYY-MM-DD'),
            {row['Hours_Worked']},
            TO_DATE('13-JUL-23', 'DD-MON-YY')
        )"""
        cursor.execute(sql)
    context.commit()
    print("Finished populating timesheet data.")

def populate_absence_data(context : DBContext):
    df = pd.read_csv(ABSENCE_DATA_CSV_PATH)
    cursor = context.cursor()
    print("Starting to populate absence data...")
    for index, row in df.iterrows():
        sql = f"""
        INSERT INTO src_absences (
            absence_id,
            employee_id,
            absence_type,
            start_date,
            end_date,
            updated_at
        ) VALUES (
            {index + 1},
            {row['Employee_ID']},
            '{row['Absence_Type']}',
            TO_DATE('{row['Start_Date']}', 'YYYY-MM-DD:hh24:mi:ss'),
            TO_DATE('{row['End_Date']}', 'YYYY-MM-DD:hh24:mi:ss'),
            TO_DATE('13-JUL-23', 'DD-MON-YY')
        )"""
        cursor.execute(sql)
    context.commit()
    print("Finished populating absence data.")

with DBContext() as context:
    populate_employee_data(context)
    populate_project_data(context)
    populate_timesheet_data(context)
    populate_absence_data(context)