import re
import pandas as pd
from datetime import time

rows = []

with open('fs_usage.log', 'r') as f:
    for line in f:
        # Extract timestamp, syscall, file path
        m = re.search(r'(\d{2}:\d{2}:\d{2}\.\d+)\s+(\w+)\s+.*?(/.*?)(\s+\d|$)', line)
        # Extract duration and process at end of line
        proc = re.search(r'\s+(\d+\.\d+)\s+([A-Za-z0-9\.\(\)\-\_\ ]+\.\d+)$', line.strip())

        if m and proc:
            timestamp = m.group(1)
            syscall = m.group(2)
            file = m.group(3).strip()
            duration = float(proc.group(1))
            process = proc.group(2)
            rows.append([timestamp, syscall, file, duration, process])

df = pd.DataFrame(rows, columns=['timestamp', 'syscall', 'file', 'duration', 'process'])

df.to_csv('file_access.csv', index=False)

df['datetime'] = pd.to_datetime(df['timestamp'], format='%H:%M:%S.%f').dt.time

# Suspicious conditions

long_ops = df[df['duration'] > 0.05]

start_work = time(9, 0, 0)
end_work = time(10, 0, 0)

outside_work_hours = df[
    (df['syscall'] == 'write') &
    ((df['datetime'] < start_work) | (df['datetime'] > end_work))
]

known_processes = [
  'Mail', 'Finder', 'fseventsd', 'Code Helper',
  'mds', 'mdworker_shared', 'mds_stores',
  'which', 'logd', 'opendirectoryd',
  'launchd', 'bash', 'ps'
]

def is_known(proc):
    prefix = proc.split('.')[0]
    return any(known in prefix for known in known_processes)
if known_processes:
    suspicious_processes = df[~df['process'].apply(is_known)]
else:
    suspicious_processes = pd.DataFrame()

suspicious_events = pd.concat([long_ops, outside_work_hours, suspicious_processes]).drop_duplicates()
print(f"Long ops count: {len(long_ops)}")
print(f"Suspicious processes count: {len(suspicious_processes)}")


print("Suspicious events found:")
print(suspicious_events[['timestamp', 'syscall', 'file', 'duration', 'process']])
