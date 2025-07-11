from pipeline.loader.base_db_loader import BaseDBLoader
from sql_builder.base_insert_query_builder import BaseInsertQueryBuilder

class AbsenceDBLoader(BaseDBLoader):
    def __init__(self, db_context):
        super().__init__(db_context, BaseInsertQueryBuilder("stg_exam_absence"))
        self.db_context = db_context

    def load(self, data, _):
        with self.db_context as connection:
            cursor = connection.cursor()
            for index, row in data.iterrows():
                (self.sql_query_builder
                .into(
                    "employee_name", "email", "week_start_date", "monday", "tuesday", 'wednesday', 'thursday', 'friday')
                .values(
                    row['Name'],
                    row['Email'],
                    f"TO_DATE({row['Start_Date']}, 'YYYY-MM-DD HH24:MI:SS')",
                    row['Monday'],
                    row['Tuesday'],
                    row['Wednesday'],
                    row['Thursday'],
                    row['Friday']
                ))
                sql = self.sql_query_builder.build()
                cursor.execute(sql)
            cursor.close()