import paramiko

# F5 device info
F5_HOST = "192.168.1.10"       # IP of the primary F5 device
USERNAME = "admin"
PASSWORD = "your_password"
DEVICE_GROUP = "Sync-Failover-Group"

def run_f5_sync_command(host, username, password, device_group):
    try:
        print(f"Connecting to {host}...")

        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to F5
        ssh.connect(hostname=host, username=username, password=password)

        # Run the config-sync command
        command = f"tmsh run cm config-sync to-group {device_group}"
        print(f"Running sync command: {command}")
        stdin, stdout, stderr = ssh.exec_command(command)

        # Output the result
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()

        if error:
            print(f"Error: {error}")
        else:
            print("Sync output:")
            print(output)

    except Exception as e:
        print(f"Connection or execution failed: {str(e)}")

if __name__ == "__main__":
    run_f5_sync_command(F5_HOST, USERNAME, PASSWORD, DEVICE_GROUP)
