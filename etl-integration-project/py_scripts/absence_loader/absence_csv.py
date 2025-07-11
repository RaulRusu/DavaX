import pandas as pd

class AbsenceCSV:
    def __init__(self, file_path):
        self.file_path = file_path
        self.absences_df = self.load_absences_data()
        self.clean_absences_data()

    def load_absences_data(self):
        # Load the CSV data into a DataFrame
        return pd.read_csv(self.file_path)

    def clean_absences_data(self):
        self.absences_df.where(pd.notnull(self.absences_df), None, inplace=True)
