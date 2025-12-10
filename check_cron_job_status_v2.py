##Checks cron job status 
#!/usr/bin/env python3

from netmiko import ConnectHandler
import getpass
from datetime import datetime

def main():
    print("=== F5 Cron Job Status Checker ===")

    # Prompt for device info and credentials
    f5_host = input("Enter F5 device IP or hostname: ").strip()
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    # Timestamp for output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"cron_job_status_{timestamp}.txt"

    # Netmiko connection parameters
    device = {
        "device_type": "f5_ltm",
        "host": f5_host,
        "username": username,
        "password": password,
    }

    try:
        print(f"\nConnecting to F5 device: {f5_host} ...")
        conn = ConnectHandler(**device)

        print("Entering bash shell...")
        conn.send_command("run util bash")

        print("\nRunning: crontab -l\n")
        output = conn.send_command("crontab -l")

        # Prepare formatted output with hostname at the top
        header = f"=== Cron Job Status for {f5_host} ===\n\n"
        full_output = header + output

        # Print to screen
        print(full_output)

        # Write to timestamped file
        with open(file_name, "w") as f:
            f.write(full_output)

        print(f"\nOutput written to: {file_name}")

        conn.disconnect()

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
