from db.db_context import DBContext
from attendace_loader.attendance_loader import AttendanceLoader
from absence_loader.absence_loader import AbsenceLoader
from report.reports import Reports
import pandas as pd

phase1_trainings = "resources/phase1/training_excel"
phase1_absences = "resources/phase1/weekly_matrix_absences"

phase2_trainings = "resources/phase2/training_excel"
phase2_absences = "resources/phase2/weekly_matrix_absences"

def run_phase1():
    with DBContext() as connection:
        attendance_loader = AttendanceLoader(connection)
        attendance_loader.load_attendance(phase1_trainings)

        absence_loader = AbsenceLoader(connection)
        absence_loader.load_absences(phase1_absences)

def run_phase2(): 
    with DBContext() as connection:
        attendance_loader = AttendanceLoader(connection)
        attendance_loader.load_attendance(phase2_trainings)

        absence_loader = AbsenceLoader(connection)
        absence_loader.load_absences(phase2_absences)


run_phase1()

with DBContext() as connection:
    r = Reports(connection)
    # 1. Raport lunar (pe lună și an)
    r.generate_monthly_report(2025, 6)

    # 2. Raport: peste 12h muncă+training pe zi
    r.generate_over_legal_hours()

    # 3. Raport: absență + activitate în aceeași zi
    r.generate_absence_conflict()

    # 4. Raport: ce a făcut un angajat într-o zi
    r.generate_one_day_report("Alin Avram", "2025-06-26")
