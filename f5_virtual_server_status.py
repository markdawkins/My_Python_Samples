import paramiko
import getpass

def get_virtual_server_status(hostname, username, password, virtual_name):
    command = f"tmsh show ltm virtual {virtual_name}"

    try:
        # SSH setup
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password, timeout=10)

        # Execute command
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Check for errors
        if "was not found" in output or error:
            print(f"❌ Virtual server '{virtual_name}' not found or error occurred.")
            if error:
                print("Error:", error.strip())
            return

        # Parse and print result
        print(f"\n✅ Status for virtual server '{virtual_name}':\n")
        for line in output.splitlines():
            if "Availability" in line or "State" in line:
                print(line.strip())

    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    hostname = input("Enter F5 hostname or IP: ")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    virtual_name = input("Enter the virtual server name: ")

    get_virtual_server_status(hostname, username, password, virtual_name)
