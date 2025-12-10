#This script checks that staatus of cronjobs on F5

#!/usr/bin/env python3

from netmiko import ConnectHandler
import getpass

def main():
    print("=== F5 Cron Job Status Checker ===")

    # Prompt for device info and credentials
    f5_host = input("Enter F5 device IP or hostname: ").strip()
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    # Netmiko connection parameters
    device = {
        "device_type": "f5_ltm",
        "host": f5_host,
        "username": username,
        "password": password,
    }

    try:
        # Connect to the F5
        print("\nConnecting to F5 device...")
        conn = ConnectHandler(**device)

        # Enter bash mode
        print("Entering bash shell...")
        conn.send_command("run util bash")

        # Run crontab -l
        print("\nRunning: crontab -l\n")
        output = conn.send_command("crontab -l")

        # Display output to screen
        print(output)

        # Write output to a file
        file_name = "cron_job_status.txt"
        with open(file_name, "w") as f:
            f.write(output)

        print(f"\nCron job output written to: {file_name}")

        # Disconnect
        conn.disconnect()

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
