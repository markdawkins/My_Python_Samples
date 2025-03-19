
import paramiko
import getpass

def get_pool_members(hostname, username, password, pool_name):
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"\n[+] Connecting to {hostname}...")
        ssh.connect(hostname, username=username, password=password)

        # Construct command to run inside bash
        tmsh_cmd = f"bash -c 'tmsh list ltm pool {pool_name}'"

        print(f"[+] Entering bash and searching for pool '{pool_name}'...")
        stdin, stdout, stderr = ssh.exec_command(tmsh_cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()

        if error or "was not found" in output:
            print(f"\n[!] Pool '{pool_name}' not found or error occurred.")
            print(f"Details: {error.strip() if error else output.strip()}")
        else:
            print(f"\n=== Pool Info: {pool_name} ===")
            print(output)

    except paramiko.AuthenticationException:
        print("[!] Authentication failed.")
    except Exception as e:
        print(f"[!] An error occurred: {e}")


if __name__ == "__main__":
    print("=== F5 Pool Lookup Tool ===")
    host = input("F5 Host/IP: ")
    user = input("Username: ")
    passwd = getpass.getpass("Password: ")
    pool = input("Enter the pool name (e.g., my_pool): ")

    get_pool_members(host, user, passwd, pool)
