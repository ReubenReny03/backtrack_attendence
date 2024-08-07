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
        
        periods_marked = {k: v for k, v in record.items() if v in ["U", "A"]}
        
        result.append({
            'date': date_str,
            'day_of_week': day_of_week,
            'periods_marked': periods_marked
        })
    return result



file_path = './class_attendance.json'  # Assuming the file is saved at this path
data = read_data_from_file(file_path)
processed_data = find_days_and_periods(data)
for each in processed_data:
    print(each['date'],each['day_of_week'],each['periods_marked'])