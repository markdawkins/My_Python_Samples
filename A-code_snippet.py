from datetime import datetime
import csv

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Filter the output lines to only include those starting with "Sys" or "Chassis Serial"
filtered_lines = []
for line in output.splitlines():
    if line.startswith("Sys") or line.startswith("Chassis Serial"):
        filtered_lines.append(line)

with open(log_file, mode="a", newline="") as file:
    writer = csv.writer(file)
    for line in filtered_lines:
        writer.writerow([timestamp, host, line, status])
