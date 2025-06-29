import random
from datetime import datetime, timedelta

def generate_anomalous_logs(num_entries=30):
    actors = ["JSmith", "MLopez", "Admin", "TempUser", "Intern"]
    files = [
        "C:\\HR\\EmployeeData.xlsx",
        "C:\\Finance\\Q3_Budget.xlsx",
        "\\\\Server\\Legal\\Client_Acquisition.docx"
    ]
    ips = ["198.51.100.25", "203.0.113.45", "192.0.2.15"]
    event_types = [
        "Logon", "Failed Logon", "Process Creation", "Object Access",
        "Audit Log Cleared", "Suspicious Connection", "Account Lockout"
    ]

    base_date = datetime.now().date()  # just the date
    log_lines = ["Date,Time,LogLevel,Source,EventID,TaskCategory,Message"]

    for i in range(num_entries):
        # Pick after-hours:
        if random.choice(["early", "late"]) == "early":
            # Before 9 AM: random time between 12:00 AM and 8:59 AM
            hour = random.randint(0, 8)
            minute = random.randint(0, 59)
        else:
            # After 5 PM: random time between 5:01 PM and 11:59 PM
            hour = random.randint(17, 23)
            minute = random.randint(0, 59)

        second = random.randint(0, 59)
        timestamp = datetime.combine(base_date, datetime.min.time()) + timedelta(
            hours=hour, minutes=minute, seconds=second
        )

        actor = random.choice(actors)
        file = random.choice(files)
        ip = random.choice(ips)
        event_type = random.choice(event_types)

        if event_type == "Logon":
            message = f"A logon was successfully performed. User: {actor}."
            level = "Information"
            event_id = 4624
        elif event_type == "Failed Logon":
            message = f"An account failed to log on. Account: {actor}."
            level = "Warning"
            event_id = 4625
        elif event_type == "Process Creation":
            message = f"User {actor} launched a suspicious process."
            level = "Warning"
            event_id = 4688
        elif event_type == "Object Access":
            message = f"User {actor} accessed sensitive file: {file}."
            level = "Information"
            event_id = 4663
        elif event_type == "Audit Log Cleared":
            message = f"The audit log was cleared by user {actor}."
            level = "Error"
            event_id = 1102
        elif event_type == "Suspicious Connection":
            message = f"A suspicious connection was made to IP: {ip} by {actor}."
            level = "Error"
            event_id = 36887
        elif event_type == "Account Lockout":
            message = f"A user account was locked out. Account: {actor}."
            level = "Error"
            event_id = 4740
        else:
            message = "Unknown event."
            level = "Information"
            event_id = 0

        line = f"{timestamp.date()},{timestamp.time().strftime('%H:%M:%S')},{level},Security,{event_id},{event_type},{message}"
        log_lines.append(line)

    return "\n".join(log_lines)


def write_logs_to_file(filename="after_hours_anomalies.txt", num_entries=800):
    logs = generate_anomalous_logs(num_entries)
    with open(filename, "w") as f:
        f.write(logs)
    print(f"✅ Anomalous log file with {num_entries} after-hours entries written to {filename}")

import re

def anonymize_log_line(line):
    # Replace user names (e.g., TEMP_ADMIN_1)
    line = re.sub(r'User TEMP_ADMIN_\d+', 'User [REDACTED_USER]', line)
    # Replace IP addresses
    line = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[REDACTED_IP]', line)
    # Replace file paths
    line = re.sub(r'/data/[^\s,]+', '/data/[REDACTED_FILE]', line)
    return line
def anonymize_file(input_path, output_path):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            anonymized_line = anonymize_log_line(line)
            outfile.write(anonymized_line)
if __name__ == "__main__":
    anonymize_file('anomalies.txt', 'anomalies_anonymized.txt')


   
