#!/usr/bin/env python
import csv
import socket
import sys
import os
import time 
from datetime import datetime
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

username = input('Enter your SSH username: ')
password = getpass()

x = input("Give starting number:")
y = input("Give ending number: ")

x = int(x)  # parse string into an integer
y = int(y)  # parse string into an integer

subname = datetime.now().strftime("%Y%m%d-%H%M%S")
filename = "/REPORTS/SYCAMORE/WIRELESS_USERS_REPORT"+ subname + ".csv" 

print ("Writing output to REPORTS directory...")
time.sleep(1)

file = open(filename , 'w')

for a in range (x,y):
	HOST =  socket.getfqdn("10.26." + str(a) + ".2")
	ios_device = {
        'device_type': 'cisco_ios',
        'ip': HOST,
        'username': username,
        'password': password
    }

	try:
		net_connect = ConnectHandler(**ios_device)
	except (AuthenticationException):
		print ('Authentication failure: ' + HOST)
		continue
	except (NetMikoTimeoutException):
		print ('Timeout to device: ' + HOST)
		continue
	except (EOFError):
		print ('End of file while attempting device ' + HOST)
		continue
	except (SSHException):
		print ('SSH Issue. Are you sure SSH is enabled? ' + HOST)
		continue
	except Exception as unknown_error:
		print ('Some other error: ' + str(unknown_error) )
		continue

	output0 = net_connect.send_command('show run | inc hostname')
	output1 = net_connect.send_command('show  mac address-table int gig 1/0/47')
	output2 = net_connect.send_command('show run | inc location')
	time.sleep(.5)
	print (output0[11:20])
	print (" ")
	print (output1)
	print (" ")
	#print (output2[20:75] + '\n')
	file.write('\n')
	file.write(output0[11:20])
	file.write('\n')
	file.write(output1)
	#file.write(output2[21:75] + '\n')
	file.write('\n')
	time.sleep(.5)
