#!/usr/bin/env python

import getpass
import sys
import telnetlib


#LIST = input("Enter List Name:")
#listname = "./LISTS/%s.txt"  % LIST
#f = open (listname)


HOST = input("Enter host name: ")
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

tn.read_until(b"Username: ")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")

tn.write(b"conf t\n")

tn.write(b"hostname R1\n")
tn.write(b"no logging host 10.10.10.10\n")

tn.write(b"end\n")
tn.write(b"exit\n")
tn.write(b"wr mem\n")

print(tn.read_all().decode('ascii'))

###TESTED AND VERIFIED TO WORK ###
