import os
import csv
import warnings
import numpy as np
import pandas as pd
from netmiko import ConnectHandler
import time
from getpass import getpass
from datetime import datetime
subname = datetime.now().strftime("%Y%m%d-%H%M%S")
#logdate = datetime.now().strftime("%b")

# Suppress specific warnings from numpy
warnings.filterwarnings("ignore", category=UserWarning, module="numpy")

# Prompt user for the host IP address
host_ip = input("Enter the switch IP address: ")
username = input("Enter the username: ")
password = input("Enter switch password: ")
# Define device information
device = {
    'device_type': 'cisco_ios',
    'host': host_ip,
    'username': username,
    'password': password,
    'secret': 'your_enable_password',  # If enable password is needed
}

#FILENAME  this builds the file name to be used to name the css file
#Ideal File Equation: Final file name = Host ip + port map + time + file extension
FILENAME = host_ip + subname + '_port_map.csv'

# File path
output_directory = '/home/mark/switch_reports/port_maps'
output_file = os.path.join(output_directory, FILENAME)
# Ensure the directory exists
os.makedirs(output_directory, exist_ok=True)

# Connect to the device
net_connect = ConnectHandler(**device)
net_connect.enable()  # Enter enable mode

# Run the command
output = net_connect.send_command("show interfaces status")

# Disconnect from the device
net_connect.disconnect()

# Process the output
lines = output.splitlines()

# Extract headers (assuming the second line contains the headers)
headers = lines[1].split()

# Extract data
data = []
for line in lines[2:]:
    if line.strip():
        row = line.split()
        # Pad the row if it has fewer columns than the headers
        while len(row) < len(headers):
            row.append("")
        # Truncate the row if it has more columns than the headers
        row = row[:len(headers)]
        data.append(row)

# Create a pandas DataFrame and save to CSV
df = pd.DataFrame(data, columns=headers)
df.to_csv(output_file, index=False)

print(f"Data has been saved to {output_file}")
