#!/usr/bin/env python
from getpass import getpass
import time
from netmiko import ConnectHandler


username = input("Enter username: ")
password = getpass()

#LIST = input("Enter List Name:")
#REPORT = input("Enter Report Name:")
#reportname = "./REPORTS/%s.txt" % REPORT
#listname = "./LISTS/%s.txt"  % LIST
listname = "./LISTS/proxmox_routers.txt"
#print ("Writing output to REPORTS directory...")
time.sleep(1)

#file = open(reportname , 'w')

f = open (listname)

for line in f:
    host = line.strip()
    iosv_l2 = {
             'device_type':'cisco_ios',
             'ip':host,
             'username': username,
             'password': password,
           }

    net_connect = ConnectHandler(**iosv_l2)
    net_connect.send_command_timing('conf t\n')
    #print (output0)
    #file.write (output0)
    net_connect.send_command_timing(' no ntp server 132.163.96.5 source GigabitEthernet 1 prefer\n')
    
    #file.write (output1) 
    net_connect.send_command_timing('end\n')
    net_connect.send_command_timing('wr mem\n')
    output0 = net_connect.send_command_timing('show run | inc hostname \n')

    print(" ")
    print("The device tracking configuration has been updated for device " +  output0[8:20] + " " + host )
    print (" ")

    #file.close()
 
#file.close()

print ("Update completed for all devices...")
time.sleep(1)
