import csv
import subprocess
import time
from datetime import datetime

INPUT_FILE = "ping_targets.csv"
OUTPUT_FILE = "ping_targets_output.csv"
PING_COUNT = 5
PING_INTERVAL = 300  # 5 minutes in seconds

def read_targets(file_path):
    """Reads IP addresses or hostnames from CSV file."""
    targets = []
    try:
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0].strip():
                    targets.append(row[0].strip())
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    return targets

def ping_target(target):
    """Pings the target and returns output and status."""
    try:
        result = subprocess.run(
            ["ping", "-c", str(PING_COUNT), target],
            capture_output=True,
            text=True
        )
        success = result.returncode == 0
        return result.stdout.strip(), "Success" if success else "Failed"
    except Exception as e:
        return str(e), "Error"

def write_output(target, status, output):
    """Writes ping results to CSV with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(OUTPUT_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, target, status, output])

def main():
    # Initialize output CSV with headers
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Target", "Status", "Ping Output"])

    targets = read_targets(INPUT_FILE)
    if not targets:
        print("No targets found in ping_targets.csv")
        return

    while True:
        for target in targets:
            output, status = ping_target(target)
            write_output(target, status, output)
        print("Ping round completed")
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()
