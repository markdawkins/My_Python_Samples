import subprocess

def run_command(command):
    """Run a shell command."""
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"Command '{command}' executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}': {e}")

def install_vsftpd():
    """Install VSFTPD and perform basic configuration."""
    # Update the package list
    run_command("sudo apt update")

    # Install VSFTPD
    run_command("sudo apt install vsftpd -y")

    # Backup the original configuration file
    run_command("sudo cp /etc/vsftpd.conf /etc/vsftpd.conf.bak")

    # Configure VSFTPD settings
    vsftpd_config = """
local_enable=YES
write_enable=YES
pasv_enable=YES
pasv_min_port=10000
pasv_max_port=10100
chroot_local_user=YES
anonymous_enable=NO
    """
    
    # Write the configuration to the vsftpd.conf file
    with open('/etc/vsftpd.conf', 'a') as config_file:
        config_file.write(vsftpd_config)
        print("VSFTPD configuration updated successfully.")

    # Restart VSFTPD to apply the changes
    run_command("sudo systemctl restart vsftpd")

    # Enable VSFTPD to start on boot
    run_command("sudo systemctl enable vsftpd")

    # Allow FTP traffic through the firewall
    run_command("sudo ufw allow 20/tcp")
    run_command("sudo ufw allow 21/tcp")
    run_command("sudo ufw allow 10000:10100/tcp")

if __name__ == "__main__":
    install_vsftpd()

#####Dont forget to make the  file to be executable  chmod +x install_vsftpd.py
#####sudo python3 install_vsftpd.py



