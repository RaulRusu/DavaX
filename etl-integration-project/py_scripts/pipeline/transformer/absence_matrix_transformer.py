import pandas as pd
from datetime import timedelta
from pipeline.transformer.multi_output_transformer import MultiOutputTransformer

class AbsenceMatrixTransformer(MultiOutputTransformer):
    def split_event(self, row):
        events = []
        start = row['Start_Time']
        end = row['End_Time']
        summary = row['Summary']
        name = row['Attendee_Name']
        email = row['Attendee_Email']
        
        # For each day the event spans
        curr = start
        while curr.date() <= end.date():
            # First day: from start time, else midnight
            day_start = curr if curr.date() == start.date() else pd.Timestamp.combine(curr.date(), pd.Timestamp.min.time())
            # Last day: to end time, else 23:59:59
            day_end = end if curr.date() == end.date() else pd.Timestamp.combine(curr.date(), pd.Timestamp.max.time())
            hours = (day_end - day_start).total_seconds() / 3600
            hours = min(hours, 8)
            if hours > 0:
                events.append({
                    'Name': name,
                    'Email': email,
                    'Summary': summary,
                    'Day': curr.date(),
                    'Hours': round(hours, 2),
                })
            curr += timedelta(days=1)
        return events
    
    def pivot_data(self, exploded_df):
        exploded_df['Day'] = pd.to_datetime(exploded_df['Day'])
        # Step 1: Assign Start_Date (Monday of the week)
        exploded_df['Start_Date'] = exploded_df['Day'] - pd.to_timedelta(exploded_df['Day'].dt.weekday, unit='d')

        # Step 2: Get weekday name
        exploded_df['Weekday'] = exploded_df['Day'].dt.day_name()

        # Step 3: Build value cell
        exploded_df['Day_Value'] = exploded_df['Summary'] + " | " + exploded_df['Hours'].astype(str)

        # Step 4: Sort and drop duplicates (keep first event per person/email/week/weekday)
        exploded_df = exploded_df.sort_values(['Name', 'Email', 'Start_Date', 'Weekday', 'Day'])
        deduped = exploded_df.drop_duplicates(['Name', 'Email', 'Start_Date', 'Weekday'], keep='first')

        # Step 5: Pivot to weekly view
        pivot = deduped.pivot_table(
            index=['Name', 'Email', 'Start_Date'],
            columns='Weekday',
            values='Day_Value',
            aggfunc='first'
        ).reset_index()

        # Step 6: Ensure weekdays columns are ordered
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        pivot = pivot[['Name', 'Email', 'Start_Date'] + [d for d in weekday_order if d in pivot.columns]]

        return pivot

    def transform(self, data: pd.DataFrame, *args, **kwargs):
        # Parse datetime columns
        data['Start_Time'] = pd.to_datetime(data['Start_Time'], format='mixed')
        data['End_Time'] = pd.to_datetime(data['End_Time'], format='mixed')

        # Remove rows where 'Summary' is blank or just whitespace
        data['Summary'] = data['Summary'].astype(str).str.strip()
        data = data[data['Summary'] != ""]
        print(data.columns)
        all_events = []
        for idx, row in data.iterrows():
            all_events.extend(self.split_event(row))

        exploded_df = pd.DataFrame(all_events)
        pivot = self.pivot_data(exploded_df)

        weekly_dataframes = [
            week_df
            for week, week_df in pivot.groupby('Start_Date')
        ]

        return weekly_dataframes
