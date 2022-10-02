#!/usr/bin/env python

import getpass
import sys
import telnetlib


LIST = input("Enter List Name:")
listname = "/LISTS/%s.txt"  % LIST
f = open (listname)


HOST = input("Enter host name")
user = input("Enter your telnet username: ")
password = getpass.getpass()



# USE AS REFERENCE TO PICK HOSTS FROM LIST ##
#for line in f:
#    host = line 
#    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
#    rep = os.system( 'ping ' + host)
#    if rep == 0: 
#	    output=('Server is up: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))
	    
 #   else:
 #	    output=('Server is down: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))





tn = telnetlib.Telnet(HOST)

tn.read_until("Username: ")
tn.write(user + "\n")
if password:
    tn.read_until("Password: ")
    tn.write(password + "\n")

tn.write("conf t\n")

tn.write("hostname TEST " + "\n")
tn.write("logging host 10.10.10.10" + "\n")

tn.write("end\n")
tn.write("exit\n")
tn.write("wr mem\n")

print tn.read_all()
