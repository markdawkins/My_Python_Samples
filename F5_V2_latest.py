import paramiko
import time
import getpass

def connect_and_get_cron(host, username, password):
    try:
        # Initialize the SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=username, password=password)
        print("Connected successfully.")

        # Start an interactive shell session
        shell = client.invoke_shell()
        time.sleep(1)  # Give it a moment to be ready

        # Clear initial output
        if shell.recv_ready():
            shell.recv(1000)

        # Enter bash
        shell.send("bash\n")
        time.sleep(1)

        # Run crontab -l
        shell.send("crontab -l\n")
        time.sleep(2)

        # Read the output
        output = ""
        while shell.recv_ready():
            output += shell.recv(1000).decode()

        print("\n--- Cron Jobs Output ---\n")
        print(output)

    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials.")
    except paramiko.SSHException as ssh_exception:
        print(f"SSH connection error: {ssh_exception}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()
        print("Connection closed.")

if __name__ == "__main__":
    f5_host = input("Enter the F5 host IP or hostname: ")
    f5_username = input("Enter your username: ")
    f5_password = getpass.getpass("Enter your password: ")

    connect_and_get_cron(f5_host, f5_username, f5_password)
