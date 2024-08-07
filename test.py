import json
from datetime import datetime

# Function to read data from file
def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to find the day from the date and identify periods marked as U or A
def find_days_and_periods(data):
    result = []
    for record in data['classAttendance']:
        date_str = record['hattdate']
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT00:00:00")
        day_of_week = date_obj.strftime("%A")
        
        periods_marked = {k: v for k, v in record.items() if v in ["A"]}
        
        result.append({
            'date': date_str,
            'day_of_week': day_of_week,
            'periods_marked': periods_marked
        })
    return result

# Function to match periods with classes and find subjects marked as absent
def find_absent_subjects(attendance_data, schedule_data):
    subjects_absent = []
    for attendance in attendance_data:
        day_of_week = attendance['day_of_week']
        periods_marked = attendance['periods_marked']
        
        for class_hour in schedule_data['classesHours']:
            if class_hour['sttdaydesc'][:3].upper() == day_of_week[:3].upper():
                for period, status in periods_marked.items():
                    period_key = period.replace("hatthouR", "stthouR") + "DESC"
                    if period_key in class_hour and class_hour[period_key]:
                        subjects_absent.append({
                            'date': attendance['date'],
                            'day_of_week': day_of_week,
                            'subject': class_hour[period_key]
                        })
    return subjects_absent

# Path to the JSON file
file_path = './class_attendance.json'

# Sample class schedule data
class_schedule = {
    "classes": [],
    "classesHours": [
        {"sttdaydesc": "MON", "stthouR1DESC": "", "stthouR2DESC": "18CS2027 C# and .NET Programming Batch 1 - CSLH001", "stthouR3DESC": "", "stthouR4DESC": "20CS2010 Cryptography and Network Security Batch 1 - CSLH001", "stthouR5DESC": "20CS2044 Reinforcement Learning Batch 1 - CSLH001", "stthouR6DESC": "", "stthouR7DESC": "21CS3006 Cyber Forensics Batch 1 - CSLH007", "stthouR8DESC": "", "stthouR9DESC": "18ME2060 Industrial Safety Engineering Batch 2 - MELH006", "stthouR10DESC": "23CS2911 CS Certification I Batch 1 - \tLecture Hall I", "stthouR11DESC": ""},
        {"sttdaydesc": "TUE", "stthouR1DESC": "", "stthouR2DESC": "18CS2028 C# and .NET Programming Lab Batch 1 - CTC Lab 18", "stthouR3DESC": "18CS2028 C# and .NET Programming Lab Batch 1 - CTC Lab 18", "stthouR4DESC": "18CS3085 Soft computing Batch 1 - CSLH001", "stthouR5DESC": "20CS2010 Cryptography and Network Security Batch 1 - CSLH001", "stthouR6DESC": "", "stthouR7DESC": "21CS2014 MLOps Batch 1 - CSLH101", "stthouR8DESC": "21CS3006 Cyber Forensics Batch 1 - CSLH007", "stthouR9DESC": "20CS2044 Reinforcement Learning Batch 1 - CSLH001", "stthouR10DESC": "21CS2015 MLOps LAB Batch 2 - \tLecture Hall I", "stthouR11DESC": ""},
        {"sttdaydesc": "WED", "stthouR1DESC": "", "stthouR2DESC": "20CS2010L Cryptography and Network Security Batch 4 - CTC Lab 13 ", "stthouR3DESC": "", "stthouR4DESC": "18CS2027 C# and .NET Programming Batch 1 - CSLH001", "stthouR5DESC": "18ME2060 Industrial Safety Engineering Batch 2 - MELH006", "stthouR6DESC": "", "stthouR7DESC": "20CS2010 Cryptography and Network Security Batch 1 - CSLH001", "stthouR8DESC": "21CS2014 MLOps Batch 1 - CSLH101", "stthouR9DESC": "20CS2044 Reinforcement Learning Batch 1 - CSLH001", "stthouR10DESC": "23CS2996 Project Work Batch 2 - \tLecture Hall I", "stthouR11DESC": ""},
        {"sttdaydesc": "THU", "stthouR1DESC": "", "stthouR2DESC": "20CS2010L Cryptography and Network Security Batch 4 - CTC Lab 13 ", "stthouR3DESC": "20CS2010L Cryptography and Network Security Batch 4 - CTC Lab 13 ", "stthouR4DESC": "18CS3085 Soft computing Batch 1 - CSLH001", "stthouR5DESC": "20CS2010 Cryptography and Network Security Batch 1 - CSLH001", "stthouR6DESC": "", "stthouR7DESC": "18CS2027 C# and .NET Programming Batch 1 - CSLH001", "stthouR8DESC": "19CS2009 Project Preparation  Batch 2 - \tLecture Hall I", "stthouR9DESC": "19CS2009 Project Preparation  Batch 2 - \tLecture Hall I", "stthouR10DESC": "21SE2010 Mentor-(Combined Class) Batch 83 - \tLecture Hall I", "stthouR11DESC": ""},
        {"sttdaydesc": "FRI", "stthouR1DESC": "", "stthouR2DESC": "18CS2028 C# and .NET Programming Lab Batch 1 - CTC Lab 18", "stthouR3DESC": "", "stthouR4DESC": "21CS2014 MLOps Batch 1 - CSLH101", "stthouR5DESC": "", "stthouR6DESC": "", "stthouR7DESC": "21CS3006 Cyber Forensics Batch 1 - CSLH007", "stthouR8DESC": "18CS3085 Soft computing Batch 1 - CSLH001", "stthouR9DESC": "18ME2060 Industrial Safety Engineering Batch 2 - MELH006", "stthouR10DESC": "21CS2015 MLOps LAB Batch 2 - \tLecture Hall I", "stthouR11DESC": ""}
    ],
    "success": True,
    "errors": []
}

data = read_data_from_file(file_path)
processed_data = find_days_and_periods(data)
absent_subjects = find_absent_subjects(processed_data, class_schedule)

# Display the result
for record in absent_subjects:
    print(f"Date: {record['date']}, Day: {record['day_of_week']}, Subject: {record['subject']}")
