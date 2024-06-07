import paramiko
import time
import getpass

def send_config_commands(commands, connection):
    for command in commands:
        connection.send(command + '\n')
        time.sleep(1)  # Adding a delay to ensure command is processed
        while not connection.recv_ready():
            time.sleep(1)  # Adding a delay to wait for the output
        output = connection.recv(65535).decode('utf-8')
        print(output)

def main():
    switch_ip = input("Enter switch IP address: ")
    username = ('admin')
    password = ('password)

    data_vlan = input("Enter data VLAN: ")
    voice_vlan = input("Enter voice VLAN number: ")
    port_range = input("Enter port range: ")

    config_commands = [
        f"config t" ,
        f"interface range GigabitEthernet{port_range}",
        f"switchport access vlan {data_vlan}",
        "switchport mode access",
        f"switchport voice vlan {voice_vlan}",
        "ipv6 nd raguard attach-policy ipv6-nd-client",
        "ipv6 dhcp guard attach-policy ipv6-dhcp-client",
        "authentication control-direction in",
        "authentication event fail action next-method",
        f"authentication event server dead action reinitialize vlan {data_vlan}",
        "authentication event server dead action authorize voice",
        "authentication event server alive action reinitialize",
        "authentication host-mode multi-auth",
        "authentication order dot1x mab",
        "authentication priority dot1x mab",
        "authentication port-control auto",
        "authentication periodic",
        "authentication timer reauthenticate server",
        "authentication timer inactivity server",
        "authentication violation restrict",
        "mab",
        "dot1x pae authenticator",
        "dot1x timeout tx-period 7",
        "dot1x max-reauth-req 1",
        "spanning-tree portfast",
        "end",
        "write mem" ,
    ]

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(switch_ip, username=username, password=password)

        remote_connection = ssh.invoke_shell()
        send_config_commands(config_commands, remote_connection)

        print("Configuration has been applied and saved.")

    except paramiko.AuthenticationException:
        print("Authentication failed.")
    except paramiko.SSHException as sshException:
        print(f"Unable to establish SSH connection: {sshException}")
    except Exception as e:
        print(f"Operation error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()















