from datetime import timedelta
import os
import pandas as pd


def split_event(row):
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

def to_file(df, name):
    output_dir = os.path.join(script_dir, 'steps')
    os.makedirs(output_dir, exist_ok=True)

    fname = f"{output_dir}/{name}.csv"
    df.to_csv(fname)

# Load the CSV file
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'merged_confluence.csv')

df = pd.read_csv(csv_path)

# Parse datetime columns
df['Start_Time'] = pd.to_datetime(df['Start_Time'], format='mixed')
df['End_Time'] = pd.to_datetime(df['End_Time'], format='mixed')

# Remove rows where 'Summary' is blank or just whitespace
df['Summary'] = df['Summary'].astype(str).str.strip()
df = df[df['Summary'] != ""]

all_events = []
for idx, row in df.iterrows():
    all_events.extend(split_event(row))

exploded_df = pd.DataFrame(all_events)

to_file(exploded_df, 'exploded_events')

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

to_file(pivot, 'weekly_events')

weekly_dataframes = [
    week_df
    for week, week_df in pivot.groupby('Start_Date')
]

output_dir = os.path.join(script_dir, 'weekly_reports')
os.makedirs(output_dir, exist_ok=True)

for week_df in weekly_dataframes:
    # Get year and ISO week from Start_Date (all rows in the week have the same Start_Date)
    start_date = week_df['Start_Date'].iloc[0]
    year, week, _ = start_date.isocalendar()
    filename = f"report_{year}_week_{week}.csv"
    path = os.path.join(output_dir, filename)
    week_df.to_csv(path, index=False)
    print(f"Saved {filename}")