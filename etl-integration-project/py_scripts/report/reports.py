import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

class Reports:
    def __init__(self, connection):
        self.conn = connection
        print("✅ Conexiune reușită!")
        self.output_path = os.path.join(os.path.expanduser("~"), "OneDrive - ENDAVA", "Desktop","Reports")
        os.makedirs(self.output_path, exist_ok=True) 

    def _generate_pdf(self, df, title, filename_prefix):
        if df.empty:
            print(f"⚠️ {title} — fără rezultate.")
            return

        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Times", 'B', 12)

        # Titlu central
        pdf.set_y(pdf.get_y() + 10)
        pdf.cell(0, 10, title, align='C', ln=1)
        pdf.ln(5)

        # === Lățimi proporționale care încap mereu ===
        pdf.set_font("Times", 'B', 8)
        page_width = pdf.w - 2 * pdf.l_margin
        padding = 4

        # Estimează lățimea relativă a fiecărei coloane
        lengths = []
        for col in df.columns:
            max_text = max([str(col)] + [str(v) for v in df[col]], key=len)
            lengths.append(len(max_text))

        total_length = sum(lengths)
        col_widths = [(length / total_length) * page_width for length in lengths]

        # Centrează tabelul
        table_width = sum(col_widths)
        start_x = pdf.l_margin + (page_width - table_width) / 2

        header_row_height = 10
        row_height = 8

        # Antet tabel
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Times", 'B', 8)
        pdf.set_x(start_x)
        for i, col in enumerate(df.columns):
            pdf.cell(col_widths[i], header_row_height, str(col).replace("_", " ").title(), border=1, align='C', fill=True)
        pdf.ln()

        # Rânduri tabel
        pdf.set_font("Times", '', 9)
        for _, row in df.iterrows():
            pdf.set_x(start_x)
            for i, col in enumerate(df.columns):
                val = row[col]
                text = f"{val:.1f}h" if 'hours' in col.lower() else str(val)
                align = 'L' if col_widths[i] > 35 else 'C'
                pdf.cell(col_widths[i], row_height, text, border=1, align=align)
            pdf.ln()

        # Salvare PDF
        timestamp = datetime.now().strftime("%Y-%m-%d_at_%H-%M")
        filename = f"{filename_prefix}_generated_on_{timestamp}.pdf"
        filepath = os.path.join(self.output_path, filename)
        pdf.output(filepath)
        print(f"✅ PDF saved: {filepath}")

    def generate_monthly_report(self, year, month):
        query = """
            SELECT * FROM vw_monthly_summary
            WHERE year_num = :1 AND month_num = :2
            ORDER BY employee_name
        """
        df = pd.read_sql(query, self.conn, params=[year, month])
        self._generate_pdf(df, f"Monthly Employee Report - {month:02d}/{year}", "monthly_report")

    def generate_over_legal_hours(self):
        query = "SELECT * FROM vw_over_legal_hours ORDER BY conflict_date, employee_name"
        df = pd.read_sql(query, self.conn)
        self._generate_pdf(df, "Employees exceeding 12h of work + training per day", "over_legal_hours_report")

    def generate_absence_conflict(self):
        query = "SELECT * FROM vw_absence_conflict ORDER BY conflict_date, employee_name"
        df = pd.read_sql(query, self.conn)
        self._generate_pdf(df, "Employees marked absent but also active (work/training) on the same day", "absence_conflict_report")

    def generate_one_day_report(self, employee_name, activity_date):
        query = """
            SELECT * FROM vw_employee_at_day
            WHERE employee_name = :1 AND activity_date = :2
            ORDER BY activity_type
        """
        df = pd.read_sql(query, self.conn, params=[employee_name, activity_date])
        self._generate_pdf(df, f"Activities of {employee_name} on {activity_date}", f"employee_day_activity_{employee_name.replace(' ', '_')}_{activity_date}")
