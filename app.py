import logging
from flask import Flask, request, send_file, render_template, jsonify
from fpdf import FPDF
import json
from datetime import datetime
import io

app = Flask(__name__, template_folder='./templates')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Hardcoded dictionary for special Saturday schedules
special_saturdays = {
    "2024-07-20T00:00:00": "THU" 
}

# Function to find the day from the date and identify periods marked as U or A
def find_days_and_periods(data):
    result = []
    for record in data['classAttendance']:
        date_str = record['hattdate']
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT00:00:00")
        day_of_week = date_obj.strftime("%A")
        
        # Check for special Saturday schedules
        if date_str in special_saturdays:
            day_of_week = f"{special_saturdays[date_str]} (SATURDAY)"
        print(record.items())
        periods_marked = {k: v for k, v in record.items() if v in ["U", "A"]}
        
        result.append({
            'date': date_str,
            'day_of_week': day_of_week,
            'periods_marked': periods_marked
        })
    return result

# Function to match periods with classes and find subjects marked as absent
def find_absent_subjects(attendance_data, schedule_data):
    subjects_absent = {}
    for attendance in attendance_data:
        day_of_week = attendance['day_of_week']
        periods_marked = attendance['periods_marked']
        # Strip off the " (SATURDAY)" part for comparison
        comparison_day = day_of_week.split()[0].upper()

        for class_hour in schedule_data['classesHours']:
            if class_hour['sttdaydesc'][:3].upper() == comparison_day[:3]:
                for period, status in periods_marked.items():
                    period_key = period.replace("hatthouR", "stthouR") + "DESC"
                    if period_key in class_hour and class_hour[period_key]:
                        subject_code = class_hour[period_key].split()[0]
                        if subject_code not in subjects_absent:
                            subjects_absent[subject_code] = []
                        subjects_absent[subject_code].append({
                            'date': attendance['date'],
                            'day_of_week': day_of_week,
                            'period': period.replace("hatthouR", "Hour "),
                            'status': status
                        })

    return subjects_absent

# Create PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Attendance Report', 0, 1, 'C')

    def chapter_title(self, subject):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, subject, 0, 1, 'L')
        self.ln(5)

    def table(self, headers, data):
        self.set_font('Arial', 'B', 10)
        col_width = self.w / 5.5  # distribute columns evenly
        row_height = self.font_size + 2
        for header in headers:
            self.cell(col_width, row_height, header, border=1)
        self.ln(row_height)
        self.set_font('Arial', '', 10)
        for row in data:
            for item in row:
                self.cell(col_width, row_height, str(item), border=1)
            self.ln(row_height)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        attendance_json = request.form['attendance_json']
        schedule_json = request.form['schedule_json']
        
        # Parse JSON data
        try:
            attendance_data = json.loads(attendance_json)
        except json.JSONDecodeError as json_err:
            logging.error("Error decoding attendance JSON: %s", json_err)
            return jsonify({"error": "Invalid attendance JSON format"}), 400

        try:
            schedule_data = json.loads(schedule_json)
        except json.JSONDecodeError as json_err:
            logging.error("Error decoding schedule JSON: %s", json_err)
            return jsonify({"error": "Invalid schedule JSON format"}), 400
        
        # Process data
        processed_data = find_days_and_periods(attendance_data)
        absent_subjects = find_absent_subjects(processed_data, schedule_data)
        
        # Define table headers
        headers = ["Date", "Day", "Period", "Status"]
        
        # Create an instance of the PDF class
        pdf = PDF()
        pdf.add_page()
        
        for subject, records in absent_subjects.items():
            pdf.chapter_title(subject)
            pdf.table(headers, [
                [record['date'], record['day_of_week'], record['period'], record['status']]
                for record in records
            ])
        
        # Create a BytesIO object to save the PDF in memory
        pdf_output = io.BytesIO()
        
        # Output the PDF to the BytesIO object
        pdf_str = pdf.output(dest='S').encode('latin1')
        pdf_output.write(pdf_str)
        
        # Move the cursor to the beginning of the BytesIO object
        pdf_output.seek(0)
        
        # Send the file
        return send_file(pdf_output, mimetype='application/pdf', as_attachment=True, download_name="attendance_report.pdf")
    
    except Exception as e:
        logging.error("Error: %s", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
