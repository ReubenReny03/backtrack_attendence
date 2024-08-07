import json
from datetime import datetime
from tabulate import tabulate

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
        
        periods_marked = {k: v for k, v in record.items() if v in ["U", "A"]}
        
        result.append({
            'date': date_str,
            'day_of_week': day_of_week,
            'periods_marked': periods_marked
        })
    print (result)
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
                            'period': period.replace("hatthouR", "Hour "),
                            'status': status,
                            'subject': class_hour[period_key]
                        })
    return subjects_absent

# Path to the JSON file
file_path = './class_attendance.json'

# Sample class schedule data
class_schedule = {"classes":[],"classesHours":[{"sttdaydesc":"MON","stthouR1DESC":"","stthouR2DESC":"20CS2017L Deep Learning Batch 1 - CTC Lab 8","stthouR3DESC":"20CS2017L Deep Learning Batch 1 - CTC Lab 8","stthouR4DESC":"20CS2017 Deep Learning Batch 1 - AI101","stthouR5DESC":"23AE2060 Basics of Aerospace Engineering Batch 1 - AI203","stthouR6DESC":"","stthouR7DESC":"","stthouR8DESC":"","stthouR9DESC":"23MA3001 Logical Reasoning and Soft Skills Batch 4 - ECLH201","stthouR10DESC":"","stthouR11DESC":""},{"sttdaydesc":"TUE","stthouR1DESC":"","stthouR2DESC":"21CS2012 Internet of Things Security Batch 1 - AI001","stthouR3DESC":"20CS3006 Applications of Cyber Physical Systems Batch 2 - AI002","stthouR4DESC":"","stthouR5DESC":"23AE2060 Basics of Aerospace Engineering Batch 1 - AI203","stthouR6DESC":"","stthouR7DESC":"23AI2014 Project Requirement Specification Batch 8 - \tLecture Hall I","stthouR8DESC":"23AI2014 Project Requirement Specification Batch 8 - \tLecture Hall I","stthouR9DESC":"23CS3001 Blockchain Technologies and Applications Batch 2 - AI001","stthouR10DESC":"","stthouR11DESC":""},{"sttdaydesc":"WED","stthouR1DESC":"","stthouR2DESC":"21CS2012 Internet of Things Security Batch 1 - AI001","stthouR3DESC":"23CS3001 Blockchain Technologies and Applications Batch 2 - AI001","stthouR4DESC":"20CS3006 Applications of Cyber Physical Systems Batch 2 - AI002","stthouR5DESC":"23MA3001 Logical Reasoning and Soft Skills Batch 4 - ECLH201","stthouR6DESC":"","stthouR7DESC":"22CS3001 Microservice Architecture Batch 1 - ECE Gallery Hall - I","stthouR8DESC":"20CS2017 Deep Learning Batch 1 - AI101","stthouR9DESC":"","stthouR10DESC":"","stthouR11DESC":""},{"sttdaydesc":"THU","stthouR1DESC":"","stthouR2DESC":"22CS3001 Microservice Architecture Batch 1 - ECE Gallery Hall - I","stthouR3DESC":"22CS3001 Microservice Architecture Batch 1 - ECE Gallery Hall - I","stthouR4DESC":"21CS3013 Data Warehousing and Data Mining Batch 2 - ECE Gallery Hall - I","stthouR5DESC":"21CS3013 Data Warehousing and Data Mining Batch 2 - ECE Gallery Hall - I","stthouR6DESC":"","stthouR7DESC":"23CS3001 Blockchain Technologies and Applications Batch 2 - AI001","stthouR8DESC":"","stthouR9DESC":"","stthouR10DESC":"","stthouR11DESC":""},{"sttdaydesc":"FRI","stthouR1DESC":"","stthouR2DESC":"21CS2012 Internet of Things Security Batch 1 - AI001","stthouR3DESC":"20CS3006 Applications of Cyber Physical Systems Batch 2 - AI002","stthouR4DESC":"20CS2017 Deep Learning Batch 1 - AI101","stthouR5DESC":"23AE2060 Basics of Aerospace Engineering Batch 1 - AI203","stthouR6DESC":"","stthouR7DESC":"21CS3013 Data Warehousing and Data Mining Batch 2 - ECE Gallery Hall - I","stthouR8DESC":"21SE2010 Mentor-(Combined Class) Batch 64 - \tLecture Hall I","stthouR9DESC":"23MA3001 Logical Reasoning and Soft Skills Batch 4 - ECLH201","stthouR10DESC":"","stthouR11DESC":""}],"success":True,"errors":[]}


data = read_data_from_file(file_path)
processed_data = find_days_and_periods(data)
absent_subjects = find_absent_subjects(processed_data, class_schedule)

# Prepare data for tabulation
table_data = []
for record in absent_subjects:
    table_data.append([
        record['date'],
        record['day_of_week'],
        record['period'],
        record['subject'],
        record['status']
    ])

# Define table headers
headers = ["Date", "Day", "Period", "Subject", "Status"]

# Print table
print(tabulate(table_data, headers, tablefmt="grid"))
