import pandas as pd

class AttendanceExcel:
    SUMMARY_SECTION = '1. Summary'
    PARTICIPANTS_SECTION = '2. Participants'
    ACTIVITIES_SECTION = '3. In-Meeting Activities'

    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path, header=None)
        
        self.summary_df, self.participants_df, self.activities_df = self.split_excel()

    def find_section_row(self, label):
        for i in range(len(self.df)):
            if self.df.iloc[i][0] == label:
                return i

    def split_excel(self):
        summary_row = self.find_section_row(self.SUMMARY_SECTION)
        participants_row = self.find_section_row(self.PARTICIPANTS_SECTION)
        activities_row = self.find_section_row(self.ACTIVITIES_SECTION)

        participants_header_row = participants_row + 1
        activities_header_row = activities_row + 1

        participants_end_row = activities_row
        activities_end_row = len(self.df)

        summary_df = self.df.iloc[summary_row+1:participants_row - 1, [0,1]].reset_index(drop=True)
        summary_df.columns = ['Field', 'Value']

        participants_header = self.df.iloc[participants_header_row].tolist()
        participants_df = self.df.iloc[participants_header_row+1:participants_end_row - 1].reset_index(drop=True)
        participants_df.columns = participants_header

        activities_header = self.df.iloc[activities_header_row].tolist()
        activities_df = self.df.iloc[activities_header_row+1:activities_end_row].reset_index(drop=True)
        activities_df.columns = activities_header

        return summary_df, participants_df, activities_df