import random
from datetime import datetime, timedelta

def generate_synthetic_log(num_entries=500):
    users = [f"USER_{i:03d}" for i in range(1, 20)]
    temp_accounts = [f"TEMP_ACC_{i:03d}" for i in range(1, 10)]
    temp_admins = [f"TEMP_ADMIN_{i}" for i in range(1, 5)]
    sys_ops = [f"SYS_OP_{i:02d}" for i in range(1, 5)]
    files = [
        "/data/HR/employee_records.xlsx",
        "/data/Finance/Q3_Budget.xlsx",
        "/data/Legal/contracts.docx",
        "/data/IT/system_config.conf"
    ]
    ips = [
        "198.51.100.25",  # TEST-NET-2 reserved IP
        "203.0.113.45",   # TEST-NET-3 reserved IP
        "192.0.2.1"       # TEST-NET-1 reserved IP
    ]

    log_levels = ["Information", "Warning", "Error", "Critical"]
    sources = ["Security", "Network", "User Management"]
    event_ids = {
        "Logon": 4624,
        "LogonFailed": 4625,
        "AccountLocked": 4740,
        "SpecialLogon": 4672,
        "ProcessCreation": 4688,
        "UserCreated": 4720,
        "ObjectAccess": 4663,
        "AuditCleared": 1102,
        "Cryptography": 36887,
        "Logoff": 4634
    }
    task_categories = {
        4624: "Logon",
        4625: "Logon",
        4740: "User Account Management",
        4672: "Special Logon",
        4688: "Process Creation",
        4720: "User Account Management",
        4663: "Object Access",
        1102: "Audit Log Cleared",
        36887: "Cryptography",
        4634: "Logoff"
    }

    base_time = datetime(2025, 6, 27, 22, 0, 0)
    logs = []

    for i in range(num_entries):
        delta = timedelta(seconds=random.randint(30, 600))
        current_time = base_time + delta * i
        time_str = current_time.strftime("%Y-%m-%d,%H:%M:%S")

        event_type = random.choices(
            population=["Logon", "LogonFailed", "AccountLocked", "SpecialLogon", "ProcessCreation",
                        "UserCreated", "ObjectAccess", "AuditCleared", "Cryptography", "Logoff"],
            weights=[20, 5, 2, 5, 10, 3, 15, 2, 3, 15],
            k=1
        )[0]

        event_id = event_ids[event_type]
        task_cat = task_categories[event_id]
        log_level = random.choices(
            population=log_levels,
            weights=[60, 25, 10, 5],
            k=1
        )[0]
        source = random.choice(sources)

        if event_type == "Logon":
            user = random.choice(users)
            message = f"User {user} successfully logged in."
        elif event_type == "LogonFailed":
            user = random.choice(temp_accounts)
            message = f"Failed logon attempt for account {user}."
        elif event_type == "AccountLocked":
            user = random.choice(temp_accounts)
            message = f"Account {user} locked due to multiple failed logons."
        elif event_type == "SpecialLogon":
            user = random.choice(sys_ops)
            message = f"Special privileges assigned to user {user}."
        elif event_type == "ProcessCreation":
            process = random.choice([
                "powershell.exe with encoded command",
                "cmd.exe /c net user TEMP_ADMIN /add",
                "7zip.exe to compress files",
                "curl.exe to upload data"
            ])
            message = f"Suspicious process created: {process}."
        elif event_type == "UserCreated":
            user = random.choice(temp_admins)
            message = f"Temporary admin account {user} added."
        elif event_type == "ObjectAccess":
            file = random.choice(files)
            message = f"Access attempt on file: {file}."
        elif event_type == "AuditCleared":
            user = random.choice(temp_admins)
            message = f"Audit log cleared by user {user}."
        elif event_type == "Cryptography":
            ip = random.choice(ips)
            message = f"Suspicious TLS connection attempt to external IP {ip}."
        elif event_type == "Logoff":
            user = random.choice(users + sys_ops)
            message = f"User {user} logged off."
        else:
            message = "Generic event."

        logs.append(f"{time_str},{log_level},{source},{event_id},{task_cat},{message}")

    return logs

def save_logs_to_txt(log_lines, filename="synthetic_logs.txt"):
    with open(filename, "w") as f:
        f.write("Date,Time,LogLevel,Source,EventID,TaskCategory,Message\n")  # header
        for line in log_lines:
            f.write(line + "\n")
def read_logs_in_chunks(filename, chunk_size=5):
    """
    Generator that reads 'chunk_size' lines at a time from a file.
    """
    with open(filename, "r") as f:
        # Skip header
        header = f.readline().strip()
        chunk = []
        for line in f:
            chunk.append(line.strip())
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk  # yield any remaining lines

if __name__ == "__main__":
     for i, chunk in enumerate(read_logs_in_chunks("synthetic_logs.txt", chunk_size=5)):
        print(f"--- Chunk {i+1} ---")
        for line in chunk:
            print(line)
