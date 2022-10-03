#!/usr/bin/env python

import getpass
import sys
import telnetlib

user = input("Enter your telnet username: ")
password = getpass.getpass()

LIST = input("Enter List Name: ")
listname = "./LISTS/%s.txt"  % LIST
f = open (listname)

for line in f:
    HOST = line
    print ("Configuring Switch") 
    tn = telnetlib.Telnet(HOST)
    
    tn.read_until(b"Username: ")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")

    tn.write(b"conf t\n")

    tn.write(b"hostname TEST\n")
    tn.write(b"logging host 10.10.10.10\n")

    tn.write(b"end\n")
    tn.write(b"exit\n")
    tn.write(b"wr mem\n")

    print(tn.read_all().decode('ascii'))


