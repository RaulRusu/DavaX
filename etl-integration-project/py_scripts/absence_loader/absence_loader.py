from absence_loader.absence_csv import AbsenceCSV
import os;
import pandas as pd

class AbsenceLoader:
    def __init__(self, db_context):
        self.db_context = db_context

    def load_absences_data(self, csv_data):
        cursor = self.db_context.cursor()
        absences_df = csv_data.absences_df

        def sql_value(val):
            if pd.isna(val):
                return "NULL"
            return f"""'{str(val).replace("'", "''")}'"""

        for index, row in absences_df.iterrows():
            name = sql_value(row['Name'])
            email = sql_value(row['Email'])
            start_date = f"TO_DATE('{row['Start_Date']}', 'YYYY-MM-DD')"
            monday = sql_value(row['Monday'])
            tuesday = sql_value(row['Tuesday'])
            wednesday = sql_value(row['Wednesday'])
            thursday = sql_value(row['Thursday'])
            friday = sql_value(row['Friday'])
            sql = f"""
            INSERT INTO stg_exam_absence (
                employee_name, email, week_start_date, monday, tuesday, wednesday, thursday, friday, process_status
            ) VALUES (
                {name},
                {email},
                {start_date},
                {monday},
                {tuesday},
                {wednesday},
                {thursday},
                {friday},
                'PENDING'
            )"""
            cursor.execute(sql)
        self.db_context.commit()

    def load_absences(self, directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(directory_path, filename)
                print(f"Processing file: {file_path}")
                csv_data = AbsenceCSV(file_path)
                self.load_absences_data(csv_data)
                print(f"Finished processing file: {file_path}")
                