from attendace_loader.attendance_excel import AttendanceExcel
import os;

class AttendanceLoader:
    def __init__(self, db_context):
        self.db_context = db_context

    def load_attendance_data(self, excel_data):
        cursor = self.db_context.cursor()
        participants_df = excel_data.participants_df
        summary_df = excel_data.summary_df
        for index, row in participants_df.iterrows():
            cursor.execute(
                "INSERT INTO stg_training_attendance (employee_name, first_join, last_leave, email, training_name, training_role, process_status) " \
                    "VALUES (:name, :first_join, :last_leave, :email, :training_name, :training_role, 'PENDING')",
                    name=row['Name'],
                    first_join=row['First Join'],
                    last_leave=row['Last Leave'],
                    email=row['Email'],
                    training_name=summary_df['Value'][0],
                    training_role=row['Role']
                )
        self.db_context.commit()

    def load_attendance(self, directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith(".xlsx"):
                file_path = os.path.join(directory_path, filename)
                print(f"Processing file: {file_path}")
                excel_data = AttendanceExcel(file_path)
                self.load_attendance_data(excel_data)
                print(f"Finished processing file: {file_path}")
